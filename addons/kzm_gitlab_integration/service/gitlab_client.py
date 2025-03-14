import gitlab
from ..tools import FernetUtils

import logging

_logger = logging.getLogger(__name__)


class GitlabClient:
    _instance = None

    def __new__(cls, private_token, timeout=10):
        if cls._instance is None:
            cls._instance = super(GitlabClient, cls).__new__(cls)
            cls._instance.private_token = private_token
            cls._instance.timeout = timeout
            cls._instance._initialize_client()
        return cls._instance

    def _initialize_client(self):
        self.client = gitlab.Gitlab(private_token=self.private_token, timeout=self.timeout, per_page=10)
        self.client.auth()

    def get_client(self):
        return self.client

    @classmethod
    def _get_gitlab_client(cls, access_token: str):
        access_token = FernetUtils.get_decrypted_token(access_token)
        _logger.info("Decrypted token: %s", access_token)
        return cls(access_token).get_client()
