"""RPyC devices."""

from types import TracebackType

import abc
import asycnio
import contextlib
import subprocess
import rpyc

from ..octavius_monitors.async_helpers import run_in_executor


class InvalidRPyCDeviceConnection(Exception):
    """Invalid connection."""

    pass


class RPyCDevice(metaclass=abc.ABCMeta):

    STARTUP_TIME: float | None = None

    def __init__(
        self,
        hostname: str,
        username: str | None = None,
        password: str | None = None
    ) -> None:
        """Init."""

        self._hostname: str = hostname
        self._username: str | None = username
        self._password: str | None  = password

        self._connection: rpyc.Connection | None = None

        self._connect()
        
    @property
    def connection(self):
        """Connection."""

        if self._connection is None:
            raise InvalidRPyCDeviceConnection()

        return self._connection

    @property
    def hostname(self):
        """Host name."""

        return self._hostname

    @property
    def username(self):
        """User name."""

        return self._username

    @property
    def password(self):
        """Password."""

        return self._password

    def run_shell_command(
        self,
        command: str,
        success_validation: bool = True,
        environment: dict[str, str] | None = None,
        capture_output: bool = True
    ) -> subprocess.CompletedProcess:
        """Runs shell command on remove machine."""

        