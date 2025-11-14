# 統合テスト結果

## テスト実施日時
2025-11-14 10:26

## テスト環境
- Docker Compose
- Proxyポート: 9100
- Service Setosaポート: 9101
- Service Versicolorポート: 9102
- Service Virginicaポート: 9103

## テスト結果

### 1. ヘルスチェック ✅
**Proxy単独**:
```json
{"health":"ok"}
```

**全サービス**:
```json
{
    "setosa": {"health": "ok"},
    "versicolor": {"health": "ok"},
    "virginica": {"health": "ok"}
}
```

### 2. 並列推論（テストデータ: setosa） ✅
**リクエスト**: `POST /predict/post/test`

**レスポンス**:
```json
{
    "setosa": {
        "prediction": [0.9824145436286926, 0.017585480585694313]
    },
    "versicolor": {
        "prediction": [0.0046140821650624275, 0.995386004447937]
    },
    "virginica": {
        "prediction": [0.011562097817659378, 0.988437831401825]
    }
}
```

**結果**: setosaが98.2%で正しく分類

### 3. ラベル選択（setosa） ✅
**リクエスト**: `POST /predict/label`
```json
{"data": [[5.1, 3.5, 1.4, 0.2]]}
```

**レスポンス**:
```json
{
    "prediction": {
        "proba": 0.9824145436286926,
        "label": "setosa"
    }
}
```

**結果**: 最も高い確率（98.2%）でsetosaを正しく選択

### 4. ラベル選択（virginica） ✅
**リクエスト**: `POST /predict/label`
```json
{"data": [[6.5, 3.0, 5.5, 1.8]]}
```

**レスポンス**:
```json
{
    "prediction": {
        "proba": 0.9521787762641907,
        "label": "virginica"
    }
}
```

**結果**: 最も高い確率（95.2%）でvirginicaを正しく選択

## 結論

✅ **すべてのテストが成功**

- Proxyが3つのサービスに並列リクエストを送信
- asyncio.gatherで並列実行を確認
- 各サービスがONNX Runtimeで正しく推論
- 最良のラベル選択が正常に動作

**Horizontal Microservice Pattern の実装は完全に動作しています！**
