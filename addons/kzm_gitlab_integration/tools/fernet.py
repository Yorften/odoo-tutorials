from dataclasses import dataclass
from cryptography.fernet import Fernet
from typing import Optional

import os

import logging

_logger = logging.getLogger(__name__)


def get_gitlab_credentials_key():
    key_or_path = os.environ.get("GITLAB_CREDENTIALS_KEY")
    if key_or_path and os.path.exists(key_or_path):
        with open(key_or_path, "r") as f:
            key = f.read().strip()
        return key
    return key_or_path


@dataclass
class FernetUtils:

    fernet: Optional[Fernet] = None

    @classmethod
    def get_fernet(cls):
        if cls.fernet is None:
            key = get_gitlab_credentials_key()
            if not key:
                raise ValueError("Environment variable GITLAB_CREDENTIALS_KEY is not set.")
            cls.fernet = Fernet(key)
        return cls.fernet

    @classmethod
    def get_decrypted_token(cls, access_token: bytes):
        _logger.info("Encrypted token: %s", access_token)
        return cls.get_fernet().decrypt(access_token)
