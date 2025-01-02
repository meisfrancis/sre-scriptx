from math import ceil
import subprocess
from ruamel.yaml import YAML


def byte_to_mb(b: int) -> int:
    return ceil(b / (1024 * 1024))


def run(commands):
    results = {}
    for command in commands:
        process = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
        results[command] = process.stdout
    return results


def load_yaml_config() -> dict:
    yaml = YAML()
    with open('config.yaml', 'r') as f:
        return yaml.load(f)

