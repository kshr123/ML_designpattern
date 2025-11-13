"""設定管理のテスト"""
import os

import pytest


class TestModelConfigurations:
    """モデル設定のテストクラス"""

    def test_model_filepath_default(self):
        """環境変数が設定されていない場合、デフォルトパスを使用する"""
        # Arrange
        from src.configurations import ModelConfigurations

        # Act & Assert
        # デフォルトパスは models/iris_svc.onnx
        assert "iris_svc.onnx" in ModelConfigurations.model_filepath

    def test_label_filepath_default(self):
        """環境変数が設定されていない場合、デフォルトラベルパスを使用する"""
        # Arrange
        from src.configurations import ModelConfigurations

        # Act & Assert
        assert "label.json" in ModelConfigurations.label_filepath


class TestAPIConfigurations:
    """API設定のテストクラス"""

    def test_api_title_default(self):
        """環境変数が設定されていない場合、デフォルトタイトルを使用する"""
        # Arrange
        from src.configurations import APIConfigurations

        # Act & Assert
        assert APIConfigurations.title is not None
        assert len(APIConfigurations.title) > 0

    def test_api_description_default(self):
        """環境変数が設定されていない場合、デフォルト説明を使用する"""
        # Arrange
        from src.configurations import APIConfigurations

        # Act & Assert
        assert APIConfigurations.description is not None
        assert len(APIConfigurations.description) > 0
