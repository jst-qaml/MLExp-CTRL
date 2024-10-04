import yaml
import tempfile
from pathlib import Path
from typing import Dict, Any

ANY_DICT = str | Dict[str, Any]

def dict2yaml(value: ANY_DICT):
    if type(value) == str:
        return value
    return yaml.dump(value, default_flow_style=False)


ROOT_DIR = Path(__file__).parent.parent
TEMP_FOLDER = ROOT_DIR / '.temp'

class TempDirectoryManager:
    def __init__(self):
        self.temp_dir = None
    
    def __enter__(self):
        TEMP_FOLDER.mkdir(exist_ok=True)
        self.temp_dir = tempfile.TemporaryDirectory(dir=TEMP_FOLDER)
        return Path(self.temp_dir.name)
    
    def __exit__(self, exc, value, tb):
        if self.temp_dir is not None:
            self.temp_dir.cleanup()
