from google.oauth2.credentials import Credentials
from google.auth.transport.requests import AuthorizedSession


GOOGLE_USERINFO_URL = (
    "https://openidconnect.googleapis.com/v1/userinfo"
)


def get_google_account_email(
    credentials: Credentials,
) -> str:

    if not credentials.token:
        raise ValueError(
            "Google access token is missing."
        )

    session = AuthorizedSession(
        credentials
    )

    response = session.get(
        GOOGLE_USERINFO_URL,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    email = data.get("email")

    if not email:
        raise ValueError(
            "Google did not return an email address."
        )

    return email