from unittest.mock import patch

from expense_tracker.utils.migration import migrate_legacy_databases


def test_migrate_legacy_databases_no_legacy_directory(tmp_path, monkeypatch):
    """Test migration when legacy directory doesn't exist."""
    # Change to a temp directory where legacy dir doesn't exist
    monkeypatch.chdir(tmp_path)

    with patch("expense_tracker.utils.migration.get_data_directory") as mock_get_dir:
        mock_get_dir.return_value = tmp_path / "new_data"
        migrate_legacy_databases()
        # Should not create any files if legacy doesn't exist
        assert not (tmp_path / "new_data").exists()


def test_migrate_legacy_databases_success(tmp_path, monkeypatch):
    """Test successful migration of legacy databases."""
    # Set up legacy directory with databases
    legacy_dir = tmp_path / "expense_tracker" / "data"
    legacy_dir.mkdir(parents=True)

    # Create mock legacy database files
    (legacy_dir / "transactions.db").write_text("legacy transactions data")
    (legacy_dir / "merchant_categories.db").write_text("legacy merchant data")

    # Set up new data directory
    new_dir = tmp_path / "new_data"
    new_dir.mkdir(parents=True)

    # Change to tmp_path so relative "expense_tracker/data" works
    monkeypatch.chdir(tmp_path)

    with patch("expense_tracker.utils.migration.get_data_directory") as mock_get_dir:
        mock_get_dir.return_value = new_dir

        migrate_legacy_databases()

        # Check that files were copied
        assert (new_dir / "transactions.db").exists()
        assert (new_dir / "merchant_categories.db").exists()
        assert (new_dir / "transactions.db").read_text() == "legacy transactions data"
        assert (
            new_dir / "merchant_categories.db"
        ).read_text() == "legacy merchant data"

        # Check that legacy files still exist (copy, not move)
        assert (legacy_dir / "transactions.db").exists()
        assert (legacy_dir / "merchant_categories.db").exists()


def test_migrate_legacy_databases_partial_migration(tmp_path, monkeypatch):
    """Test migration when only one database exists in legacy location."""
    legacy_dir = tmp_path / "expense_tracker" / "data"
    legacy_dir.mkdir(parents=True)

    # Create only one legacy database
    (legacy_dir / "transactions.db").write_text("legacy transactions data")

    new_dir = tmp_path / "new_data"
    new_dir.mkdir(parents=True)

    monkeypatch.chdir(tmp_path)

    with patch("expense_tracker.utils.migration.get_data_directory") as mock_get_dir:
        mock_get_dir.return_value = new_dir

        migrate_legacy_databases()

        # Only transactions.db should be migrated
        assert (new_dir / "transactions.db").exists()
        assert not (new_dir / "merchant_categories.db").exists()


def test_migrate_legacy_databases_skip_if_new_exists(tmp_path, monkeypatch):
    """Test that migration skips files that already exist in new location."""
    legacy_dir = tmp_path / "expense_tracker" / "data"
    legacy_dir.mkdir(parents=True)
    (legacy_dir / "transactions.db").write_text("legacy data")

    new_dir = tmp_path / "new_data"
    new_dir.mkdir(parents=True)
    (new_dir / "transactions.db").write_text("new data")

    monkeypatch.chdir(tmp_path)

    with patch("expense_tracker.utils.migration.get_data_directory") as mock_get_dir:
        mock_get_dir.return_value = new_dir

        migrate_legacy_databases()

        # Should not overwrite existing file
        assert (new_dir / "transactions.db").read_text() == "new data"


def test_migrate_legacy_databases_handles_copy_error(tmp_path, monkeypatch, caplog):
    """Test that migration continues even if one file copy fails."""
    legacy_dir = tmp_path / "expense_tracker" / "data"
    legacy_dir.mkdir(parents=True)
    (legacy_dir / "transactions.db").write_text("data1")
    (legacy_dir / "merchant_categories.db").write_text("data2")

    new_dir = tmp_path / "new_data"
    new_dir.mkdir(parents=True)

    monkeypatch.chdir(tmp_path)

    with (
        patch("expense_tracker.utils.migration.get_data_directory") as mock_get_dir,
        patch("shutil.copy2") as mock_copy,
    ):
        mock_get_dir.return_value = new_dir

        # Make first copy fail, second succeed
        mock_copy.side_effect = [
            PermissionError("Cannot copy"),
            new_dir / "merchant_categories.db",
        ]

        migrate_legacy_databases()

        # Should have attempted both copies
        assert mock_copy.call_count == 2
