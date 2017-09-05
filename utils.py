import os
from subprocess import Popen, PIPE, STDOUT


SUPERVISOR_CONFIG_DIR = '/Users/arpitbh/tools/supervisor/config'
SUPERVISORCTL = 'supervisorctl -c ' + SUPERVISOR_CONFIG_DIR + '/supervisord.conf '


def system(cmd):
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,
              stderr=STDOUT, close_fds=True)
    output = p.stdout.read()
    return output


def supervisorctl_update():
    output = system(SUPERVISORCTL + 'update')
    return str(output)


def supervisorctl_start_proc(proc):
    output = system(SUPERVISORCTL + 'start ' + proc)
    return str(output)


def supervisorctl_stop_proc(proc):
    output = system(SUPERVISORCTL + 'stop ' + proc)
    return str(output)


def supervisorctl_add_pg_config(name, config):
    cfilepath = os.path.join(SUPERVISOR_CONFIG_DIR, name + '.conf')
    with open(cfilepath, 'w') as f:
        f.write(config)


def fetch_status(closure_name):
    output = system(SUPERVISORCTL + 'status ' + closure_name + ':')
    output = output.decode("utf-8")
    if 'ERROR (no such group)' in output:
        return None
    processmap = {}
    for line in output.split('\n'):
        line = line.strip()
        if not line:
            continue
        tokens = ' '.join(line.split()).split()
        processmap[tokens[0].split(":")[1]] = {
            'state': tokens[1],
            'id': tokens[0],
            'elapsed': tokens[-1],
        }

    return processmap
