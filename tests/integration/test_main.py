import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.config import Settings
from app.main import create_app

def test_create_app_default_settings():
    app = create_app()
    assert app.title == Settings().APP_TITLE
    assert app.description == Settings().APP_DESCRIPTION
    assert app.version == Settings().APP_VERSION

def test_create_app_custom_settings():
    custom_settings = Settings(
        APP_TITLE="Custom Pokemon API",
        APP_DESCRIPTION="Custom Description",
        APP_VERSION="2.0.0",
        ALLOWED_ORIGINS=["http://localhost:3000"],
        LOG_LEVEL="DEBUG",
        LOG_FILE="custom.log",
        JSON_LOG_FORMAT=True
    )
    
    app = create_app(settings=custom_settings)
    assert app.title == "Custom Pokemon API"
    assert app.description == "Custom Description"
    assert app.version == "2.0.0"

@pytest.fixture
def test_app():
    app = create_app()
    return TestClient(app)

def test_logging_middleware_integration(test_app):
    with patch('app.middleware.logging_middleware.logging.getLogger') as mock_logger:
        test_app.get("/api/v1/pokemon")
        assert mock_logger.called

def test_nonexistent_endpoint(test_app):
    response = test_app.get("/api/v1/nonexistent")
    assert response.status_code == 404
