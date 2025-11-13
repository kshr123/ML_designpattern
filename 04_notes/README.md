# 📚 学習ノート・ガイド集

このディレクトリには、プロジェクトで使用するツールや技術の完全ガイドが含まれています。

---

## 📖 ガイド一覧

### 1. [uvパッケージマネージャーガイド](./01_uv_package_manager_guide.md)
**対象**: Pythonの依存関係管理を学びたい人、uvを初めて使う人

#### 📝 内容
- uvとは何か（pipの10-100倍速い）
- なぜuvを使うのか（速度、依存関係の再現性、一元管理）
- 基本コマンド（venv、install、freeze）
- pyproject.tomlとの連携
- uvとDockerの違い
- トラブルシューティング

#### 🎯 こんな時に読む
- 「uvって何？」
- 「pipとどう違うの？」
- 「依存関係を管理したい」
- 「Dockerは必要？」

#### ⏱️ 読了時間
約20分

---

### 2. [Git & GitHub 初心者ガイド](./02_git_github_beginner_guide.md)
**対象**: Gitを初めて使う人、バージョン管理の基礎を学びたい人

#### 📝 内容
- GitとGitHubの違い
- なぜGitを使うのか
- 基本的な概念（リポジトリ、コミット、ブランチ、ステージング）
- 初期設定（ユーザー情報、GitHub認証）
- 基本的なワークフロー（8ステップ）
- よく使うコマンド一覧
- 実践例（新規プロジェクト、既存プロジェクトのクローン）
- トラブルシューティング（認証エラー、コンフリクト解決）
- ベストプラクティス

#### 🎯 こんな時に読む
- 「Gitって何？」
- 「git addとgit pushの違いは？」
- 「GitHubにコードをアップロードしたい」
- 「コンフリクトが発生した」
- 「過去のバージョンに戻したい」

#### ⏱️ 読了時間
約40分

---

### 3. [MCP設定完全ガイド](./03_mcp_setup_guide.md)
**対象**: Claude Codeを使う人、外部サービスと連携したい人

#### 📝 内容
- MCPとは何か（Model Context Protocol）
- このプロジェクトで設定済みのMCP（GitHub、Notion、Serena、Context7、PostgreSQL）
- MCP の設定方法（APIキー取得、設定ファイル編集、再起動）
- 各MCPの使い方と実践例
- トラブルシューティング
- 新しいMCPの追加方法
- ベストプラクティス（セキュリティ、権限管理）

#### 🎯 こんな時に読む
- 「MCPって何？」
- 「Claude CodeからGitHubを操作したい」
- 「最新のライブラリドキュメントを参照したい」
- 「Notionに学習記録を自動で書き込みたい」
- 「コードベース全体を分析したい」

#### ⏱️ 読了時間
約45分

---

### 4. [テストコード作成ガイド](./04_test_writing_guide.md)
**対象**: テストを書いたことがない人、pytestの使い方を学びたい人

#### 📝 内容
- テストコードの基本概念（3Aパターン：Arrange-Act-Assert）
- テストの種類（ユニットテスト、統合テスト、E2Eテスト）
- pytestの使い方（fixture、assert、コマンド）
- ベストプラクティス（1テスト1アサーション、独立性、エッジケース）
- 実践的な例題と練習問題

#### 🎯 こんな時に読む
- 「テストって何？」
- 「pytestの使い方がわからない」
- 「どうやってテストを書けばいい？」
- 「TDD（テスト駆動開発）を実践したい」

#### ⏱️ 読了時間
約30分

---

### 5. [GitHub Actions 完全ガイド](./05_github_actions_guide.md) ⭐
**対象**: CI/CDを学びたい人、GitHub Actionsを初めて使う人

#### 📝 内容
- GitHub Actionsとは何か（CI/CD自動化）
- 基本概念（ワークフロー、イベント、ジョブ、ステップ、アクション、ランナー）
- ワークフローの構造とYAML構文
- UIでの結果確認方法
- トラブルシューティング（5つの一般的エラーと解決策）
- ベストプラクティス（7つのパターン）
- 実践例（iris_sklearn_svcプロジェクト）

#### 🎯 こんな時に読む
- 「GitHub Actionsって何？」
- 「CIサーバーを構築したい」
- 「テストを自動実行したい」
- 「コードの品質を自動チェックしたい」
- 「ワークフローが失敗した」

#### ⏱️ 読了時間
約50分

---

### 6. [ONNX推論パターン完全ガイド](./06_onnx_inference_patterns.md) ⭐
**対象**: 機械学習モデルのデプロイを学びたい人、推論パターンを理解したい人

#### 📝 内容
- ONNXとONNX Runtimeの基礎
- 7つの推論パターン（同期、バッチ、非同期、ストリーミング、REST API、gRPC、サーバーレス）
- 各パターンの実装例（完全なコード付き）
- パターン選択ガイドとフローチャート
- シナリオ別推奨パターン
- ベストプラクティス（モデルロード最適化、入力検証、エラーハンドリング、ログ、バージョン管理）
- トラブルシューティング（5つの一般的問題と解決策）

#### 🎯 こんな時に読む
- 「ONNXって何？」
- 「モデルをデプロイしたい」
- 「推論パターンの違いがわからない」
- 「高スループットな推論システムを作りたい」
- 「FastAPIでモデルを公開したい」
- 「AWS Lambdaでモデルを動かしたい」

#### ⏱️ 読了時間
約60分

---

### 7. [One-Class SVMと外れ値検出手法](./07_one_class_svm_and_anomaly_detection.md)
**対象**: 異常検知を学びたい人、教師なし学習を理解したい人

#### 📝 内容
- One-Class SVMの基本概念（正常データのみから学習）
- 決定境界の学習とカーネルトリック
- nuパラメータによる外れ値率の制御
- 他の外れ値検出手法（Isolation Forest、Local Outlier Factor、DBSCAN）
- 手法選択ガイド（データサイズ、次元数、目的別）
- 実装例とユースケース（不正検知、異常検知、品質管理）

#### 🎯 こんな時に読む
- 「異常検知ってどうやるの？」
- 「正常データしかない場合は？」
- 「One-Class SVMって何？」
- 「外れ値検出手法の違いがわからない」
- 「不正検知システムを作りたい」

#### ⏱️ 読了時間
約30分

---

### 8. [PyTorch画像分類 完全ガイド](./08_pytorch_image_classification_guide.md) ⭐
**対象**: PyTorchを初めて使う人、深層学習で画像分類に挑戦したい人

#### 📝 内容
- PyTorchとは何か（特徴、他フレームワークとの比較）
- 画像分類の基礎（CIFAR-10データセット）
- CNN（畳み込みニューラルネットワーク）の仕組み
  - 畳み込み層、活性化関数、プーリング層、全結合層の詳細解説
  - SimpleCNNアーキテクチャの全体像
- PyTorchの基本概念（Tensor、nn.Module、DataLoader、損失関数、最適化、デバイス管理）
- 実践: CIFAR-10画像分類（完全なコード付き5ステップ）
- よくある質問とトラブルシューティング（7つのQ&A）
- 次のステップ（4レベル別の学習パス、プロジェクトアイデア）

#### 🎯 こんな時に読む
- 「PyTorchって何？」
- 「深層学習で画像分類をしたい」
- 「CNNの仕組みを知りたい」
- 「どうやって学習ループを書くの？」
- 「ハイパーパラメータの調整方法は？」
- 「精度が上がらない」
- 「メモリ不足エラーが出る」

#### ⏱️ 読了時間
約70分

---

### 9. [Docker & Kubernetes 入門ガイド](./09_docker_kubernetes_basics.md) ⭐
**対象**: Docker・Kubernetes初心者、機械学習モデルをコンテナ化してデプロイしたい人

#### 📝 内容
- なぜDockerとKubernetesが必要なのか（従来の問題と解決策）
- Dockerの基礎
  - 重要な概念（イメージ、コンテナ、Dockerfile、レジストリ）
  - 基本コマンド（build、run、logs、stop、rm）
  - Dockerfileの書き方と構造
  - Dockerの利点
- Kubernetesの基礎
  - 重要な概念（Pod、Deployment、Service、Namespace、HPA）
  - 基本コマンド（apply、get、describe、logs、exec、delete）
  - マニフェストファイル（YAML）の書き方
- 実践: Model-in-Image Pattern
  - プロジェクト構成
  - Dockerイメージのビルドとテスト
  - minikubeへのデプロイ（4ステップ）
  - 動作確認
- よくあるトラブルと解決方法
  - Docker関連（ModuleNotFoundError、イメージサイズ、コンテナ終了）
  - Kubernetes関連（ImagePullBackOff、CrashLoopBackOff、Service接続）
- 次のステップ（学習リソース、発展的なトピック）

#### 🎯 こんな時に読む
- 「Dockerって何？」
- 「コンテナとは？」
- 「Kubernetesって何？」
- 「機械学習モデルをデプロイしたい」
- 「環境の違いで動かない問題を解決したい」
- 「自動でスケールするシステムを作りたい」
- 「Model-in-Imageパターンを理解したい」
- 「ImagePullBackOffエラーが出た」

#### ⏱️ 読了時間
約60分

---

### 10. [ResNetとCNNモデル使い分けガイド](./10_resnet_and_cnn_models_guide.md) ⭐ NEW!
**対象**: 画像分類モデルの選択に迷っている人、ResNetを使いたい人

#### 📝 内容
- ResNetとは何か（残差接続、深いネットワークの学習）
- ResNetの特徴とバリエーション（ResNet-18/34/50/101/152）
- ResNet50の使い方
  - ONNXモデルのダウンロード
  - ImageNet標準の前処理（リサイズ、正規化、チャンネル順序変換）
  - ONNX Runtimeでの推論
  - 後処理（Softmax、ラベルマッピング）
- 他のCNNモデルとの比較
  - VGG、GoogLeNet、DenseNet、EfficientNet、Vision Transformer
  - 精度・パラメータ数・速度の比較表
- モデルの使い分け（ユースケース別推奨）
  - リアルタイム推論、高精度重視、転移学習、エッジデバイス、物体検出、医療画像
- 実装パターン（ONNXモデル、転移学習、アンサンブル、A/Bテスト）
- よくある質問（ResNet-50 vs ResNet-101、転移学習、前処理の必要性、GPU vs CPU）

#### 🎯 こんな時に読む
- 「ResNetって何？」
- 「どのCNNモデルを選べばいい？」
- 「ResNet-50の使い方を知りたい」
- 「ImageNet正規化って何？」
- 「VGGとResNetの違いは？」
- 「EfficientNetとResNetどちらを使うべき？」
- 「転移学習に最適なモデルは？」
- 「Prep-Pred PatternでResNet50を使いたい」

#### ⏱️ 読了時間
約50分

---

## 🎓 学習の進め方

### 初心者向けの推奨順序

```
1. uvパッケージマネージャーガイド
   ↓ (依存関係管理)

2. Git & GitHub 初心者ガイド
   ↓ (バージョン管理の基礎)

3. MCP設定完全ガイド
   ↓ (開発効率化)

4. テストコード作成ガイド
   ↓ (品質保証)

5. GitHub Actions 完全ガイド
   ↓ (CI/CD自動化)

6. ONNX推論パターン完全ガイド
   ↓ (モデルデプロイ)

7. Docker & Kubernetes 入門ガイド ⭐
   ↓ (コンテナ化・オーケストレーション)

8. One-Class SVMと外れ値検出手法
   ↓ (異常検知)

9. PyTorch画像分類 完全ガイド
   ↓ (深層学習)

10. ResNetとCNNモデル使い分けガイド ⭐ NEW!
   ↓ (モデル選択・画像分類)

11. 実際のプロジェクトに適用
```

### シナリオ別ガイド

#### 📦 新しいプロジェクトを始める時

1. [uvパッケージマネージャーガイド](./01_uv_package_manager_guide.md) - 環境構築
2. [Git & GitHub 初心者ガイド](./02_git_github_beginner_guide.md) - リポジトリ作成
3. [テストコード作成ガイド](./04_test_writing_guide.md) - TDD実践
4. [GitHub Actions 完全ガイド](./05_github_actions_guide.md) - CI/CD構築

#### 🔧 既存プロジェクトに参加する時

1. [Git & GitHub 初心者ガイド](./02_git_github_beginner_guide.md) - クローンとブランチ
2. [uvパッケージマネージャーガイド](./01_uv_package_manager_guide.md) - 依存関係インストール
3. [MCP設定完全ガイド](./03_mcp_setup_guide.md) - 開発環境整備

#### 🚀 モデルをデプロイする時

1. [ONNX推論パターン完全ガイド](./06_onnx_inference_patterns.md) - 推論パターン選択
2. [GitHub Actions 完全ガイド](./05_github_actions_guide.md) - 自動テスト・デプロイ

#### 🐛 トラブルシューティング

| 問題 | 参照するガイド |
|------|--------------|
| テストが書けない | [テストコード作成ガイド](./04_test_writing_guide.md) |
| パッケージインストールエラー | [uvパッケージマネージャーガイド](./01_uv_package_manager_guide.md) |
| Gitコマンドがわからない | [Git & GitHub 初心者ガイド](./02_git_github_beginner_guide.md) |
| MCPが動かない | [MCP設定完全ガイド](./03_mcp_setup_guide.md) |
| GitHub Actionsが失敗 | [GitHub Actions 完全ガイド](./05_github_actions_guide.md) |
| モデルデプロイ方法がわからない | [ONNX推論パターン完全ガイド](./06_onnx_inference_patterns.md) |
| Dockerって何？ | [Docker & Kubernetes 入門ガイド](./09_docker_kubernetes_basics.md) |
| Kubernetesが難しい | [Docker & Kubernetes 入門ガイド](./09_docker_kubernetes_basics.md) |
| ImagePullBackOffエラー | [Docker & Kubernetes 入門ガイド](./09_docker_kubernetes_basics.md) |
| コンテナ化したい | [Docker & Kubernetes 入門ガイド](./09_docker_kubernetes_basics.md) |
| 異常検知の手法がわからない | [One-Class SVMと外れ値検出手法](./07_one_class_svm_and_anomaly_detection.md) |
| PyTorchの使い方がわからない | [PyTorch画像分類 完全ガイド](./08_pytorch_image_classification_guide.md) |
| CNNの仕組みを知りたい | [PyTorch画像分類 完全ガイド](./08_pytorch_image_classification_guide.md) |
| ResNetって何？ | [ResNetとCNNモデル使い分けガイド](./10_resnet_and_cnn_models_guide.md) |
| どのCNNモデルを選べばいい？ | [ResNetとCNNモデル使い分けガイド](./10_resnet_and_cnn_models_guide.md) |
| ImageNet正規化がわからない | [ResNetとCNNモデル使い分けガイド](./10_resnet_and_cnn_models_guide.md) |
| モデルの使い分けを知りたい | [ResNetとCNNモデル使い分けガイド](./10_resnet_and_cnn_models_guide.md) |

---

## 📊 各ガイドの対応表

| ガイド | 対象レベル | 実践度 | ページ数 |
|--------|-----------|--------|---------|
| **uvパッケージマネージャーガイド** | 初級 | ⭐⭐⭐ | 約400行 |
| **Git & GitHub 初心者ガイド** | 初級 | ⭐⭐⭐ | 約650行 |
| **MCP設定完全ガイド** | 中級 | ⭐⭐ | 約775行 |
| **テストコード作成ガイド** | 初級〜中級 | ⭐⭐⭐ | 約150行 |
| **GitHub Actions 完全ガイド** ⭐ | 中級 | ⭐⭐⭐ | 約873行 |
| **ONNX推論パターン完全ガイド** ⭐ | 中級〜上級 | ⭐⭐⭐ | 約1400行 |
| **One-Class SVMと外れ値検出手法** | 中級 | ⭐⭐⭐ | 約600行 |
| **PyTorch画像分類 完全ガイド** ⭐ | 初級〜中級 | ⭐⭐⭐ | 約1100行 |
| **Docker & Kubernetes 入門ガイド** ⭐ | 初級〜中級 | ⭐⭐⭐ | 約850行 |
| **ResNetとCNNモデル使い分けガイド** ⭐ | 初級〜中級 | ⭐⭐⭐ | 約800行 |

---

## 💡 よくある質問

### Q1: どのガイドから読めばいい？

**A**: プロジェクトを始める場合は以下の順序がおすすめです：

1. **uvパッケージマネージャーガイド** - 環境構築に必要
2. **Git & GitHub 初心者ガイド** - バージョン管理は必須
3. **MCP設定完全ガイド** - 効率化のため（オプション）
4. **テストコード作成ガイド** - 品質保証のため
5. **GitHub Actions 完全ガイド** - CI/CD自動化のため
6. **ONNX推論パターン完全ガイド** - モデルデプロイ時に
7. **One-Class SVMと外れ値検出手法** - 異常検知を実装する時に
8. **PyTorch画像分類 完全ガイド** - 深層学習で画像分類をする時に

### Q2: 全部読まないとダメ？

**A**: いいえ、必要な部分だけ読んでOKです。各ガイドは独立しているので、困った時に該当するガイドを参照してください。

### Q3: 実践的な例はある？

**A**: はい、全てのガイドに実践例が含まれています。特に：
- **テストコード作成ガイド**: 練習問題付き
- **Git & GitHub 初心者ガイド**: 毎日の開発ワークフロー
- **uvパッケージマネージャーガイド**: プロジェクトセットアップ例
- **MCP設定完全ガイド**: 各MCPの使用例
- **GitHub Actions 完全ガイド**: iris_sklearn_svcの実際のワークフロー
- **ONNX推論パターン完全ガイド**: 7つのパターンの完全な実装例
- **One-Class SVMと外れ値検出手法**: iris_sklearn_outlierの実装例
- **PyTorch画像分類 完全ガイド**: CIFAR-10の完全な実装（5ステップ）

### Q4: このプロジェクト以外でも使える？

**A**: はい！これらのガイドは汎用的な内容なので、他のPythonプロジェクトでも活用できます。

---

## 🔄 ガイドの更新方針

### 更新頻度
- 新しいツールやベストプラクティスが見つかったら随時更新
- 学習を通じて得た知見を追加

### 更新履歴
- **2025-11-13**:
  - ResNetとCNNモデル使い分けガイドを追加 ⭐ NEW!
- **2025-11-06**:
  - Docker & Kubernetes 入門ガイドを追加 ⭐
- **2025-11-05**:
  - One-Class SVMと外れ値検出手法を追加
  - PyTorch画像分類 完全ガイドを追加 ⭐
  - ガイドに連番を付与するルールを明確化
- **2025-11-04 (夜)**:
  - GitHub Actions 完全ガイドを追加 ⭐
  - ONNX推論パターン完全ガイドを追加 ⭐
  - ファイル名に接頭番号を付与（作成順）
- **2025-11-04 (昼)**:
  - MCP設定完全ガイドを追加
  - Git & GitHub 初心者ガイドを追加
  - uvパッケージマネージャーガイドを追加
  - テストコード作成ガイドを追加

---

## 🤝 フィードバック

ガイドの内容で分かりにくい部分や、追加してほしい内容があれば：

1. プロジェクトのIssueを作成
2. Pull Requestで直接修正を提案
3. Claude Codeに質問

---

## 📂 ディレクトリ構造

```
04_notes/
├── README.md                                    # このファイル（ガイドのインデックス）
├── 01_uv_package_manager_guide.md               # uvパッケージマネージャーガイド
├── 02_git_github_beginner_guide.md              # Git & GitHub 初心者ガイド
├── 03_mcp_setup_guide.md                        # MCP設定完全ガイド
├── 04_test_writing_guide.md                     # テストコード作成ガイド
├── 05_github_actions_guide.md                   # GitHub Actions 完全ガイド ⭐
├── 06_onnx_inference_patterns.md                # ONNX推論パターン完全ガイド ⭐
├── 07_one_class_svm_and_anomaly_detection.md    # One-Class SVMと外れ値検出手法
├── 08_pytorch_image_classification_guide.md     # PyTorch画像分類 完全ガイド ⭐
├── 09_docker_kubernetes_basics.md               # Docker & Kubernetes 入門ガイド ⭐
└── 10_resnet_and_cnn_models_guide.md            # ResNetとCNNモデル使い分けガイド ⭐
```

---

## 🚀 次のステップ

### ガイドを読み終えたら

1. **実際にコードを書く**
   - `my_implementations/` で実践
   - Model DB パターンを参考に

2. **学習を記録する**
   - `progress/learning_log.md` に記録
   - 気づきや疑問点をメモ

3. **次のパターンに挑戦**
   - Chapter 2-6 の26パターン
   - 興味のある分野から始める

---

**準備完了！実践に移りましょう 🎉**
