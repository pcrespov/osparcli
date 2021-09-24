
import uvicorn
from pathlib import Path
import sys

CURRENT_DIR = Path(sys.argv[0] if __name__=="__main__" else __file__).resolve().parent


def run(app_name: str):
    uvicorn.run(
        f"{app_name}:the_app",
        host="0.0.0.0",
        reload=True,
        reload_dirs=[str(CURRENT_DIR)],
        log_level="debug",
    )
