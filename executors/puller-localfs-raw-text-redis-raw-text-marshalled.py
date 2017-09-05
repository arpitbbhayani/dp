import os
import sys
import time
import redis
import pymongo
from bson.objectid import ObjectId
from os import listdir

stacsdb = pymongo.MongoClient().stacs

def pull(puller_id):
    print("input format: raw-text", flush=True)
    print("source: localfs", flush=True)
    print("pipeline: redis", flush=True)
    print("pipeline-format: raw-text-marshalled", flush=True)

    filesdone = set([])

    pullersdb = stacsdb.pullers
    puller = pullersdb.find_one({
        '_id': puller_id
    })

    directory = puller['input_source']['meta']['directory']
    redis_url = puller['pipeline']['meta']['url']

    print("directory: " + directory, flush=True)
    print("redis_url: " + redis_url, flush=True)

    rconnection = redis.Redis.from_url(redis_url)

    while True:
        files = [f for f in listdir(directory)]
        for f in files:
            if f in filesdone:
                continue
            filesdone.add(f)
            print("Waiting for 1 second", flush=True)
            time.sleep(1)
            with open(os.path.join(directory, f), 'r') as fp:
                content = fp.read()
                print(f, len(content), flush=True)
                rconnection.set(f, content)
                print("Putting key:" + f, flush=True)



if __name__ == '__main__':
    puller_id = ObjectId(sys.argv[1])
    pull(puller_id)
