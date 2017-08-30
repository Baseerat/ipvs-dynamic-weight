#!/usr/bin/env python

import os, socket, sys, commands, memcache, time

#TODO: handle multiple sites.

if len(sys.argv) < 7:
    raise Exception('You must pass the host ip addresses, and hostname and port of your memcached server, '
                    'along with a timeout value for probing the state')

server_addresses_string = sys.argv[1]
server_addresses = server_addresses_string.split(',')
server_port = sys.argv[2]
mc = memcache.Client([sys.argv[3]],)
timeout = float(sys.argv[4])
service_address = sys.argv[5]
service_port = sys.argv[6]
enable = sys.argv[7]
debug = len(sys.argv) > 8

while True:
    for server_address in server_addresses:
        weight = mc.get('%s-weight' % server_address,)
        if not weight:
            continue
        if not enable:
            weight = 1
        script = "sudo ipvsadm -e -t %s:%s -r %s:%s -m -w %s" % (service_address, service_port, server_address, server_port, weight)
        if debug: print '  - Running [%s]' % (script,)
        commands.getstatusoutput(script)
    time.sleep(timeout)
