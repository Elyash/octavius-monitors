"""Packets monitor."""

from typing import Callable, Any

import socket
import struct


BUFFER_SIZE = 2 ** 12
STRUCT_BPF_NODE = 'HBBI'