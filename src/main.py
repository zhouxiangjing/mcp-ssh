import logging

import click

from src.common.config import set_ssh_config_from_cli
from src.common.logging_utils import configure_logging
from src.common.server import mcp


class SSHMCPServer:
    def __init__(self) -> None:
        configure_logging()
        self._logger = logging.getLogger(__name__)
        self._logger.info("Starting SSH MCP Server")

    def run(self) -> None:
        mcp.run()


@click.command()
@click.option("--host", default=None, help="SSH server hostname or IP address")
@click.option("--port", default=None, type=int, help="SSH port (default 22)")
@click.option("--username", default=None, help="SSH username")
@click.option("--password", default=None, help="SSH password")
@click.option("--key-file", default=None, help="Path to SSH private key file")
@click.option("--key-passphrase", default=None, help="Passphrase for encrypted private key")
@click.option("--timeout", default=None, type=int, help="Connection timeout in seconds (default 30)")
@click.option(
    "--ignore-known-hosts",
    is_flag=True,
    default=False,
    help="Skip host key verification (not recommended for production)",
)
def cli(
    host: str,
    port: int,
    username: str,
    password: str,
    key_file: str,
    key_passphrase: str,
    timeout: int,
    ignore_known_hosts: bool,
) -> None:
    """SSH MCP Server - Model Context Protocol server for remote Linux system management."""
    config: dict = {}
    if host:
        config["host"] = host
    if port is not None:
        config["port"] = port
    if username:
        config["username"] = username
    if password:
        config["password"] = password
    if key_file:
        config["key_file"] = key_file
    if key_passphrase:
        config["key_passphrase"] = key_passphrase
    if timeout is not None:
        config["timeout"] = timeout
    if ignore_known_hosts:
        config["ignore_known_hosts"] = True

    set_ssh_config_from_cli(config)

    server = SSHMCPServer()
    server.run()


if __name__ == "__main__":
    cli()
