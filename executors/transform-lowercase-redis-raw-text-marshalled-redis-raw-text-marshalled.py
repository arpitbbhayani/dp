import os
import sys
import time
import redis
import pymongo
from bson.objectid import ObjectId
from os import listdir

stacsdb = pymongo.MongoClient().stacs

def transform(transform_id):
    print("input format: raw-text-marshalledt", flush=True)
    print("source: redis", flush=True)
    print("target: redis", flush=True)
    print("output format: raw-text-marshalled", flush=True)

    transformsdb = stacsdb.transforms
    transform = transformsdb.find_one({
        '_id': transform_id
    })

    input_redis_url = transform['input_source']['meta']['url']
    output_redis_url = transform['output_target']['meta']['url']

    print("input_redis_url: " + input_redis_url, flush=True)
    print("output_redis_url: " + output_redis_url, flush=True)

    irc = redis.Redis.from_url(input_redis_url)
    orc = redis.Redis.from_url(output_redis_url)

    while True:
        for key in irc.scan_iter():
            time.sleep(1)
            key = key.decode('utf-8')
            content = irc.get(key).decode('utf-8')
            # Transform
            print("Transforming key: " + key, flush=True)
            content = content.lower()

            print("Putting in output pipeline: " + key, flush=True)
            orc.set(key, content)

            print("Deleting key from input pipeline: " + key, flush=True)
            irc.delete(key)


if __name__ == '__main__':
    transform_id = ObjectId(sys.argv[1])
    transform(transform_id)
