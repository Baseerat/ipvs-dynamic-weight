#!/usr/bin/env python

import os, socket, sys, commands, memcache, time

#TODO: handle multiple sites.

server_ids = [_SERVER_IDS_]

if len(sys.argv) < 3:
    raise Exception('You must pass the hostname and port of your memcached server, '
                    'along with a timeout value for probing the state')

mc = memcache.Client([sys.argv[1]], )

timeout = float(sys.argv[2])
debug = len(sys.argv) > 3

while True:
    for server_id in server_ids:
        weight = mc.get('server-weight-%s' % server_id, )
        if not weight:
            continue
        script = "sudo ipvsadm -e -t XXX:8080 -r YYY%s:8080 -w %s" % (server_id, weight)
        if debug: print '  - Running [%s]' % (script,)
        commands.getstatusoutput(script)
    time.sleep(timeout)
