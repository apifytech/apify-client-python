from typing import Any, Dict, Optional

from ..._errors import ApifyApiError
from ..._utils import _catch_not_found_or_throw, _parse_date_fields, _pluck_data
from ..base.resource_client import ResourceClient


class RequestQueueClient(ResourceClient):
    """Sub-client for manipulating a single request queue."""
    def __init__(self, *args: Any, client_key: str = None, **kwargs: Any) -> None:
        """Initializes the RequestQueueClient.

        Args:
            client_key (str): A unique identifier of the client accessing the request queue
        """
        super().__init__(*args, resource_path='request-queues', **kwargs)
        self.client_key = client_key

    def get(self) -> Optional[Dict]:
        """Retrieves the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/get-request-queue

        Returns:
            The retrieved request queue
        """
        return self._get()

    def update(self, new_fields: Dict) -> Optional[Dict]:
        """Updates the request queue with specified fields.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/update-request-queue

        Args:
            new_fields (dict): The fields of the request queue to update

        Returns:
            The updated request queue
        """
        return self._update(new_fields)

    def delete(self) -> None:
        """Deletes the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/delete-request-queue
        """
        return self._delete()

    def list_head(self, *, limit: int = None) -> Dict:
        """Retrieves a given number of requests from the beginning of the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-head/get-head

        Args:
            limit (int): How many requests to retrieve
        """
        request_params = self._params(limit=limit, clientKey=self.client_key)

        response = self.http_client.call(
            url=self._url('head'),
            method='GET',
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def add_request(self, request: Dict, *, forefront: bool = None) -> Dict:
        """Adds a request to the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/add-request

        Args:
            request (dict): The request to add to the queue
            forefront (bool): Whether to add the request to the head or the end of the queue
        """
        request_params = self._params(
            forefront=forefront,
            clientKey=self.client_key,
        )

        response = self.http_client.call(
            url=self._url('requests'),
            method='POST',
            json=request,
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def get_request(self, request_id: str) -> Optional[Dict]:
        """Retrieves a request from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/get-request

        Args:
            request_id (str): ID of the request to retrieve
        """
        try:
            response = self.http_client.call(
                url=self._url(f'requests/{request_id}'),
                method='GET',
                params=self._params(),
            )
            return _parse_date_fields(_pluck_data(response.json()))

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None

    def update_request(self, request: Dict, *, forefront: bool = None) -> Optional[Dict]:
        """Updates a request in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/update-request

        Args:
            request (dict): The updated request
            forefront (bool): Whether to put the updated request in the beginning or the end of the queue
        """
        request_id = request['id']

        request_params = self._params(
            forefront=forefront,
            clientKey=self.client_key,
        )

        response = self.http_client.call(
            url=self._url(f'requests/{request_id}'),
            method='PUT',
            json=request,
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def delete_request(self, request_id: str) -> None:
        """Deletes a request from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/delete-request

        Args:
            request_id (str): ID of the request to delete.
        """
        request_params = self._params(
            clientKey=self.client_key,
        )

        self.http_client.call(
            url=self._url(f'requests/{request_id}'),
            method='DELETE',
            params=request_params,
        )
