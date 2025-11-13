"""
Configurationsモジュールのテスト

このモジュールは、環境変数の読み込みと設定管理をテストします。
"""

import os
import pytest


class TestModelConfigurations:
    """ModelConfigurationsクラスのテスト"""

    def test_model_filepath_default(self):
        """MODEL_FILEPATHのデフォルト値を取得できる"""
        from src.configurations.constants import ModelConfigurations

        # 環境変数が設定されていない場合のデフォルト値
        assert ModelConfigurations.model_filepath is not None
        assert isinstance(ModelConfigurations.model_filepath, str)

    def test_label_filepath_default(self):
        """LABEL_FILEPATHのデフォルト値を取得できる"""
        from src.configurations.constants import ModelConfigurations

        # 環境変数が設定されていない場合のデフォルト値
        assert ModelConfigurations.label_filepath is not None
        assert isinstance(ModelConfigurations.label_filepath, str)


class TestAPIConfigurations:
    """APIConfigurationsクラスのテスト"""

    def test_api_title_default(self):
        """API_TITLEのデフォルト値を取得できる"""
        from src.configurations.constants import APIConfigurations

        assert APIConfigurations.title is not None
        assert isinstance(APIConfigurations.title, str)

    def test_api_description_default(self):
        """API_DESCRIPTIONのデフォルト値を取得できる"""
        from src.configurations.constants import APIConfigurations

        assert APIConfigurations.description is not None
        assert isinstance(APIConfigurations.description, str)

    def test_api_version_default(self):
        """API_VERSIONのデフォルト値を取得できる"""
        from src.configurations.constants import APIConfigurations

        assert APIConfigurations.version is not None
        assert isinstance(APIConfigurations.version, str)
