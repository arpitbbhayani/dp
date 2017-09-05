import os
import pymongo
import traceback
from celery import Celery
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
from bson.objectid import ObjectId
from entities.stages import LocalFS
from entities.pipelines import RedisPipeline

import utils


app = Celery('tasks', broker='redis://localhost')
stacsdb = pymongo.MongoClient().stacs

T_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
j2_env = Environment(loader=FileSystemLoader(T_DIR),
                     trim_blocks=True,
                     extensions=['jinja2.ext.do'])


@app.task
def start_provision(provision_id):
    provisionsdb = stacsdb.provisions
    closuresdb = stacsdb.closures
    provision_id = ObjectId(provision_id)

    provision = provisionsdb.find_one({
        '_id': provision_id
    })

    provisionsdb.update_one({
        '_id': provision_id,
    }, {'$set': {
        'state': 'IN_PROGRESS',
    }})

    try:
        closure_id = ObjectId(provision['cid'])
        closure = closuresdb.find_one({
            '_id': closure_id
        })

        # Provision Stages
        stagesdb = stacsdb.stages
        stages = [stage for stage in stagesdb.find({
            'cid': closure_id
        })]
        for stage in stages:
            t = stage['location']['type']

            logs = []
            if t == 'localfs':
                logs.extend(LocalFS(stage['location']['meta']).provision())
            else:
                raise Exception("Unsupported stage type: " + t)

            provisionsdb.update_one({'_id': provision_id}, {"$set": {
                ('details.stages.' + stage['name']): logs
            }})

        # Provision Pipelines
        pipelinesdb = stacsdb.pipelines
        pipelines = [pipeline for pipeline in pipelinesdb.find({
            'cid': closure_id
        })]
        for pipeline in pipelines:
            t = pipeline['type']

            logs = []
            if t == 'redis':
                logs.extend(RedisPipeline(pipeline['meta']).provision())
            else:
                raise Exception("Unsupported pipeline type: " + t)

            provisionsdb.update_one({'_id': provision_id}, {"$set": {
                ('details.pipelines.' + pipeline['name']): logs
            }})

        # Provision Transforms
        transformsdb = stacsdb.transforms
        transforms = [transform for transform in transformsdb.find({
            'cid': closure_id
        })]
        for transform in transforms:
            t = transform['input_source']['type']
            logs = []
            if t == 'redis':
                logs.extend(RedisPipeline(transform['input_source']['meta']).provision())
            else:
                raise Exception("Unsupported pipeline type: " + t)

            t = transform['output_target']['type']
            if t == 'redis':
                logs.extend(RedisPipeline(transform['output_target']['meta']).provision())
            else:
                raise Exception("Unsupported pipeline type: " + t)

            provisionsdb.update_one({'_id': provision_id}, {"$set": {
                ('details.transforms.' + transform['name']): logs
            }})

        pullersdb = stacsdb.pullers
        pullers = [puller for puller in pullersdb.find({
            'cid': closure_id
        })]

        pushersdb = stacsdb.pushers
        pushers = [pusher for pusher in pushersdb.find({
            'cid': closure_id
        })]

        logs = []
        logs.append(("INFO", "Creating or Updating Supervisor Config File"))
        c = j2_env.get_template('supervisor/closure.conf').render(
            closure=closure, transforms=transforms, pullers=pullers, pushers=pushers
        )
        logs.append(('INFO', c))
        files_required = set([tokens for tokens in c.split() if tokens.endswith('.py')])
        logs.append(('INFO', "Make sure following executors are present:\n" + '\n'.join(files_required)))

        utils.supervisorctl_add_pg_config(closure['name'], c)

        provisionsdb.update_one({'_id': provision_id}, {"$set": {
            'details.supervisor.config': logs
        }})

        logs = []

        logs.append(('INFO', 'Updating supervisord'))
        output = utils.supervisorctl_update()
        logs.append(('INFO', output))

        provisionsdb.update_one({'_id': provision_id}, {"$set": {
            'details.supervisor.commands': logs
        }})

        provisionsdb.update_one({
            '_id': provision_id
        }, {
            '$set': {
                'state': 'COMPLETED',
            }
        })

    except Exception as e:
        provisionsdb.update_one({
            '_id': provision_id,
        }, {
            '$set': {
                'state': 'FAILED',
                'error': str(e) + "-" + traceback.format_exc()
            }
        })

    return None
