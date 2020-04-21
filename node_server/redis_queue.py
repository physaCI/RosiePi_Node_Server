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
import redis
import rq

_redis_kwargs = {
    'host': os.environ.get('ROSIE_REDIS_HOST', u'localhost'),
    'port': os.environ.get('ROSIE_REDIS_PORT', 6379)
}


class RosieJobQueue():
    """ Class to provide RQ shortcut functions.
    """

    def __init__(self, redis_kwargs=_redis_kwargs):
        redis_conn = redis.Redis(**redis_kwargs)
        self.rq_queue = rq.Queue('rosiepi', connection=redis_conn)

    @property
    def jobs(self):
        """ The current jobs in the queue.

            :returns: rq.registry.StartedJobRegistry object
        """
        return self.rq_queue.started_job_registry

    def new_job(self, function, func_args=None, func_kwargs=None):
        """ Enqueue a new job to the queue.

            :params: function: The function to add to the queue.
            :params: dict info: A dict that contains the information to
                                pass into the queued job.

            :returns: int job-id
        """

        job = rq.Job.create(
            function,
            timeout="1h",
            args=func_args,
            kwargs=func_kwargs,
        )

        return self.rq_queue.enqueue_job(job)
