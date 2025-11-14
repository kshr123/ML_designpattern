"""ResNet50 ONNXモデルとTransformerの抽出スクリプト

このスクリプトは以下を実行します：
1. ResNet50モデルをONNX形式でエクスポート（--pred）
2. 前処理・後処理transformerをpickleファイルとして保存（--prep）
3. 両方を実行した場合、推論テストを実行（--pred --prep）

Usage:
    python extract_resnet50_onnx.py --pred --prep
"""

import json
import os
from typing import List

import click
import joblib
import numpy as np
import onnxruntime as rt
import torch
from PIL import Image
from src.ml.transformers import PytorchImagePreprocessTransformer, SoftmaxTransformer
from torchvision.models.resnet import resnet50


def dump_sklearn(model, name: str):
    """モデルをpickleファイルとして保存

    Args:
        model: 保存するモデル（transformerオブジェクト）
        name: ファイル名（パス含む）
    """
    joblib.dump(model, name)


def get_label(json_path: str = "./data/image_net_labels.json") -> List[str]:
    """ImageNetラベルを読み込む

    Args:
        json_path: ラベルJSONファイルのパス

    Returns:
        ImageNet 1000クラスのラベルリスト
    """
    with open(json_path, "r") as f:
        labels = json.load(f)
    return labels


@click.command(name="extract resnet50 onnx runtime and preprocessing")
@click.option("--pred", is_flag=True, help="Extract ResNet50 ONNX model for Pred Service")
@click.option("--prep", is_flag=True, help="Extract transformers for Prep Service")
def main(pred: bool, prep: bool):
    """ResNet50 ONNXモデルとTransformerを抽出

    Args:
        pred: Pred Service用のONNXモデルを抽出
        prep: Prep Service用のtransformerを抽出
    """
    model_directory = "./models/"
    os.makedirs(model_directory, exist_ok=True)

    onnx_filename = "resnet50.onnx"
    onnx_filepath = os.path.join(model_directory, onnx_filename)

    preprocess_filename = "preprocess_transformer.pkl"
    preprocess_filepath = os.path.join(model_directory, preprocess_filename)

    postprocess_filename = "softmax_transformer.pkl"
    postprocess_filepath = os.path.join(model_directory, postprocess_filename)

    if pred:
        print("Extracting ResNet50 ONNX model...")
        model = resnet50(pretrained=True)
        x_dummy = torch.rand((1, 3, 224, 224), device="cpu")
        model.eval()
        torch.onnx.export(
            model,
            x_dummy,
            onnx_filepath,
            export_params=True,
            opset_version=10,
            do_constant_folding=True,
            input_names=["input"],
            output_names=["output"],
            verbose=False,
        )
        print(f"✅ Saved ONNX model to {onnx_filepath}")

    if prep:
        print("Extracting preprocessing transformers...")
        preprocess = PytorchImagePreprocessTransformer()
        dump_sklearn(preprocess, preprocess_filepath)
        print(f"✅ Saved preprocess transformer to {preprocess_filepath}")

        postprocess = SoftmaxTransformer()
        dump_sklearn(postprocess, postprocess_filepath)
        print(f"✅ Saved postprocess transformer to {postprocess_filepath}")

    if prep and pred:
        print("\nRunning inference test...")
        image = Image.open("./data/cat.jpg")
        np_image = preprocess.transform(image)
        print(f"Preprocessed image shape: {np_image.shape}")

        sess = rt.InferenceSession(onnx_filepath)
        inp, out = sess.get_inputs()[0], sess.get_outputs()[0]
        print(f"ONNX input: name='{inp.name}' shape={inp.shape} type={inp.type}")
        print(f"ONNX output: name='{out.name}' shape={out.shape} type={out.type}")

        pred_onx = sess.run([out.name], {inp.name: np_image})
        prediction = postprocess.transform(np.array(pred_onx))

        labels = get_label(json_path="./data/image_net_labels.json")
        print(f"Prediction shape: {prediction.shape}")
        predicted_class = labels[np.argmax(prediction[0])]
        print(f"✅ Predicted class: {predicted_class}")


if __name__ == "__main__":
    main()
