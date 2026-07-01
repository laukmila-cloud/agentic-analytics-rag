import json
import os
from datetime import datetime, timezone

from app.config import settings


class MetricsLogger:
    def write(self, metrics: dict) -> None:
        os.makedirs(os.path.dirname(settings.metrics_path), exist_ok=True)

        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **metrics,
        }

        with open(settings.metrics_path, "a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")