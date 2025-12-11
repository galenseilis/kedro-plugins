import pytest
import textwrap
from pathlib import Path, PurePosixPath
from kedro.io.core import Version, DatasetError

# Adjust import for your package structure
from kedro_datasets_experimental.python.module_dataset import PythonModuleDataset


def test_save_and_load_module(tmp_path):
    module_code = textwrap.dedent("""
        VALUE = 42
        def add(x, y):
            return x + y
    """)

    module_file = tmp_path / "mymod.py"
    ds = PythonModuleDataset(filepath=str(module_file))

    ds.save(module_code)
    assert module_file.exists()

    mod = ds.load()
    assert mod.VALUE == 42
    assert mod.add(1, 2) == 3


def test_save_invalid_syntax(tmp_path):
    module_file = tmp_path / "bad.py"
    ds = PythonModuleDataset(filepath=str(module_file))

    bad_code = "def broken(:"

    # Kedro wraps SyntaxError inside DatasetError
    with pytest.raises(DatasetError):
        ds.save(bad_code)


def test_exists(tmp_path):
    module_file = tmp_path / "exists.py"
    ds = PythonModuleDataset(filepath=str(module_file))

    assert ds.exists() is False

    module_file.write_text("x = 1")
    assert ds.exists() is True


def test_load_nonexistent_file(tmp_path):
    module_file = tmp_path / "missing.py"
    ds = PythonModuleDataset(filepath=str(module_file))

    # Kedro wraps FileNotFoundError in DatasetError
    with pytest.raises(DatasetError):
        ds.load()

def test_describe(tmp_path):
    module_file = tmp_path / "foo.py"
    version = Version(load="2024-01-01T00.00.00.000Z", save=None)

    ds = PythonModuleDataset(filepath=str(module_file), version=version)
    desc = ds._describe()

    assert desc["filepath"] == str(PurePosixPath(module_file))
    assert desc["version"] == version


def test_filepath_is_pureposixpath(tmp_path):
    module_file = tmp_path / "x.py"
    ds = PythonModuleDataset(filepath=str(module_file))

    assert isinstance(ds._filepath, PurePosixPath)
    assert ds._filepath.as_posix().endswith("x.py")
