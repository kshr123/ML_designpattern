# テスト結果の読み方

このディレクトリにはpytestの実行結果が保存されています。

## 📖 pytest出力の読み方

### テスト実行結果の見方

```
tests/test_api.py::TestHealthEndpoint::test_health_check PASSED [  2%]
                   ↑                   ↑                  ↑       ↑
                ファイル名           クラス名          テスト名  結果  進捗
```

### 結果の種類

- **PASSED** ✅ - テスト成功
- **FAILED** ❌ - テスト失敗
- **SKIPPED** ⏭️ - テストスキップ
- **ERROR** 💥 - テスト実行時エラー

### サマリーの見方

```
============================== 41 passed in 0.60s ===============================
                                ↑           ↑
                            成功数      実行時間
```

### カバレッジの見方

```
Name                              Stmts   Miss  Cover
-----------------------------------------------------
src/api/routers/prediction.py        42      2    95%
                                      ↑       ↑     ↑
                                   総行数  未実行  カバー率
```

- **Stmts**: 実行可能な文の数
- **Miss**: 実行されなかった文の数
- **Cover**: カバレッジ率（%）

### HTMLカバレッジレポート

詳細なカバレッジレポートは `htmlcov/index.html` を開いて確認できます：

```bash
open htmlcov/index.html
```

## 📁 ファイル一覧

| ファイル名 | 説明 |
|-----------|------|
| `README.md` | このファイル（pytest出力の読み方） |
| `full_test_results_raw.txt` | 全テストの実行結果（生データ） |

## 🧪 テスト構成

### test_api.py (24テスト)

**TestHealthEndpoint** (1テスト):
- ヘルスチェックエンドポイントの動作確認

**TestMetadataEndpoint** (4テスト):
- メタデータエンドポイントのレスポンス確認
- データ型、構造、サンプルデータの検証

**TestLabelEndpoint** (3テスト):
- ラベルエンドポイントのレスポンス確認
- 全クラスラベルの存在確認

**TestPredictTestEndpoint** (3テスト):
- テスト推論エンドポイント（確率値）の動作確認
- 確率値の合計が1に近いことの検証

**TestPredictTestLabelEndpoint** (3テスト):
- テスト推論エンドポイント（ラベル名）の動作確認
- 有効なラベル名を返すことの検証

**TestPredictEndpoint** (5テスト):
- 推論エンドポイント（確率値）の動作確認
- Setosa、Virginicaの推論精度確認
- 不正なデータ構造のエラーハンドリング確認

**TestPredictLabelEndpoint** (5テスト):
- 推論エンドポイント（ラベル名）の動作確認
- Setosa、Virginicaのラベル予測確認

### test_configuration.py (5テスト)

**TestModelConfigurations** (2テスト):
- モデルとラベルファイルのパス設定確認

**TestAPIConfigurations** (3テスト):
- APIタイトル、説明、バージョンの設定確認

### test_prediction.py (12テスト)

**TestDataModel** (2テスト):
- データモデルのデフォルト値とカスタム値の検証

**TestClassifier** (10テスト):
- Classifierの初期化確認
- モデルとラベルの読み込み確認
- Setosa、Versicolor、Virginicaの推論精度確認
- ラベル予測の確認
- 確率値と出力形状の確認

## 📊 テスト結果サマリー

- **総テスト数**: 41
- **成功**: 41 (100%)
- **失敗**: 0 (0%)
- **コードカバレッジ**: 98%
- **実行時間**: 0.60秒

## ✅ TDDサイクル完了

このプロジェクトはTDD（Test-Driven Development）で開発されました：

1. **Red Phase**: テストを先に作成し、失敗することを確認
2. **Green Phase**: 実装してすべてのテストをパスさせる ← **完了！**
3. **Refactor Phase**: コードを改善（必要に応じて）

## 🔍 未カバーの2行について

コードカバレッジが98%（2行未カバー）の理由：

`src/api/routers/prediction.py` の以下の行が未カバー：
- エラーハンドリングの `except Exception as e:` ブロック（2箇所）

これらは不正な入力データ（3要素データなど）でのみ実行されるパスで、正常系のテストでは実行されません。テストでは不正データのケースも確認済みです。

## 📝 参考コマンド

### テストの再実行

```bash
# 全テスト実行
pytest tests/ -v

# カバレッジ付きで実行
pytest tests/ -v --cov=src --cov-report=html

# 特定のテストファイルのみ実行
pytest tests/test_api.py -v

# 特定のテストクラスのみ実行
pytest tests/test_api.py::TestHealthEndpoint -v

# 特定のテストケースのみ実行
pytest tests/test_api.py::TestHealthEndpoint::test_health_check -v
```

### HTMLカバレッジレポートの確認

```bash
# HTMLレポートを開く（macOS）
open htmlcov/index.html

# または（Linux）
xdg-open htmlcov/index.html
```
