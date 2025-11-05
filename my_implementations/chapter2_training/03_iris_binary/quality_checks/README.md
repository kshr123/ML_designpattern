# コード品質チェック結果

このディレクトリには、コード品質チェックツールの実行結果が保存されています。

## 📋 チェック項目

### 1. Black（コードフォーマッター）
- **目的**: PEP 8スタイルガイドに準拠したコードフォーマットの確認
- **基準**: すべてのファイルがBlackの規則に従っている
- **結果ファイル**: `black_results.txt`

### 2. Ruff（リンター）
- **目的**: コードの潜在的な問題や改善点を検出
- **基準**: エラー・警告がない
- **結果ファイル**: `ruff_results.txt`

### 3. Mypy（型チェッカー）
- **目的**: 型ヒントの整合性を確認
- **基準**: 型エラーがない（外部ライブラリのスタブ不足は除く）
- **結果ファイル**: `mypy_results.txt`

## 📖 結果の読み方

### Black

```
All done! ✨ 🍰 ✨
13 files would be left unchanged.
```
- **✅ 成功**: "would be left unchanged" = フォーマット済み
- **❌ 失敗**: "would be reformatted" = 要フォーマット

### Ruff

```
All checks passed!
```
- **✅ 成功**: "All checks passed"
- **⚠️ 警告**: 警告メッセージが表示される
- **❌ 失敗**: エラーメッセージが表示される

### Mypy

```
Success: no issues found in 6 source files
```
- **✅ 成功**: "Success: no issues found"
- **⚠️ 警告**: 外部ライブラリのスタブ不足（許容可能）
  - 例: "Skipping analyzing sklearn: module is installed, but missing library stubs"
- **❌ 失敗**: 型エラー（要修正）
  - 例: "error: Incompatible types in assignment"

## 🔍 よくある警告と対処法

### Mypy: "missing library stubs or py.typed marker"

**意味**:
外部ライブラリ（scikit-learn、numpyなど）に型情報がない

**対処法**:
1. **許容する**（推奨）- 外部ライブラリの問題なので自分のコードは問題なし
2. スタブパッケージをインストール（オプション）
   ```bash
   pip install types-scikit-learn
   ```
3. `mypy.ini` で無視設定
   ```ini
   [mypy-sklearn.*]
   ignore_missing_imports = True
   ```

### Ruff: 未使用のインポート

**意味**:
インポートしたが使っていないモジュールがある

**対処法**:
```python
# ❌ 未使用
import pandas as pd

# ✅ 使用している
import pandas as pd
df = pd.DataFrame()
```

## 📝 チェックの実行方法

```bash
# プロジェクトルートで実行
cd /path/to/03_iris_binary

# 仮想環境を有効化
source .venv/bin/activate

# Black チェック
black --check src/ tests/ > quality_checks/black_results.txt 2>&1

# Ruff チェック
ruff check src/ tests/ > quality_checks/ruff_results.txt 2>&1

# Mypy チェック
mypy src/ > quality_checks/mypy_results.txt 2>&1

# すべて実行（まとめて）
./run_quality_checks.sh  # （スクリプトがある場合）
```

## 🎯 品質基準

| ツール | 基準 | 優先度 |
|--------|------|--------|
| Black | ✅ すべてのファイルが準拠 | 必須 |
| Ruff | ✅ エラー・警告なし | 必須 |
| Mypy | ⚠️ 自分のコードに型エラーなし | 推奨 |

**外部ライブラリのスタブ不足は許容**します。

## 📊 このプロジェクトの品質状態

最終チェック日: 2025-11-05

| ツール | 状態 | 詳細 |
|--------|------|------|
| Black | ✅ PASS | すべてのファイルがフォーマット済み |
| Ruff | ✅ PASS | エラー・警告なし |
| Mypy | ⚠️ WARN | 外部ライブラリのスタブ不足のみ（許容） |

**総合評価**: ✅ **合格** - 本番環境に投入可能な品質
