"""Exception Module for Siyuan Helper."""


from __future__ import annotations


class SiyuanApiException(Exception):
    """Siyuan Api Request with return code other than `0` will intrigue this exception. A SiyuanResponse object will be offered."""


class SiyuanAuthFailedException(Exception):
    """Authorization Failed Exception. May due to wrong Authorization Token."""


class SiyuanApiTypeException(Exception):
    """Type Exception when invoking API."""


class SiyuanNoResultException(Exception):
    """Exception when no results are found."""
