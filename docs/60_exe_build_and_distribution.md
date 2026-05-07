# EXEビルド・配布手順

## 目的

NameVerification v3 を Windows で実行できる EXE としてビルドし、ローカル運用できる状態にする。

## 前提

- Windows 10/11
- Python 3.12 以上
- PowerShell
- GitHubから取得したリポジトリ
- 仮想環境 `.venv` の利用を推奨

## 事前確認

PowerShellで以下を実行する。

```powershell
python --version
```

Python 3.12 以上であることを確認する。

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

## GitHub Actionsでのビルド

`.github/workflows/windows-exe.yml` は、Windows runner上で以下を実行する。

1. リポジトリをcheckoutする。
2. Python 3.12をセットアップする。
3. `scripts/build_exe_windows.ps1` で品質ゲートとEXEビルドを実行する。
4. `scripts/package_release_windows.ps1` で配布用zipを作成する。
5. `dist/NameVerification.exe` をartifactとしてアップロードする。
6. `release/NameVerification-windows.zip` をartifactとしてアップロードする。

artifact名:

```text
NameVerification-windows-exe
NameVerification-windows-release-zip
```

## EXE smoke test

EXEビルド後、PowerShellで以下を実行する。

```powershell
.\scripts\smoke_test_exe_windows.ps1
```

このスクリプトは以下を確認する。

1. `dist\NameVerification.exe` が存在すること
2. smoke test用の一時DBパスを作成できること
3. `NAMEVERIFICATION_DB_PATH` でDB保存先を上書きしてEXE起動できること
4. 起動後、一定時間プロセスが生存すること
5. smoke test用DBが作成されること
6. 確認後にEXEプロセスを停止できること

## 配布用zip作成

EXEビルド後、PowerShellで以下を実行する。

```powershell
.\scripts\package_release_windows.ps1
```

このスクリプトは以下を実行する。

1. `dist\NameVerification.exe` が存在することを確認する。
2. `release\NameVerification-windows` を作成し、EXEをコピーする。
3. `README_起動前に読む.txt` を同梱する。
4. `release\NameVerification-windows.zip` を作成する。

生成物:

```text
release/NameVerification-windows.zip
```

## PyInstaller同梱ファイル

`packaging/NameVerification.spec` では、以下をEXEにdataとして同梱する。

- `db/schema.sql`
- `db/migrations`

タイトル/サブタイトル管理画面の互換モジュール `app.ui.old.title_subtitle_management_tab` は、通常のPython import対象としてパッケージに含める。ファイルパスを直接読む方式ではないため、個別data同梱は不要である。

## 起動後確認

EXE起動後、以下を確認する。

- 画面が表示される。
- `ヘルプ / 設定` タブでDB保存先が表示される。
- `検索` タブが開ける。
- `名前を管理` タブが開ける。
- `データ入出力` タブが開ける。

## DB保存先

既定では、起動ディレクトリ直下の以下を使う。

```text
nameverification.db
```

環境変数 `NAMEVERIFICATION_DB_PATH` を指定すると、DB保存先を起動時に上書きできる。

```powershell
$env:NAMEVERIFICATION_DB_PATH = "C:\\path\\to\\nameverification.db"
.\dist\NameVerification.exe
```

`ヘルプ / 設定` タブでは、現在のDB保存先、`NAMEVERIFICATION_DB_PATH` の設定状態、DB保存先コピー、PowerShell用の環境変数コマンドコピーを確認できる。

将来的には、アプリ起動中にDBへ再接続する保存先変更UIも検討する。現時点では安全性を優先し、DB保存先変更は起動前の環境変数指定で行う。

## 配布時の注意

- `dist/NameVerification.exe` を配布する。
- zip配布する場合は `release/NameVerification-windows.zip` を使う。
- 初回起動時にDBが作成される。
- 重要データ投入前に `データ入出力` タブでバックアップ運用を確認する。
- 既存DBを使う場合は、EXEと同じディレクトリに `nameverification.db` を配置するか、`NAMEVERIFICATION_DB_PATH` を指定する。

## 既知の制約

- 署名付きインストーラは未対応。
- 自動アップデートは未対応。
- 起動中のDB保存先変更UIは未対応。
- 完全なUUID移行は未対応。

## 次PR候補

- Inno Setup等でインストーラを作成する。
- DB保存先をユーザーデータディレクトリに変更する。
- ヘルプ画面にバージョン表示を追加する。
