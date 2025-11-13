"""gRPC Protocol Buffers

ONNX Runtime Serverとの通信に使用するProtocol Buffersの定義。

モジュール:
- onnx_ml_pb2: ONNX型定義（TensorProtoなど）
- predict_pb2: 推論リクエスト/レスポンスメッセージ
- prediction_service_pb2_grpc: 推論サービスのgRPCスタブ
"""

from src.proto import onnx_ml_pb2, predict_pb2, prediction_service_pb2_grpc

__all__ = ["onnx_ml_pb2", "predict_pb2", "prediction_service_pb2_grpc"]
