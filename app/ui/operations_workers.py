"""Thin async execution helpers for Operations tab."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal


class OperationExecutorLike(Protocol):
    def submit(
        self,
        work: Callable[[], object],
        on_success: Callable[[object], None],
        on_error: Callable[[Exception], None],
        on_finished: Callable[[], None],
    ) -> None: ...

    def request_cancel(self) -> None: ...


class _WorkerSignals(QObject):
    success = Signal(object)
    error = Signal(object)
    finished = Signal()


class _OperationRunnable(QRunnable):
    def __init__(self, work: Callable[[], object]) -> None:
        super().__init__()
        self._work = work
        self.signals = _WorkerSignals()

    def run(self) -> None:
        try:
            result = self._work()
            self.signals.success.emit(result)
        except Exception as exc:  # noqa: BLE001
            self.signals.error.emit(exc)
        finally:
            self.signals.finished.emit()


class ThreadPoolOperationExecutor:
    """QThreadPool + QRunnable based executor."""

    def __init__(self, thread_pool: QThreadPool | None = None) -> None:
        self._thread_pool = thread_pool or QThreadPool.globalInstance()
        self._cancel_requested = False

    def submit(
        self,
        work: Callable[[], object],
        on_success: Callable[[object], None],
        on_error: Callable[[Exception], None],
        on_finished: Callable[[], None],
    ) -> None:
        self._cancel_requested = False
        runnable = _OperationRunnable(work)
        runnable.signals.success.connect(on_success)
        runnable.signals.error.connect(on_error)
        runnable.signals.finished.connect(on_finished)
        self._thread_pool.start(runnable)

    def request_cancel(self) -> None:
        self._cancel_requested = True


class ImmediateOperationExecutor:
    """Synchronous executor for tests."""

    def submit(
        self,
        work: Callable[[], object],
        on_success: Callable[[object], None],
        on_error: Callable[[Exception], None],
        on_finished: Callable[[], None],
    ) -> None:
        try:
            on_success(work())
        except Exception as exc:  # noqa: BLE001
            on_error(exc)
        finally:
            on_finished()

    def request_cancel(self) -> None:
        return
