# Docker 基礎チュートリアル

**所要時間**: 約30分
**対象**: Dockerを初めて使う人

このチュートリアルでは、実際にコマンドを実行しながらDockerの基礎を学びます。

---

## 📋 このチュートリアルで学ぶこと

- [ ] Dockerコンテナを起動・停止・削除する
- [ ] コンテナのログを確認する
- [ ] 簡単なWebアプリをコンテナ化する
- [ ] Dockerfileを書く
- [ ] イメージをビルドする
- [ ] トラブルシューティング

---

## 🚀 Step 1: Hello World - Dockerコンテナを動かす

### 1.1 最初のコンテナを起動

```bash
# Hello World コンテナを起動
docker run hello-world
```

**期待される出力**:
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
...
```

✅ **成功**: 上記のメッセージが表示されればDocker環境は正常です。

### 1.2 コンテナの履歴を確認

```bash
# 停止したコンテナも含めてすべて表示
docker ps -a
```

**出力例**:
```
CONTAINER ID   IMAGE         COMMAND    CREATED         STATUS
abc123def456   hello-world   "/hello"   10 seconds ago  Exited (0) 8 seconds ago
```

**説明**:
- `CONTAINER ID`: コンテナの一意な識別子
- `IMAGE`: 使用したイメージ名
- `STATUS`: コンテナの状態（Exited = 終了済み）

### 1.3 クリーンアップ

```bash
# 停止したコンテナを削除
docker rm $(docker ps -aq)

# イメージを削除
docker rmi hello-world
```

---

## 🌐 Step 2: Webサーバーを動かす

### 2.1 Nginxコンテナを起動

```bash
# Nginxウェブサーバーをバックグラウンドで起動
docker run -d --name my-nginx -p 8080:80 nginx:alpine
```

**コマンドの意味**:
- `-d`: バックグラウンドで実行（デタッチモード）
- `--name my-nginx`: コンテナに名前を付ける
- `-p 8080:80`: ホストの8080ポートをコンテナの80ポートにマッピング
- `nginx:alpine`: 使用するイメージ（軽量版Nginx）

### 2.2 コンテナが起動しているか確認

```bash
# 起動中のコンテナを表示
docker ps
```

**出力例**:
```
CONTAINER ID   IMAGE          COMMAND                  CREATED         STATUS         PORTS                  NAMES
xyz789abc123   nginx:alpine   "/docker-entrypoint.…"   5 seconds ago   Up 4 seconds   0.0.0.0:8080->80/tcp   my-nginx
```

### 2.3 ブラウザでアクセス

ブラウザで http://localhost:8080 を開いてください。

✅ **成功**: Nginxのデフォルトページ「Welcome to nginx!」が表示される

または、curlで確認：

```bash
curl http://localhost:8080
```

### 2.4 コンテナのログを確認

```bash
# ログをリアルタイムで表示
docker logs -f my-nginx
```

ブラウザをリロードすると、アクセスログが表示されます。

**Ctrl + C** で終了できます。

### 2.5 コンテナを停止・削除

```bash
# コンテナを停止
docker stop my-nginx

# コンテナを削除
docker rm my-nginx

# イメージを削除（オプション）
docker rmi nginx:alpine
```

---

## 🐍 Step 3: PythonアプリをDocker化

### 3.1 作業ディレクトリを作成

```bash
# 一時ディレクトリを作成
mkdir -p ~/docker-tutorial && cd ~/docker-tutorial
```

### 3.2 簡単なPythonアプリを作成

```bash
# app.py を作成
cat > app.py << 'EOF'
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {
            "message": "Hello from Docker!",
            "path": self.path
        }
        self.wfile.write(json.dumps(response).encode())

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8000), SimpleHandler)
    print("Server running on port 8000...")
    server.serve_forever()
EOF
```

### 3.3 Dockerfileを作成

```bash
# Dockerfile を作成
cat > Dockerfile << 'EOF'
# ベースイメージ
FROM python:3.13-slim

# 作業ディレクトリを設定
WORKDIR /app

# アプリケーションコードをコピー
COPY app.py .

# ポートを公開
EXPOSE 8000

# アプリケーションを起動
CMD ["python", "app.py"]
EOF
```

**Dockerfileの説明**:
- `FROM`: ベースとなるイメージ（Python 3.13の軽量版）
- `WORKDIR`: コンテナ内の作業ディレクトリ
- `COPY`: ホストからコンテナへファイルをコピー
- `EXPOSE`: ドキュメント目的（このポートを使うことを示す）
- `CMD`: コンテナ起動時に実行するコマンド

### 3.4 イメージをビルド

```bash
# イメージをビルド
docker build -t my-python-app:v1.0 .
```

**コマンドの意味**:
- `build`: イメージをビルド
- `-t my-python-app:v1.0`: タグ名（イメージ名:バージョン）
- `.`: Dockerfileがあるディレクトリ（カレントディレクトリ）

**出力を確認**:
```
[+] Building 2.5s (8/8) FINISHED
...
=> => naming to docker.io/library/my-python-app:v1.0
```

### 3.5 イメージを確認

```bash
# ビルドしたイメージを表示
docker images | grep my-python-app
```

**出力例**:
```
my-python-app   v1.0   abc123def456   10 seconds ago   145MB
```

### 3.6 コンテナを起動

```bash
# コンテナを起動
docker run -d --name python-app -p 8000:8000 my-python-app:v1.0
```

### 3.7 動作確認

```bash
# ルートパスにアクセス
curl http://localhost:8000

# 別のパスにアクセス
curl http://localhost:8000/hello
```

**期待される出力**:
```json
{"message": "Hello from Docker!", "path": "/"}
{"message": "Hello from Docker!", "path": "/hello"}
```

### 3.8 ログを確認

```bash
# アクセスログを確認
docker logs python-app
```

**出力例**:
```
Server running on port 8000...
127.0.0.1 - - [06/Nov/2025 10:30:15] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [06/Nov/2025 10:30:20] "GET /hello HTTP/1.1" 200 -
```

### 3.9 コンテナ内部に入る

```bash
# コンテナ内でbashを実行
docker exec -it python-app /bin/bash

# コンテナ内で実行
ls -la
pwd
cat app.py
exit
```

### 3.10 クリーンアップ

```bash
# コンテナを停止・削除
docker stop python-app
docker rm python-app

# イメージを削除
docker rmi my-python-app:v1.0

# 作業ディレクトリを削除
cd ~ && rm -rf ~/docker-tutorial
```

---

## 🚀 Step 4: FastAPIアプリをDocker化

### 4.1 作業ディレクトリを作成

```bash
mkdir -p ~/fastapi-docker && cd ~/fastapi-docker
```

### 4.2 FastAPIアプリを作成

```bash
# app.py を作成
cat > app.py << 'EOF'
from fastapi import FastAPI

app = FastAPI(title="My FastAPI App")

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI in Docker!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
EOF
```

### 4.3 requirements.txt を作成

```bash
cat > requirements.txt << 'EOF'
fastapi>=0.111.0
uvicorn[standard]>=0.30.0
EOF
```

### 4.4 Dockerfileを作成

```bash
cat > Dockerfile << 'EOF'
FROM python:3.13-slim

WORKDIR /app

# 依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY app.py .

# ポートを公開
EXPOSE 8000

# Uvicornでアプリを起動
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
```

### 4.5 イメージをビルドして起動

```bash
# ビルド
docker build -t my-fastapi:v1.0 .

# 起動
docker run -d --name fastapi-app -p 8000:8000 my-fastapi:v1.0
```

### 4.6 動作確認

```bash
# ルートエンドポイント
curl http://localhost:8000

# ヘルスチェック
curl http://localhost:8000/health

# パスパラメータ付き
curl "http://localhost:8000/items/42?q=test"

# APIドキュメント（ブラウザで開く）
open http://localhost:8000/docs
```

### 4.7 ログを確認

```bash
docker logs -f fastapi-app
```

**Ctrl + C** で終了

### 4.8 クリーンアップ

```bash
docker stop fastapi-app
docker rm fastapi-app
docker rmi my-fastapi:v1.0
cd ~ && rm -rf ~/fastapi-docker
```

---

## 🔧 よくあるトラブルと解決方法

### ❌ 問題 1: `docker: command not found`

**原因**: Dockerがインストールされていないか、パスが通っていない

**解決策**:
```bash
# Docker Desktopが起動しているか確認
open -a Docker

# Dockerのバージョン確認
docker --version
```

---

### ❌ 問題 2: `Cannot connect to the Docker daemon`

**原因**: Docker Desktopが起動していない

**解決策**:
```bash
# Docker Desktopを起動
open -a Docker

# 起動するまで待つ（数十秒）
# 再度コマンドを実行
```

---

### ❌ 問題 3: `port is already allocated`

**原因**: 指定したポートが既に使用されている

**解決策**:
```bash
# 使用中のコンテナを確認
docker ps

# 該当するコンテナを停止
docker stop <container_name>

# または別のポートを使う
docker run -d -p 8001:8000 my-app
```

---

### ❌ 問題 4: コンテナがすぐに終了する

**原因**: アプリケーションがエラーで終了している

**解決策**:
```bash
# ログを確認
docker logs <container_name>

# 詳細情報を確認
docker inspect <container_name>
```

---

### ❌ 問題 5: イメージビルドが失敗する

**原因**: Dockerfileの記述ミスやファイルが見つからない

**解決策**:
```bash
# カレントディレクトリを確認
pwd
ls -la

# Dockerfileの内容を確認
cat Dockerfile

# ビルドログを詳しく見る
docker build -t my-app:v1.0 . --no-cache
```

---

## 📊 Docker コマンドチートシート

### コンテナ操作

```bash
# コンテナを起動
docker run [options] <image>

# 起動中のコンテナを表示
docker ps

# すべてのコンテナを表示（停止中も含む）
docker ps -a

# コンテナを停止
docker stop <container>

# コンテナを再起動
docker restart <container>

# コンテナを削除
docker rm <container>

# すべての停止中コンテナを削除
docker container prune
```

### イメージ操作

```bash
# イメージをビルド
docker build -t <name>:<tag> .

# イメージ一覧
docker images

# イメージを削除
docker rmi <image>

# 未使用イメージを削除
docker image prune -a
```

### ログとデバッグ

```bash
# ログを表示
docker logs <container>

# リアルタイムログ
docker logs -f <container>

# コンテナ内でコマンド実行
docker exec -it <container> <command>

# コンテナの詳細情報
docker inspect <container>
```

### クリーンアップ

```bash
# すべての停止中コンテナを削除
docker rm $(docker ps -aq)

# すべての未使用イメージを削除
docker rmi $(docker images -q)

# システム全体をクリーンアップ
docker system prune -a
```

---

## ✅ チェックリスト

このチュートリアルで学んだことを確認しましょう：

- [ ] Hello World コンテナを動かした
- [ ] Nginxでウェブサーバーを起動した
- [ ] コンテナのログを確認した
- [ ] 簡単なPythonアプリをDocker化した
- [ ] Dockerfileを書いた
- [ ] イメージをビルドした
- [ ] FastAPIアプリをDocker化した
- [ ] コンテナ内部に入った（docker exec）
- [ ] クリーンアップした

---

## 🎯 次のステップ

Dockerの基礎を学んだので、次は Kubernetes を学びましょう！

👉 [02_minikube_kubernetes.md](./02_minikube_kubernetes.md)

---

## 📚 参考資料

- [Docker 公式ドキュメント](https://docs.docker.com/)
- [Dockerfile リファレンス](https://docs.docker.com/engine/reference/builder/)
- [Docker CLI リファレンス](https://docs.docker.com/engine/reference/commandline/cli/)
- [04_notes/09_docker_kubernetes_basics.md](../../../04_notes/09_docker_kubernetes_basics.md)

---

**お疲れ様でした！🎉**
