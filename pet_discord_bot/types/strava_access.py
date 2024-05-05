from dataclasses import dataclass


@dataclass
class StravaAccess:
    """Dictionary containing token exchange response from Strava."""

    access_token: str
    """A short live token the access Strava API"""

    refresh_token: str
    """The refresh token for this user, to be used to get the next access token
    for this user. Please expect that this value can change anytime you
    retrieve a new access token. Once a new refresh token code has been
    returned, the older code will no longer work.
    """

    expires_at: int
    """The number of seconds since the epoch when the provided access token
    will expire"""