import sys
from pathlib import Path
from loguru import logger

from .config import settings

# 로그 파일 경로 설정
log_file_path = Path("logs/app.log")
log_file_path.parent.mkdir(parents=True, exist_ok=True)

# 로거 설정
config = {
    "handlers": [
        {"sink": sys.stdout, "format": "{time} - {name} - {level} - {message}"},
        {"sink": str(log_file_path), "rotation": "10 MB", "retention": "1 week"},
    ],
}

# DEBUG 모드에 따라 로그 레벨 설정
log_level = "DEBUG" if settings.DEBUG else "INFO"

# 로거 설정 적용
logger.configure(**config)
logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level=log_level)