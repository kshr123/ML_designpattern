# プロジェクト概要

## プロジェクトの目的

このプロジェクトは『AIエンジニアのための機械学習システムデザインパターン』の学習と実践を目的としています。
参考リポジトリ（reference/）を基に、**AI駆動開発でゼロから機械学習システムを実装**します。

## プロジェクトの特徴

1. **仕様駆動開発（SDD）**: まずSPECIFICATION.mdで仕様を明確化してから実装
2. **テスト駆動開発（TDD）**: Red→Green→Refactorサイクルで品質を担保
3. **段階的開発**: 小さなステップで確実に進める
4. **実践重視**: 本番環境を想定した品質のコードを書く

## 学習内容

- **Chapter 2: Training** - モデル学習のパターン
- **Chapter 3: Release** - モデルリリースのパターン
- **Chapter 4: Serving** - 推論サービスのパターン（最重要）
- **Chapter 5: Operations** - 運用のパターン
- **Chapter 6: Operation Management** - 運用管理のパターン

## ディレクトリ構造

```
.
├── reference/              # 参考リポジトリ（読み取り専用）
│   ├── chapter2_training/
│   ├── chapter3_release_patterns/
│   ├── chapter4_serving_patterns/
│   ├── chapter5_operations/
│   └── chapter6_operation_management/
├── my_implementations/     # 自分で実装するコード（書き込み可）
├── templates/              # テンプレートファイル
│   ├── SPECIFICATION.template.md
│   ├── pyproject.toml.template
│   └── test_*.template.py
├── notes/                  # 学習ノート・メモ（書き込み可）
├── progress/               # 進捗管理（書き込み可）
│   └── learning_log.md
└── docs/                   # ドキュメント
    └── DEVELOPMENT_WORKFLOW.md
```

## 重要なルール

1. **`reference/` は読み取り専用** - 参考コードは変更しない
2. **`my_implementations/` に実装する** - ゼロから実装したコードはここに配置
3. **パターンごとにサブディレクトリを作成** - 命名規則: `ch{N}__{pattern_name}/`
4. **テンプレートを活用する** - `templates/` から必要なファイルをコピー

## 現在の状態

- ✅ プロジェクト環境構築完了
- ✅ 開発方法論確立（SDD + TDD）
- ✅ テンプレート作成完了
- ✅ MCP設定完了（GitHub, Notion, Serena）
- ⏭️ 次: 最初のパターンの実装開始
