# テストコードの書き方ガイド

作成日: 2025-11-04

---

## 目次

1. [テストコードとは](#1-テストコードとは)
2. [テストの種類](#2-テストの種類)
3. [テストコードの書き方](#3-テストコードの書き方)
4. [pytestの基本](#4-pytestの基本)
5. [実践例](#5-実践例)
6. [ベストプラクティス](#6-ベストプラクティス)

---

## 1. テストコードとは

**テストコード = コードが正しく動くことを確認するためのコード**

### 最もシンプルな例

```python
# テスト対象の関数（実装コード）
def add(a, b):
    return a + b

# テストコード
def test_add():
    result = add(2, 3)
    assert result == 5  # 結果が5であることを確認
```

`assert`は「〜であることを主張する」という意味。条件が`False`の場合はテストが失敗する。

---

## 2. テストの種類

### ユニットテスト（Unit Test）

**目的**: 個々の関数やクラスが正しく動くか確認

**特徴**:
- 1つの関数・メソッドをテスト
- 外部依存（DB、API等）を持たない
- 高速に実行できる

**例**:
```python
def test_add_project_success(db_session):
    """プロジェクト作成が成功する"""
    project = cruds.add_project(
        db=db_session,
        project_name="test_project",
        description="Test description",
        commit=True,
    )

    assert project.project_id is not None
    assert project.project_name == "test_project"
    assert project.description == "Test description"
```

### 統合テスト（Integration Test）

**目的**: 複数のコンポーネントが連携して正しく動くか確認

**特徴**:
- 複数のレイヤーをまたいでテスト
- データベース、APIなどの実際の連携をテスト
- ユニットテストより遅い

**例**:
```python
def test_create_project(test_client):
    """プロジェクト作成APIが正常に動作する"""
    # APIにリクエストを送る
    response = test_client.post(
        "/projects",
        json={"project_name": "test_project", "description": "Test description"},
    )

    # レスポンスを確認
    assert response.status_code == 200
    data = response.json()
    assert data["project_name"] == "test_project"
    assert "project_id" in data
```

### E2Eテスト（End-to-End Test）

**目的**: システム全体が正しく動くか確認

**特徴**:
- ユーザーの操作を模擬
- 全てのコンポーネントを通してテスト
- 最も遅いが、最も現実に近い

---

## 3. テストコードの書き方

### 3Aパターン（Arrange-Act-Assert）

全てのテストは以下の3つのステップで構成される：

```python
def test_multiply():
    # 1. Arrange（準備）: テストに必要なデータを用意
    a = 3
    b = 4

    # 2. Act（実行）: テスト対象の関数を実行
    result = multiply(a, b)

    # 3. Assert（確認）: 結果が期待通りか確認
    assert result == 12
```

### テストケースの考え方

**テストケース = テストのシナリオ**

例：`add_project()`関数のテストケース

| テストケース | 入力 | 期待する出力 |
|------------|------|-------------|
| 正常系：新規作成 | project_name="test" | 新しいプロジェクトが作成される |
| 正常系：重複 | 既存のproject_name | 既存のプロジェクトが返される |
| 境界値：空文字列 | project_name="" | エラーまたは空文字列で作成 |
| 異常系：必須項目なし | project_name=None | エラーが発生する |

### テストすべき項目

1. **正常系（Happy Path）**: 期待通りの使い方
2. **異常系（Error Path）**: エラーが起きる使い方
3. **境界値（Edge Case）**: 特殊な値（0, 空文字列, None, 最大値等）

---

## 4. pytestの基本

### インストール

```bash
uv pip install pytest pytest-cov
```

### 基本コマンド

```bash
# 全テスト実行
pytest

# 詳細表示
pytest -v

# 特定のファイルだけ
pytest tests/test_cruds.py

# 特定のテストだけ
pytest tests/test_cruds.py::test_add_project_success

# カバレッジ表示
pytest --cov=src

# 失敗したテストだけ再実行
pytest --lf

# 最初の失敗で止める
pytest -x

# 標準出力を表示
pytest -s
```

### fixture（共通のセットアップ）

テストで共通して使うデータやセットアップを定義する：

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.database import Base

@pytest.fixture
def db_session():
    """テスト用データベースセッション"""
    # セットアップ：各テストの前に実行
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)

    db = SessionLocal()
    yield db  # テストにdbを渡す

    # クリーンアップ：各テストの後に実行
    db.close()
    Base.metadata.drop_all(bind=engine)

# 使い方
def test_something(db_session):
    # db_sessionが自動的に渡される
    result = some_function(db_session)
    assert result is not None
```

### アサーション（assert）

```python
# 等価チェック
assert result == expected

# 不等価チェック
assert result != unexpected

# 真偽チェック
assert condition is True
assert condition is False

# Noneチェック
assert value is not None
assert value is None

# 例外チェック
with pytest.raises(ValueError):
    function_that_raises_error()

# 含まれているかチェック
assert "key" in dictionary
assert item in list_items

# 型チェック
assert isinstance(result, str)
```

---

## 5. 実践例

### 例1：基本的な関数のテスト

```python
# 実装
def is_even(n):
    """数値が偶数かどうか判定"""
    return n % 2 == 0

# テスト
def test_is_even_with_even_number():
    """偶数を渡すとTrueが返る"""
    assert is_even(4) == True
    assert is_even(0) == True
    assert is_even(-2) == True

def test_is_even_with_odd_number():
    """奇数を渡すとFalseが返る"""
    assert is_even(3) == False
    assert is_even(1) == False
    assert is_even(-1) == False
```

### 例2：例外のテスト

```python
# 実装
def divide(a, b):
    if b == 0:
        raise ValueError("0で割ることはできません")
    return a / b

# テスト
def test_divide_success():
    """正常な割り算"""
    assert divide(10, 2) == 5
    assert divide(9, 3) == 3

def test_divide_by_zero():
    """0で割るとValueErrorが発生する"""
    with pytest.raises(ValueError):
        divide(10, 0)
```

### 例3：データベースを使うテスト

```python
def test_add_and_select_project(db_session):
    """プロジェクトを作成して取得できる"""
    # Arrange: プロジェクトを作成
    created = cruds.add_project(
        db=db_session,
        project_name="test_project",
        commit=True,
    )

    # Act: IDで取得
    found = cruds.select_project_by_id(
        db=db_session,
        project_id=created.project_id,
    )

    # Assert: 同じプロジェクトが取得できる
    assert found is not None
    assert found.project_id == created.project_id
    assert found.project_name == "test_project"
```

### 例4：APIのテスト

```python
def test_create_project_api(test_client):
    """プロジェクト作成APIのテスト"""
    # Arrange: リクエストデータ
    request_data = {
        "project_name": "test_project",
        "description": "Test description"
    }

    # Act: POSTリクエスト
    response = test_client.post("/projects", json=request_data)

    # Assert: レスポンスを確認
    assert response.status_code == 200
    data = response.json()
    assert data["project_name"] == "test_project"
    assert data["description"] == "Test description"
    assert "project_id" in data
    assert "created_datetime" in data
```

---

## 6. ベストプラクティス

### ✅ すべきこと（DO）

#### 1. テスト名は具体的に

```python
# ✅ Good: 何をテストするか明確
def test_add_project_returns_existing_if_duplicate():
    pass

def test_select_project_by_name_returns_none_if_not_found():
    pass

# ❌ Bad: 何をテストするか不明確
def test_project():
    pass

def test_1():
    pass
```

#### 2. 1つのテストで1つのことをテスト

```python
# ✅ Good: 各テストが1つの側面をテスト
def test_project_has_id():
    project = cruds.add_project(db, "test")
    assert project.project_id is not None

def test_project_has_correct_name():
    project = cruds.add_project(db, "test")
    assert project.project_name == "test"

# ❌ Bad: 1つのテストで複数のことをテスト
def test_project():
    project = cruds.add_project(db, "test")
    assert project.project_id is not None
    assert project.project_name == "test"
    assert project.description is None
    assert project.created_datetime is not None
    # ... 10個以上のアサーション
```

#### 3. エッジケースもテスト

```python
def test_with_normal_input():
    """通常の入力"""
    assert is_positive(5) == True

def test_with_zero():
    """境界値：0"""
    assert is_positive(0) == False

def test_with_negative():
    """負の数"""
    assert is_positive(-5) == False

def test_with_very_large_number():
    """非常に大きな数"""
    assert is_positive(999999999) == True
```

#### 4. テストは独立させる

```python
# ✅ Good: 各テストが独立
def test_create_project_1(db_session):
    project = cruds.add_project(db_session, "project1")
    assert project.project_name == "project1"

def test_create_project_2(db_session):
    # 前のテストに依存しない（新しいdb_session）
    project = cruds.add_project(db_session, "project2")
    assert project.project_name == "project2"

# ❌ Bad: テストが依存している
# （このパターンは避ける）
project_id = None

def test_create():
    global project_id
    project = cruds.add_project(db, "test")
    project_id = project.project_id

def test_get():
    # 前のテストに依存している！
    project = cruds.select_project_by_id(db, project_id)
    assert project is not None
```

#### 5. わかりやすいアサーションメッセージ

```python
# ✅ Good: メッセージ付き
assert len(projects) == 2, f"Expected 2 projects, got {len(projects)}"

# ✅ Good: 明確なアサーション
assert response.status_code == 200
assert "project_id" in response.json()

# ❌ Bad: 何が悪いのか分からない
assert x
```

### ❌ 避けるべきこと（DON'T）

#### 1. テストが実装に依存しすぎ

```python
# ❌ Bad: 内部実装に依存
def test_add_project():
    # 実装の詳細（UUID生成方法）に依存
    assert len(project.project_id) == 6
    assert project.project_id.startswith("a")

# ✅ Good: 外部から見える振る舞いをテスト
def test_add_project():
    assert project.project_id is not None
    assert isinstance(project.project_id, str)
```

#### 2. テストが遅い

```python
# ❌ Bad: 毎回実際のDBに接続
def test_slow():
    db = connect_to_real_database()  # 遅い
    # ...

# ✅ Good: インメモリDBを使う
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")  # 速い
    # ...
```

#### 3. テストが不安定（フレーキー）

```python
# ❌ Bad: ランダム値を使う
import random

def test_unstable():
    value = random.randint(1, 100)  # 毎回違う値
    result = some_function(value)
    assert result > 50  # 時々失敗する

# ✅ Good: 固定値を使う
def test_stable():
    value = 42  # 常に同じ値
    result = some_function(value)
    assert result == expected_value
```

---

## 7. テストの実行と確認方法

### テストを実行する

```bash
# 全テスト実行
pytest

# 出力例:
# ======================== test session starts =========================
# collected 31 items
#
# tests/test_cruds.py ............... [  48%]
# tests/test_api.py ................ [ 100%]
#
# ======================== 31 passed in 0.90s ==========================
```

### 失敗したテストを確認する

```bash
pytest -v

# 出力例（失敗時）:
# tests/test_cruds.py::test_add_project FAILED
#
# ==================== FAILURES ====================
# def test_add_project():
#     result = add_project(db, "test")
# >   assert result.project_name == "expected"
# E   AssertionError: assert 'test' == 'expected'
```

### カバレッジを確認する

```bash
pytest --cov=src --cov-report=term

# 出力例:
# Name                     Stmts   Miss  Cover
# --------------------------------------------
# src/db/cruds.py             84     10    88%
# src/db/models.py            29      0   100%
# src/api/routers/api.py      59      5    92%
# --------------------------------------------
# TOTAL                      235     19    92%
```

---

## 8. 練習問題

### 問題1：基本のテスト

以下の関数に対してテストを書いてください：

```python
def get_grade(score):
    """点数から成績を返す"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"
```

<details>
<summary>解答例</summary>

```python
def test_get_grade_a():
    assert get_grade(95) == "A"
    assert get_grade(90) == "A"

def test_get_grade_b():
    assert get_grade(85) == "B"
    assert get_grade(80) == "B"

def test_get_grade_c():
    assert get_grade(75) == "C"

def test_get_grade_f():
    assert get_grade(50) == "F"
    assert get_grade(0) == "F"

def test_get_grade_boundary():
    """境界値のテスト"""
    assert get_grade(89) == "B"  # Aの1つ下
    assert get_grade(90) == "A"  # Aの最小
```
</details>

### 問題2：例外のテスト

以下の関数に対してテストを書いてください：

```python
def withdraw(balance, amount):
    """口座から出金する"""
    if amount < 0:
        raise ValueError("金額は正の数でなければなりません")
    if amount > balance:
        raise ValueError("残高不足です")
    return balance - amount
```

<details>
<summary>解答例</summary>

```python
def test_withdraw_success():
    """正常な出金"""
    result = withdraw(1000, 500)
    assert result == 500

def test_withdraw_negative_amount():
    """負の金額でエラー"""
    with pytest.raises(ValueError, match="金額は正の数"):
        withdraw(1000, -100)

def test_withdraw_insufficient_balance():
    """残高不足でエラー"""
    with pytest.raises(ValueError, match="残高不足"):
        withdraw(1000, 1500)
```
</details>

---

## まとめ

### テスト作成の手順

1. **テスト対象を決める** - 何をテストするか明確にする
2. **テストケースを考える** - 正常系、異常系、境界値
3. **3Aパターンで書く** - Arrange → Act → Assert
4. **実行して確認** - `pytest -v`
5. **失敗を修正** - エラーメッセージを読んで修正

### 重要なポイント

- **テストは仕様書** - テストを読めば何をするコードか分かる
- **テストは保険** - リファクタリング時に安心できる
- **テストは自動化** - 手動テストより速くて正確
- **小さく書く** - 1つのテストで1つのことをテスト
- **独立させる** - テスト同士が依存しないようにする

---

**次回の学習**:
- 実際にテストを書いてみる（TDDの実践）
- モックやスタブの使い方
- より高度なテスト技法

**参考資料**:
- [pytest公式ドキュメント](https://docs.pytest.org/)
- [Test Driven Development: By Example (Kent Beck)](https://www.amazon.com/dp/0321146530)
