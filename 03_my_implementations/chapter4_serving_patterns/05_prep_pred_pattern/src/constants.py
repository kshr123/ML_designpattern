"""定数定義モジュール

プロジェクト全体で使用する定数を定義します。
"""

import enum


class PLATFORM_ENUM(enum.Enum):
    """実行環境の列挙型"""

    DOCKER = "docker"
    DOCKER_COMPOSE = "docker_compose"
    KUBERNETES = "kubernetes"
    TEST = "test"

    @staticmethod
    def has_value(item: str) -> bool:
        """指定された値がenumに含まれるかチェック

        Args:
            item: チェックする値

        Returns:
            含まれる場合True、それ以外False
        """
        return item in [v.value for v in PLATFORM_ENUM.__members__.values()]


def constant(f):
    """定数プロパティデコレータ

    プロパティを読み取り専用にするデコレータ。
    """

    def fset(self, value):
        raise TypeError("Cannot modify constant")

    def fget(self):
        return f()

    return property(fget, fset)


class _Constants(object):
    """定数クラス

    プロジェクト全体で使用する定数を定義します。
    """

    @constant
    def IMAGE_SIZE():
        """ResNet50の入力画像サイズ"""
        return (224, 224)

    @constant
    def PREDICTION_SHAPE():
        """推論入力のテンソル形状 (batch, channels, height, width)"""
        return (1, 3, 224, 224)

    @constant
    def IMAGENET_MEAN():
        """ImageNet正規化の平均値 (RGB)"""
        return [0.485, 0.456, 0.406]

    @constant
    def IMAGENET_STDDEV():
        """ImageNet正規化の標準偏差 (RGB)"""
        return [0.229, 0.224, 0.225]

    @constant
    def NUM_CLASSES():
        """ImageNetクラス数"""
        return 1000


CONSTANTS = _Constants()
