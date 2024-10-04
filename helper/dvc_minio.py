"""
dvc's python api is implemented for reading only.
If you try to use the python api for writing, you will end up using the internal API.
Therefore, subprocess is used.
"""

import subprocess
from pathlib import Path
from typing import List
from . import types

class DvcMinio:
    def __init__(self, temp_dir: Path, config: types.Bucket):
        # TODO: The value of minio is currently passed to subprocess
        # so verify the value appropriately or implement it differently.
        self._temp_dir = temp_dir
        self._config = config

    def init(self):
        config = self._config
        self._exec(["dvc", "init"])
        self._exec(["dvc", "remote", "add", "-d", config.remote_name, config.url])
        self._exec(["dvc", "config", "core.autostage", "true"])
        self._modify(["endpointurl", self._config.endpointurl])
        self._modify(["access_key_id", self._config.access_key_id])
        self._modify(["secret_access_key", self._config.secret_access_key])
    
    def _exec(self, args: List[str]):
        subprocess.run(args, check=True, cwd=self._temp_dir)

    def _modify(self, args: List[str]):
        self._exec(["dvc", "remote", "modify", self._config.remote_name, *args])
