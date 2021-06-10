import io
import time
import unittest
from datetime import datetime, timezone
from typing import Any, Callable

from apify_client._utils import (
    _encode_webhook_list_to_base64,
    _is_content_type_json,
    _is_content_type_text,
    _is_content_type_xml,
    _is_file_or_bytes,
    _parse_date_fields,
    _pluck_data,
    _retry_with_exp_backoff,
    _to_safe_id,
)
from apify_client.consts import WebhookEventType


class UtilsTest(unittest.TestCase):
    def test__to_safe_id(self) -> None:
        self.assertEqual(_to_safe_id('abc'), 'abc')
        self.assertEqual(_to_safe_id('abc/def'), 'abc~def')
        self.assertEqual(_to_safe_id('abc~def'), 'abc~def')

    def test__parse_date_fields(self) -> None:
        # works correctly on empty dicts
        self.assertEqual(_parse_date_fields({}), {})

        # correctly parses dates on fields ending with -At
        expected_datetime = datetime(2016, 11, 14, 11, 10, 52, 425000, timezone.utc)
        self.assertEqual(_parse_date_fields({'createdAt': '2016-11-14T11:10:52.425Z'}), {'createdAt': expected_datetime})

        # doesn't parse dates on fields not ending with -At
        self.assertEqual(_parse_date_fields({'saveUntil': '2016-11-14T11:10:52.425Z'}), {'saveUntil': '2016-11-14T11:10:52.425Z'})

        # parses dates in dicts in lists
        expected_datetime = datetime(2016, 11, 14, 11, 10, 52, 425000, timezone.utc)
        self.assertEqual(_parse_date_fields([{'createdAt': '2016-11-14T11:10:52.425Z'}]), [{'createdAt': expected_datetime}])

        # parses nested dates
        expected_datetime = datetime(2020, 2, 29, 10, 9, 8, 100000, timezone.utc)
        self.assertEqual(
            _parse_date_fields({'a': {'b': {'c': {'createdAt': '2020-02-29T10:09:08.100Z'}}}}),
            {'a': {'b': {'c': {'createdAt': expected_datetime}}}},
        )

        # doesn't parse dates nested too deep
        expected_datetime = datetime(2020, 2, 29, 10, 9, 8, 100000, timezone.utc)
        self.assertEqual(
            _parse_date_fields({'a': {'b': {'c': {'d': {'createdAt': '2020-02-29T10:09:08.100Z'}}}}}),
            {'a': {'b': {'c': {'d': {'createdAt': '2020-02-29T10:09:08.100Z'}}}}},
        )

        # doesn't die when the date can't be parsed
        self.assertEqual(_parse_date_fields({'createdAt': 'NOT_A_DATE'}), {'createdAt': 'NOT_A_DATE'})

    def test__pluck_data(self) -> None:
        # works correctly when data is present
        self.assertEqual(_pluck_data({'data': {}}), {})
        self.assertEqual(_pluck_data({'a': 'b', 'data': {'b': 'c'}}), {'b': 'c'})

        # throws the right error when it is not
        with self.assertRaises(ValueError):
            _pluck_data({'a': 'b'})
        with self.assertRaises(ValueError):
            _pluck_data(None)
        with self.assertRaises(ValueError):
            _pluck_data('{"a": "b"}')

    def test__is_content_type_json(self) -> None:
        # returns True for the right content types
        self.assertEqual(_is_content_type_json('application/json'), True)
        self.assertEqual(_is_content_type_json('application/jsonc'), True)
        # returns False for bad content types
        self.assertEqual(_is_content_type_json('application/xml'), False)
        self.assertEqual(_is_content_type_json('application/ld+json'), False)

    def test__is_content_type_xml(self) -> None:
        # returns True for the right content types
        self.assertEqual(_is_content_type_xml('application/xml'), True)
        self.assertEqual(_is_content_type_xml('application/xhtml+xml'), True)
        # returns False for bad content types
        self.assertEqual(_is_content_type_xml('application/json'), False)
        self.assertEqual(_is_content_type_xml('text/html'), False)

    def test__is_content_type_text(self) -> None:
        # returns True for the right content types
        self.assertEqual(_is_content_type_text('text/html'), True)
        self.assertEqual(_is_content_type_text('text/plain'), True)
        # returns False for bad content types
        self.assertEqual(_is_content_type_text('application/json'), False)
        self.assertEqual(_is_content_type_text('application/text'), False)

    def test__is_file_or_bytes(self) -> None:
        # returns True for the right value types
        self.assertEqual(_is_file_or_bytes(b'abc'), True)
        self.assertEqual(_is_file_or_bytes(bytearray.fromhex('F0F1F2')), True)
        self.assertEqual(_is_file_or_bytes(io.BytesIO(b'\x00\x01\x02')), True)

        # returns False for bad value types
        self.assertEqual(_is_file_or_bytes('abc'), False)
        self.assertEqual(_is_file_or_bytes(['a', 'b', 'c']), False)
        self.assertEqual(_is_file_or_bytes({'a': 'b'}), False)
        self.assertEqual(_is_file_or_bytes(None), False)

    def test__retry_with_exp_backoff(self) -> None:
        attempt_counter = 0

        class RetryableException(Exception):
            pass

        class BailException(Exception):
            pass

        def returns_on_fifth_attempt(bail: Callable, attempt: int) -> Any:
            nonlocal attempt_counter
            attempt_counter += 1

            if attempt == 5:
                return 'SUCCESS'
            raise RetryableException()

        def bails_on_third_attempt(bail: Callable, attempt: int) -> Any:
            nonlocal attempt_counter
            attempt_counter += 1

            if attempt == 3:
                bail(BailException())
            raise RetryableException()

        # Returns the correct result after the correct time (should take 100 + 200 + 400 + 800 = 1500 ms)
        start = time.time()
        result = _retry_with_exp_backoff(returns_on_fifth_attempt, backoff_base_millis=100, backoff_factor=2, random_factor=0)
        elapsed_time_seconds = time.time() - start
        self.assertEqual(result, 'SUCCESS')
        self.assertEqual(attempt_counter, 5)
        self.assertGreater(elapsed_time_seconds, 1.4)
        self.assertLess(elapsed_time_seconds, 2.0)

        # Stops retrying when failed for max_retries times
        attempt_counter = 0
        with self.assertRaises(RetryableException):
            _retry_with_exp_backoff(returns_on_fifth_attempt, max_retries=3, backoff_base_millis=1)
        self.assertEqual(attempt_counter, 4)

        # Bails when the bail function is called
        attempt_counter = 0
        with self.assertRaises(BailException):
            _retry_with_exp_backoff(bails_on_third_attempt, backoff_base_millis=1)
        self.assertEqual(attempt_counter, 3)

    def test__encode_webhook_list_to_base64(self) -> None:
        self.assertEqual(_encode_webhook_list_to_base64([]), b'W10=')
        self.assertEqual(
            _encode_webhook_list_to_base64([
                {
                    'event_types': [WebhookEventType.ACTOR_RUN_CREATED],
                    'request_url': 'https://example.com/run-created',
                },
                {
                    'event_types': [WebhookEventType.ACTOR_RUN_SUCCEEDED],
                    'request_url': 'https://example.com/run-succeeded',
                    'payload_template': '{"hello": "world", "resource":{{resource}}}',
                },
            ]),
            b'W3siZXZlbnRUeXBlcyI6IFsiQUNUT1IuUlVOLkNSRUFURUQiXSwgInJlcXVlc3RVcmwiOiAiaHR0cHM6Ly9leGFtcGxlLmNvbS9ydW4tY3JlYXRlZCJ9LCB7ImV2ZW50VHlwZXMiOiBbIkFDVE9SLlJVTi5TVUNDRUVERUQiXSwgInJlcXVlc3RVcmwiOiAiaHR0cHM6Ly9leGFtcGxlLmNvbS9ydW4tc3VjY2VlZGVkIiwgInBheWxvYWRUZW1wbGF0ZSI6ICJ7XCJoZWxsb1wiOiBcIndvcmxkXCIsIFwicmVzb3VyY2VcIjp7e3Jlc291cmNlfX19In1d',  # noqa: E501
        )
