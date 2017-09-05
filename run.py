import json
from datetime import datetime
import pymongo
from bson.objectid import ObjectId
from flask import Flask, request, render_template, redirect

import tasks
import utils

app = Flask(__name__)
stacsdb = pymongo.MongoClient().stacs


@app.route('/', methods=["GET"])
def index():
    return redirect('/closures')


@app.route('/closures', methods=["GET"])
def closures():
    closuresdb = stacsdb.closures
    return render_template('closures/index.html',
                           closures=[c for c in closuresdb.find()])


@app.route('/data-formats', methods=["GET"])
def dataformats():
    dataformatsdb = stacsdb.dataformats
    return render_template('dataformats/index.html',
                           dataformats=[d for d in dataformatsdb.find()])


@app.route('/pipeline-types', methods=["GET"])
def pipelinetypes():
    pipelinetypesdb = stacsdb.pipelinetypes
    return render_template('pipelinetypes/index.html',
                           pipelinetypes=[p for p in pipelinetypesdb.find()])


@app.route('/stage-types', methods=["GET"])
def stagetypes():
    stagetypesdb = stacsdb.stagetypes
    return render_template('stagetypes/index.html',
                           stagetypes=[s for s in stagetypesdb.find()])


@app.route('/closures/<cid>', methods=["GET", "POST"])
def closure_info(cid):
    cid = ObjectId(cid)
    closuresdb = stacsdb.closures

    if request.method == "GET":
        closure = closuresdb.find_one({
            '_id': cid
        })
        stagesdb = stacsdb.stages
        pipelinesdb = stacsdb.pipelines
        transformsdb = stacsdb.transforms
        pullersdb = stacsdb.pullers
        pushersdb = stacsdb.pushers
        status = utils.fetch_status(closure['name'])
        return render_template('closures/info.html',
                               closure=closure,
                               stages=[s for s in stagesdb.find({'cid': cid})],
                               pipelines=[p for p in pipelinesdb.find({'cid': cid})],
                               transforms=[p for p in transformsdb.find({'cid': cid})],
                               pullers=[p for p in pullersdb.find({'cid': cid})],
                               pushers=[p for p in pushersdb.find({'cid': cid})],
                               status=status)

    closuresdb.update_one({'_id': cid}, {"$set": {"graph": request.form.get('graph')}})

    return redirect("/closures/" + str(cid))


@app.route('/data-formats/<slug>', methods=["GET"])
def dataformat_info(slug):
    dataformatsdb = stacsdb.dataformats

    dataformat = dataformatsdb.find_one({
        'slug': slug
    })
    return render_template('dataformats/info.html',
                           dataformat=dataformat)


@app.route('/pipeline-types/<slug>', methods=["GET"])
def pipelinetypes_info(slug):
    pipelinetypesdb = stacsdb.pipelinetypes
    pipelinetype = pipelinetypesdb.find_one({
        'slug': slug
    })
    return render_template('pipelinetypes/info.html',
                           pipelinetype=pipelinetype)


@app.route('/stage-types/<slug>', methods=["GET"])
def stagetypes_info(slug):
    stagetypesdb = stacsdb.stagetypes
    stagetype = stagetypesdb.find_one({
        'slug': slug
    })
    return render_template('stagetypes/info.html',
                           stagetype=stagetype)


@app.route('/closures/create', methods=["GET", "POST"])
def closure_create():
    if request.method == "GET":
        return render_template('closures/create.html')

    name = request.form.get('name')

    closuresdb = stacsdb.closures
    closuresdb.insert_one({
        'name': request.form.get('name')
    })

    return redirect('/closures')


@app.route('/data-formats/create', methods=["GET", "POST"])
def dataformat_create():
    if request.method == "GET":
        return render_template('dataformats/create.html')

    name = request.form.get('name')
    slug = request.form.get('slug')
    description = request.form.get('description')

    dataformatsdb = stacsdb.dataformats
    dataformatsdb.insert_one({
        'name': name,
        'slug': slug,
        'description': description
    })

    return redirect('/data-formats')


@app.route('/pipeline-types/create', methods=["GET", "POST"])
def pipelinetype_create():
    if request.method == "GET":
        return render_template('pipelinetypes/create.html')

    name = request.form.get('name')
    slug = request.form.get('slug')
    params = request.form.get('params')
    if params:
        params = params.split(',')
    else:
        params = []

    pipelinetypesdb = stacsdb.pipelinetypes
    pipelinetypesdb.insert_one({
        'name': name,
        'slug': slug,
        'params': params
    })

    return redirect('/pipeline-types')


@app.route('/stage-types/create', methods=["GET", "POST"])
def stagetype_create():
    if request.method == "GET":
        return render_template('stagetypes/create.html')

    name = request.form.get('name')
    slug = request.form.get('slug')
    params = request.form.get('params')
    if params:
        params = params.split(',')
    else:
        params = []

    stagetypesdb = stacsdb.stagetypes
    stagetypesdb.insert_one({
        'name': name,
        'slug': slug,
        'params': params
    })

    return redirect('/stage-types')


@app.route('/closures/<cid>/pipelines/create', methods=["GET", "POST"])
def closure_pipeline_create(cid):
    cid = ObjectId(cid)
    if request.method == "GET":
        return render_template('pipelines/create.html', cid=cid)

    name = request.form.get('name')
    pipelinesdb = stacsdb.pipelines
    pipelinesdb.insert_one({
        'name': request.form.get('name'),
        'cid': cid
    })

    return redirect('/closures/' + str(cid))


@app.route('/closures/<cid>/pipelines/<pid>', methods=["GET"])
def closure_pipeline_info(cid, pid):
    pid = ObjectId(pid)
    pipelinesdb = stacsdb.pipelines
    pipeline = pipelinesdb.find_one({
        '_id': pid
    })
    pipeline['_id'] = str(pipeline['_id'])
    pipeline['cid'] = str(pipeline['cid'])
    return render_template('pipelines/info.html', pipeline=pipeline,
                            pipelineJSON=json.dumps(pipeline, indent=4))


@app.route('/closures/<cid>/pipelines/<pid>/edit', methods=["GET", "POST"])
def closure_pipeline_edit(cid, pid):
    cid = ObjectId(cid)
    pid = ObjectId(pid)

    pipelinesdb = stacsdb.pipelines

    if request.method == "GET":
        pipeline = pipelinesdb.find_one({
            '_id': pid
        })
        dataformatsdb = stacsdb.dataformats
        pipelinetypesdb = stacsdb.pipelinetypes
        return render_template('pipelines/edit.html', pipeline=pipeline,
                               dataformats=[d for d in dataformatsdb.find()],
                               pipelinetypes=[p for p in pipelinetypesdb.find()])

    name = request.form.get('name')
    pipeline_type = request.form.get('pipeline-type')
    meta = {}
    if pipeline_type == 'null':
        pass
    elif pipeline_type == 'redis':
        meta['url'] = request.form.get('pipeline-redis-url')
        meta['format'] = request.form.get('format')
    elif pipeline_type == 'rabbitmq':
        meta['url'] = request.form.get('pipeline-rabbitmq-url')
        meta['format'] = request.form.get('format')

    pipelinesdb.update_one({'_id': pid}, {"$set": {
        "name": name,
        "type": pipeline_type,
        "meta": meta
    }})

    return redirect('/closures/' + str(cid))


@app.route('/closures/<cid>/pullers/create', methods=["GET", "POST"])
def closure_puller_create(cid):
    cid = ObjectId(cid)
    if request.method == "GET":
        return render_template('pullers/create.html', cid=cid)

    name = request.form.get('name')
    pullersdb = stacsdb.pullers
    pullersdb.insert_one({
        'name': request.form.get('name'),
        'cid': cid
    })

    return redirect('/closures/' + str(cid))


@app.route('/closures/<cid>/pullers/<pid>', methods=["GET"])
def closure_pullers_info(cid, pid):
    pid = ObjectId(pid)
    pullersdb = stacsdb.pullers
    puller = pullersdb.find_one({
        '_id': pid
    })
    puller['_id'] = str(puller['_id'])
    puller['cid'] = str(puller['cid'])
    return render_template('pullers/info.html', puller=puller,
                            pullerJSON=json.dumps(puller, indent=4))


@app.route('/closures/<cid>/pullers/<pid>/edit', methods=["GET", "POST"])
def closure_puller_edit(cid, pid):
    cid = ObjectId(cid)
    pid = ObjectId(pid)

    pullersdb = stacsdb.pullers

    if request.method == "GET":
        puller = pullersdb.find_one({
            '_id': pid
        })
        dataformatsdb = stacsdb.dataformats
        pipelinetypesdb = stacsdb.pipelinetypes
        stagetypesdb = stacsdb.stagetypes
        return render_template('pullers/edit.html', puller=puller,
                               dataformats=[d for d in dataformatsdb.find()],
                               pipelinetypes=[p for p in pipelinetypesdb.find()],
                               stagetypes=[s for s in stagetypesdb.find()])

    name = request.form.get('name')
    input_source_type = request.form.get('stage-type')
    meta = {}
    if input_source_type == 's3':
        meta['s3-location'] = request.form.get('input-source-s3-location')
        meta['format'] = request.form.get('input-format')
    elif input_source_type == 'localfs':
        meta['directory'] = request.form.get('input-source-directory')
        meta['format'] = request.form.get('input-format')
    input_source = {
        "type": input_source_type,
        "meta": meta,
    }

    pipeline_type = request.form.get('pipeline-type')
    meta = {}
    if pipeline_type == "redis":
        meta['url'] = request.form.get('pipeline-redis-url')
        meta['format'] = request.form.get('pipeline-format')
    elif pipeline_type == "rabbitmq":
        meta['url'] = request.form.get('pipeline-rabbitmq-url')
        meta['format'] = request.form.get('pipeline-format')
    pipeline = {
        "type": pipeline_type,
        "meta": meta
    }

    pullersdb.update_one({'_id': pid}, {"$set": {
        "name": name,
        "input_source": input_source,
        "pipeline": pipeline,
    }})

    return redirect('/closures/' + str(cid))



@app.route('/closures/<cid>/pushers/create', methods=["GET", "POST"])
def closure_pusher_create(cid):
    cid = ObjectId(cid)
    if request.method == "GET":
        return render_template('pushers/create.html', cid=cid)

    name = request.form.get('name')
    pushersdb = stacsdb.pushers
    pushersdb.insert_one({
        'name': request.form.get('name'),
        'cid': cid
    })

    return redirect('/closures/' + str(cid))


@app.route('/closures/<cid>/pushers/<pid>', methods=["GET"])
def closure_pusher_info(cid, pid):
    pid = ObjectId(pid)
    pushersdb = stacsdb.pushers
    pusher = pushersdb.find_one({
        '_id': pid
    })
    pusher['_id'] = str(pusher['_id'])
    pusher['cid'] = str(pusher['cid'])
    return render_template('pushers/info.html', pusher=pusher,
                            pusherJSON=json.dumps(pusher, indent=4))


@app.route('/closures/<cid>/pushers/<pid>/edit', methods=["GET", "POST"])
def closure_pusher_edit(cid, pid):
    cid = ObjectId(cid)
    pid = ObjectId(pid)

    pushersdb = stacsdb.pushers

    if request.method == "GET":
        pusher = pushersdb.find_one({
            '_id': pid
        })
        dataformatsdb = stacsdb.dataformats
        pipelinetypesdb = stacsdb.pipelinetypes
        stagetypesdb = stacsdb.stagetypes
        return render_template('pushers/edit.html', pusher=pusher,
                               dataformats=[d for d in dataformatsdb.find()],
                               pipelinetypes=[p for p in pipelinetypesdb.find()],
                               stagetypes=[s for s in stagetypesdb.find()])

    name = request.form.get('name')
    output_target_type = request.form.get('stage-type')
    meta = {}
    if output_target_type == 's3':
        meta['s3-location'] = request.form.get('output-target-s3-location')
        meta['format'] = request.form.get('output-format')
    elif output_target_type == 'localfs':
        meta['directory'] = request.form.get('output-target-directory')
        meta['format'] = request.form.get('output-format')
    output_target = {
        "type": output_target_type,
        "meta": meta,
    }

    pipeline_type = request.form.get('pipeline-type')
    meta = {}
    if pipeline_type == "redis":
        meta['url'] = request.form.get('pipeline-redis-url')
        meta['format'] = request.form.get('pipeline-format')
    elif pipeline_type == "rabbitmq":
        meta['url'] = request.form.get('pipeline-rabbitmq-url')
        meta['format'] = request.form.get('pipeline-format')
    pipeline = {
        "type": pipeline_type,
        "meta": meta
    }

    pushersdb.update_one({'_id': pid}, {"$set": {
        "name": name,
        "output_target": output_target,
        "pipeline": pipeline,
    }})

    return redirect('/closures/' + str(cid))


@app.route('/closures/<cid>/stages/create', methods=["GET", "POST"])
def closure_stage_create(cid):
    cid = ObjectId(cid)
    if request.method == "GET":
        return render_template('stages/create.html', cid=cid)

    name = request.form.get('name')
    stagesdb = stacsdb.stages
    stagesdb.insert_one({
        'name': request.form.get('name'),
        'cid': cid
    })

    return redirect('/closures/' + str(cid))


@app.route('/closures/<cid>/stages/<sid>', methods=["GET"])
def closure_stages_info(cid, sid):
    sid = ObjectId(sid)
    stagesdb = stacsdb.stages
    stage = stagesdb.find_one({
        '_id': sid
    })
    stage['_id'] = str(stage['_id'])
    stage['cid'] = str(stage['cid'])
    return render_template('stages/info.html', stage=stage,
                            stageJSON=json.dumps(stage, indent=4))


@app.route('/closures/<cid>/stages/<sid>/edit', methods=["GET", "POST"])
def closure_stage_edit(cid, sid):
    cid = ObjectId(cid)
    sid = ObjectId(sid)

    stagesdb = stacsdb.stages

    if request.method == "GET":
        stage = stagesdb.find_one({
            '_id': sid
        })
        dataformatsdb = stacsdb.dataformats
        stagetypesdb = stacsdb.stagetypes
        return render_template('stages/edit.html', stage=stage,
                               dataformats=[d for d in dataformatsdb.find()],
                               stagetypes=[s for s in stagetypesdb.find()])

    name = request.form.get('name')
    location_type = request.form.get('location')

    meta = {}
    if location_type == 's3':
        meta['s3location'] = request.form.get('stage-s3-location')
        meta['format'] = request.form.get('format')
    elif location_type == 'localfs':
        meta['directory'] = request.form.get('stage-directory')
        meta['format'] = request.form.get('format')

    stagesdb.update_one({'_id': sid}, {"$set": {
        "name": name,
        "location": {
            "type": location_type,
            "meta": meta
        },
    }})

    return redirect('/closures/' + str(cid))


@app.route('/closures/<cid>/transforms/create', methods=["GET", "POST"])
def closure_transform_create(cid):
    cid = ObjectId(cid)
    if request.method == "GET":
        return render_template('transforms/create.html', cid=cid)

    name = request.form.get('name')
    transformsdb = stacsdb.transforms
    transformsdb.insert_one({
        'name': request.form.get('name'),
        'cid': cid
    })

    return redirect('/closures/' + str(cid))


@app.route('/closures/<cid>/transforms/<tid>', methods=["GET"])
def closure_transform_info(cid, tid):
    tid = ObjectId(tid)
    transformsdb = stacsdb.transforms
    transform = transformsdb.find_one({
        '_id': tid
    })
    transform['_id'] = str(transform['_id'])
    transform['cid'] = str(transform['cid'])
    return render_template('transforms/info.html', transform=transform,
                            transformJSON=json.dumps(transform, indent=4))


@app.route('/closures/<cid>/transforms/<tid>/edit', methods=["GET", "POST"])
def closure_transform_edit(cid, tid):
    cid = ObjectId(cid)
    tid = ObjectId(tid)

    transformsdb = stacsdb.transforms

    if request.method == "GET":
        transform = transformsdb.find_one({
            '_id': tid
        })
        dataformatsdb = stacsdb.dataformats
        pipelinetypesdb = stacsdb.pipelinetypes
        return render_template('transforms/edit.html', transform=transform,
                               dataformats=[d for d in dataformatsdb.find()],
                               pipelinetypes=[p for p in pipelinetypesdb.find()])

    name = request.form.get('name')
    input_source_type = request.form.get('input-source')
    input_source = {
        'type': input_source_type,
        'meta': {}
    }

    if input_source_type == 'null':
        pass
    elif input_source_type == 'redis':
        input_source['meta']['url'] = request.form.get('input-source-redis-url')
        input_source['meta']['format'] = request.form.get('input-format')
    elif input_source_type == 'rabbitmq':
        input_source['meta']['url'] = request.form.get('input-source-rabbitmq-url')
        input_source['meta']['format'] = request.form.get('input-format')

    output_target_type = request.form.get('output-target')
    output_target = {
        'type': output_target_type,
        'meta': {}
    }

    if output_target_type == 'null':
        pass
    elif output_target_type == 'redis':
        output_target['meta']['url'] = request.form.get('output-target-redis-url')
        output_target['meta']['format'] = request.form.get('output-format')
    elif output_target_type == 'rabbitmq':
        output_target['meta']['url'] = request.form.get('output-target-rabbitmq-url')
        output_target['meta']['format'] = request.form.get('output-format')

    transformsdb.update_one({'_id': tid}, {"$set": {
        "name": name,
        "input_source": input_source,
        "output_target": output_target,
    }})

    return redirect('/closures/' + str(cid))


@app.route('/closures/<cid>/provisions', methods=["POST", "GET"])
def closure_provision_create(cid):
    closuresdb = stacsdb.closures
    provisionsdb = stacsdb.provisions

    if request.method == 'GET':
        provisions = [p for p in provisionsdb.find({
            'cid': ObjectId(cid)
        }).sort('created_at', pymongo.DESCENDING)]
        return render_template('provisions/all.html', provisions=provisions)

    result = provisionsdb.insert_one({
        'cid': ObjectId(cid),
        'details': {},
        'created_at': datetime.now(),
        'state': 'SCHEDULED',
    })
    provision_id = str(result.inserted_id)
    tasks.start_provision.delay(provision_id)
    return redirect('/closures/' + cid + '/provisions/' + provision_id)


@app.route('/closures/<cid>/provisions/<pid>', methods=["GET"])
def closure_provision_info(cid, pid):
    provisionsdb = stacsdb.provisions
    provision = provisionsdb.find_one({
        '_id': ObjectId(pid)
    })
    return render_template('provisions/info.html', provision=provision)


@app.route('/closures/<cid>/processes/<proc>/<action>', methods=["POST"])
def process_management(cid, proc, action):
    if action == 'start':
        utils.supervisorctl_start_proc(proc)
    elif action == 'stop':
        utils.supervisorctl_stop_proc(proc)
    return redirect('/closures/' + cid)

@app.route('/partials/meta/<whichtype>/<slug>/<prefix>')
def partials_meta(whichtype, slug, prefix):
    if whichtype == 'pipelinetypes':
        db = stacsdb.pipelinetypes
    elif whichtype == 'stagetypes':
        db = stacsdb.stagetypes
    else:
        raise Exception("Invalid type " + whichtype)

    params = db.find_one({
        'slug': slug
    })['params']
    return render_template('partials/meta/textfield.html', params=params,
                           prefix=prefix)


if __name__ == '__main__':
    app.run()
