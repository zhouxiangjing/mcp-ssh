import logging
import os
from typing import Optional

import paramiko

from src.common.config import SSH_CFG, SSH_HOSTS

_logger = logging.getLogger(__name__)


class SSHConnectionManager:
    """单例 SSH 连接管理器。

    默认连接 SSH_CFG 中的主机；也可通过 get_connection(host_name=...) 按名称
    获取 SSH_HOSTS 中配置的其他主机连接。每个主机各自维护一个单例连接。
    """

    _instances: dict[str, paramiko.SSHClient] = {}

    @classmethod
    def get_connection(cls, host_name: Optional[str] = None) -> paramiko.SSHClient:
        """获取 SSH 连接（懒加载，自动重连）。

        Args:
            host_name: SSH_HOSTS 中的主机名；为 None 时使用默认 SSH_CFG。

        Returns:
            已连接的 paramiko.SSHClient 实例。
        """
        key = host_name or "__default__"

        # 检查现有连接是否仍然活跃
        if key in cls._instances:
            try:
                transport = cls._instances[key].get_transport()
                if transport and transport.is_active():
                    return cls._instances[key]
            except Exception:
                pass
            del cls._instances[key]

        # 确定连接参数：per-host cfg 优先，fallback 到 SSH_CFG
        if host_name and host_name in SSH_HOSTS:
            cfg = SSH_HOSTS[host_name]
        else:
            cfg = SSH_CFG

        # ignore_known_hosts / known_hosts_file 优先读 per-host cfg，再 fallback SSH_CFG
        ignore_known = cfg.get("ignore_known_hosts", SSH_CFG.get("ignore_known_hosts", False))
        known_hosts_file = cfg.get("known_hosts_file") or SSH_CFG.get("known_hosts_file")

        client = paramiko.SSHClient()

        if ignore_known:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        else:
            known_hosts = known_hosts_file or os.path.expanduser("~/.ssh/known_hosts")
            if os.path.exists(known_hosts):
                client.load_host_keys(known_hosts)
            client.set_missing_host_key_policy(paramiko.WarningPolicy())

        connect_kwargs: dict = {
            "hostname": cfg.get("host", SSH_CFG["host"]),
            "port":     int(cfg.get("port", SSH_CFG["port"])),
            "username": cfg.get("username", SSH_CFG["username"]),
            "timeout":  int(cfg.get("timeout", SSH_CFG["timeout"])),
        }

        # 优先使用密钥认证
        key_file = cfg.get("key_file") or SSH_CFG.get("key_file")
        password  = cfg.get("password") or SSH_CFG.get("password")
        passphrase = cfg.get("key_passphrase") or SSH_CFG.get("key_passphrase")

        if key_file:
            connect_kwargs["key_filename"] = os.path.expanduser(key_file)
            if passphrase:
                connect_kwargs["passphrase"] = passphrase
        if password:
            connect_kwargs["password"] = password

        _logger.info(
            "Connecting to %s:%s as %s",
            connect_kwargs["hostname"],
            connect_kwargs["port"],
            connect_kwargs["username"],
        )

        client.connect(**connect_kwargs)
        cls._instances[key] = client
        return client

    @classmethod
    def close_connection(cls, host_name: Optional[str] = None) -> None:
        """关闭指定主机的 SSH 连接。"""
        key = host_name or "__default__"
        if key in cls._instances:
            try:
                cls._instances[key].close()
            except Exception:
                pass
            del cls._instances[key]

    @classmethod
    def close_all(cls) -> None:
        """关闭所有 SSH 连接。"""
        for client in cls._instances.values():
            try:
                client.close()
            except Exception:
                pass
        cls._instances.clear()
