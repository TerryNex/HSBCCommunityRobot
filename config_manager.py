import json
import os

class ConfigManager:
    """Manages persistent configuration like tokens."""
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.config = self._load()

    def _load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {}

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self._save()

    def _save(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
