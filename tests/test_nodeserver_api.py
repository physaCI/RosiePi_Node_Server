# The MIT License (MIT)
#
# Copyright (c) 2019 Michael Schroeder
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from datetime import datetime
import json

import pytest

from flask import jsonify

req_headers = {
    'Authorization':'Signature key-id=test-key,algorithm="hmac-sha256",headers="(request-target) date",signature=foob4r=',
    'Date': datetime.now().strftime('%Y-%m-%dT%H:%M:%S%Z')
}

def test_node_deny_no_http_signature(client):
    """ Test node that does not have the required HTTP Signature
        in the Authorization header.
    """

    response = client.get('/')

    assert response.status_code == 401

def test_node_status_returns_json(client):
    """ Test node status returning valid json.
    """

    response = client.get('/status', headers=req_headers)
    ret_json = response.get_json()

    assert json.dumps(ret_json)

def test_node_status_return_info(client):
    """ Test node status returns proper info.
    """
    response = client.get('/status', headers=req_headers)
    ret_json = response.get_json()

    for item in ['node_name', 'busy', 'job_count']:
        assert item in ret_json

def test_node_runtest_get_verb(client):
    """ Test node RunTest GET verb
    """

    response = client.get('/run-test', headers=req_headers)

    assert response.status_code == 405

def test_node_runtest_post_success(client):
    """ Test node RunTest with valid POST verb
    """

    payload = {
        'commit_sha': '123456abcdefg'
    }

    response = client.post('/run-test', json=payload, headers=req_headers)

    assert response.status_code == 200

def test_node_runtest_post_non_json(client):
    """ Test node RunTest with invalid POST verb
    """

    payload = 'null'

    response = client.post('/run-test', data=payload, headers=req_headers)

    assert response.status_code == 406

def test_node_runtest_post_no_commit_sha(client):
    """ Test node RunTest POST with JSON payload not containing a
        'commit_sha' field.
    """

    payload = {
        'null': 'null'
    }

    response = client.post('/run-test', json=payload, headers=req_headers)

    assert response.status_code == 400
