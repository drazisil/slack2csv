# Standard library imports...
from unittest.mock import Mock, patch

# Local imports...
from slack2csv.slack2csv import fetch_from_slack

# content of test_sample.py


@patch('slack2csv.slack2csv.requests.get')
def test_fetch_from_slack(mock_get):
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
    messages = fetch_from_slack('a', 'b', 'c')

    # If the request is sent successfully, then I expect a response to be returned.
    assert(len(messages) == 1)
