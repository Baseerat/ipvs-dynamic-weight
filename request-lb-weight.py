#!/usr/bin/env python

import os, socket, site, sys, memcache, time

# If the calculation of the load AND the weighting/aing
# of the load data is at the same interval (1 minute) then we
# will see a lot of jerkiness. So we take the 5 minute average.
# This means servers get lowered in priority more slowly.
server_id = _SERVER_ID_

if len(sys.argv) < 3:
    raise Exception('You must pass the hostname and port of your memcached server, '
                    'along with a timeout value for probing the state and the max load')

mc = memcache.Client([sys.argv[1]], )
timeout = float(sys.argv[2])
max_load = int(sys.argv[3])

while True:
    load = os.getloadavg()[1]

    # Weight must range from 1 - 256
    if load < 0.001:
        load = 0.001
    if load > max_load:
        load = max_load

    weight = int(((255 / max_load) * ((max_load + 0.001) - load)) + 1)

    if len(sys.argv) > 3:
        print 'Declaring weight of %s for %s for %ss, given load of %s' % (weight, server_id, timeout, load)

    mc.set('server-weight-%s' % server_id, weight, time=60 * 2)  # Set a two minute expiry
    time.sleep(timeout)
