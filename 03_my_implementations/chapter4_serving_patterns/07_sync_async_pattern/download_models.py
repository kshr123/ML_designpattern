"""ONNXモデルのダウンロードスクリプト"""
import urllib.request
from pathlib import Path

def download_model(url: str, output_path: Path):
    """モデルをダウンロード"""
    print(f"Downloading {output_path.name}...")
    urllib.request.urlretrieve(url, output_path)
    print(f"✓ Downloaded to {output_path}")

def main():
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # MobileNet v2（同期推論用、速い）
    mobilenet_url = "https://github.com/onnx/models/raw/main/validated/vision/classification/mobilenet/model/mobilenetv2-12.onnx"
    mobilenet_path = models_dir / "mobilenet_v2.onnx"
    
    # ResNet50（非同期推論用、遅くて高精度）
    resnet_url = "https://github.com/onnx/models/raw/main/validated/vision/classification/resnet/model/resnet50-v2-7.onnx"
    resnet_path = models_dir / "resnet50.onnx"
    
    if not mobilenet_path.exists():
        download_model(mobilenet_url, mobilenet_path)
    else:
        print(f"✓ {mobilenet_path.name} already exists")
    
    if not resnet_path.exists():
        download_model(resnet_url, resnet_path)
    else:
        print(f"✓ {resnet_path.name} already exists")
    
    print("\n✅ All models ready!")

if __name__ == "__main__":
    main()
