import sys
import yaml
import datetime
from pathlib import Path

def data_gen(input_path: Path, output_path: Path):
    data = yaml.safe_load(input_path.open('r'))
    data['time'] = str(datetime.datetime.now())
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(yaml.dump(data, default_flow_style=False))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python data-gen.py <input_path> <output_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    data_gen(Path(input_path), Path(output_path))
