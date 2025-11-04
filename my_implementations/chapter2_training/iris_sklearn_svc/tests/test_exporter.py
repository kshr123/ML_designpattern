"""
Tests for exporter module
"""

import os
from pathlib import Path

import onnx
import pytest

from iris_sklearn_svc.data_loader import get_data
from iris_sklearn_svc.exporter import export_to_onnx
from iris_sklearn_svc.model import build_pipeline
from iris_sklearn_svc.trainer import train_model


class TestExportToOnnx:
    """Tests for export_to_onnx function"""

    @pytest.fixture
    def trained_model(self):
        """学習済みモデルを準備"""
        x_train, x_test, y_train, y_test = get_data(test_size=0.3, random_state=42)
        pipeline = build_pipeline()
        trained_model = train_model(pipeline, x_train, y_train)
        return trained_model

    @pytest.fixture
    def output_path(self, tmp_path):
        """テスト用の出力パスを準備"""
        return str(tmp_path / "model.onnx")

    def test_export_creates_file(self, trained_model, output_path):
        """ONNXファイルが作成されることを確認"""
        export_to_onnx(trained_model, output_path)

        assert os.path.exists(output_path)

    def test_exported_file_is_valid_onnx(self, trained_model, output_path):
        """エクスポートされたファイルが有効なONNXモデルであることを確認"""
        export_to_onnx(trained_model, output_path)

        # ONNXモデルとして読み込めることを確認
        onnx_model = onnx.load(output_path)
        assert onnx_model is not None

    def test_onnx_model_passes_checker(self, trained_model, output_path):
        """ONNXモデルがチェッカーを通過することを確認"""
        export_to_onnx(trained_model, output_path)

        onnx_model = onnx.load(output_path)
        # checker.check_modelでエラーが出ないことを確認
        onnx.checker.check_model(onnx_model)

    def test_onnx_model_has_correct_input_shape(self, trained_model, output_path):
        """ONNXモデルの入力形状が正しいことを確認"""
        export_to_onnx(trained_model, output_path)

        onnx_model = onnx.load(output_path)

        # 入力ノードを取得
        input_tensor = onnx_model.graph.input[0]

        # Irisデータセットは4次元特徴量
        # 形状: [batch_size, 4]
        assert len(input_tensor.type.tensor_type.shape.dim) == 2
        assert input_tensor.type.tensor_type.shape.dim[1].dim_value == 4  # 4つの特徴量

    def test_onnx_model_has_output(self, trained_model, output_path):
        """ONNXモデルに出力ノードがあることを確認"""
        export_to_onnx(trained_model, output_path)

        onnx_model = onnx.load(output_path)

        # 出力ノードが存在することを確認
        assert len(onnx_model.graph.output) > 0

    def test_export_with_different_path(self, trained_model, tmp_path):
        """異なるパスでエクスポートできることを確認"""
        output_path = str(tmp_path / "subdir" / "custom_model.onnx")

        # 親ディレクトリを作成
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        export_to_onnx(trained_model, output_path)

        assert os.path.exists(output_path)

    def test_export_overwrites_existing_file(self, trained_model, output_path):
        """既存のファイルを上書きできることを確認"""
        # 1回目のエクスポート
        export_to_onnx(trained_model, output_path)
        first_mtime = os.path.getmtime(output_path)

        # 少し待ってから2回目のエクスポート
        import time

        time.sleep(0.1)

        export_to_onnx(trained_model, output_path)
        second_mtime = os.path.getmtime(output_path)

        # ファイルが更新されている
        assert second_mtime > first_mtime

    def test_exported_model_metadata(self, trained_model, output_path):
        """エクスポートされたモデルにメタデータがあることを確認"""
        export_to_onnx(trained_model, output_path)

        onnx_model = onnx.load(output_path)

        # モデルがグラフを持つことを確認
        assert onnx_model.graph is not None
        assert len(onnx_model.graph.node) > 0  # ノードが存在

    def test_file_size_is_reasonable(self, trained_model, output_path):
        """エクスポートされたファイルサイズが妥当であることを確認"""
        export_to_onnx(trained_model, output_path)

        file_size = os.path.getsize(output_path)

        # SVCモデルは小さいはず（1KB - 10MB）
        assert 1024 < file_size < 10 * 1024 * 1024
