"""
E2E（End-to-End）テストテンプレート

ユーザーの視点から、システム全体が正しく動作することをテストします。
実際のHTTPリクエストやDocker環境を使用します。
"""

import pytest
import requests
import time
from typing import Any, Generator
import subprocess
import signal


# ===== フィクスチャ =====

@pytest.fixture(scope="module")
def server_url() -> str:
    """テストサーバーのURL"""
    return "http://localhost:8000"


@pytest.fixture(scope="module")
def running_server(server_url: str) -> Generator[str, None, None]:
    """テストサーバーを起動して返す

    テスト実行前にサーバーを起動し、終了後にシャットダウン
    """
    # サーバーの起動
    # process = subprocess.Popen(
    #     ["python", "-m", "uvicorn", "src.main:app", "--port", "8000"],
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE
    # )

    # サーバーが起動するまで待機
    max_retries = 30
    for _ in range(max_retries):
        try:
            response = requests.get(f"{server_url}/health")
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    else:
        # process.kill()
        pytest.fail("Server failed to start")

    yield server_url

    # サーバーのシャットダウン
    # process.send_signal(signal.SIGTERM)
    # process.wait(timeout=5)


@pytest.fixture
def api_client(server_url: str) -> requests.Session:
    """APIクライアントセッション"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def sample_request_data() -> dict[str, Any]:
    """テスト用のリクエストデータ"""
    return {
        "data": {
            "field1": "test_value",
            "field2": 123
        },
        "options": {
            "threshold": 0.5
        }
    }


# ===== ヘルスチェックE2Eテスト =====

class TestHealthCheckE2E:
    """ヘルスチェックのE2Eテスト"""

    def test_health_endpoint_returns_200(
        self, running_server: str, api_client: requests.Session
    ) -> None:
        """ヘルスチェックエンドポイントが200を返すことを確認"""
        # Act
        response = api_client.get(f"{running_server}/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check_response_format(
        self, running_server: str, api_client: requests.Session
    ) -> None:
        """ヘルスチェックのレスポンス形式が正しいことを確認"""
        # Act
        response = api_client.get(f"{running_server}/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert isinstance(data["checks"], dict)


# ===== 推論エンドポイントE2Eテスト =====

class TestPredictionE2E:
    """推論エンドポイントのE2Eテスト"""

    def test_prediction_endpoint_returns_result(
        self,
        running_server: str,
        api_client: requests.Session,
        sample_request_data: dict
    ) -> None:
        """推論エンドポイントが結果を返すことを確認"""
        # Act
        response = api_client.post(
            f"{running_server}/predict",
            json=sample_request_data
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "metadata" in data

    def test_prediction_response_format(
        self,
        running_server: str,
        api_client: requests.Session,
        sample_request_data: dict
    ) -> None:
        """推論レスポンスの形式が仕様通りであることを確認"""
        # Act
        response = api_client.post(
            f"{running_server}/predict",
            json=sample_request_data
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        # 予測結果の確認
        assert "prediction" in data
        prediction = data["prediction"]
        assert "result" in prediction
        assert "confidence" in prediction

        # メタデータの確認
        assert "metadata" in data
        metadata = data["metadata"]
        assert "model_version" in metadata
        assert "timestamp" in metadata
        assert "inference_time_ms" in metadata

    def test_prediction_with_various_inputs(
        self, running_server: str, api_client: requests.Session
    ) -> None:
        """様々な入力で推論が動作することを確認"""
        # Arrange
        test_cases = [
            {"data": {"field1": "value1", "field2": 100}},
            {"data": {"field1": "value2", "field2": 200}},
            {"data": {"field1": "value3", "field2": 300}},
        ]

        # Act & Assert
        for test_input in test_cases:
            response = api_client.post(
                f"{running_server}/predict",
                json=test_input
            )
            assert response.status_code == 200
            data = response.json()
            assert "prediction" in data


# ===== エラーハンドリングE2Eテスト =====

class TestErrorHandlingE2E:
    """エラーハンドリングのE2Eテスト"""

    def test_invalid_request_returns_400(
        self, running_server: str, api_client: requests.Session
    ) -> None:
        """不正なリクエストで400エラーが返ることを確認"""
        # Arrange
        invalid_request = {"invalid": "data"}

        # Act
        response = api_client.post(
            f"{running_server}/predict",
            json=invalid_request
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_missing_required_field_returns_400(
        self, running_server: str, api_client: requests.Session
    ) -> None:
        """必須フィールドが欠けている場合に400エラーが返ることを確認"""
        # Arrange
        incomplete_request = {"options": {"threshold": 0.5}}

        # Act
        response = api_client.post(
            f"{running_server}/predict",
            json=incomplete_request
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "INVALID_INPUT" in data["error"]["code"]

    def test_error_response_format(
        self, running_server: str, api_client: requests.Session
    ) -> None:
        """エラーレスポンスの形式が仕様通りであることを確認"""
        # Arrange
        invalid_request = None

        # Act
        response = api_client.post(
            f"{running_server}/predict",
            json=invalid_request
        )

        # Assert
        assert response.status_code >= 400
        data = response.json()
        assert "error" in data
        error = data["error"]
        assert "code" in error
        assert "message" in error


# ===== パフォーマンスE2Eテスト =====

class TestPerformanceE2E:
    """パフォーマンスのE2Eテスト"""

    def test_response_time_within_limit(
        self,
        running_server: str,
        api_client: requests.Session,
        sample_request_data: dict
    ) -> None:
        """レスポンスタイムが制限内であることを確認"""
        # Arrange
        max_response_time = 1.0  # 1秒

        # Act
        start_time = time.time()
        response = api_client.post(
            f"{running_server}/predict",
            json=sample_request_data
        )
        elapsed_time = time.time() - start_time

        # Assert
        assert response.status_code == 200
        assert elapsed_time < max_response_time

    @pytest.mark.slow
    def test_handles_concurrent_requests(
        self,
        running_server: str,
        api_client: requests.Session,
        sample_request_data: dict
    ) -> None:
        """同時リクエストを処理できることを確認"""
        import concurrent.futures

        # Arrange
        num_concurrent = 10

        def make_request() -> requests.Response:
            return api_client.post(
                f"{running_server}/predict",
                json=sample_request_data
            )

        # Act
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(make_request) for _ in range(num_concurrent)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]

        # Assert
        assert len(responses) == num_concurrent
        assert all(r.status_code == 200 for r in responses)

    @pytest.mark.slow
    def test_sustained_load(
        self,
        running_server: str,
        api_client: requests.Session,
        sample_request_data: dict
    ) -> None:
        """持続的な負荷に耐えられることを確認"""
        # Arrange
        num_requests = 100
        max_avg_response_time = 0.5  # 500ms

        # Act
        start_time = time.time()
        responses = []
        for _ in range(num_requests):
            response = api_client.post(
                f"{running_server}/predict",
                json=sample_request_data
            )
            responses.append(response)
        total_time = time.time() - start_time

        # Assert
        assert all(r.status_code == 200 for r in responses)
        avg_response_time = total_time / num_requests
        assert avg_response_time < max_avg_response_time


# ===== セキュリティE2Eテスト =====

class TestSecurityE2E:
    """セキュリティのE2Eテスト"""

    def test_rejects_malicious_input(
        self, running_server: str, api_client: requests.Session
    ) -> None:
        """悪意のある入力を拒否することを確認"""
        # Arrange
        malicious_inputs = [
            {"data": {"field1": "<script>alert('xss')</script>"}},
            {"data": {"field1": "'; DROP TABLE users; --"}},
            {"data": {"field1": "../../../etc/passwd"}},
        ]

        # Act & Assert
        for malicious_input in malicious_inputs:
            response = api_client.post(
                f"{running_server}/predict",
                json=malicious_input
            )
            # エラーを返すか、安全に処理されることを確認
            assert response.status_code in [200, 400]

    def test_rate_limiting(
        self, running_server: str, api_client: requests.Session
    ) -> None:
        """レート制限が機能することを確認（実装されている場合）"""
        # Arrange
        num_rapid_requests = 100

        # Act
        responses = []
        for _ in range(num_rapid_requests):
            response = api_client.get(f"{running_server}/health")
            responses.append(response)

        # Assert
        # レート制限が実装されている場合、429エラーが返されることを確認
        # status_codes = [r.status_code for r in responses]
        # assert 429 in status_codes or all(code == 200 for code in status_codes)
        pass


# ===== データの整合性E2Eテスト =====

class TestDataConsistencyE2E:
    """データの整合性E2Eテスト"""

    def test_repeated_requests_return_consistent_results(
        self,
        running_server: str,
        api_client: requests.Session,
        sample_request_data: dict
    ) -> None:
        """同じ入力で一貫した結果が返ることを確認"""
        # Act
        responses = []
        for _ in range(5):
            response = api_client.post(
                f"{running_server}/predict",
                json=sample_request_data
            )
            responses.append(response.json())

        # Assert
        # 全てのレスポンスが同じ予測結果を返すことを確認
        results = [r["prediction"]["result"] for r in responses]
        assert all(result == results[0] for result in results)


# ===== ログとモニタリングE2Eテスト =====

class TestLoggingAndMonitoringE2E:
    """ログとモニタリングのE2Eテスト"""

    def test_metrics_endpoint_available(
        self, running_server: str, api_client: requests.Session
    ) -> None:
        """メトリクスエンドポイントが利用可能であることを確認"""
        # Act
        response = api_client.get(f"{running_server}/metrics")

        # Assert
        # メトリクスエンドポイントが実装されている場合
        # assert response.status_code == 200
        pass

    def test_request_logging(
        self,
        running_server: str,
        api_client: requests.Session,
        sample_request_data: dict
    ) -> None:
        """リクエストがログに記録されることを確認"""
        # Act
        response = api_client.post(
            f"{running_server}/predict",
            json=sample_request_data
        )

        # Assert
        assert response.status_code == 200
        # ログファイルを確認するか、ログ収集システムから確認
        pass


# ===== Docker環境でのE2Eテスト =====

@pytest.mark.docker
class TestDockerE2E:
    """Docker環境でのE2Eテスト"""

    @pytest.fixture(scope="class")
    def docker_container(self) -> Generator[str, None, None]:
        """Dockerコンテナを起動"""
        # subprocess.run(["docker-compose", "up", "-d"], check=True)
        time.sleep(10)  # コンテナ起動待ち

        yield "http://localhost:8000"

        # subprocess.run(["docker-compose", "down"], check=True)

    def test_docker_service_running(self, docker_container: str) -> None:
        """Dockerコンテナでサービスが動作することを確認"""
        # Act
        response = requests.get(f"{docker_container}/health")

        # Assert
        assert response.status_code == 200


# テスト実行時のマーカー
# pytest -m "not slow" でスローテストをスキップ
# pytest -m "not docker" でDockerテストをスキップ
