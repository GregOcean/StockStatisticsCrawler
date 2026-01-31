"""Storage module"""

from .base import BaseStorage
from .mysql_storage import MySQLStorage

__all__ = ["BaseStorage", "MySQLStorage"]

