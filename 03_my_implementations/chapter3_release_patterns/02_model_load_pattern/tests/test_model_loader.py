"""InitContainerのモデルローダーのテスト"""
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from model_loader.main import download_model


class TestModelLoader:
    """モデルローダーのテストクラス"""

    def test_download_model_from_gcs_success(self, tmp_path: Path):
        """GCSからモデルをダウンロードできる"""
        # Arrange
        gcs_bucket = "test-bucket"
        gcs_model_blob = "models/iris_svc.onnx"
        model_filepath = str(tmp_path / "model.onnx")

        # GCSクライアントをモック
        with patch("model_loader.main.storage.Client") as mock_client:
            mock_storage_client = MagicMock()
            mock_bucket = MagicMock()
            mock_blob = MagicMock()

            mock_client.create_anonymous_client.return_value = mock_storage_client
            mock_storage_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob

            # Act
            download_model(
                gcs_bucket=gcs_bucket,
                gcs_model_blob=gcs_model_blob,
                model_filepath=model_filepath,
            )

            # Assert
            mock_client.create_anonymous_client.assert_called_once()
            mock_storage_client.bucket.assert_called_once_with(gcs_bucket)
            mock_bucket.blob.assert_called_once_with(gcs_model_blob)
            mock_blob.download_to_filename.assert_called_once_with(model_filepath)

    def test_download_model_creates_directory(self, tmp_path: Path):
        """モデル保存先のディレクトリが存在しない場合、作成される"""
        # Arrange
        gcs_bucket = "test-bucket"
        gcs_model_blob = "models/iris_svc.onnx"
        model_filepath = str(tmp_path / "subdir" / "model.onnx")

        assert not os.path.exists(tmp_path / "subdir")

        # GCSクライアントをモック
        with patch("model_loader.main.storage.Client") as mock_client:
            mock_storage_client = MagicMock()
            mock_bucket = MagicMock()
            mock_blob = MagicMock()

            mock_client.create_anonymous_client.return_value = mock_storage_client
            mock_storage_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob

            # Act
            download_model(
                gcs_bucket=gcs_bucket,
                gcs_model_blob=gcs_model_blob,
                model_filepath=model_filepath,
            )

            # Assert
            assert os.path.exists(tmp_path / "subdir")

    def test_download_model_with_invalid_gcs_path(self, tmp_path: Path):
        """GCSパスが無効な場合、エラーが発生する"""
        # Arrange
        gcs_bucket = ""
        gcs_model_blob = ""
        model_filepath = str(tmp_path / "model.onnx")

        # Act & Assert
        with pytest.raises(ValueError):
            download_model(
                gcs_bucket=gcs_bucket,
                gcs_model_blob=gcs_model_blob,
                model_filepath=model_filepath,
            )
