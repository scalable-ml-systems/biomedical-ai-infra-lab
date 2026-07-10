from app.config.settings import get_settings


def test_settings_load_defaults() -> None:
    settings = get_settings()

    assert settings.app_env == "local"
    assert settings.enable_pubmed is True
    assert settings.enable_graph_validation is True
    assert settings.enable_strict_safety is True
    assert settings.ncbi_tool_name == "governed-biomedical-graphrag"
