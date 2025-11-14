"""Proxyサービスのエンドポイント

3つの専門サービスに並列リクエストを送信（asyncio.gather）
"""

import asyncio
import uuid
from typing import Any, Dict

import httpx
from fastapi import APIRouter

from src.configurations import AppConfig, ProxyConfig
from src.models import PredictRequest

router = APIRouter()


@router.get("/health")
def health() -> Dict[str, str]:
    """ヘルスチェック"""
    return {"health": "ok"}


@router.get("/health/all")
async def health_all() -> Dict[str, Any]:
    """全サービスのヘルスチェック"""
    services = ProxyConfig.get_services()
    results = {}

    async with httpx.AsyncClient() as client:

        async def check_health(service_name: str, url: str):
            """個別サービスのヘルスチェック"""
            response = await client.get(f"{url}/health")
            return service_name, response.json()

        # 並列実行
        tasks = [check_health(name, url) for name, url in services.items()]
        responses = await asyncio.gather(*tasks)

        for service_name, result in responses:
            results[service_name] = result

    return results


@router.get("/metadata")
def metadata() -> Dict[str, Any]:
    """メタデータ取得"""
    return {
        "data_type": "float32",
        "data_structure": "(1,4)",
        "data_sample": AppConfig.test_data,
        "prediction_type": "float32",
        "prediction_structure": "(1,2)",
        "prediction_sample": {
            "service_setosa": [0.97, 0.03],
            "service_versicolor": [0.97, 0.03],
            "service_virginica": [0.97, 0.03],
        },
    }


@router.get("/predict/get/test")
async def predict_get_test() -> Dict[str, Any]:
    """テストデータで推論（GET）"""
    job_id = str(uuid.uuid4())[:6]
    services = ProxyConfig.get_services()
    results = {}

    async with httpx.AsyncClient() as client:

        async def send_request(service_name: str, url: str):
            """個別サービスに推論リクエスト"""
            response = await client.get(f"{url}/predict/test", params={"id": job_id})
            return service_name, response.json()

        # 並列実行
        tasks = [send_request(name, url) for name, url in services.items()]
        responses = await asyncio.gather(*tasks)

        for service_name, result in responses:
            results[service_name] = result

    return results


@router.post("/predict/post/test")
async def predict_post_test() -> Dict[str, Any]:
    """テストデータで推論（POST）"""
    job_id = str(uuid.uuid4())[:6]
    services = ProxyConfig.get_services()
    results = {}

    test_request = PredictRequest(data=AppConfig.test_data)

    async with httpx.AsyncClient() as client:

        async def send_request(service_name: str, url: str):
            """個別サービスに推論リクエスト"""
            response = await client.post(
                f"{url}/predict",
                json={"data": test_request.data},
                params={"id": job_id},
            )
            return service_name, response.json()

        # 並列実行
        tasks = [send_request(name, url) for name, url in services.items()]
        responses = await asyncio.gather(*tasks)

        for service_name, result in responses:
            results[service_name] = result

    return results


@router.post("/predict")
async def predict(request: PredictRequest) -> Dict[str, Any]:
    """推論実行（全サービス）"""
    job_id = str(uuid.uuid4())[:6]
    services = ProxyConfig.get_services()
    results = {}

    async with httpx.AsyncClient() as client:

        async def send_request(service_name: str, url: str):
            """個別サービスに推論リクエスト"""
            response = await client.post(
                f"{url}/predict", json={"data": request.data}, params={"id": job_id}
            )
            return service_name, response.json()

        # 並列実行（重要！）
        tasks = [send_request(name, url) for name, url in services.items()]
        responses = await asyncio.gather(*tasks)

        for service_name, result in responses:
            results[service_name] = result

    return results


@router.post("/predict/label")
async def predict_label(request: PredictRequest) -> Dict[str, Any]:
    """推論実行（最良ラベル選択）"""
    job_id = str(uuid.uuid4())[:6]
    services = ProxyConfig.get_services()

    best_label = None
    best_proba = -1.0

    async with httpx.AsyncClient() as client:

        async def send_request(service_name: str, url: str):
            """個別サービスに推論リクエスト"""
            response = await client.post(
                f"{url}/predict", json={"data": request.data}, params={"id": job_id}
            )
            return service_name, response.json()

        # 並列実行
        tasks = [send_request(name, url) for name, url in services.items()]
        responses = await asyncio.gather(*tasks)

        # 最も高い確率を持つクラスを選択
        for service_name, result in responses:
            proba = result["prediction"][0]  # そのクラスである確率
            if proba > best_proba:
                best_proba = proba
                best_label = service_name

    return {"prediction": {"proba": best_proba, "label": best_label}}
