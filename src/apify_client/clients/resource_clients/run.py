from typing import Any, Dict, Optional

from ..._utils import _encode_key_value_store_record_value, _parse_date_fields, _pluck_data, _to_safe_id
from ..base import ActorJobBaseClient
from .dataset import DatasetClient
from .key_value_store import KeyValueStoreClient
from .log import LogClient
from .request_queue import RequestQueueClient


class RunClient(ActorJobBaseClient):
    """Sub-client for manipulating a single actor run."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the RunClient."""
        resource_path = kwargs.pop('resource_path', 'actor-runs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Optional[Dict]:
        """Return information about the actor run.

        https://docs.apify.com/api/v2#/reference/actor-runs/run-object/get-run

        Returns:
            dict: The retrieved actor run data
        """
        return self._get()

    def abort(self) -> Dict:
        """Abort the actor run which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-runs/abort-run/abort-run

        Returns:
            dict: The data of the aborted actor run
        """
        return self._abort()

    def wait_for_finish(self, *, wait_secs: Optional[int] = None) -> Optional[Dict]:
        """Wait synchronously until the run finishes or the server times out.

        Args:
            wait_secs (int, optional): how long does the client wait for run to finish. None for indefinite.

        Returns:
            dict, optional: The actor run data. If the status on the object is not one of the terminal statuses
                (SUCEEDED, FAILED, TIMED_OUT, ABORTED), then the run has not yet finished.
        """
        return self._wait_for_finish(wait_secs=wait_secs)

    def metamorph(
        self,
        *,
        target_actor_id: str,
        target_actor_build: Optional[str] = None,
        run_input: Optional[Any] = None,
        content_type: Optional[str] = None,
    ) -> Dict:
        """Transform an actor run into a run of another actor with a new input.

        https://docs.apify.com/api/v2#/reference/actor-runs/metamorph-run/metamorph-run

        Args:
            target_actor_id (str): ID of the target actor that the run should be transformed into
            target_actor_build (str, optional): The build of the target actor. It can be either a build tag or build number.
                By default, the run uses the build specified in the default run configuration for the target actor (typically the latest build).
            run_input (Any, optional): The input to pass to the new run.
            content_type (str, optional): The content type of the input.

        Returns:
            dict: The actor run data.
        """
        run_input, content_type = _encode_key_value_store_record_value(run_input, content_type)

        safe_target_actor_id = _to_safe_id(target_actor_id)

        request_params = self._params(
            targetActorId=safe_target_actor_id,
            build=target_actor_build,
        )

        response = self.http_client.call(
            url=self._url('metamorph'),
            method='POST',
            headers={'content-type': content_type},
            data=run_input,
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def resurrect(self) -> Dict:
        """Resurrect a finished actor run.

        Only finished runs, i.e. runs with status FINISHED, FAILED, ABORTED and TIMED-OUT can be resurrected.
        Run status will be updated to RUNNING and its container will be restarted with the same default storages.

        https://docs.apify.com/api/v2#/reference/actor-runs/resurrect-run/resurrect-run

        Returns:
            dict: The actor run data.
        """
        response = self.http_client.call(
            url=self._url('resurrect'),
            method='POST',
            params=self._params(),
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def dataset(self) -> DatasetClient:
        """Get the client for the default dataset of the actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            DatasetClient: A client allowing access to the default dataset of this actor run.
        """
        return DatasetClient(
            **self._sub_resource_init_options(resource_path='dataset'),
        )

    def key_value_store(self) -> KeyValueStoreClient:
        """Get the client for the default key-value store of the actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            KeyValueStoreClient: A client allowing access to the default key-value store of this actor run.
        """
        return KeyValueStoreClient(
            **self._sub_resource_init_options(resource_path='key-value-store'),
        )

    def request_queue(self) -> RequestQueueClient:
        """Get the client for the default request queue of the actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            RequestQueueClient: A client allowing access to the default request_queue of this actor run.
        """
        return RequestQueueClient(
            **self._sub_resource_init_options(resource_path='request-queue'),
        )

    def log(self) -> LogClient:
        """Get the client for the log of the actor run.

        https://docs.apify.com/api/v2#/reference/actors/last-run-object-and-its-storages

        Returns:
            LogClient: A client allowing access to the log of this actor run.
        """
        return LogClient(
            **self._sub_resource_init_options(resource_path='log'),
        )
