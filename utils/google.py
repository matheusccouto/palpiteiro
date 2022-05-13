"""Google cloud helper functions."""

import logging
import os

from google.oauth2 import service_account


def get_creds_from_env_vars():
    """Get credentials from environmental variables."""
    logging.info("Trying to load credentials from environment variables.")
    creds = service_account.Credentials.from_service_account_info(
        info={
            "type": os.environ["GCP_SERVICE_ACCOUNT_TYPE"],
            "project_id": os.environ["GCP_SERVICE_ACCOUNT_PROJECT_ID"],
            "private_key_id": os.environ["GCP_SERVICE_ACCOUNT_PRIVATE_KEY_ID"],
            "private_key": os.environ["GCP_SERVICE_ACCOUNT_PRIVATE_KEY"].replace(
                "\\n", "\n"
            ),
            "client_email": os.environ["GCP_SERVICE_ACCOUNT_CLIENT_EMAIL"],
            "client_id": os.environ["GCP_SERVICE_ACCOUNT_CLIENT_ID"],
            "auth_uri": os.environ["GCP_SERVICE_ACCOUNT_AUTH_URI"],
            "token_uri": os.environ["GCP_SERVICE_ACCOUNT_TOKEN_URI"],
            "auth_provider_x509_cert_url": os.environ[
                "GCP_SERVICE_ACCOUNT_AUTH_PROVIDER_X509_CERT_URL"
            ],
            "client_x509_cert_url": os.environ[
                "GCP_SERVICE_ACCOUNT_CLIENT_X509_CERT_URL"
            ],
        }
    )
    logging.info("Loaded credentials successfully.")
    return creds