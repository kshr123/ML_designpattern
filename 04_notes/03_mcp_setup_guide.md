# MCP (Model Context Protocol) 完全ガイド

## 📚 目次

1. [MCP とは](#mcpとは)
2. [このプロジェクトで設定済みのMCP](#このプロジェクトで設定済みのmcp)
3. [MCP の設定方法](#mcpの設定方法)
4. [各MCPの使い方](#各mcpの使い方)
5. [トラブルシューティング](#トラブルシューティング)
6. [新しいMCPの追加方法](#新しいmcpの追加方法)

---

## MCP とは

### Model Context Protocol（モデルコンテキストプロトコル）

**Claude Code が外部サービスと連携するための仕組み**

```
┌─────────────────────────────────────────┐
│         Claude Code                     │
│                                         │
│  あなた → Claude に指示                │
└──────────────┬──────────────────────────┘
               │
               ↓ MCP経由で連携
┌──────────────────────────────────────────┐
│         外部サービス                      │
├──────────────────────────────────────────┤
│  ✅ GitHub    - リポジトリ操作           │
│  ✅ Notion    - ドキュメント管理         │
│  ✅ Serena    - 高度なコード分析         │
│  ✅ Context7  - 最新ライブラリドキュメント│
│  ✅ PostgreSQL - データベース操作        │
└──────────────────────────────────────────┘
```

### MCPがないと...

```bash
# GitHub にリポジトリを作成したい
❌ ブラウザを開く
❌ GitHub にログイン
❌ New repository をクリック
❌ 設定を入力
❌ Create をクリック
❌ URLをコピー
❌ ターミナルで git remote add ...
```

### MCPがあると...

```bash
# Claude Code に指示するだけ
✅ 「GitHubにリポジトリを作成して」

→ Claude が自動で全てやってくれる
```

---

## このプロジェクトで設定済みのMCP

### 📊 MCP一覧

| MCP | 用途 | 必須度 | 設定状況 |
|-----|------|--------|---------|
| **GitHub** | リポジトリ操作、Issue/PR管理 | ⭐⭐⭐ | ✅ 設定済み |
| **Notion** | Notionページ・DB操作 | ⭐⭐ | ✅ 設定済み |
| **Serena** | 高度なコード分析・編集 | ⭐⭐⭐ | ✅ 設定済み |
| **Context7** | 最新ライブラリドキュメント | ⭐⭐ | ✅ 設定済み |
| **PostgreSQL** | データベース操作 | ⭐ | ✅ 設定済み |

---

## MCP の設定方法

### 設定ファイルの場所

```
ML_designpattern/
├── .mcp.json                    # MCP サーバー定義（APIキー含む）
└── .claude/
    └── settings.local.json      # MCP 有効化設定
```

### .mcp.json の構造

```json
{
  "mcpServers": {
    "サーバー名": {
      "command": "実行コマンド",
      "args": ["引数1", "引数2"],
      "env": {
        "API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### .claude/settings.local.json の構造

```json
{
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": [
    "github",
    "notion",
    "serena",
    "context7",
    "postgres"
  ]
}
```

### 設定手順（一般的な流れ）

1. **APIキー/トークンを取得**
2. **`.mcp.json` にサーバーを追加**
3. **`.claude/settings.local.json` で有効化**
4. **Claude Code を再起動**
5. **動作確認**

---

## 各MCPの使い方

### 1. GitHub MCP

#### 🎯 用途
- リポジトリの作成・管理
- Issue/Pull Requestの作成・管理
- コードの検索
- ファイルのアップロード

#### 🔑 セットアップ

**1. Personal Access Token を取得**

```bash
# 1. GitHub にログイン
# 2. Settings → Developer settings → Personal access tokens → Tokens (classic)
# 3. "Generate new token (classic)" をクリック
# 4. 権限を選択:
#    ✅ repo (フルアクセス)
#    ✅ workflow
#    ✅ read:org
# 5. "Generate token" をクリック
# 6. トークンをコピー（二度と表示されない！）
```

**2. `.mcp.json` に追加**

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxxxxxxxxxx"
      }
    }
  }
}
```

**3. 有効化して再起動**

```json
// .claude/settings.local.json
{
  "enabledMcpjsonServers": ["github"]
}
```

#### 💡 使用例

```
# リポジトリを作成
「GitHubに新しいリポジトリ ML_project を作成して」

# Issue を作成
「GitHubのIssueでバグ報告を作成して。タイトル: ログインエラー」

# Pull Request を作成
「現在のブランチでPRを作成して」

# コードを検索
「このリポジトリでFastAPIを使っている箇所を検索して」

# ファイルをアップロード
「README.mdをGitHubにプッシュして」
```

---

### 2. Notion MCP

#### 🎯 用途
- Notionページの作成・編集
- データベースのクエリ
- タスク管理
- ドキュメント管理

#### 🔑 セットアップ

**1. Notion Integration を作成**

```bash
# 1. https://www.notion.so/my-integrations にアクセス
# 2. "+ New integration" をクリック
# 3. 名前: "Claude Code Integration"
# 4. ワークスペースを選択
# 5. 権限を選択:
#    ✅ Read content
#    ✅ Update content
#    ✅ Insert content
# 6. "Submit" をクリック
# 7. "Internal Integration Token" をコピー
```

**2. Notionページに接続を追加**

```bash
# 1. 使用したいNotionページを開く
# 2. 右上の「...」→「接続」または「Add connections」
# 3. 作成したIntegrationを選択
```

**3. `.mcp.json` に追加**

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": [
        "-y",
        "@notionhq/notion-mcp-server"
      ],
      "env": {
        "NOTION_TOKEN": "secret_xxxxxxxxxxxxx"
      }
    }
  }
}
```

#### 💡 使用例

```
# ページを作成
「Notionに今日の学習記録ページを作成して」

# データベースを検索
「Notionのタスクデータベースで未完了のタスクを検索して」

# ページを更新
「Notionのプロジェクトページに進捗を追加して」

# ページを読む
「Notionの会議メモを読んで要約して」
```

---

### 3. Serena MCP

#### 🎯 用途
- 高度なコード分析（シンボル検索）
- コードベース全体の構造理解
- リファクタリング支援
- 依存関係の追跡

#### 🔑 セットアップ

**1. プロジェクトパスを設定**

```json
{
  "mcpServers": {
    "serena": {
      "command": "npx",
      "args": [
        "-y",
        "git+https://github.com/oraios/serena"
      ],
      "env": {
        "SERENA_PROJECT_PATH": "/Users/kshr123/Desktop/dev/ML_designpattern"
      }
    }
  }
}
```

**注意**: プロジェクトパスは**絶対パス**で指定

#### 💡 使用例

```
# シンボル検索
「FastAPI関連のクラスを全て検索して」

# コード構造を理解
「このプロジェクトのアーキテクチャを説明して」

# 依存関係を追跡
「この関数を使っている箇所を全て見つけて」

# リファクタリング
「このクラス名をUserModelに変更して、全ての参照も更新して」
```

#### 🌟 Serenaの強み

```
通常のGrepやFind:
✅ ファイル名やテキスト検索

Serena:
✅ シンボル単位の検索（クラス、関数、変数）
✅ コード構造の理解（継承関係、依存関係）
✅ 安全なリファクタリング
✅ 大規模コードベースでも高速
```

---

### 4. Context7 MCP

#### 🎯 用途
- 最新のライブラリドキュメントを取得
- バージョン固有のドキュメント参照
- ベストプラクティスの学習
- 非推奨APIの回避

#### 🔑 セットアップ

**1. `.mcp.json` に追加（APIキー不要）**

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp"
      ]
    }
  }
}
```

**2. APIキー追加（オプション、より高いレート制限）**

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp",
        "--api-key",
        "YOUR_API_KEY"
      ]
    }
  }
}
```

#### 💡 使用例

**重要**: プロンプトに **"use context7"** を含める

```
# 最新のライブラリを使う
「FastAPIで基本的なWebサーバーを作成して。use context7」

# 特定のライブラリの機能を調べる
「PyTorchでTransformerモデルを実装したい。最新のAPIを教えて。use context7」

# 複数のライブラリ
「FastAPIとPydanticを使ってREST APIを作成。use context7」

# バージョン指定
「Pydantic v2の新機能を教えて。use context7」
```

#### 🌟 Context7の利点

```
Claude の通常の知識:
❌ 2025年1月までの情報
❌ 古いバージョンのAPIを提案する可能性

Context7あり:
✅ 常に最新のドキュメント
✅ 使用しているバージョンに対応
✅ 非推奨APIを避けられる
✅ 最新のベストプラクティス
```

---

### 5. PostgreSQL MCP

#### 🎯 用途
- データベースのクエリ実行
- テーブル構造の確認
- データ分析
- 自然言語でSQL生成

#### 🔑 セットアップ

**1. PostgreSQLをインストール（macOS）**

```bash
# Homebrewでインストール
brew install postgresql@15

# サービス開始
brew services start postgresql@15

# データベース作成（オプション）
createdb ml_patterns
```

**2. `.mcp.json` に追加**

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://localhost/postgres"
      ]
    }
  }
}
```

**接続URLのカスタマイズ**:
```
postgresql://ユーザー名:パスワード@ホスト:ポート/データベース名
```

例:
- ローカル: `postgresql://localhost/postgres`
- 認証付き: `postgresql://user:password@localhost:5432/ml_patterns`
- リモート: `postgresql://user:pass@example.com:5432/production`

#### 💡 使用例

```
# テーブル一覧を取得
「PostgreSQLのテーブル一覧を表示して」

# データを検索
「usersテーブルから最新の10件を取得して」

# 自然言語でクエリ
「先月登録したユーザー数を教えて」

# データ分析
「実験結果テーブルから平均accuracyを計算して」

# テーブル作成
「実験結果を保存するテーブルを作成して」
```

---

## トラブルシューティング

### 問題1: MCPサーバーが認識されない

**症状**:
```
MCP tools not available
```

**解決方法**:

```bash
# 1. Claude Codeを完全に再起動
pkill -f "Claude Code"

# 2. 設定ファイルを確認
cat .mcp.json
cat .claude/settings.local.json

# 3. Node.jsのバージョン確認（v18以上必要）
node --version
```

---

### 問題2: GitHub MCPが認証エラー

**症状**:
```
GitHub authentication failed
```

**解決方法**:

```bash
# 1. トークンの有効期限を確認
# GitHub → Settings → Developer settings → Personal access tokens

# 2. トークンの権限を確認
# ✅ repo
# ✅ workflow
# ✅ read:org

# 3. トークンを再生成して .mcp.json を更新
# 4. Claude Codeを再起動
```

---

### 問題3: Notion MCPが動作しない

**症状**:
```
Notion API error: unauthorized
```

**解決方法**:

```bash
# 1. Integrationがページに接続されているか確認
# Notionページ → 右上「...」→「接続」で確認

# 2. トークンが正しいか確認
cat .mcp.json | grep NOTION_TOKEN

# 3. Integration の権限を確認
# Read content, Update content, Insert content が有効か
```

---

### 問題4: Context7が応答しない

**症状**:
```
Context7 timeout
```

**解決方法**:

```bash
# 1. プロンプトに "use context7" を含めているか確認

# 2. ネットワーク接続を確認

# 3. レート制限に達していないか確認
# → APIキーを追加してレート制限を増やす

# 4. 完全に再起動
pkill -9 -f "Claude Code"
```

---

### 問題5: Serenaが遅い

**症状**:
```
Serena taking too long to respond
```

**解決方法**:

```bash
# 1. プロジェクトパスが正しいか確認
cat .mcp.json | grep SERENA_PROJECT_PATH

# 2. .gitignore が適切に設定されているか確認
# 大きなファイル（node_modules, .venv）が除外されているか

# 3. Serenaのキャッシュをクリア
rm -rf .serena/cache/
```

---

## 新しいMCPの追加方法

### ステップ1: 使いたいMCPを探す

**公式MCPリポジトリ**:
- https://github.com/modelcontextprotocol

**人気のMCP**:
- `@modelcontextprotocol/server-slack` - Slack連携
- `@modelcontextprotocol/server-filesystem` - ファイル操作
- `@modelcontextprotocol/server-puppeteer` - Web自動化
- `@modelcontextprotocol/server-everything` - 汎用ツール

### ステップ2: `.mcp.json` に追加

```json
{
  "mcpServers": {
    "新しいMCP": {
      "command": "npx",
      "args": [
        "-y",
        "パッケージ名"
      ],
      "env": {
        "API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### ステップ3: `.claude/settings.local.json` で有効化

```json
{
  "enabledMcpjsonServers": [
    "github",
    "notion",
    "新しいMCP"
  ]
}
```

### ステップ4: Claude Codeを再起動

```bash
pkill -f "Claude Code"
# Claude Codeを再度起動
```

### ステップ5: 動作確認

```
「利用可能なMCPサーバーをリストアップして」
```

---

## 📊 MCP設定のベストプラクティス

### ✅ やるべきこと

1. **APIキー/トークンは .gitignore に追加**
   ```gitignore
   .mcp.json
   .claude/settings.local.json
   ```

2. **サンプルファイルを用意**
   ```bash
   # .mcp.json.example を作成（トークン無し）
   cp .mcp.json .mcp.json.example
   # APIキーを <YOUR_TOKEN_HERE> に置換
   ```

3. **定期的にトークンをローテーション**
   ```bash
   # GitHub トークンは90日で期限切れ
   # カレンダーにリマインダーを設定
   ```

4. **必要最小限の権限を付与**
   ```bash
   # GitHub: repo のみ（admin は不要）
   # Notion: Read/Write のみ（Delete は不要）
   ```

### ❌ やってはいけないこと

1. **APIキーをGitにコミット**
   ```bash
   # ❌ Bad
   git add .mcp.json
   git commit -m "MCP設定"
   git push
   # → APIキーが公開される！
   ```

2. **全ての権限を付与**
   ```bash
   # ❌ Bad: admin権限を付与
   # リスクが高い
   ```

3. **期限切れトークンを放置**
   ```bash
   # ❌ Bad: 動かなくなってから気づく
   # ✅ Good: 定期的に更新
   ```

---

## 🎯 このプロジェクトでのMCP活用例

### 開発ワークフロー

```
1. コード分析（Serena）
   「このプロジェクトの構造を説明して」

2. 仕様書作成（Context7）
   「FastAPIで実装する仕様書を作成。use context7」

3. 実装
   （通常のClaude Code機能）

4. GitHub連携（GitHub MCP）
   「GitHubにプッシュして」

5. 学習記録（Notion MCP）
   「今日の学習内容をNotionに記録して」

6. データ分析（PostgreSQL MCP）
   「実験結果を分析して」
```

---

## 📚 参考リンク

### 公式ドキュメント
- [MCP公式サイト](https://modelcontextprotocol.io/)
- [MCPサーバー一覧](https://github.com/modelcontextprotocol)
- [Claude Code MCP設定](https://docs.anthropic.com/claude-code/mcp)

### 各MCPのドキュメント
- [GitHub MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/github)
- [Notion MCP](https://github.com/notionhq/notion-mcp-server)
- [Context7 MCP](https://github.com/upstash/context7-mcp)
- [PostgreSQL MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/postgres)

---

## 💡 まとめ

### MCPの3つのメリット

1. **効率化**: 手動操作が自動化される
2. **統合**: 複数のツールをClaude Codeから操作
3. **学習**: 最新の情報にアクセス（Context7）

### このプロジェクトで特に重要なMCP

| MCP | 重要度 | 理由 |
|-----|--------|------|
| **Serena** | ⭐⭐⭐ | 大規模コードベースの理解 |
| **GitHub** | ⭐⭐⭐ | Git操作の自動化 |
| **Context7** | ⭐⭐ | 最新のライブラリドキュメント |
| **Notion** | ⭐⭐ | 学習記録の管理 |
| **PostgreSQL** | ⭐ | データ分析（オプション） |

---

これでMCP設定は完璧です！🎉
