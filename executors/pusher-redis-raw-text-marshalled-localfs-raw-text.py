import os
import sys
import time
import redis
import pymongo
from bson.objectid import ObjectId
from os import listdir

stacsdb = pymongo.MongoClient().stacs

def push(pusher_id):
    print("pipeline: redis", flush=True)
    print("pipeline format: raw-text-marshalled", flush=True)
    print("output format: raw-text", flush=True)
    print("target: localfs", flush=True)

    pushersdb = stacsdb.pushers
    pusher = pushersdb.find_one({
        '_id': pusher_id
    })

    directory = pusher['output_target']['meta']['directory']
    redis_url = pusher['pipeline']['meta']['url']

    print("directory: " + directory, flush=True)
    print("redis_url: " + redis_url, flush=True)

    irc = redis.Redis.from_url(redis_url)

    while True:
        for key in irc.scan_iter():
            time.sleep(1)
            key = key.decode('utf-8')
            content = irc.get(key).decode('utf-8')

            with open(os.path.join(directory, key), 'w') as f:
                f.write(content)

            print("Deleting key from input pipeline: " + key, flush=True)
            irc.delete(key)


if __name__ == '__main__':
    pusher_id = ObjectId(sys.argv[1])
    push(pusher_id)
