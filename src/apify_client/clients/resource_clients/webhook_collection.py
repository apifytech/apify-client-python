from typing import Any, Dict, List, Optional

from apify_client.consts import WebhookEventType

from ..._utils import ListPage
from ..base import ResourceCollectionClient
from .webhook import _prepare_webhook_representation


class WebhookCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating webhooks."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the WebhookCollectionClient."""
        resource_path = kwargs.pop('resource_path', 'webhooks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: Optional[bool] = None,
    ) -> ListPage:
        """List the available webhooks.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/get-list-of-webhooks

        Args:
            limit (int, optional): How many webhooks to retrieve
            offset (int, optional): What webhook to include as first when retrieving the list
            desc (bool, optional): Whether to sort the webhooks in descending order based on their date of creation

        Returns:
            ListPage: The list of available webhooks matching the specified filters.
        """
        return self._list(limit=limit, offset=offset, desc=desc)

    def create(
        self,
        *,
        event_types: List[WebhookEventType],
        request_url: str,
        payload_template: Optional[str] = None,
        actor_id: Optional[str] = None,
        actor_task_id: Optional[str] = None,
        actor_run_id: Optional[str] = None,
        ignore_ssl_errors: Optional[bool] = None,
        do_not_retry: Optional[bool] = None,
        idempotency_key: Optional[str] = None,
        is_ad_hoc: Optional[bool] = None,
    ) -> Dict:
        """Create a new webhook.

        You have to specify exactly one out of actor_id, actor_task_id or actor_run_id.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-collection/create-webhook

        Args:
            event_types (list of WebhookEventType): List of event types that should trigger the webhook. At least one is required.
            request_url (str): URL that will be invoked once the webhook is triggered.
            payload_template (str, optional): Specification of the payload that will be sent to request_url
            actor_id (str, optional): Id of the actor whose runs should trigger the webhook.
            actor_task_id (str, optional): Id of the actor task whose runs should trigger the webhook.
            actor_run_id (str, optional): Id of the actor run which should trigger the webhook.
            ignore_ssl_errors (bool, optional): Whether the webhook should ignore SSL errors returned by request_url
            do_not_retry (bool, optional): Whether the webhook should retry sending the payload to request_url upon
                                           failure.
            idempotency_key (str, optional): A unique identifier of a webhook. You can use it to ensure that you won't
                                             create the same webhook multiple times.
            is_ad_hoc (bool, optional): Set to True if you want the webhook to be triggered only the first time the
                                        condition is fulfilled. Only applicable when actor_run_id is filled.

        Returns:
            dict: The created webhook
        """
        parameters = locals()
        parameters.pop('self')
        webhook = _prepare_webhook_representation(**parameters)
        return self._create(resource=webhook)
