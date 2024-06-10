from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal, Dict, Optional

    from httpx import Response
    from .config import Config

import httpx
from deprecation import deprecated
from devgoldyutils import LoggerAdapter, Colours

from .utils import hide_ip
from . import errors, __version__
from .logger import mov_cli_logger

__all__ = ("HTTPClient",)

class SiteMaybeBlocked(errors.MovCliException):
    """Raises there's a connection error during a get request."""
    def __init__(self, url: str, error: httpx.ConnectError) -> None:
        super().__init__(
            f"A connection error occurred while making a GET request to '{url}'.\n" \
            "There's most likely nothing wrong with mov-cli. Your ISP's DNS could be blocking this site or perhaps the site is down. " \
            f"{Colours.GREEN}SOLUTION: Use a VPN or switch DNS!{Colours.RED}\n" \
            f"Actual Error >> {error}"
        )

class HTTPClient():
    def __init__(self, config: Config) -> None:
        self.config = config
        self.logger = LoggerAdapter(mov_cli_logger, prefix = self.__class__.__name__)

        self.__httpx_client = httpx.Client(
            timeout = config.http_timeout, 
            cookies = None
        )
        
        super().__init__()

    def request(
        self, 
        method: Literal["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"],
        url: str, 
        params: Optional[Dict[str, str]] = None, 
        headers: Optional[Dict[str, str]] = None, 
        include_default_headers: bool = False, 
        redirect: bool = False, 
        **kwargs
    ) -> Response:
        """Performs a request with httpx and returns `httpx.Response`."""
        if headers is None:
            headers = {}

        if include_default_headers is True:

            if headers.get("Referer") is None:
                headers.update({"Referer": url})

            headers.update(self.config.http_headers)

        try:
            self.logger.debug(
                Colours.ORANGE.apply(method.upper()) + f" -> {hide_ip(url, self.config.hide_ip)}"
            )

            response = self.__httpx_client.request(
                method = method, 
                url = url, 
                params = params, 
                headers = headers, 
                follow_redirects = redirect, 
                **kwargs
            )

            if response.is_error:
                self.logger.debug(
                    f"{method.upper()} request to '{response.url}' {Colours.RED.apply('failed!')} ({response})"
                )

            return response

        except httpx.ConnectError as e:
            # TODO: I think this needs improving. I see people are getting certificate errors that aren't being caught here.
            if "[SSL: CERTIFICATE_VERIFY_FAILED]" in str(e):
                raise SiteMaybeBlocked(url, e)

            raise e

    @deprecated(
        deprecated_in = "4.4", 
        current_version = __version__, 
        details = "Switch to 'HTTPClient.request()' for the latest functionality."
    )
    def get(
        self, 
        url: str, 
        headers: Dict[str, str] = {}, 
        include_default_headers: bool = True, 
        redirect: bool = False, 
        **kwargs
    ) -> Response:
        """Performs a GET request and returns httpx.Response."""
        return self.request(
            "GET", 
            url = url, 
            headers = headers, 
            include_default_headers = include_default_headers, 
            redirect = redirect,
            **kwargs
        )

    @deprecated(
        deprecated_in = "4.4", 
        current_version = __version__, 
        details = "Switch to 'HTTPClient.request()' for the latest functionality."
    )
    def post(
        self, 
        url: str,
        data: dict = {},
        json: dict = {}, 
        headers: dict = {}, 
        include_default_headers: bool = True, 
        redirect: bool = False, 
        **kwargs
    ) -> Response:
        """Performs a POST request and returns httpx.Response."""

        return self.request(
            "POST", 
            url = url, 
            data = data, 
            json = json, 
            headers = headers, 
            include_default_headers = include_default_headers, 
            redirect = redirect,
            **kwargs
        )

    def set_cookies(self, cookies: dict) -> None:
        """Sets cookies."""
        self.__httpx_client.cookies = cookies