import platform
from pathlib import Path
from unittest.mock import patch
import os

from expense_tracker.utils.path import get_data_directory, get_database_path


def test_get_data_directory_macos():
    """Test data directory resolution on macOS."""
    with patch("platform.system", return_value="Darwin"):
        data_dir = get_data_directory()
        expected = Path.home() / "Library" / "Application Support" / "spendwise-tracker"
        assert data_dir == expected
        assert data_dir.exists()


def test_get_data_directory_linux():
    """Test data directory resolution on Linux."""
    with patch("platform.system", return_value="Linux"):
        data_dir = get_data_directory()
        expected = Path.home() / ".local" / "share" / "spendwise-tracker"
        assert data_dir == expected
        assert data_dir.exists()


def test_get_data_directory_windows():
    """Test data directory resolution on Windows."""
    with (
        patch("platform.system", return_value="Windows"),
        patch.dict(os.environ, {"LOCALAPPDATA": str(Path.home() / "AppData" / "Local")}),
    ):
        data_dir = get_data_directory()
        expected = Path.home() / "AppData" / "Local" / "spendwise-tracker"
        assert data_dir == expected
        assert data_dir.exists()


def test_get_data_directory_creates_directory(tmp_path, monkeypatch):
    """Test that get_data_directory creates the directory if it doesn't exist."""
    # Mock home directory to tmp_path
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    with patch("platform.system", return_value="Linux"):
        data_dir = get_data_directory()
        assert data_dir.exists()
        assert data_dir.is_dir()


def test_get_database_path():
    """Test database path construction."""
    db_path = get_database_path("transactions.db")
    assert db_path.name == "transactions.db"
    assert db_path.parent == get_data_directory()


def test_get_database_path_merchant_categories():
    """Test merchant categories database path."""
    db_path = get_database_path("merchant_categories.db")
    assert db_path.name == "merchant_categories.db"
    assert db_path.parent == get_data_directory()


def test_data_directory_on_current_platform():
    """Test that data directory is created correctly on the current platform."""
    data_dir = get_data_directory()
    system = platform.system()

    if system == "Darwin":
        assert "Library/Application Support/spendwise-tracker" in str(data_dir)
    elif system == "Windows":
        assert "spendwise-tracker" in str(data_dir)
        assert ("AppData" in str(data_dir) or "LOCALAPPDATA" in str(data_dir))
    else:  # Linux and Unix-like
        assert ".local/share/spendwise-tracker" in str(data_dir)

    assert data_dir.exists()
    assert data_dir.is_dir()
