import gitlab
from ..tools import FernetUtils

import logging

_logger = logging.getLogger(__name__)


class GitlabClient:
    _instances = {}

    def __new__(cls, private_token, timeout=10):
        if private_token not in cls._instances:
            instance = super(GitlabClient, cls).__new__(cls)
            instance.private_token = private_token
            instance.timeout = timeout
            instance._initialize_client()
            cls._instances[private_token] = instance
        return cls._instances[private_token]

    def _initialize_client(self):
        self.client = gitlab.Gitlab(private_token=self.private_token, timeout=self.timeout, per_page=10)
        _logger.info("Decrypted token: %s", self.private_token)
        self.client.auth()

    def get_client(self):
        return self.client

    @classmethod
    def _get_gitlab_client(cls, access_token: str):
        access_token = FernetUtils.get_decrypted_token(access_token)
        return cls(access_token).get_client()
