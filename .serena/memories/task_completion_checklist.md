# タスク完了時のチェックリスト

## コード品質チェック

実装が完了したら、以下のコマンドを**順番に**実行してすべてパスすることを確認する:

### 1. コードフォーマット

```bash
black src/ tests/
```

**期待結果**: すべてのファイルがフォーマットされる（または"All done!"）

---

### 2. リント（静的解析）

```bash
ruff check src/ tests/
```

**期待結果**: エラーや警告がゼロ

エラーがある場合:
```bash
ruff check --fix src/ tests/  # 自動修正
```

---

### 3. 型チェック

```bash
mypy src/
```

**期待結果**: "Success: no issues found"

---

### 4. テスト実行（カバレッジ付き）

```bash
pytest tests/ -v --cov=src --cov-report=html --cov-report=term
```

**期待結果**:
- すべてのテストがパス（Green）
- カバレッジが**80%以上**

カバレッジレポートの確認:
```bash
open htmlcov/index.html  # macOS
```

---

## 統合チェック（推奨）

すべてのチェックを一度に実行:

```bash
black src/ tests/ && \
ruff check src/ tests/ && \
mypy src/ && \
pytest tests/ -v --cov=src --cov-report=html
```

すべてパスすれば次のステップへ進める。

---

## 動作確認

### 実際の動作テスト

コードが実際に動作することを確認:

```bash
# 実装したアプリケーションを起動
python src/{pattern_name}/main.py

# または、Dockerコンテナで起動
docker-compose up -d

# ヘルスチェック（APIの場合）
curl http://localhost:8000/health
```

### ログの確認

ログが適切に出力されているか確認:
- エラーログが適切に記録されるか
- 重要なイベントがログに残るか

---

## ドキュメント確認

### README.md

以下が含まれていることを確認:
- [ ] 概要
- [ ] アーキテクチャの説明
- [ ] セットアップ手順
- [ ] 実行方法
- [ ] テスト方法
- [ ] 学んだこと

### SPECIFICATION.md

以下が含まれていることを確認:
- [ ] 要件定義（機能要件・非機能要件）
- [ ] アーキテクチャ設計
- [ ] API仕様
- [ ] データモデル
- [ ] 成功基準

---

## Git操作

### コミット前の最終チェック

```bash
# 変更内容を確認
git status
git diff

# 不要なファイルが含まれていないか確認
git status --ignored
```

**重要**: 以下のファイルがコミットされないことを確認:
- `.env` ファイル
- `*.pem`, `*.key` などのシークレット
- `.mcp.json`（トークンを含む）
- `__pycache__/` などのキャッシュ

### コミット

```bash
# ステージング
git add .

# コミット（コミットメッセージの規約に従う）
git commit -m "feat: implement {pattern_name}"

# プッシュ（必要に応じて）
git push origin main
```

**コミットメッセージの規約**:
- `feat:` - 新機能
- `fix:` - バグ修正
- `docs:` - ドキュメントのみの変更
- `refactor:` - リファクタリング
- `test:` - テストの追加・修正
- `chore:` - ビルドプロセスやツールの変更

---

## 学習記録

### progress/learning_log.md に記録

以下を記録する:
- [ ] 実装したパターン名と日時
- [ ] 学んだこと
- [ ] 躓いた点とその解決方法
- [ ] 改善できる点
- [ ] 次回への持ち越し事項

---

## タスク完了の定義（Definition of Done）

以下をすべて満たしたら、そのパターンは完了:

- [ ] **SPECIFICATION.md**が作成されている
- [ ] **README.md**が作成されている
- [ ] すべての**テストがパス**する（Green）
- [ ] **コードカバレッジが80%以上**
- [ ] **フォーマット、リント、型チェック**がすべてパス
- [ ] 実際に**動作確認**ができている
- [ ] **progress/learning_log.md**に記録されている
- [ ] **Gitにコミット**されている（機密情報を除く）

---

## オプション: Makefile の活用

`Makefile`を作成してコマンドをショートカット化すると便利:

```makefile
.PHONY: check format lint typecheck test clean

# すべてのチェックを実行
check: format lint typecheck test

format:
	black src/ tests/

lint:
	ruff check src/ tests/

typecheck:
	mypy src/

test:
	pytest tests/ -v --cov=src --cov-report=html

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache htmlcov .coverage
```

使い方:
```bash
make check  # すべてのチェックを一度に実行
```

---

## トラブルシューティング

### チェックが失敗する場合

1. **フォーマットが通らない**: 
   - `black src/ tests/` を実行して修正

2. **リントが通らない**:
   - エラーメッセージを読んで修正
   - `ruff check --fix src/ tests/` で自動修正

3. **型チェックが通らない**:
   - 型ヒントを追加または修正
   - `# type: ignore` は最後の手段（多用しない）

4. **テストが失敗する**:
   - エラーメッセージを読んで原因を特定
   - デバッガやprintデバッグを使用
   - TDDサイクル（Red-Green-Refactor）を思い出す

5. **カバレッジが低い**:
   - カバレッジレポート（htmlcov/index.html）を確認
   - テストされていないコードパスを特定
   - 追加のテストケースを作成

---

## 最終確認

すべてのチェックが完了したら、以下を確認:

- ✅ コードが動作する
- ✅ テストがすべてパスする
- ✅ ドキュメントが完成している
- ✅ 学習内容が記録されている
- ✅ Gitにコミットされている

**お疲れさまでした！次のパターンへ進みましょう！** 🎉
