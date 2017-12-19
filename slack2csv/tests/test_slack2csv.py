# Standard library imports...
from os import environ
import pytest
from mock import Mock, patch

# Local imports...
from slack2csv.slack2csv import fetch_from_slack, lookup_channel_id_by_name


@patch('slack2csv.slack2csv.requests.get')
def test_lookup_channel_id_by_name_success(mock_get):
    true = 1
    false = 0
    fake_response = {
        "ok": true,
        "channels": [{
            "id": "C8675309",
            "name": "jenny",
        }]
    }

    mock_get.return_value.json.return_value = fake_response

    # Configure the mock to return a response with an OK status code.
    mock_get.return_value.ok = True

    # Call the service, which will send a request to the server.
    messages = lookup_channel_id_by_name('a', 'jenny')

    # If the request is sent successfully, then I expect a response to be returned.
    assert(messages == "C8675309")


@patch('slack2csv.slack2csv.requests.get')
def test_lookup_channel_id_by_name_fail(mock_get):
    true = 1
    false = 0
    fake_response = {
        "ok": true,
        "channels": [{
            "id": "C884288",
            "name": "bob",
        }]
    }

    mock_get.return_value.json.return_value = fake_response

    # Configure the mock to return a response with an OK status code.
    mock_get.return_value.ok = True

    # Call the service, which will send a request to the server.
    messages = lookup_channel_id_by_name('a', 'jenny')

    # If the request is sent successfully, then I expect a response to be returned.
    assert(messages == "")


@patch('slack2csv.slack2csv.requests.get')
def test_fetch_from_slack_success(mock_get):
    true = 1
    false = 0
    fake_response = {
        "ok": true,
        "has_more": false,
        "messages": [{
            "type": "message",
            "user": "U0012345",
            "text": "Hey!",
            "ts": "1513173325.000024"
        }]
    }

    mock_get.return_value.json.return_value = fake_response

    # Configure the mock to return a response with an OK status code.
    mock_get.return_value.ok = True

    # Call the service, which will send a request to the server.
    messages = fetch_from_slack('a', 'b', '1')

    # If the request is sent successfully, then I expect a response to be returned.
    assert(len(messages) == 1)


@patch('slack2csv.slack2csv.requests.get')
def test_fetch_from_slack_fail(mock_get):

    true = 1
    false = 0
    fake_response = {
        "ok": false,
        "error": "I'm an error",
        "has_more": false,
        "messages": [{
            "type": "message",
            "user": "U0012345",
            "text": "Hey!",
            "ts": "1513173325.000024"
        }]
    }

    mock_get.return_value.json.return_value = fake_response

    # Configure the mock to return a response with an OK status code.
    mock_get.return_value.ok = True

    # Call the service, which will send a request to the server.
    with pytest.raises(ValueError) as exc_info:
        messages = fetch_from_slack('a', 'b', '1')

    assert "I'm an error" in str(exc_info.value)
