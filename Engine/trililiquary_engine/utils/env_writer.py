from pathlib import Path

def write_env_file(path: Path, data: dict):
    lines = []
    for key, value in data.items():
        lines.append(f"{key}={value}")
    path.write_text("\n".join(lines))
