import sys
from pathlib import Path

import yaml

CURRENT_DIR = Path(sys.argv[0] if __name__ == "__main__" else __file__).resolve().parent


service_to_path = {
    path.stem: path for path in (CURRENT_DIR / ".." / "services").glob("*.py")
}
service_names = sorted(service_to_path.keys())

compose = {
    "version": "3.9",
    "services": {
        name: {
            "image": "local/mini-osparc",
            "build": ".",
            "ports": [f"{8000+n}:8000"],
            "volumes": [
                "./services:/src",
            ],
            "command": ["python", "/src/projects.py"],
            "user": "${UID}:${GID}",
        }
        for n, name in enumerate(service_names)
    },
}


if __name__ == "__main__":
    # import json
    # print(json.dumps(compose, indent=2))
    yaml.safe_dump(compose, sys.stdout, sort_keys=False)
