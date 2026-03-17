import json
import os

from dotenv import load_dotenv

load_dotenv()

SSH_CFG = {
    "host":        os.getenv("SSH_HOST", "127.0.0.1"),
    "port":        int(os.getenv("SSH_PORT", 22)),
    "username":    os.getenv("SSH_USERNAME", "root"),
    "password":    os.getenv("SSH_PASSWORD", None),
    "key_file":    os.getenv("SSH_KEY_FILE", None),
    "key_passphrase": os.getenv("SSH_KEY_PASSPHRASE", None),
    "timeout":     int(os.getenv("SSH_TIMEOUT", 30)),
    "ignore_known_hosts": os.getenv("SSH_IGNORE_KNOWN_HOSTS", "false").lower() in ("true", "1", "t"),
    "known_hosts_file": os.getenv("SSH_KNOWN_HOSTS_FILE", None),
}

# 多主机配置（可选），JSON 数组格式
_hosts_json = os.getenv("SSH_HOSTS_JSON", None)
SSH_HOSTS: dict[str, dict] = {}
if _hosts_json:
    try:
        hosts_list = json.loads(_hosts_json)
        for h in hosts_list:
            SSH_HOSTS[h["name"]] = h
    except (json.JSONDecodeError, KeyError):
        pass


def set_ssh_config_from_cli(config: dict) -> None:
    """使用 CLI 参数覆盖全局 SSH 配置。"""
    for key, value in config.items():
        if value is None:
            continue
        if key == "port":
            SSH_CFG[key] = int(value)
        elif key == "timeout":
            SSH_CFG[key] = int(value)
        elif key == "ignore_known_hosts":
            SSH_CFG[key] = bool(value)
        else:
            SSH_CFG[key] = value
