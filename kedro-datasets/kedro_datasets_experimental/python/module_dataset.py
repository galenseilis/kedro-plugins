from __future__ import annotations

import ast
import importlib.util
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Any, Dict, Final, Optional

from kedro.io.core import AbstractVersionedDataset, Version


class PythonModuleDataset(AbstractVersionedDataset[str, ModuleType]):
    """Kedro dataset for loading Python modules from a file path."""

    DEFAULT_LOAD_ARGS: Final[Dict[str, Any]] = {}
    DEFAULT_SAVE_ARGS: Final[Dict[str, Any]] = {}

    def __init__(
        self,
        filepath: str | PurePosixPath,
        version: Version | None = None,
        load_args: Optional[Dict[str, Any]] = None,
        save_args: Optional[Dict[str, Any]] = None,
    ) -> None:


        super().__init__(
            filepath=PurePosixPath(filepath),
            version=version,
        )

        self._load_args = {**self.DEFAULT_LOAD_ARGS, **(load_args or {})}
        self._save_args = {**self.DEFAULT_SAVE_ARGS, **(save_args or {})}

    def _load(self) -> ModuleType:
        """Load a Python module dynamically from file."""
        resolved_path = PurePosixPath(self._get_load_path())

        spec = importlib.util.spec_from_file_location(
            name=resolved_path.stem,
            location=str(resolved_path),
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot import module from {resolved_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _save(self, data: str) -> None:
        """
        Saving is optional. If enabled, `data` must be a string of Python code
        that will be written to the module file.
        """
        ast.parse(data) # Check if data has valid Python syntax.
        save_path = Path(self._get_save_path())
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(data, encoding="utf8")

    def _exists(self) -> bool:
        return Path(self._get_load_path()).exists()

    def _describe(self) -> Dict[str, Any]:
        return {
            "filepath": str(self._filepath),
            "version": self._version,
        }
