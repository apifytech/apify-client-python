from typing import Any, Dict, Optional

from ..._utils import ListPage, _filter_out_none_values_recursively
from ..base import ResourceCollectionClient


class TaskCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating tasks."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the TaskCollectionClient."""
        resource_path = kwargs.pop('resource_path', 'actor-tasks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: Optional[bool] = None,
    ) -> ListPage:
        """List the available tasks.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/get-list-of-tasks

        Args:
            limit (int, optional): How many tasks to list
            offset (int, optional): What task to include as first when retrieving the list
            desc (bool, optional): Whether to sort the tasks in descending order based on their creation date

        Returns:
            ListPage: The list of available tasks matching the specified filters.
        """
        return self._list(limit=limit, offset=offset, desc=desc)

    def create(
        self,
        *,
        actor_id: str,
        name: str,
        build: Optional[str] = None,
        timeout_secs: Optional[int] = None,
        memory_mbytes: Optional[int] = None,
        task_input: Optional[Dict] = None,
    ) -> Dict:
        """Create a new task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-collection/create-task

        Args:
            actor_id (str): Id of the actor that should be run
            name (str): Name of the task
            build (str, optional): Actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the task settings (typically latest).
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the task settings.
            timeout_secs (int, optional): Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.
            task_input (dict, optional): Task input object.

        Returns:
            dict: The created task.
        """
        new_fields = {
            'actId': actor_id,
            'name': name,
            'options': {
                'build': build,
                'memoryMbytes': memory_mbytes,
                'timeoutSecs': timeout_secs,
            },
            'input': task_input,
        }

        return self._create(_filter_out_none_values_recursively(new_fields))
