# One-Class SVMと外れ値検出手法

**作成日**: 2025-11-05
**関連実装**: 05_iris_sklearn_outlier

---

## 📚 目次

1. [One-Class SVMとは](#one-class-svmとは)
2. [他の外れ値検出手法](#他の外れ値検出手法)
3. [手法選択ガイド](#手法選択ガイド)
4. [実装例](#実装例)
5. [ユースケース](#ユースケース)

---

## One-Class SVMとは

### 基本概念

**One-Class SVM（One-Class Support Vector Machine）** は、**正常データのみ**から学習し、異常や外れ値を検出する教師なし学習アルゴリズム。

### 主な特徴

#### 1. 教師なし学習
- ラベル（正常/異常）が不要
- 正常データだけで学習可能
- 異常データの収集が困難な場合に有効

#### 2. 決定境界の学習

```
正常データの分布
    ┌─────────────────┐
    │  ●  ●  ●       │
    │   ●  ●  ●      │ ← 決定境界（超平面）
    │  ●  ●  ●       │
    └─────────────────┘
         ↓
    境界外 = 外れ値
```

#### 3. カーネルトリック
- 非線形な境界を学習可能
- RBF、linear、poly、sigmoidカーネルが利用可能

#### 4. nuパラメータによる制御

```python
# nu = 外れ値の上限割合
OneClassSVM(nu=0.1)  # 最大10%を外れ値として許容
OneClassSVM(nu=0.05) # 最大5%を外れ値として許容
```

### 数学的仕組み

1. **原点からの距離を最大化**
   - 正常データを原点から最も遠い超平面で分離
   - 境界内が「正常」、境界外が「異常」

2. **決定関数**
   ```
   f(x) = w·φ(x) - ρ

   f(x) > 0  → 正常（+1）
   f(x) < 0  → 異常（-1）
   ```

3. **サポートベクター**
   - 決定境界上にあるサンプル
   - モデルの複雑さを決定

### 実装例（scikit-learn）

```python
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# パイプライン構築
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("ocs", OneClassSVM(nu=0.1, gamma="auto", kernel="rbf"))
])

# 学習（正常データのみ）
pipeline.fit(X_train)

# 予測
predictions = pipeline.predict(X_test)  # +1: 正常, -1: 異常

# 異常スコア（決定関数値）
scores = pipeline.decision_function(X_test)  # 負の値ほど異常
```

---

## 他の外れ値検出手法

### 1. Isolation Forest

**特徴**:
- ランダムフォレストベースの手法
- 異常データは「孤立しやすい」という性質を利用

**仕組み**:
- ランダムに特徴量を選択
- ランダムに分割点を選択
- 孤立するまでの分割回数が少ない → 異常

**実装**:
```python
from sklearn.ensemble import IsolationForest

clf = IsolationForest(
    contamination=0.1,  # 外れ値の割合
    random_state=42,
    n_estimators=100
)
clf.fit(X)
predictions = clf.predict(X)  # +1: 正常, -1: 異常
```

**メリット**:
- 高速（O(n log n)）
- 高次元データに強い
- スケーラブル
- パラメータ調整が簡単

**デメリット**:
- ランダム性が高い
- 解釈性が低い
- 精度がOne-Class SVMより劣る場合がある

**One-Class SVMとの比較**:

| 項目 | One-Class SVM | Isolation Forest |
|------|---------------|------------------|
| 速度 | 遅い（O(n²)） | 速い（O(n log n)）|
| 精度 | 高い | やや低い |
| 高次元 | 苦手 | 得意 |
| パラメータ調整 | 難しい（nu, gamma） | 簡単（contamination） |
| 新データ予測 | 可能 | 可能 |
| 解釈性 | 中 | 低 |

---

### 2. Local Outlier Factor (LOF)

**特徴**:
- 局所的な密度に基づく異常検知
- k近傍法ベース

**仕組み**:
- 各点の周辺密度を計算
- 周辺の点と比較して密度が低い → 異常

**実装**:
```python
from sklearn.neighbors import LocalOutlierFactor

lof = LocalOutlierFactor(
    n_neighbors=20,      # 近傍数
    contamination=0.1,   # 外れ値の割合
    novelty=True         # 新データ予測を有効化
)
lof.fit(X_train)
predictions = lof.predict(X_test)  # +1: 正常, -1: 異常
```

**メリット**:
- 局所的な異常を検出可能
- 密度の異なるクラスタにも対応
- 解釈性が高い

**デメリット**:
- パラメータ（n_neighbors）の選択が難しい
- 大規模データでは遅い
- デフォルトでは新データ予測不可（novelty=True必要）

**One-Class SVMとの比較**:

| 項目 | One-Class SVM | LOF |
|------|---------------|-----|
| 異常の種類 | グローバル | 局所的 |
| 新データ予測 | 可能 | novelty=Trueで可能 |
| 解釈性 | 中 | 高い |
| 速度 | 中 | 遅い |

---

### 3. Autoencoder（深層学習）

**特徴**:
- ニューラルネットワークで正常データの再構成を学習
- 再構成誤差が大きい = 異常

**仕組み**:
```
入力 → Encoder → Bottleneck → Decoder → 出力
  X  →   圧縮   →   潜在表現  →  復元   →  X'

再構成誤差 = ||X - X'||²
```

**実装**:
```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# Encoder-Decoder
model = Sequential([
    Dense(10, activation='relu', input_dim=4),  # Encoder
    Dense(2, activation='relu'),                # Bottleneck
    Dense(10, activation='relu'),               # Decoder
    Dense(4, activation='linear')               # Output
])

model.compile(optimizer='adam', loss='mse')
model.fit(X_train, X_train, epochs=50)  # 自分自身を再構成

# 異常検知
reconstructed = model.predict(X_test)
mse = np.mean((X_test - reconstructed)**2, axis=1)
threshold = np.percentile(mse, 95)
anomalies = mse > threshold
```

**メリット**:
- 複雑な非線形パターンを学習可能
- 高次元データに強い
- 画像・テキスト・時系列にも対応
- 柔軟なアーキテクチャ設計

**デメリット**:
- 大量のデータが必要
- 学習に時間がかかる
- ハイパーパラメータが多い
- 過学習しやすい

---

### 4. 統計的手法

#### 4.1 Gaussian Distribution（ガウス分布）

**仕組み**:
```python
from scipy import stats

# 正常データが正規分布に従うと仮定
mean = np.mean(X, axis=0)
cov = np.cov(X.T)

# マハラノビス距離で異常検知
distances = [stats.mahalanobis(x, mean, np.linalg.inv(cov)) for x in X]
threshold = np.percentile(distances, 95)
anomalies = distances > threshold
```

**メリット**:
- シンプルで解釈しやすい
- 高速
- 理論的背景が明確

**デメリット**:
- 正規分布の仮定が必要
- 多峰性分布に弱い
- 非線形パターンに対応できない

#### 4.2 PCA（主成分分析）ベース

**仕組み**:
```python
from sklearn.decomposition import PCA

pca = PCA(n_components=2)
pca.fit(X)
X_reconstructed = pca.inverse_transform(pca.transform(X))

# 再構成誤差
reconstruction_error = np.sum((X - X_reconstructed)**2, axis=1)
threshold = np.percentile(reconstruction_error, 95)
anomalies = reconstruction_error > threshold
```

**メリット**:
- 次元削減と異常検知を同時実行
- 計算が高速
- ノイズ除去効果

**デメリット**:
- 線形変換のみ
- 主成分数の選択が重要
- 非線形パターンに対応できない

---

### 5. DBSCAN（密度ベースクラスタリング）

**仕組み**:
```python
from sklearn.cluster import DBSCAN

dbscan = DBSCAN(
    eps=0.5,         # 近傍半径
    min_samples=5    # 最小サンプル数
)
labels = dbscan.fit_predict(X)

# -1 = ノイズ（外れ値）
anomalies = labels == -1
```

**メリット**:
- クラスタ数を事前指定不要
- 任意の形状のクラスタを検出
- ノイズを明示的に識別

**デメリット**:
- パラメータ（eps, min_samples）の選択が難しい
- 密度が異なるクラスタに弱い
- 高次元データでは性能低下

---

## 手法選択ガイド

### データ量で選ぶ

| データサイズ | 推奨手法 | 理由 |
|------------|---------|------|
| 小（< 1,000） | One-Class SVM, LOF | 精度重視 |
| 中（1,000-10,000） | Isolation Forest, One-Class SVM | バランス |
| 大（> 10,000） | Isolation Forest, Autoencoder | 速度重視 |
| 超大規模（> 100万） | Isolation Forest, MiniBatch手法 | スケーラビリティ |

### データ特性で選ぶ

| データ特性 | 推奨手法 | 理由 |
|-----------|---------|------|
| 低次元（< 10） | One-Class SVM, LOF | カーネル・密度ベースが有効 |
| 中次元（10-100） | Isolation Forest, PCA | バランスが良い |
| 高次元（> 100） | Isolation Forest, Autoencoder, PCA | 次元の呪いに強い |
| 画像 | Autoencoder（CNN） | 空間構造を保持 |
| テキスト | Autoencoder（RNN/Transformer） | シーケンス構造 |
| 時系列 | Autoencoder（LSTM）, 統計的手法 | 時間依存性 |
| 非線形 | One-Class SVM（RBF）, Autoencoder | 複雑な境界 |
| 線形 | PCA, One-Class SVM（linear） | シンプル |

### 要件で選ぶ

| 要件 | 推奨手法 | トレードオフ |
|-----|---------|------------|
| 高精度 | One-Class SVM, Autoencoder | 速度・複雑さ |
| 高速 | Isolation Forest, 統計的手法 | 精度 |
| 解釈性 | LOF, 統計的手法, DBSCAN | 精度・速度 |
| 新データ予測 | One-Class SVM, Isolation Forest | - |
| オンライン学習 | Incremental PCA, ストリーミング手法 | 精度 |
| ロバスト性 | Isolation Forest | 解釈性 |
| 少ない調整 | Isolation Forest | 最適性 |

### ユースケース別推奨

| ユースケース | 推奨手法 | 理由 |
|------------|---------|------|
| 製造業（品質管理） | One-Class SVM | 高精度、正常データのみ |
| 不正検知（金融） | Isolation Forest, Autoencoder | 大規模、リアルタイム |
| セキュリティ（侵入検知） | One-Class SVM, LOF | パターン学習 |
| IoTセンサー異常 | Isolation Forest, 統計的手法 | ストリーミング |
| 医療診断 | One-Class SVM, Autoencoder | 高精度、説明可能性 |
| ログ監視 | Isolation Forest | 高次元、高速 |
| 画像検査 | Autoencoder（CNN） | 空間パターン |

---

## 実装例

### 複数手法の比較

```python
import numpy as np
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.covariance import EllipticEnvelope
from sklearn.datasets import load_iris

# データ準備
X = load_iris().data

# 1. One-Class SVM
ocs = OneClassSVM(nu=0.1, gamma='auto')
ocs_pred = ocs.fit_predict(X)

# 2. Isolation Forest
iforest = IsolationForest(contamination=0.1, random_state=42)
if_pred = iforest.fit_predict(X)

# 3. LOF
lof = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
lof_pred = lof.fit_predict(X)

# 4. Gaussian (Elliptic Envelope)
ee = EllipticEnvelope(contamination=0.1)
ee_pred = ee.fit_predict(X)

# 結果比較
methods = {
    "One-Class SVM": ocs_pred,
    "Isolation Forest": if_pred,
    "LOF": lof_pred,
    "Elliptic Envelope": ee_pred
}

for name, pred in methods.items():
    n_outliers = np.sum(pred == -1)
    print(f"{name:20s}: {n_outliers:3d} outliers ({n_outliers/len(X)*100:.1f}%)")
```

### 実行結果例

```
One-Class SVM       :  14 outliers (9.3%)
Isolation Forest    :  15 outliers (10.0%)
LOF                 :  15 outliers (10.0%)
Elliptic Envelope   :  15 outliers (10.0%)
```

### 性能比較コード

```python
import time
from sklearn.metrics import confusion_matrix, classification_report

# 人工的に異常データを追加
from sklearn.datasets import make_blobs
X_normal, _ = make_blobs(n_samples=200, centers=1, random_state=42)
X_anomaly = np.random.uniform(low=-10, high=10, size=(20, 2))
X = np.vstack([X_normal, X_anomaly])
y_true = np.array([1]*200 + [-1]*20)  # 1: 正常, -1: 異常

methods = {
    "One-Class SVM": OneClassSVM(nu=0.1),
    "Isolation Forest": IsolationForest(contamination=0.1, random_state=42),
}

for name, clf in methods.items():
    # 学習時間測定
    start = time.time()
    y_pred = clf.fit_predict(X)
    elapsed = time.time() - start

    # 評価
    cm = confusion_matrix(y_true, y_pred)
    print(f"\n{name}")
    print(f"  学習時間: {elapsed:.4f}秒")
    print(f"  混同行列:\n{cm}")
```

---

## ユースケース

### One-Class SVMが最適な場合

#### 1. 製造業の品質管理
- **状況**: 正常品のデータのみ大量にある、不良品のデータが少ない
- **理由**:
  - 高精度な境界学習
  - 正常データのみで学習可能
  - カーネルで複雑なパターンを捉える
- **例**: 半導体検査、溶接品質チェック

#### 2. 医療診断
- **状況**: 健康な人のデータは豊富、病気のデータは少ない
- **理由**:
  - 高い精度が要求される
  - 誤検知（偽陽性）のコストが高い
- **例**: 心電図異常検知、MRI画像診断

#### 3. セキュリティ（侵入検知）
- **状況**: 正常な通信パターンを学習、異常な通信を検出
- **理由**:
  - 複雑な攻撃パターンに対応
  - 精度重視
- **例**: ネットワーク侵入検知、認証システム

---

### Isolation Forestが最適な場合

#### 1. 不正検知（クレジットカード）
- **状況**: 大量のトランザクションデータ、リアルタイム処理
- **理由**:
  - 高速処理
  - スケーラブル
  - 高次元データに強い
- **例**: クレジットカード不正利用検知、保険金詐欺検知

#### 2. ログ異常検知
- **状況**: 大量のログデータ、多次元
- **理由**:
  - 高速処理
  - パラメータ調整が簡単
- **例**: サーバーログ監視、アプリケーションログ分析

---

### Autoencoderが最適な場合

#### 1. 画像検査
- **状況**: 正常画像のみで学習、傷や欠陥を検出
- **理由**:
  - CNNで空間構造を保持
  - 複雑な非線形パターン学習
- **例**: 製品外観検査、X線検査

#### 2. 時系列異常検知
- **状況**: センサーデータ、複雑なパターン
- **理由**:
  - LSTMで時間依存性を学習
  - 長期的なパターンを捉える
- **例**: 設備故障予知、株価異常検知

---

## 学習メモ

### One-Class SVMを選んだ理由（05_iris_sklearn_outlier）

1. **教師なし学習の基礎を学ぶため**
   - ラベルなしでの学習体験
   - 正常データのみからの学習

2. **SVMの応用を理解するため**
   - 分類SVMとの違い
   - カーネルトリックの応用

3. **パラメータチューニングの経験**
   - nuの影響を理解
   - gammaの影響を理解

4. **実務で重要なパターン**
   - 異常データが少ない状況は現実的
   - 製造業・医療など幅広い応用

### 今後の学習課題

- [ ] Isolation Forestの実装と比較
- [ ] Autoencoderによる画像異常検知（06_cifar10で学習予定）
- [ ] LOFとの性能比較
- [ ] 実データでの評価

---

## 参考資料

### 論文
- Schölkopf et al. (2001) "Estimating the Support of a High-Dimensional Distribution"
- Liu et al. (2008) "Isolation Forest"
- Breunig et al. (2000) "LOF: Identifying Density-Based Local Outliers"

### ドキュメント
- [scikit-learn: Novelty and Outlier Detection](https://scikit-learn.org/stable/modules/outlier_detection.html)
- [scikit-learn: OneClassSVM](https://scikit-learn.org/stable/modules/generated/sklearn.svm.OneClassSVM.html)
- [scikit-learn: IsolationForest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)

### 実装
- [05_iris_sklearn_outlier](../03_my_implementations/chapter2_training/05_iris_sklearn_outlier/)
- [参考実装](../01_reference/chapter2_training/iris_sklearn_outlier/)

---

**更新履歴**:
- 2025-11-05: 初版作成
