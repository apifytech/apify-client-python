from typing import Any, Optional

from ..._errors import ApifyApiError
from ..._utils import _catch_not_found_or_throw
from ..base.resource_client import ResourceClient


class LogClient(ResourceClient):
    """Sub-client for manipulating logs."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes the LogClient."""
        super().__init__(*args, resource_path='logs', **kwargs)

    def get(self) -> Optional[str]:
        """Retrieves the log as text.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            The retrieved log
        """
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(),
            )

            return response.text

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None

    def stream(self) -> Any:
        """Retrieves the log as a file-like object.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            The retrieved log
        """
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(),
                stream=True,
                parse_response=False,
            )

            response.raw.decode_content = True
            # TODO explain response.raw.close()
            return response.raw

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None
