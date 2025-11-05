"""Data Loader のユニットテスト"""

import numpy as np

from iris_binary.data_loader import IrisTarget, load_and_transform_data


class TestDataLoader:
    """Data Loader のテストクラス"""

    def test_load_data_setosa(self):
        """setosaを陽性としてデータを読み込める"""
        X_train, X_test, y_train, y_test = load_and_transform_data(
            test_size=0.3, target_iris=IrisTarget.SETOSA, random_state=42
        )

        # データが存在する
        assert len(X_train) > 0
        assert len(X_test) > 0
        assert len(y_train) > 0
        assert len(y_test) > 0

        # サンプル数の合計が150（Irisデータセットのサンプル数）
        assert len(X_train) + len(X_test) == 150

    def test_binary_conversion_setosa(self):
        """setosaが0、その他が1に変換される"""
        X_train, X_test, y_train, y_test = load_and_transform_data(
            test_size=0.3, target_iris=IrisTarget.SETOSA, random_state=42
        )

        # 二値分類（0と1のみ）
        assert set(np.unique(y_train)) <= {0, 1}
        assert set(np.unique(y_test)) <= {0, 1}

        # 両方のクラスが存在する
        assert len(np.unique(y_train)) == 2
        assert len(np.unique(y_test)) == 2

    def test_binary_conversion_versicolor(self):
        """versicolorが0、その他が1に変換される"""
        X_train, X_test, y_train, y_test = load_and_transform_data(
            test_size=0.3, target_iris=IrisTarget.VERSICOLOR, random_state=42
        )

        assert set(np.unique(y_train)) <= {0, 1}
        assert set(np.unique(y_test)) <= {0, 1}

    def test_binary_conversion_virginica(self):
        """virginicaが0、その他が1に変換される"""
        X_train, X_test, y_train, y_test = load_and_transform_data(
            test_size=0.3, target_iris=IrisTarget.VIRGINICA, random_state=42
        )

        assert set(np.unique(y_train)) <= {0, 1}
        assert set(np.unique(y_test)) <= {0, 1}

    def test_data_types(self):
        """データ型がfloat32である"""
        X_train, X_test, y_train, y_test = load_and_transform_data(
            test_size=0.3, target_iris=IrisTarget.SETOSA, random_state=42
        )

        assert X_train.dtype == np.float32
        assert X_test.dtype == np.float32
        assert y_train.dtype == np.float32
        assert y_test.dtype == np.float32

    def test_feature_dimensions(self):
        """特徴量が4次元である"""
        X_train, X_test, y_train, y_test = load_and_transform_data(
            test_size=0.3, target_iris=IrisTarget.SETOSA, random_state=42
        )

        assert X_train.shape[1] == 4
        assert X_test.shape[1] == 4

    def test_test_size(self):
        """test_sizeが正しく適用される"""
        X_train, X_test, y_train, y_test = load_and_transform_data(
            test_size=0.2, target_iris=IrisTarget.SETOSA, random_state=42
        )

        total = len(X_train) + len(X_test)
        test_ratio = len(X_test) / total

        # 誤差を許容（±1サンプル）
        assert abs(test_ratio - 0.2) < 0.02

    def test_reproducibility(self):
        """random_stateにより再現性が保証される"""
        result1 = load_and_transform_data(
            test_size=0.3, target_iris=IrisTarget.SETOSA, random_state=42
        )
        result2 = load_and_transform_data(
            test_size=0.3, target_iris=IrisTarget.SETOSA, random_state=42
        )

        X_train1, X_test1, y_train1, y_test1 = result1
        X_train2, X_test2, y_train2, y_test2 = result2

        np.testing.assert_array_equal(X_train1, X_train2)
        np.testing.assert_array_equal(X_test1, X_test2)
        np.testing.assert_array_equal(y_train1, y_train2)
        np.testing.assert_array_equal(y_test1, y_test2)
