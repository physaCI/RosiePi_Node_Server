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

import os
import pwd
from socket import gethostname
import subprocess
import time

from flask import jsonify, request
from flask.views import MethodView

from werkzeug.exceptions import abort

from node_server import redis_queue

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        ret_val = dict(self.payload or ())
        ret_val['message'] = self.message
        return ret_val

class NodeStatus(MethodView):

    @staticmethod
    def _node_status():
        node_name = gethostname()

        job_count = redis_queue.RosieJobQueue()
        status = {
            'node_name': node_name,
            'busy': 0 < job_count.jobs.count,
            'job_count': job_count.jobs.count
        }

        return status

    def get(self):
        return jsonify(NodeStatus._node_status())


def rq_dummy(**kwargs):
    """ dummy func for rq job queue dev
    """

    time.sleep(30)
    print(kwargs)

class RunTest(MethodView):

    def post(self):
        if not request.is_json:
            raise InvalidUsage('Endpoint requires valid json payload.',
                               status_code=406)

        payload = request.get_json()
        if 'commit_sha' not in payload:
            raise InvalidUsage('No commit sha found in payload.',
                               status_code=400)
        elif 'check_run_id' not in payload:
            raise InvalidUsage('No check run ID found in payload.',
                               status_code=400)
        else:
            job = redis_queue.RosieJobQueue()
            user_dir = pwd.getpwnam('rosie-backend')[5]
            run_args = (
                f'{user_dir}/.local/bin/run_rosie',
                payload['commit_sha'],
                payload['check_run_id'],
            )
            run_kwargs = {
                'shell': True,
                'stdout': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                #'check': True,
                'cwd': user_dir,
                'env': {
                    'PYTHONUSERBASE': f'{user_dir}/.local'
                },
            }
            result = job.new_job(subprocess.run, run_args, kwargs=run_kwargs)
            if result.get_status() != 'failed':
                return jsonify(NodeStatus._node_status())
            else:
                return (str(result.exc_info), 500)
