# macOS（Darwin）システムコマンド

このプロジェクトは**macOS（Darwin）**環境で開発されています。
Linux（GNU）とは一部コマンドの挙動が異なるため注意が必要です。

---

## ファイル操作

### ディレクトリの一覧表示

```bash
# 基本的なリスト
ls -la

# ツリー表示（treeコマンドが必要）
tree -L 2 -a

# treeがインストールされていない場合
brew install tree
```

### ファイルの検索

```bash
# ファイル名で検索（BSD版find）
find . -name "*.py" -type f

# 内容で検索（BSD版grep）
grep -r "pattern" .

# より高速な検索（ripgrepを推奨）
brew install ripgrep
rg "pattern"
```

### ファイルのコピー・移動

```bash
# コピー
cp source.txt destination.txt
cp -r source_dir/ destination_dir/

# 移動
mv source.txt destination.txt

# 削除
rm file.txt
rm -rf directory/
```

---

## テキスト処理

### sedコマンド（BSD版）

macOSの`sed`はBSD版なので、GNU版とは構文が異なります。

```bash
# ファイルを直接編集（BSD版）
sed -i '' 's/old/new/g' file.txt

# GNU版（Linux）だと以下だが、macOSでは動かない
# sed -i 's/old/new/g' file.txt

# GNU sedを使いたい場合
brew install gnu-sed
gsed -i 's/old/new/g' file.txt
```

### awkコマンド

```bash
# フィールドを抽出
awk '{print $1}' file.txt

# パターンマッチ
awk '/pattern/ {print $0}' file.txt
```

---

## ディスク・ファイルシステム

### ディスク使用量の確認

```bash
# ディレクトリのサイズ
du -sh directory/

# カレントディレクトリのサイズ
du -sh .

# 各サブディレクトリのサイズ
du -sh */
```

### ファイルシステム情報

```bash
# マウントされているファイルシステム
df -h

# ファイルの詳細情報
stat file.txt
```

---

## プロセス管理

### プロセスの確認

```bash
# すべてのプロセス
ps aux

# 特定のプロセスを検索
ps aux | grep python

# プロセスツリー
pstree  # インストールが必要: brew install pstree
```

### プロセスの終了

```bash
# プロセスIDで終了
kill <PID>

# 強制終了
kill -9 <PID>

# プロセス名で終了
pkill python

# Claude Codeの再起動
pkill -f "Claude Code"
```

---

## ネットワーク

### ポートの確認

```bash
# リスニングしているポート
lsof -i -P | grep LISTEN

# 特定のポート（例: 8000番）
lsof -i :8000

# ネットワーク統計
netstat -an | grep LISTEN
```

### HTTP リクエスト

```bash
# curl
curl http://localhost:8000/health

# curlでJSONをPOST
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"data": [1, 2, 3]}'

# HTTPie（より使いやすい）
brew install httpie
http GET http://localhost:8000/health
```

---

## 環境変数

### 環境変数の確認

```bash
# すべての環境変数
env

# 特定の環境変数
echo $PATH
echo $PYTHONPATH
```

### 環境変数の設定

```bash
# 一時的に設定（現在のセッションのみ）
export MY_VAR="value"

# .zshrcや.bash_profileに永続的に設定
echo 'export MY_VAR="value"' >> ~/.zshrc
source ~/.zshrc
```

---

## パッケージ管理（Homebrew）

macOSではHomebrewがデファクトスタンダードのパッケージマネージャー。

### 基本コマンド

```bash
# パッケージのインストール
brew install <package>

# パッケージのアンインストール
brew uninstall <package>

# パッケージの検索
brew search <package>

# インストール済みパッケージの一覧
brew list

# パッケージの更新
brew update
brew upgrade <package>
```

### よく使うパッケージ

```bash
# 開発ツール
brew install git
brew install tree
brew install ripgrep
brew install fd

# Python関連
brew install python@3.13
brew install uv

# Docker
brew install --cask docker
```

---

## シェル

### デフォルトシェル

macOS Catalina以降、デフォルトシェルは**zsh**。

```bash
# 現在のシェルを確認
echo $SHELL

# zshの設定ファイル
~/.zshrc
~/.zprofile

# bashを使う場合
bash
```

### シェル設定ファイルの編集

```bash
# zshの設定を編集
vim ~/.zshrc

# 設定を再読み込み
source ~/.zshrc
```

---

## ファイルのパーミッション

### パーミッションの確認

```bash
# ファイルのパーミッション
ls -l file.txt

# 出力例: -rw-r--r-- (644)
# - : ファイル種別（- = 通常ファイル、d = ディレクトリ）
# rw- : オーナーの権限（読み書き）
# r-- : グループの権限（読み取りのみ）
# r-- : その他の権限（読み取りのみ）
```

### パーミッションの変更

```bash
# 実行権限を付与
chmod +x script.sh

# 数値で指定
chmod 755 script.sh  # rwxr-xr-x
chmod 644 file.txt   # rw-r--r--

# 再帰的に変更
chmod -R 755 directory/
```

---

## 圧縮・解凍

```bash
# tar.gz（圧縮）
tar -czf archive.tar.gz directory/

# tar.gz（解凍）
tar -xzf archive.tar.gz

# zip（圧縮）
zip -r archive.zip directory/

# zip（解凍）
unzip archive.zip
```

---

## システム情報

### OS情報

```bash
# OSバージョン
sw_vers

# カーネル情報
uname -a

# アーキテクチャ
uname -m  # arm64（Apple Silicon）または x86_64（Intel）
```

### ハードウェア情報

```bash
# CPU情報
sysctl -n machdep.cpu.brand_string

# メモリ情報
sysctl hw.memsize

# ディスク情報
diskutil list
```

---

## 開発関連

### Git

```bash
# Git操作（基本）
git status
git add .
git commit -m "message"
git push origin main

# ブランチ操作
git branch
git checkout -b feature/new-feature
git merge feature/new-feature
```

### Docker

```bash
# Dockerコンテナの起動
docker run -p 8000:8000 image_name

# Docker Compose
docker-compose up -d
docker-compose down
docker-compose logs -f

# イメージの確認
docker images

# コンテナの確認
docker ps
docker ps -a
```

### Python仮想環境

```bash
# uvで仮想環境を作成
uv venv

# 仮想環境を有効化（zsh）
source .venv/bin/activate

# 仮想環境を無効化
deactivate
```

---

## エイリアス（ショートカット）

`~/.zshrc`に以下を追加すると便利:

```bash
# よく使うコマンドのエイリアス
alias ll='ls -lah'
alias grep='grep --color=auto'
alias python='python3'
alias pip='pip3'

# Git
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'

# Docker
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'

# プロジェクト固有
alias activate='source .venv/bin/activate'
alias check='black src/ tests/ && ruff check src/ tests/ && mypy src/ && pytest tests/ -v'
```

エイリアスを設定したら:
```bash
source ~/.zshrc  # 設定を再読み込み
```

---

## トラブルシューティング

### コマンドが見つからない場合

```bash
# コマンドの場所を確認
which python
which uv

# PATHを確認
echo $PATH

# Homebrewでインストール
brew install <command>
```

### ポートが既に使用されている場合

```bash
# ポートを使用しているプロセスを確認
lsof -i :8000

# プロセスを終了
kill -9 <PID>
```

### ファイルが見つからない場合

```bash
# ファイルを検索
find . -name "file.txt"

# または
mdfind -name "file.txt"  # macOS Spotlight検索
```

---

## まとめ

- macOSのコマンドはBSD系なので、Linuxとは一部異なる
- `sed -i ''` のように、BSD版特有の構文に注意
- Homebrewでパッケージ管理
- デフォルトシェルはzsh（設定: `~/.zshrc`）
- エイリアスを活用して効率化
