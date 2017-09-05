import os
import json
import redis
import traceback


class RedisPipeline:
    def __init__(self, meta):
        self.url = meta['url']

    def provision(self):
        logs = []
        try:
            logs.append(("INFO", "Provisioning RedisPipeline: " + self.url))
            logs.append(("INFO", "Connecting To Redis"))
            connection = redis.Redis.from_url(self.url)
            logs.append(("INFO", "Fetching info from Redis"))
            logs.append(("INFO", json.dumps(connection.info(), indent=4)))
            logs.append(("INFO", "Connection To Redis successful at URL: " + self.url))
            logs.append(("SUCCESS", "Provisioned RedisPipeline " + self.url))
        except Exception as e:
            logs.append(("FAIL", str(e)))
            logs.append(("FAIL", traceback.format_exc()))

        return logs
