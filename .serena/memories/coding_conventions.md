# コーディング規約とスタイル

## Python コーディング規約

### スタイルガイド

- **ベース**: PEP 8に準拠
- **行の長さ**: 100文字（black, ruffで設定済み）
- **Pythonバージョン**: 3.13以上

### 命名規則

- **関数/変数**: `snake_case`
- **クラス**: `PascalCase`
- **定数**: `UPPER_CASE`
- **プライベート**: 先頭に `_` (例: `_private_function()`)

### 型ヒント

- **必須**: 可能な限りすべての関数・メソッドに型ヒントを付ける
- **ツール**: mypyでstrict modeでチェック

例:
```python
def calculate_score(data: np.ndarray, threshold: float = 0.5) -> float:
    """スコアを計算する
    
    Args:
        data: 入力データ
        threshold: 閾値（デフォルト: 0.5）
    
    Returns:
        計算されたスコア
    """
    return float(np.mean(data > threshold))
```

### Docstring

- **形式**: Google スタイル
- **必須**: 重要な関数・クラスには必ずdocstringを書く
- **内容**: Args, Returns, Raises（該当する場合）

### インポート順序

1. 標準ライブラリ
2. サードパーティライブラリ
3. ローカルモジュール

各グループはアルファベット順に並べる。

例:
```python
# 標準ライブラリ
import os
from typing import Optional

# サードパーティ
import numpy as np
from fastapi import FastAPI

# ローカル
from .models import Model
from .utils import load_config
```

## ファイル構成

### 必須ファイル

各実装ディレクトリには以下を含める:

1. **`SPECIFICATION.md`**: 仕様書（要件、アーキテクチャ、API設計）
2. **`README.md`**: 実装の説明、セットアップ手順、実行方法
3. **`pyproject.toml`**: プロジェクトメタデータと依存関係
4. **`tests/`**: テストコード
   - `test_unit.py` - ユニットテスト
   - `test_integration.py` - 統合テスト
   - `test_e2e.py` - E2Eテスト（必要に応じて）
5. **`src/{pattern_name}/`**: 実装コード
   - `__init__.py` - パッケージ初期化
   - その他のモジュール

### オプションファイル

- `.python-version` - Pythonバージョンの指定
- `docker-compose.yml` - Docker環境
- `Makefile` - よく使うコマンドのショートカット
- `.env.example` - 環境変数のサンプル

## セキュリティ

### 機密情報の管理

- **環境変数**: APIキー、パスワード等は`.env`ファイルで管理
- **gitignore**: `.env`, `*.pem`, `*.key`等を必ず追加済み
- **入力検証**: 外部からの入力は必ず検証・サニタイズ

### .gitignoreの重要項目

```
.env
.env.local
*.pem
*.key
credentials.json
secrets.yaml
.mcp.json  # MCPトークンを含む
```

## エラーハンドリング

- **例外**: 適切な例外クラスを使用
- **ログ**: エラーは必ずログに記録
- **ユーザーフレンドリー**: エラーメッセージは分かりやすく

例:
```python
import logging

logger = logging.getLogger(__name__)

def process_data(data: str) -> dict:
    try:
        result = parse_data(data)
    except ValueError as e:
        logger.error(f"Failed to parse data: {e}")
        raise ValueError(f"Invalid data format: {e}")
    return result
```

## テストの書き方

### テスト命名規則

- **ファイル**: `test_*.py`
- **関数**: `test_*`
- **クラス**: `Test*`

### テストの構成

1. **Arrange**: テストデータの準備
2. **Act**: テスト対象の実行
3. **Assert**: 結果の検証

例:
```python
def test_calculate_score_with_valid_data():
    # Arrange
    data = np.array([0.1, 0.6, 0.8, 0.3])
    threshold = 0.5
    
    # Act
    score = calculate_score(data, threshold)
    
    # Assert
    assert score == 0.5
```

## コメント

- **必要な場所にのみ**: 自明なコードにはコメント不要
- **なぜを説明**: 何をするかではなく、なぜそうするかを説明
- **最新に保つ**: コードを変更したらコメントも更新

## 絵文字の使用

- **原則**: 絵文字は使用しない
- **例外**: ユーザーが明示的に要求した場合のみ
