from typing import Dict
import yaml


_ENV_MAPPING = {
  'TELEGRAM_API_TOKEN': 'telegram_api_token',
  'TELEGRAM_USER_ID': 'telegram_user_id',
}

def _load_config(file: str):
    with open(file) as f:
        content = f.read()
        return yaml.load(content, Loader=yaml.CLoader)

def load_config(config_path: str, environment: Dict[str, str]):
    config = _load_config(config_path)

    for env_key, conf_key in _ENV_MAPPING.items():
        if env_key in environment and environment[env_key]:
            config[conf_key] = environment[env_key]

    return config
