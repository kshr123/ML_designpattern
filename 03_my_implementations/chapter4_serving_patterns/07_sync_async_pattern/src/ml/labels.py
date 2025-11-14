"""ImageNetラベル（簡略版）"""

# ImageNet 1000クラスの代表的なラベル（簡略版）
IMAGENET_LABELS = {
    0: "tench",
    1: "goldfish",
    2: "great white shark",
    # ... 省略 ...
    281: "tabby cat",
    282: "tiger cat",
    283: "Persian cat",
    284: "Siamese cat",
    285: "Egyptian cat",
    # ... 省略 ...
    999: "ear",
}


def get_label(class_id: int) -> str:
    """クラスIDからラベル名を取得"""
    return IMAGENET_LABELS.get(class_id, f"class_{class_id}")
