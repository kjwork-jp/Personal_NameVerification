# EXEビルド・配布手順

## 目的

NameVerification v3 を Windows で実行できる EXE としてビルドし、ローカル運用できる状態にする。

## 前提

- Windows 10/11
- Python 3.12
- PowerShell
- GitHubから取得したリポジトリ
- 仮想環境 `.venv` の利用を推奨

## 事前確認

PowerShellで以下を実行する。

```powershell
python --version
```

Python 3.12 系であることを確認する。

## 手動ビルド手順

### 1. 仮想環境を作成

```powershell
python -m venv .venv
```

### 2. 仮想環境を有効化

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. 依存関係をインストール

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 4. 品質ゲートを実行

```powershell
pytest -q
ruff check .
black --check .
mypy app
```

すべて通過してからEXE化する。

### 5. EXEをビルド

```powershell
pyinstaller --clean --noconfirm packaging/NameVerification.spec
```

### 6. 成果物を確認

```text
dist/NameVerification.exe
```

## 一括ビルド手順

PowerShellで以下を実行する。

```powershell
.\scripts\build_exe_windows.ps1
```

このスクリプトは以下を実行する。

1. Pythonバージョン確認
2. dev依存関係インストール
3. 品質ゲート実行
4. 既存build/dist削除
5. PyInstallerでEXE作成

## 起動後確認

EXE起動後、以下を確認する。

- 画面が表示される。
- `ヘルプ / 設定` タブでDB保存先が表示される。
- `検索` タブが開ける。
- `名前を管理` タブが開ける。
- `データ入出力` タブが開ける。

## DB保存先

現時点では、起動ディレクトリ直下の以下を使う。

```text
nameverification.db
```

将来的には、ユーザーデータディレクトリ配下への保存も検討する。

## 配布時の注意

- `dist/NameVerification.exe` を配布する。
- 初回起動時にDBが作成される。
- 重要データ投入前に `データ入出力` タブでバックアップ運用を確認する。
- 既存DBを使う場合は、EXEと同じディレクトリに `nameverification.db` を配置する。

## 既知の制約

- 署名付きインストーラは未対応。
- 自動アップデートは未対応。
- DB保存先変更UIは未対応。
- 完全なUUID移行は未対応。

## 次PR候補

- GitHub ActionsでWindows EXEを自動ビルドする。
- Inno Setup等でインストーラを作成する。
- DB保存先をユーザーデータディレクトリに変更する。
- ヘルプ画面にバージョン表示を追加する。
