from typing import Any, List, Dict, Optional

from ..base.resource_client import ResourceClient
from .webhook_dispatch_collection import WebhookDispatchCollectionClient


def prepare_webhook_representation(
    event_types: Optional[List] = None,
    request_url: Optional[str] = None,
    payload_template: Optional[str] = None,
    actor_id: Optional[str] = None,
    actor_task_id: Optional[str] = None,
    actor_run_id: Optional[str] = None,
    ignore_ssl_errors: Optional[bool] = None,
    do_not_retry: Optional[bool] = None,
    idempotency_key: Optional[str] = None,
    is_ad_hoc: Optional[bool] = None
) -> Dict:
    webhook = {}

    if event_types is not None:
        webhook["eventTypes"] = event_types

    if request_url is not None:
        webhook["requestUrl"] = request_url

    if payload_template is not None:
        webhook["payloadTemplate"] = payload_template

    condition = {}
    if actor_run_id is not None:
        condition["actorRunId"] = actor_run_id
        webhook["isAdHoc"] = True
    elif actor_task_id is not None:
        condition["actorTaskId"] = actor_task_id
    elif actor_id is not None:
        condition["actorId"] = actor_id

    if condition != {}:
        webhook["condition"] = condition

    if ignore_ssl_errors is not None:
        webhook["ignoreSslErrors"] = ignore_ssl_errors

    if do_not_retry is not None:
        webhook["doNotRetry"] = do_not_retry

    if idempotency_key is not None:
        webhook["idempotencyKey"] = idempotency_key

    if is_ad_hoc is not None:
        webhook["isAdHoc"] = is_ad_hoc

    return webhook


class WebhookClient(ResourceClient):
    """Sub-client for manipulating a single webhook."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the WebhookClient"""
        super().__init__(*args, resource_path='webhooks', **kwargs)

    def get(self) -> Optional[Dict]:
        """Retrieve the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/get-webhook

        Returns:
            The retrieved webhook
        """
        return self._get()

    def update(
        self,
        event_types: Optional[List] = None,
        request_url: Optional[str] = None,
        payload_template: Optional[str] = None,
        actor_id: Optional[str] = None,
        actor_task_id: Optional[str] = None,
        actor_run_id: Optional[str] = None,
        ignore_ssl_errors: Optional[bool] = None,
        do_not_retry: Optional[bool] = None,
        is_ad_hoc: Optional[bool] = None
    ) -> Dict:
        """Update the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/update-webhook

        Args:
            event_types (list, optional): List of event types that should trigger the webhook.
                                Present in the client constants as WebhookEventType. At least one is required.
            request_url (str, optional): URL that will be invoked once the webhook is triggered.
            payload_template (str, optional): Specification of the payload that will be sent to request_url
            actor_id (str, optional): Id of the actor whose runs should trigger the webhook.
            actor_task_id (str, optional): Id of the actor task whose runs should trigger the webhook.
            actor_run_id (str, optional): Id of the actor run which should trigger the webhook.
            ignore_ssl_errors (bool, optional): Whether the webhook should ignore SSL errors returned by request_url
            do_not_retry (bool, optional): Whether the webhook should retry sending the payload to request_url upon
                                           failure.
            is_ad_hoc (bool, optional): Set to True if you want the webhook to be triggered only the first time the
                                        condition is fulfilled. Only applicable when actor_run_id is filled.

        Returns:
            The updated webhook
        """
        parameters = locals()
        parameters.pop("self")
        webhook = prepare_webhook_representation(**parameters)
        return self._update(new_fields=webhook)

    def delete(self) -> None:
        """Delete the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/webhook-object/delete-webhook
        """
        return self._delete()

    def dispatches(self) -> WebhookDispatchCollectionClient:
        """Get dispatches of the webhook.

        https://docs.apify.com/api/v2#/reference/webhooks/dispatches-collection

        Returns:
            A client allowing access to dispatches of this webhook using its list method
        """
        return WebhookDispatchCollectionClient(
            self._init_options(resource_path="dispatches", resource_id=self.resource_id)
        )
