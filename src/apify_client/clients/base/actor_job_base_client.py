import math
import time
from datetime import datetime
from typing import Dict, Optional

from ..._errors import ApifyApiError
from ..._utils import _catch_not_found_or_throw, _parse_date_fields, _pluck_data
from ...consts import ActorJobStatus
from .resource_client import ResourceClient

DEFAULT_WAIT_FOR_FINISH_SEC = 999999

# After how many seconds we give up trying in case job doesn't exist
DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC = 3


class ActorJobBaseClient(ResourceClient):
    """Base sub-client class for actor runs and actor builds."""

    def _wait_for_finish(self, wait_secs: Optional[int] = None) -> Optional[Dict]:
        started_at = datetime.now()
        should_repeat = True
        job: Optional[Dict] = None
        seconds_elapsed = 0

        while should_repeat:
            wait_for_finish = DEFAULT_WAIT_FOR_FINISH_SEC
            if wait_secs is not None:
                wait_for_finish = wait_secs - seconds_elapsed

            try:
                response = self.http_client.call(
                    url=self._url(),
                    method='GET',
                    params=self._params(waitForFinish=wait_for_finish),
                )
                job = _parse_date_fields(_pluck_data(response.json()))

                seconds_elapsed = math.floor(((datetime.now() - started_at).total_seconds()))
                if (
                    ActorJobStatus(job['status'])._is_terminal or (wait_secs is not None and seconds_elapsed >= wait_secs)
                ):
                    should_repeat = False

                if not should_repeat:
                    # Early return here so that we avoid the sleep below if not needed
                    return job

            except ApifyApiError as exc:
                _catch_not_found_or_throw(exc)

                # If there are still not found errors after DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC, we give up and return None
                # In such case, the requested record probably really doesn't exist.
                if (seconds_elapsed > DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC):
                    return None

            # It might take some time for database replicas to get up-to-date so sleep a bit before retrying
            time.sleep(250)

        return job

    def _abort(self) -> Dict:
        response = self.http_client.call(
            url=self._url('abort'),
            method='POST',
            params=self._params(),
        )
        return _parse_date_fields(_pluck_data(response.json()))
