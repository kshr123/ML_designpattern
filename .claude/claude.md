# 機械学習システムデザインパターン学習プロジェクト

> **このプロジェクトについて**: 『AIエンジニアのための機械学習システムデザインパターン』の学習と実践を、AI駆動開発で行うプロジェクトです。

---

## 📋 プロジェクト概要

このプロジェクトは以下の4つの柱で構成されています：

1. **参考コード分析** - 既存実装から設計思想を学ぶ
2. **仕様駆動開発（SDD）** - まず仕様を明確にしてから実装
3. **テスト駆動開発（TDD）** - Red→Green→Refactorのサイクル
4. **学習記録** - 知識を体系化して蓄積

### プロジェクトの目的

- 機械学習システムの各種デザインパターンを理解する
- 参考コードを分析し、設計思想を学ぶ
- 学んだパターンをゼロから実装して実践的スキルを習得する
- 学習過程を記録し、知識を体系化する

---

## 📁 ディレクトリ構造

```
.
├── 01_reference/           # 参考リポジトリ（読み取り専用）
├── 02_templates/           # テンプレートファイル
├── 03_my_implementations/  # 自分で実装するコード
├── 04_notes/               # 学習ノート・メモ
├── 05_progress/            # 進捗管理
├── 06_docs/                # ドキュメント
└── 07_tutorials/           # チュートリアル
```

---

## 🚀 クイックスタート

### 新しいパターンを実装する場合

```bash
# 1. プロジェクトセットアップ
mkdir -p 03_my_implementations/chapter{N}_{category}/{NN}_{pattern_name}
cd 03_my_implementations/chapter{N}_{category}/{NN}_{pattern_name}

# 2. 仮想環境セットアップ
echo "3.13" > .python-version
uv venv
source .venv/bin/activate

# 3. 開発ツールインストール
uv pip install pytest pytest-cov black ruff mypy

# 4. ディレクトリ構造作成
mkdir -p tests src/{pattern_name}
touch src/{pattern_name}/__init__.py tests/__init__.py
```

### 学習の流れ

```
理解 → 仕様策定 → テスト作成(Red) → 実装(Green) → リファクタリング → 検証 → 振り返り
```

詳細は [project_rules.md](./project_rules.md) を参照してください。

---

## 📚 ルールファイル構成

このプロジェクトのルールは3つのファイルに分かれています：

### 1. このファイル (CLAUDE.md)
- プロジェクト概要
- クイックリファレンス
- ルールファイルの構成

### 2. [project_rules.md](./project_rules.md)
**このプロジェクト固有のルール**
- ディレクトリ構造とルール（詳細）
- 学習の優先順位
- 進捗管理ルール
- 機械学習特有の注意点
- データセット管理
- チュートリアル実施時のルール

### 3. [general_rules.md](./general_rules.md)
**どんなプロジェクトでも使える汎用的なルール**
- 仕様駆動開発（SDD）
- テスト駆動開発（TDD）
- コーディング規約
- セキュリティ・パフォーマンス
- Git管理
- Claude Codeとの協働ルール

**重要**: `general_rules.md`は他のプロジェクト（Webアプリ、データサイエンス、DevOpsなど）でもそのまま使えます。

---

## 🎯 現在の進捗

- **完了パターン数**: 7 / 26 パターン
- **完了チュートリアル数**: 4 / 4 チュートリアル（すべて完了！）
- **現在の章**: Chapter 3: Release Patterns（進行中）
- **最新の完了**: Model-in-Image Pattern ハンズオン (2025-11-13)
- **次の目標**: Chapter 3: 02_model_load_pattern の実装

詳細は [05_progress/learning_log.md](../05_progress/learning_log.md) を参照してください。

---

## 🎓 学習の推奨順序

1. **Chapter 2: Training** - 基礎となるモデル学習
2. **Chapter 3: Release Patterns** - モデルのリリース方法
3. **Chapter 4: Serving Patterns** - 推論サービスの実装（最重要）
4. **Chapter 5: Operations** - 運用とモニタリング
5. **Chapter 6: Operation Management** - 高度な運用管理

ただし、興味のある分野から始めてもOK。モチベーション維持が最優先。

---

## 🔌 外部ツール連携

このプロジェクトでは、以下の外部ツールをMCP (Model Context Protocol) 経由で利用できます：

- **GitHub MCP**: リポジトリ操作、Issue/PR管理
- **Notion MCP**: 学習記録の管理
- **Serena MCP**: 高度なコード分析・編集
- **Context7 MCP**: 最新ライブラリドキュメントの参照
- **PostgreSQL MCP**: データベース操作

詳細な設定方法は [04_notes/mcp_setup_guide.md](../04_notes/mcp_setup_guide.md) を参照してください。

---

## 📖 参考情報

- **プロジェクト固有ルール**: [project_rules.md](./project_rules.md)
- **汎用開発ルール**: [general_rules.md](./general_rules.md)
- **進捗記録**: [05_progress/learning_log.md](../05_progress/learning_log.md)
- **学習ノート**: [04_notes/](../04_notes/)
- **チュートリアル**: [07_tutorials/](../07_tutorials/)

---

## 🔄 更新履歴

**2025-11-13**:
- **ファイル構成を3分割**:
  - `CLAUDE.md` - プロジェクト概要とクイックリファレンス
  - `project_rules.md` - このプロジェクト固有のルール
  - `general_rules.md` - 他プロジェクトでも使える汎用ルール
- Model-in-Image Pattern ハンズオン完了
- 全チュートリアル完了（4/4）

**2025-11-05（夜）**:
- ノートファイル命名規則を強化（連番接頭辞必須）
- `04_notes/README.md`の更新を必須化

**2025-11-05（昼）**:
- プロジェクト全体のルールと開発プロセスを整理
- 一時ファイル管理ルールを追加
- 個人情報とセキュリティルールを追加
- progress/learning_log.md の役割を明確化
- ドキュメント更新フローを必須化（4段階）

---

**最終更新**: 2025-11-13
