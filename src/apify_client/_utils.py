import base64
import io
import json
import random
import re
import time
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, cast

from ._errors import ApifyApiError

PARSE_DATE_FIELDS_MAX_DEPTH = 3
PARSE_DATE_FIELDS_KEY_SUFFIX = 'At'

NOT_FOUND_TYPE = 'record-not-found'
NOT_FOUND_ON_S3 = '<Code>NoSuchKey</Code>'


def _to_safe_id(id: str) -> str:
    # Identificators of resources in the API are either in the format `resource_id` or `username/resource_id`.
    # Since the `/` character has a special meaning in URL paths,
    # we replace it with `~` for proper route parsing on the API, where after parsing the URL it's replaced back to `/`.
    return id.replace('/', '~')


def _parse_date_fields(data: Dict) -> Dict:
    return cast(Dict, _parse_date_fields_internal(data))


def _parse_date_fields_internal(data: object, max_depth: int = PARSE_DATE_FIELDS_MAX_DEPTH) -> object:
    if max_depth < 0:
        return data

    if isinstance(data, list):
        return [_parse_date_fields_internal(item, max_depth - 1) for item in data]

    if isinstance(data, dict):
        def parse(key: str, value: object) -> object:
            parsed_value = value
            if key.endswith(PARSE_DATE_FIELDS_KEY_SUFFIX) and isinstance(value, str):
                try:
                    parsed_value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
                except ValueError:
                    pass
            else:
                parsed_value = _parse_date_fields_internal(value, max_depth - 1)
            return parsed_value

        return {key: parse(key, value) for (key, value) in data.items()}

    return data


def _pluck_data(parsed_response: Any) -> Dict:
    if isinstance(parsed_response, dict) and 'data' in parsed_response:
        return cast(Dict, parsed_response['data'])

    raise ValueError('The "data" property is missing in the response.')


def _pluck_data_as_list(parsed_response: Any) -> List:
    if isinstance(parsed_response, dict) and 'data' in parsed_response:
        return cast(List, parsed_response['data'])

    raise ValueError('The "data" property is missing in the response.')


def _is_content_type_json(content_type: str) -> bool:
    return bool(re.search(r'^application/json', content_type, flags=re.IGNORECASE))


def _is_content_type_xml(content_type: str) -> bool:
    return bool(re.search(r'^application/.*xml$', content_type, flags=re.IGNORECASE))


def _is_content_type_text(content_type: str) -> bool:
    return bool(re.search(r'^text/', content_type, flags=re.IGNORECASE))


def _is_file_or_bytes(value: Any) -> bool:
    # The check for IOBase is not ideal, it would be better to use duck typing,
    # but then the check would be super complex, judging from how the 'requests' library does it.
    # This way should be good enough for the vast majority of use cases, if it causes issues, we can improve it later.
    return isinstance(value, (bytes, bytearray, io.IOBase))


T = TypeVar('T')
BailType = Callable[[Exception], None]


def _retry_with_exp_backoff(
    func: Callable[[BailType, int], T],
    *,
    max_retries: int = 8,
    backoff_base_millis: int = 500,
    backoff_factor: float = 2,
    random_factor: float = 1,
) -> T:

    random_factor = min(max(0, random_factor), 1)
    backoff_factor = min(max(1, backoff_factor), 10)
    swallow = True

    def bail(exception: Exception) -> None:
        nonlocal swallow
        swallow = False
        raise exception

    for attempt in range(1, max_retries + 1):
        try:
            return func(bail, attempt)
        except Exception as e:
            if not swallow:
                raise e

        random_sleep_factor = random.uniform(1, 1 + random_factor)
        backoff_base_secs = backoff_base_millis / 1000
        backoff_exp_factor = backoff_factor ** (attempt - 1)

        sleep_time_secs = random_sleep_factor * backoff_base_secs * backoff_exp_factor
        time.sleep(sleep_time_secs)

    return func(bail, max_retries + 1)


def _catch_not_found_or_throw(exc: ApifyApiError) -> None:
    is_not_found_status = (exc.status_code == HTTPStatus.NOT_FOUND)
    is_not_found_message = (exc.type == NOT_FOUND_TYPE) or (isinstance(exc.message, str) and NOT_FOUND_ON_S3 in exc.message)
    if not (is_not_found_status and is_not_found_message):
        raise exc

    return None


def _encode_webhook_list_to_base64(webhooks: List[Dict]) -> bytes:
    """Encode a list of dictionaries representing webhooks to their base64-encoded representation for the API."""
    data = []
    for webhook in webhooks:
        webhook_representation = {
            'eventTypes': webhook['event_types'],
            'requestUrl': webhook['request_url'],
        }
        if 'payload_template' in webhook:
            webhook_representation['payloadTemplate'] = webhook['payload_template']
        data.append(webhook_representation)

    return base64.b64encode(json.dumps(data).encode('utf-8'))


def _filter_out_none_values(dictionary: Dict) -> Dict:
    """Return copy of the dictionary, omitting all keys for which values are None.

    >>> _filter_out_none_values({"k1": "v1", "k2": None})
    {'k1': 'v1'}
    """
    return {k: v for k, v in dictionary.items() if v is not None}


def _filter_out_none_values_recursively(dictionary: Dict) -> Dict:
    """Return copy of the dictionary, recursively omitting all keys for which values are None.

    >>> _filter_out_none_values_recursively({"k1": "v1", "k2": None, "k3": {"k4": "v4", "k5": None}})
    {'k1': 'v1', 'k3': {'k4': 'v4'}}
    """
    return {
        k: v if not isinstance(v, Dict) else _filter_out_none_values_recursively(v)
        for k, v in dictionary.items()
        if v is not None
    }


def _snake_case_to_camel_case(str_snake_case: str) -> str:
    """Convert string in snake case to camel case.

    >>> _snake_case_to_camel_case("")
    ''
    >>> _snake_case_to_camel_case("making")
    'making'
    >>> _snake_case_to_camel_case("making_the_web_programmable")
    'makingTheWebProgrammable'
    >>> _snake_case_to_camel_case("making_the_WEB_programmable")
    'makingTheWebProgrammable'
    """
    return ''.join([
        part.capitalize() if i > 0 else part
        for i, part in enumerate(str_snake_case.split('_'))
    ])


def _encode_key_value_store_record_value(value: Any, content_type: Optional[str] = None) -> Tuple[Any, str]:
    if not content_type:
        if _is_file_or_bytes(value):
            content_type = 'application/octet-stream'
        elif isinstance(value, str):
            content_type = 'text/plain; charset=utf-8'
        else:
            content_type = 'application/json; charset=utf-8'

    if 'application/json' in content_type and not _is_file_or_bytes(value) and not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False, indent=2).encode('utf-8')

    return (value, content_type)


class ListPage:
    """A single page of items returned from a list() method."""

    #: list: List of returned objects on this page
    items: List
    #: int: Count of the returned objects on this page
    count: int
    #: int: The limit on the number of returned objects offset specified in the API call
    offset: int
    #: int: The offset of the first object specified in the API call
    limit: int
    #: int: Total number of objects matching the API call criteria
    total: int

    def __init__(self, data: Dict) -> None:
        """Initialize a ListPage instance from the API response data."""
        self.items = data['items'] if 'items' in data else []
        self.offset = data['offset'] if 'offset' in data else 0
        self.limit = data['limit'] if 'limit' in data else 0
        self.count = data['count'] if 'count' in data else len(self.items)
        self.total = data['total'] if 'total' in data else self.offset + self.count
