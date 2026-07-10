from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
BUILD_ROOT = REPO_ROOT / "builds" / "001-governed-biomedical-graphrag"


def test_expected_build_directories_exist() -> None:
    expected_directories = [
        BUILD_ROOT / "app" / "api",
        BUILD_ROOT / "app" / "contracts",
        BUILD_ROOT / "app" / "retrieval",
        BUILD_ROOT / "app" / "graph",
        BUILD_ROOT / "app" / "generation",
        BUILD_ROOT / "app" / "validation",
        BUILD_ROOT / "app" / "audit",
        BUILD_ROOT / "app" / "dashboard",
        BUILD_ROOT / "app" / "config",
        BUILD_ROOT / "data" / "cached_sources" / "dailymed",
        BUILD_ROOT / "data" / "cached_sources" / "pubmed",
        BUILD_ROOT / "data" / "graph_seed",
        BUILD_ROOT / "evals",
        BUILD_ROOT / "tests",
    ]

    for directory in expected_directories:
        assert directory.exists(), f"Missing expected directory: {directory}"
        assert directory.is_dir(), f"Expected directory path is not a directory: {directory}"


def test_expected_documentation_files_exist() -> None:
    expected_files = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs" / "safety_boundaries.md",
        BUILD_ROOT / "README.md",
        BUILD_ROOT / "docs" / "scope.md",
        BUILD_ROOT / "docs" / "technical_specification.md",
        BUILD_ROOT / "docs" / "implementation_plan.md",
    ]

    for file_path in expected_files:
        assert file_path.exists(), f"Missing expected file: {file_path}"
        assert file_path.is_file(), f"Expected file path is not a file: {file_path}"
