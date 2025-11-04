# Git & GitHub 完全ガイド（初心者向け）

## 📚 目次

1. [Git とは？GitHub とは？](#gitとはgithubとは)
2. [なぜ Git を使うのか](#なぜgitを使うのか)
3. [基本的な概念](#基本的な概念)
4. [初期設定](#初期設定)
5. [基本的なワークフロー](#基本的なワークフロー)
6. [よく使うコマンド一覧](#よく使うコマンド一覧)
7. [実践例](#実践例)
8. [トラブルシューティング](#トラブルシューティング)
9. [ベストプラクティス](#ベストプラクティス)

---

## Git とは？GitHub とは？

### Git（ギット）

**バージョン管理システム**

```
┌─────────────────────────────────────┐
│           Git                       │
├─────────────────────────────────────┤
│ あなたのPC（ローカル）で動くツール  │
│                                     │
│ ✅ ファイルの変更履歴を記録        │
│ ✅ 過去のバージョンに戻せる        │
│ ✅ 複数人での開発を助ける          │
└─────────────────────────────────────┘
```

**例え話**:
- **Gitなし**: Wordで「論文_最終版.docx」「論文_最終版2.docx」「論文_本当に最終版.docx」を作る
- **Gitあり**: 1つのファイルで、全ての変更履歴を記録。いつでも過去に戻れる

### GitHub（ギットハブ）

**Git のリモートホスティングサービス**

```
┌─────────────────────────────────────┐
│          GitHub                     │
├─────────────────────────────────────┤
│ クラウド上のサービス                │
│                                     │
│ ✅ コードをオンラインに保存         │
│ ✅ チームでコードを共有             │
│ ✅ バックアップ                     │
│ ✅ 公開・ポートフォリオ             │
└─────────────────────────────────────┘
```

**例え話**:
- **Git**: あなたのPC内の「履歴付きノート」
- **GitHub**: そのノートをクラウドに保存する「Dropbox」のようなもの

### 関係性

```
┌─────────────┐          ┌─────────────┐
│   あなたのPC │          │   GitHub    │
│             │          │             │
│    Git      │  push    │  リモート   │
│  ローカル   │ ────→    │ リポジトリ  │
│ リポジトリ  │          │             │
│             │  pull    │             │
│             │ ←────    │             │
└─────────────┘          └─────────────┘
```

---

## なぜ Git を使うのか

### 1. 変更履歴を完全に記録できる

**Before Git:**
```
project/
├── app_v1.py
├── app_v2.py
├── app_v2_fixed.py
├── app_final.py
└── app_final_really.py  ← どれが最新？
```

**With Git:**
```
project/
└── app.py  ← 1つのファイル

# Git が全ての変更履歴を記録
git log
→ 2025-11-04: バグ修正
→ 2025-11-03: 新機能追加
→ 2025-11-02: 初期実装
```

### 2. 安心して実験できる

```bash
# 新しいアイデアを試したい
git branch experiment  # 実験用ブランチ作成
# → 失敗しても元のコードは無傷

# 成功したら元のコードに反映
git merge experiment
```

### 3. チーム開発が楽になる

```
太郎さん: ログイン機能を開発
花子さん: 検索機能を開発
        ↓
Gitが自動で統合してくれる
```

### 4. いつでも過去に戻れる

```bash
# 「昨日のコード、動いてたのに...」
git log  # 昨日のコミットを確認
git checkout <昨日のコミットID>  # 昨日に戻る
```

---

## 基本的な概念

### 1. リポジトリ（Repository）

**プロジェクトの保管庫**

```
my_project/
├── .git/           ← Git の履歴データ（見えない）
├── src/
│   └── app.py
├── tests/
│   └── test_app.py
└── README.md
```

### 2. コミット（Commit）

**変更の記録（スナップショット）**

```
時系列で記録される「セーブポイント」

コミット1: プロジェクト開始
   ↓
コミット2: ログイン機能追加
   ↓
コミット3: バグ修正
   ↓
コミット4: UI改善 ← 今ここ
```

### 3. ブランチ（Branch）

**並行して作業するための分岐**

```
         main（メインブランチ）
          │
コミット1─┼─コミット2─┬─コミット4
          │           │
          │      feature（新機能）
          │           │
          │      コミット3
          │
```

### 4. ステージング（Staging）

**コミットする変更を選ぶ場所**

```
┌────────────────┐
│ 作業ディレクトリ │  ← ファイル編集
└────────┬───────┘
         │ git add
         ↓
┌────────────────┐
│  ステージング   │  ← コミット準備
└────────┬───────┘
         │ git commit
         ↓
┌────────────────┐
│ ローカルリポジトリ│  ← 履歴に記録
└────────┬───────┘
         │ git push
         ↓
┌────────────────┐
│     GitHub     │  ← オンラインに保存
└────────────────┘
```

---

## 初期設定

### 1. Git のインストール確認

```bash
# Gitがインストールされているか確認
git --version

# 出力例: git version 2.39.0
```

**インストールされていない場合**:

```bash
# macOS
brew install git

# Windows
# https://git-scm.com/download/win からダウンロード

# Linux (Ubuntu/Debian)
sudo apt-get install git
```

### 2. ユーザー情報の設定

**最初に1回だけ実行**

```bash
# 名前を設定（コミットに記録される）
git config --global user.name "あなたの名前"

# メールアドレスを設定（GitHubと同じものを推奨）
git config --global user.email "your-email@example.com"

# 設定を確認
git config --list
```

**例**:
```bash
git config --global user.name "Taro Yamada"
git config --global user.email "taro@example.com"
```

### 3. エディタの設定（オプション）

```bash
# コミットメッセージ用のエディタを設定
git config --global core.editor "vim"
# または
git config --global core.editor "code --wait"  # VSCode
```

### 4. デフォルトブランチ名の設定

```bash
# 新しいリポジトリのデフォルトブランチを main に
git config --global init.defaultBranch main
```

### 5. GitHub アカウントの作成

1. https://github.com にアクセス
2. 「Sign up」をクリック
3. メールアドレス、パスワードを入力
4. アカウント作成完了

### 6. GitHub との認証設定

#### 方法1: Personal Access Token（推奨）

```bash
# 1. GitHub にログイン
# 2. Settings → Developer settings → Personal access tokens → Tokens (classic)
# 3. "Generate new token (classic)" をクリック
# 4. 権限を選択:
#    ✅ repo (フルアクセス)
#    ✅ workflow
# 5. トークンをコピー（二度と表示されない！）

# 6. プッシュ時に使用
git push
# Username: <GitHubのユーザー名>
# Password: <コピーしたトークン>
```

#### 方法2: SSH キー（上級者向け）

```bash
# SSH キーを生成
ssh-keygen -t ed25519 -C "your-email@example.com"

# 公開鍵をコピー
cat ~/.ssh/id_ed25519.pub

# GitHub に登録
# Settings → SSH and GPG keys → New SSH key
# コピーした公開鍵を貼り付け
```

---

## 基本的なワークフロー

### 🎯 シナリオ: 新しいプロジェクトを始める

#### ステップ1: ローカルリポジトリを作成

```bash
# プロジェクトディレクトリを作成
mkdir my_project
cd my_project

# Git リポジトリを初期化
git init

# 確認
ls -la
# → .git/ ディレクトリが作成される
```

#### ステップ2: ファイルを作成・編集

```bash
# ファイルを作成
echo "# My Project" > README.md
echo "print('Hello, World!')" > app.py

# 現在の状態を確認
git status
```

**出力例**:
```
On branch main
Untracked files:
  README.md
  app.py

nothing added to commit
```

#### ステップ3: 変更をステージング

```bash
# 特定のファイルをステージング
git add README.md
git add app.py

# または、全てのファイルをステージング
git add .

# 状態を確認
git status
```

**出力例**:
```
Changes to be committed:
  new file:   README.md
  new file:   app.py
```

#### ステップ4: コミット（記録）

```bash
# コミット（変更を記録）
git commit -m "初回コミット: プロジェクト開始"

# コミット履歴を確認
git log
```

**出力例**:
```
commit abc123... (HEAD -> main)
Author: Taro Yamada <taro@example.com>
Date:   Mon Nov 4 10:00:00 2025 +0900

    初回コミット: プロジェクト開始
```

#### ステップ5: GitHub にリポジトリを作成

**GitHub Web UI で**:
1. https://github.com にログイン
2. 右上の「+」→「New repository」
3. Repository name: `my_project`
4. Public / Private を選択
5. **「Initialize this repository with a README」はチェックしない**
6. 「Create repository」をクリック

#### ステップ6: リモートリポジトリを追加

```bash
# GitHub のリポジトリを「origin」という名前で登録
git remote add origin https://github.com/ユーザー名/my_project.git

# 確認
git remote -v
```

**出力例**:
```
origin  https://github.com/taro/my_project.git (fetch)
origin  https://github.com/taro/my_project.git (push)
```

#### ステップ7: GitHub にプッシュ

```bash
# main ブランチを GitHub にプッシュ
git push -u origin main

# 初回のみ -u オプションが必要
# 2回目以降は git push だけでOK
```

**成功メッセージ**:
```
To https://github.com/taro/my_project.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

#### ステップ8: GitHub で確認

ブラウザで `https://github.com/ユーザー名/my_project` にアクセス
→ コードがアップロードされている！

---

## よく使うコマンド一覧

### 📋 基本コマンド

```bash
# リポジトリを初期化
git init

# 状態を確認（最も重要！）
git status

# 変更をステージング
git add <ファイル名>
git add .                # 全てのファイル

# コミット
git commit -m "メッセージ"

# 履歴を表示
git log
git log --oneline        # 1行で表示
git log --graph          # グラフ表示

# 変更内容を確認
git diff                 # 未ステージングの変更
git diff --staged        # ステージング済みの変更
```

### 🔄 リモート操作

```bash
# リモートリポジトリを追加
git remote add origin <URL>

# リモート一覧
git remote -v

# プッシュ（アップロード）
git push origin main
git push                 # 2回目以降

# プル（ダウンロード）
git pull origin main
git pull                 # 2回目以降

# クローン（既存リポジトリをダウンロード）
git clone <URL>
```

### 🌿 ブランチ操作

```bash
# ブランチ一覧
git branch

# 新しいブランチを作成
git branch <ブランチ名>

# ブランチを切り替え
git checkout <ブランチ名>

# ブランチを作成して切り替え（ショートカット）
git checkout -b <ブランチ名>

# ブランチを削除
git branch -d <ブランチ名>

# ブランチをマージ
git merge <ブランチ名>
```

### ↩️ 取り消し・修正

```bash
# ステージングを取り消し
git reset <ファイル名>
git reset                # 全てのファイル

# 変更を破棄（注意！元に戻せない）
git checkout -- <ファイル名>

# 直前のコミットを修正
git commit --amend

# 過去のコミットに戻る
git reset --hard <コミットID>  # 注意：変更が消える
git reset --soft <コミットID>  # 変更は残る
```

### 🔍 情報確認

```bash
# 誰が変更したか確認
git blame <ファイル名>

# コミットの詳細を表示
git show <コミットID>

# タグを作成
git tag v1.0.0

# タグ一覧
git tag
```

---

## 実践例

### 例1: 既存プロジェクトを Git 管理下に置く

```bash
# プロジェクトディレクトリに移動
cd ~/my_existing_project

# Git リポジトリを初期化
git init

# .gitignore を作成（不要なファイルを除外）
cat << 'EOF' > .gitignore
# Python
__pycache__/
*.pyc
.venv/

# OS
.DS_Store
EOF

# 全てのファイルをステージング
git add .

# 初回コミット
git commit -m "Initial commit"

# GitHub にリポジトリを作成（Web UIで）
# リモートを追加
git remote add origin https://github.com/ユーザー名/my_existing_project.git

# プッシュ
git push -u origin main
```

### 例2: 他人のプロジェクトをダウンロードして開発

```bash
# GitHub からクローン
git clone https://github.com/他人/awesome_project.git
cd awesome_project

# 新しいブランチで作業開始
git checkout -b my-feature

# ファイルを編集
vim src/app.py

# 変更をコミット
git add src/app.py
git commit -m "feat: 新機能追加"

# 自分の GitHub にプッシュ（フォーク先）
git push origin my-feature

# GitHub の Web UI で Pull Request を作成
```

### 例3: 毎日の開発ワークフロー

```bash
# 朝: 最新のコードを取得
git pull origin main

# 新しい機能を開発
vim src/new_feature.py

# 変更を確認
git status
git diff

# ステージング
git add src/new_feature.py

# コミット
git commit -m "feat: 新機能を追加"

# GitHub にプッシュ
git push origin main

# 夕方: もう一度最新を取得（他の人の変更を反映）
git pull origin main
```

### 例4: コミットメッセージの規約（Conventional Commits）

```bash
# 新機能
git commit -m "feat: ユーザー登録機能を追加"

# バグ修正
git commit -m "fix: ログイン時のエラーを修正"

# ドキュメント
git commit -m "docs: READMEにセットアップ手順を追加"

# リファクタリング
git commit -m "refactor: コード整理"

# テスト
git commit -m "test: ユニットテストを追加"

# スタイル
git commit -m "style: コードフォーマット修正"
```

---

## トラブルシューティング

### 問題1: git push が認証エラーになる

**症状**:
```
remote: Invalid username or password.
fatal: Authentication failed
```

**解決方法**:
```bash
# Personal Access Token を使う
# GitHub でトークンを生成して、パスワードの代わりに使用

# または、リモートURLにトークンを含める
git remote set-url origin https://<TOKEN>@github.com/ユーザー名/リポジトリ.git
```

### 問題2: コミットメッセージを間違えた

**解決方法**:
```bash
# 直前のコミットメッセージを修正（まだプッシュしていない場合）
git commit --amend -m "正しいメッセージ"

# すでにプッシュしてしまった場合
# → そのまま新しいコミットで修正するのが安全
```

### 問題3: 間違えてファイルをコミットした

**解決方法**:
```bash
# ステージングを取り消す（コミット前）
git reset HEAD <ファイル名>

# コミット後（まだプッシュしていない）
git reset --soft HEAD~1  # コミットを取り消し、変更は残す
git reset --hard HEAD~1  # コミットと変更を完全に削除（注意！）

# すでにプッシュした場合
git revert <コミットID>  # 安全に取り消すコミットを作成
```

### 問題4: マージでコンフリクト（競合）が発生

**症状**:
```
CONFLICT (content): Merge conflict in app.py
Automatic merge failed; fix conflicts and then commit the result.
```

**解決方法**:
```bash
# 1. コンフリクトしているファイルを開く
vim app.py

# 2. コンフリクトマーカーを探す
<<<<<<< HEAD
あなたの変更
=======
他の人の変更
>>>>>>> branch-name

# 3. どちらを採用するか決めて、マーカーを削除

# 4. 修正したファイルをステージング
git add app.py

# 5. マージを完了
git commit -m "Merge: コンフリクトを解決"
```

### 問題5: .git フォルダを間違えて削除した

**症状**:
```
fatal: not a git repository
```

**解決方法**:
```bash
# 残念ながら、ローカルの履歴は失われる
# GitHub にプッシュ済みなら、再クローン
git clone https://github.com/ユーザー名/リポジトリ.git

# GitHub にプッシュしていない場合
# → 履歴は失われる。再度 git init から開始
```

### 問題6: GitHub にプッシュできない（too large）

**症状**:
```
remote: error: File large_file.zip is 123.45 MB; this exceeds GitHub's file size limit of 100.00 MB
```

**解決方法**:
```bash
# 1. .gitignore に大きなファイルを追加
echo "large_file.zip" >> .gitignore

# 2. Git履歴から削除（すでにコミット済みの場合）
git rm --cached large_file.zip
git commit -m "Remove large file"

# 3. GitHub に再プッシュ
git push origin main
```

---

## ベストプラクティス

### 1. コミットは小さく、頻繁に

❌ **悪い例**:
```bash
# 1週間作業してから1回だけコミット
git commit -m "色々修正"
```

✅ **良い例**:
```bash
# 機能ごとに小さくコミット
git commit -m "feat: ログイン機能追加"
git commit -m "fix: バリデーションのバグ修正"
git commit -m "test: ログイン機能のテスト追加"
```

### 2. コミットメッセージは明確に

❌ **悪い例**:
```bash
git commit -m "修正"
git commit -m "変更"
git commit -m "aaa"
```

✅ **良い例**:
```bash
git commit -m "feat: ユーザー登録APIを実装"
git commit -m "fix: パスワードハッシュ化の不具合を修正"
git commit -m "docs: API仕様書を更新"
```

### 3. main ブランチは常に動く状態に保つ

```bash
# 新機能は別ブランチで開発
git checkout -b feature/user-login

# 開発＆テスト
# ✅ 動作確認OK

# main にマージ
git checkout main
git merge feature/user-login
git push origin main
```

### 4. .gitignore を活用する

```bash
# .gitignore を作成
cat << 'EOF' > .gitignore
# Python
__pycache__/
*.pyc
.venv/
*.egg-info/

# 環境変数（APIキーなど）
.env
*.pem
*.key

# データベース
*.sqlite
*.db

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
EOF

git add .gitignore
git commit -m "chore: .gitignoreを追加"
```

### 5. 定期的にプッシュする

```bash
# 朝、昼、夕方など、定期的にプッシュ
git push origin main

# 理由:
# ✅ バックアップになる
# ✅ チームメンバーに共有できる
# ✅ PCが壊れても安心
```

### 6. プルしてからプッシュ

```bash
# プッシュ前に必ず最新を取得
git pull origin main

# コンフリクトがあれば解決

# プッシュ
git push origin main
```

### 7. 重要なファイルは Git で管理しない

❌ **Git に入れてはいけないもの**:
- APIキー、パスワード（.env）
- 秘密鍵（*.pem, *.key）
- 大きなファイル（動画、データセットなど）
- 自動生成ファイル（__pycache__, *.pyc）

✅ **Git に入れるべきもの**:
- ソースコード
- ドキュメント
- 設定ファイルのサンプル（.env.example）
- README.md

### 8. コミット前に必ず確認

```bash
# 変更内容を確認
git status
git diff

# ステージング後も確認
git diff --staged

# 問題なければコミット
git commit -m "メッセージ"
```

---

## 📚 さらに学ぶためのリソース

### 公式ドキュメント
- [Git公式ドキュメント](https://git-scm.com/doc)
- [GitHub Docs](https://docs.github.com/)

### インタラクティブチュートリアル
- [Learn Git Branching](https://learngitbranching.js.org/?locale=ja) - ゲーム感覚でGitを学べる
- [GitHub Skills](https://skills.github.com/) - GitHubの使い方を学べる

### チートシート
- [Git Cheat Sheet（PDF）](https://education.github.com/git-cheat-sheet-education.pdf)

### おすすめ書籍
- 『Pro Git』- 無料で読める公式本
- 『サルでもわかるGit入門』- 日本語の入門書

---

## 💡 覚えておくべき重要コマンド（最低限）

```bash
# この7つだけ覚えれば日常開発は可能

1. git init          # リポジトリ作成
2. git status        # 状態確認
3. git add .         # 全てステージング
4. git commit -m ""  # コミット
5. git push          # GitHub にアップロード
6. git pull          # GitHub から最新取得
7. git log           # 履歴確認
```

---

## 🎯 このプロジェクトでの使い方（まとめ）

### 新しいパターンを実装する時

```bash
# 1. 最新を取得
git pull origin main

# 2. 実装作業
cd my_implementations/chapter2_training/new_pattern
# ... コード書く ...

# 3. 状態確認
git status

# 4. ステージング
git add .

# 5. コミット
git commit -m "feat: 新パターン実装完了"

# 6. プッシュ
git push origin main
```

### 学習記録を更新する時

```bash
# 1. 学習記録を編集
vim progress/learning_log.md

# 2. コミット
git add progress/learning_log.md
git commit -m "docs: 学習記録を更新"

# 3. プッシュ
git push origin main
```

これでGit & GitHubの基礎は完璧です！🎉
