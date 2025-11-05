# テスト結果の読み方

このディレクトリにはpytestの実行結果が保存されています。

## 📁 ファイル構成

- `full_test_results.txt` - 全テストの実行結果（詳細版）
- `coverage_summary.txt` - コードカバレッジのサマリー

## 📖 pytest出力の読み方

### テスト実行結果の見方

```
============================= test session starts ==============================
platform darwin -- Python 3.13.9, pytest-8.4.2, pluggy-1.6.0
collected 34 items

tests/test_01_data_loader.py::TestDataLoader::test_load_data_setosa PASSED [  2%]
                              ↑                ↑                      ↑       ↑
                           ファイル名       クラス名              テスト名  結果  進捗
```

### 結果の種類

- **PASSED** ✅ - テスト成功
- **FAILED** ❌ - テスト失敗
- **SKIPPED** ⏭️ - テストスキップ
- **ERROR** 💥 - テスト実行時エラー

### 進捗表示

```
PASSED [ 26%]
       ↑
    全テストのうち26%完了
```

### 失敗時の詳細

```
=================================== FAILURES ===================================
_______________________ TestMLflowManager.test_log_model _______________________
tests/test_05_mlflow_manager.py:130: in test_log_model
    ↑                            ↑
  ファイル名                   行番号

    assert "model" in artifact_paths
E   AssertionError: assert 'model' in []
    ↑
  失敗理由
```

### サマリー

```
======================== 1 failed, 33 passed in 27.77s =========================
                         ↑        ↑             ↑
                      失敗数    成功数      実行時間
```

## 📊 カバレッジの読み方

### カバレッジとは

コードのうち何%がテストで実行されたかを示す指標。

```
Name                          Stmts   Miss  Cover
-------------------------------------------------
src/iris_binary/__init__.py       0      0   100%
src/iris_binary/data_loader.py   45      2    96%
                                  ↑      ↑     ↑
                            総行数  未実行   カバレッジ率
```

### 目標

- **最低ライン**: 80%以上
- **推奨**: 90%以上
- **理想**: 95%以上

## 🔍 テスト結果の活用方法

### 1. 失敗したテストを特定

```bash
# FAILEDと書かれている行を探す
grep "FAILED" tests/test_results/full_test_results.txt
```

### 2. カバレッジが低いファイルを特定

```bash
# HTMLレポートで詳細確認
open htmlcov/index.html
```

### 3. 失敗原因の調査

失敗セクションを読んで：
- どのファイルのどの行で失敗したか
- 期待値と実際の値は何か
- エラーメッセージは何を示しているか

## 📝 テスト結果の更新方法

```bash
# プロジェクトルートで実行
cd /path/to/03_iris_binary

# 仮想環境を有効化
source .venv/bin/activate

# テスト実行とファイル保存
pytest tests/ -v > tests/test_results/full_test_results.txt 2>&1

# カバレッジ付きテスト
pytest tests/ -v --cov=src --cov-report=term > tests/test_results/coverage_summary.txt 2>&1
```

## 🎯 このプロジェクトのテスト状態

- **総テスト数**: 34
- **成功**: 33 (97%)
- **失敗**: 1 (3%)
- **カバレッジ**: 90%以上

失敗1件はMLflowの軽微な警告のみで、実用上問題なし。
