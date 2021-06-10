from typing import Any, Dict, List, Optional

from ..._utils import _encode_key_value_store_record_value, _encode_webhook_list_to_base64, _parse_date_fields, _pluck_data
from ...consts import ActorJobStatus
from ..base import ResourceClient
from .actor_version import ActorVersionClient
from .actor_version_collection import ActorVersionCollectionClient
from .build_collection import BuildCollectionClient
from .run import RunClient
from .run_collection import RunCollectionClient
from .webhook_collection import WebhookCollectionClient


class ActorClient(ResourceClient):
    """Sub-client for manipulating a single actor."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorClient."""
        resource_path = kwargs.pop('resource_path', 'acts')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Optional[Dict]:
        """Retrieve the actor.

        https://docs.apify.com/api/v2#/reference/actors/actor-object/get-actor

        Returns:
            dict, optional: The retrieved actor
        """
        return self._get()

    def update(
        self,
        *,
        name: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        seo_title: Optional[str] = None,
        seo_description: Optional[str] = None,
        versions: Optional[List[Dict]] = None,
        restart_on_error: Optional[bool] = None,
        is_public: Optional[bool] = None,
        is_deprecated: Optional[bool] = None,
        is_anonymously_runnable: Optional[bool] = None,
        categories: Optional[List[str]] = None,
        default_run_build: Optional[str] = None,
        default_run_memory_mbytes: Optional[int] = None,
        default_run_timeout_secs: Optional[int] = None,
        example_run_input_body: Optional[Any] = None,
        example_run_input_content_type: Optional[str] = None,
    ) -> Dict:
        """Update the actor with the specified fields.

        https://docs.apify.com/api/v2#/reference/actors/actor-object/update-actor

        Args:
            name (str, optional): The name of the actor
            title (str, optional): The title of the actor (human-readable)
            description (str, optional): The description for the actor
            seo_title (str, optional): The title of the actor optimized for search engines
            seo_description (str, optional): The description of the actor optimized for search engines
            versions (list of dict, optional): The list of actor versions
            restart_on_error (bool, optional): If true, the main actor run process will be restarted whenever it exits with a non-zero status code.
            is_public (bool, optional): Whether the actor is public.
            is_deprecated (bool, optional): Whether the actor is deprecated.
            is_anonymously_runnable (bool, optional): Whether the actor is anonymously runnable.
            categories (list of str, optional): The categories to which the actor belongs to.
            default_run_build (str, optional): Tag or number of the build that you want to run by default.
            default_run_memory_mbytes (int, optional): Default amount of memory allocated for the runs of this actor, in megabytes.
            default_run_timeout_secs (int, optional): Default timeout for the runs of this actor in seconds.
            example_run_input_body (Any, optional): Input to be prefilled as default input to new users of this actor.
            example_run_input_content_type (str, optional): The content type of the example run input.

        Returns:
            dict: The updated actor
        """
        actor_fields: Dict[str, Any] = {}
        if name is not None:
            actor_fields['name'] = name
        if title is not None:
            actor_fields['title'] = title
        if description is not None:
            actor_fields['description'] = description
        if seo_title is not None:
            actor_fields['seoTitle'] = seo_title
        if seo_description is not None:
            actor_fields['seoDescription'] = seo_description
        if versions is not None:
            actor_fields['versions'] = versions
        if restart_on_error is not None:
            actor_fields['restartOnError'] = restart_on_error
        if is_public is not None:
            actor_fields['isPublic'] = is_public
        if is_deprecated is not None:
            actor_fields['isDeprecated'] = is_deprecated
        if is_anonymously_runnable is not None:
            actor_fields['isAnonymouslyRunnable'] = is_anonymously_runnable
        if categories is not None:
            actor_fields['categories'] = categories

        default_run_options: Dict[str, Any] = {}
        if default_run_build is not None:
            default_run_options['build'] = default_run_build
        if default_run_memory_mbytes is not None:
            default_run_options['memoryMbytes'] = default_run_memory_mbytes
        if default_run_timeout_secs is not None:
            default_run_options['timeoutSecs'] = default_run_timeout_secs
        if default_run_options:
            actor_fields['defaultRunOptions'] = default_run_options

        example_run_input: Dict[str, Any] = {}
        if example_run_input_body is not None:
            example_run_input['body'] = example_run_input_body
        if example_run_input_content_type is not None:
            example_run_input['contentType'] = example_run_input_content_type
        if example_run_input:
            actor_fields['exampleRunInput'] = example_run_input

        return self._update(actor_fields)

    def delete(self) -> None:
        """Delete the actor.

        https://docs.apify.com/api/v2#/reference/actors/actor-object/delete-actor
        """
        return self._delete()

    def start(
        self,
        *,
        run_input: Optional[Any] = None,
        content_type: Optional[str] = None,
        build: Optional[str] = None,
        memory_mbytes: Optional[int] = None,
        timeout_secs: Optional[int] = None,
        wait_for_finish: Optional[int] = None,
        webhooks: Optional[List[Dict]] = None,
    ) -> Dict:
        """Start the actor and immediately return the Run object.

        https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor

        Args:
            run_input (Any, optional): The input to pass to the actor run.
            content_type (str, optional): The content type of the input.
            build (str, optional): Specifies the actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the default run configuration for the actor (typically latest).
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the default run configuration for the actor.
            timeout_secs (int, optional): Optional timeout for the run, in seconds.
                                          By default, the run uses timeout specified in the default run configuration for the actor.
            wait_for_finish (int, optional): The maximum number of seconds the server waits for the run to finish.
                                               By default, it is 0, the maximum value is 300.
            webhooks (list of dict, optional): Optional ad-hoc webhooks (https://docs.apify.com/webhooks/ad-hoc-webhooks)
                                               associated with the actor run which can be used to receive a notification,
                                               e.g. when the actor finished or failed.
                                               If you already have a webhook set up for the actor or task, you do not have to add it again here.
                                               Each webhook is represented by a dictionary containing these items:
                                               * ``event_types``: list of ``WebhookEventType`` values which trigger the webhook
                                               * ``request_url``: URL to which to send the webhook HTTP request
                                               * ``payload_template`` (optional): Optional template for the request payload

        Returns:
            dict: The run object
        """
        run_input, content_type = _encode_key_value_store_record_value(run_input, content_type)

        request_params = self._params(
            build=build,
            memory=memory_mbytes,
            timeout=timeout_secs,
            waitForFinish=wait_for_finish,
            webhooks=_encode_webhook_list_to_base64(webhooks) if webhooks is not None else None,
        )

        response = self.http_client.call(
            url=self._url('runs'),
            method='POST',
            headers={'content-type': content_type},
            data=run_input,
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def call(
        self,
        *,
        run_input: Optional[Any] = None,
        content_type: Optional[str] = None,
        build: Optional[str] = None,
        memory_mbytes: Optional[int] = None,
        timeout_secs: Optional[int] = None,
        webhooks: Optional[List[Dict]] = None,
        wait_secs: Optional[int] = None,
    ) -> Optional[Dict]:
        """Start the actor and wait for it to finish before returning the Run object.

        It waits indefinitely, unless the wait_secs argument is provided.

        https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor

        Args:
            run_input (Any, optional): The input to pass to the actor run.
            content_type (str, optional): The content type of the input.
            build (str, optional): Specifies the actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the default run configuration for the actor (typically latest).
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the default run configuration for the actor.
            timeout_secs (int, optional): Optional timeout for the run, in seconds.
                                          By default, the run uses timeout specified in the default run configuration for the actor.
            webhooks (list, optional): Optional webhooks (https://docs.apify.com/webhooks) associated with the actor run,
                                       which can be used to receive a notification, e.g. when the actor finished or failed.
                                       If you already have a webhook set up for the actor, you do not have to add it again here.
            wait_secs (int, optional): The maximum number of seconds the server waits for the run to finish. If not provided, waits indefinitely.

        Returns:
            dict: The run object
        """
        started_run = self.start(
            run_input=run_input,
            content_type=content_type,
            build=build,
            memory_mbytes=memory_mbytes,
            timeout_secs=timeout_secs,
            webhooks=webhooks,
        )

        return self.root_client.run(started_run['id']).wait_for_finish(wait_secs=wait_secs)

    def build(
        self,
        *,
        version_number: str,
        beta_packages: Optional[bool] = None,
        tag: Optional[str] = None,
        use_cache: Optional[bool] = None,
        wait_for_finish: Optional[int] = None,
    ) -> Dict:
        """Build the actor.

        https://docs.apify.com/api/v2#/reference/actors/build-collection/build-actor

        Args:
            version_number (str): Actor version number to be built.
            beta_packages (bool, optional): If True, then the actor is built with beta versions of Apify NPM packages.
                                            By default, the build uses latest stable packages.
            tag (str, optional): Tag to be applied to the build on success. By default, the tag is taken from the actor version's buildTag property.
            use_cache (bool, optional): If true, the actor's Docker container will be rebuilt using layer cache
                                        (https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#leverage-build-cache).
                                        This is to enable quick rebuild during development.
                                        By default, the cache is not used.
            wait_for_finish (int, optional): The maximum number of seconds the server waits for the build to finish before returning.
                                             By default it is 0, the maximum value is 300.

        Returns:
            dict: The build object
        """
        request_params = self._params(
            version=version_number,
            betaPackages=beta_packages,
            tag=tag,
            useCache=use_cache,
            waitForFinish=wait_for_finish,
        )

        response = self.http_client.call(
            url=self._url('builds'),
            method='POST',
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def builds(self) -> BuildCollectionClient:
        """Retrieve a client for the builds of this actor."""
        return BuildCollectionClient(**self._sub_resource_init_options(resource_path='builds'))

    def runs(self) -> RunCollectionClient:
        """Retrieve a client for the runs of this actor."""
        return RunCollectionClient(**self._sub_resource_init_options(resource_path='runs'))

    def last_run(self, *, status: Optional[ActorJobStatus] = None) -> RunClient:
        """Retrieve the client for the last run of this actor.

        Last run is retrieved based on the start time of the runs.

        Args:
            status (ActorJobStatus, optional): Consider only runs with this status.

        Returns:
            RunClient: The resource client for the last run of this actor.
        """
        return RunClient(**self._sub_resource_init_options(
            resource_id='last',
            resource_path='runs',
            params=self._params(status=status.value if status is not None else None),
        ))

    def versions(self) -> ActorVersionCollectionClient:
        """Retrieve a client for the versions of this actor."""
        return ActorVersionCollectionClient(**self._sub_resource_init_options())

    def version(self, version_number: str) -> ActorVersionClient:
        """Retrieve the client for the specified version of this actor.

        Args:
            version_number (str): The version number for which to retrieve the resource client.

        Returns:
            ActorVersionClient: The resource client for the specified actor version.
        """
        return ActorVersionClient(**self._sub_resource_init_options(resource_id=version_number))

    def webhooks(self) -> WebhookCollectionClient:
        """Retrieve a client for webhooks associated with this actor."""
        return WebhookCollectionClient(**self._sub_resource_init_options())
