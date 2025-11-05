# テスト結果の読み方

このディレクトリにはpytestの実行結果が保存されています。

## 📖 pytest出力の読み方

### テスト実行結果の見方

```
tests/test_prediction.py::TestPrediction::test_predict_label PASSED [  2%]
                          ↑                 ↑                  ↑       ↑
                       ファイル名        クラス名          テスト名  結果  進捗
```

### 結果の種類

- **PASSED** ✅ - テスト成功
- **FAILED** ❌ - テスト失敗
- **SKIPPED** ⏭️ - テストスキップ
- **ERROR** 💥 - テスト実行時エラー

### サマリー

```
======================== 10 passed in 2.77s =========================
                         ↑           ↑
                      成功数      実行時間
```

### コードカバレッジの見方

```
---------- coverage: platform darwin, python 3.13.0-final-0 ----------
Name                                Stmts   Miss  Cover
-------------------------------------------------------
src/model_in_image/__init__.py          0      0   100%
src/model_in_image/app.py              25      0   100%
src/model_in_image/prediction.py       42      0   100%
-------------------------------------------------------
TOTAL                                  67      0   100%
```

- **Stmts**: コードの総行数
- **Miss**: テストでカバーされていない行数
- **Cover**: カバレッジ率（高いほど良い）

### ファイルの種類

このディレクトリには以下のファイルがあります：

1. **README.md** (このファイル)
   - pytestの出力の読み方ガイド

2. **full_test_results.txt**
   - 全テストの実行結果
   - すべてのテストケースの詳細

3. **full_test_with_coverage.txt**
   - カバレッジ付き全テスト結果
   - コードカバレッジレポート付き

## 💡 Tips

### テスト結果の確認方法

```bash
# テスト結果ファイルを読む
cat tests/test_results/full_test_results.txt

# 失敗したテストのみ抽出
grep "FAILED" tests/test_results/full_test_results.txt

# サマリーのみ表示
tail -n 5 tests/test_results/full_test_results.txt
```

### HTMLカバレッジレポート

詳細なカバレッジレポートは`htmlcov/index.html`で確認できます：

```bash
# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

## 🔍 テスト項目

### test_prediction.py

推論ロジックのテスト：
- ✅ ONNXモデルの読み込み
- ✅ ラベルファイルの読み込み
- ✅ 推論実行（ラベル予測）
- ✅ 推論実行（確率予測）
- ✅ エラーハンドリング

### test_api.py

FastAPI エンドポイントのテスト：
- ✅ ヘルスチェックエンドポイント
- ✅ `/predict/label` エンドポイント（Setosa, Versicolor, Virginica）
- ✅ `/predict/proba` エンドポイント（確率付き予測）
- ✅ バリデーションエラー処理

## 📊 成功基準

以下の条件を満たしていれば、実装は成功とみなされます：

- ✅ 全テストケースがPASSED
- ✅ コードカバレッジが80%以上（目標は100%）
- ✅ 実行時間が10秒以内
- ✅ エラーハンドリングが適切

## 🔗 関連ドキュメント

- [SPECIFICATION.md](../../SPECIFICATION.md) - 仕様書（成功基準の詳細）
- [README.md](../../README.md) - 実装ドキュメント
- [htmlcov/index.html](../../htmlcov/index.html) - HTMLカバレッジレポート
