#!/usr/bin/env python

import os, sys, memcache, time, psutil

# If the calculation of the load AND the weighting/aing
# of the load data is at the same interval (1 minute) then we
# will see a lot of jerkiness. So we take the 5 minute average.
# This means servers get lowered in priority more slowly.

if len(sys.argv) < 5:
    raise Exception('You must pass the host ip address, and hostname and port of your memcached server, '
                    'along with a timeout value for probing the state, debug, metric, and ...')

server_address = sys.argv[1]
mc = memcache.Client([sys.argv[2]], )
timeout = float(sys.argv[3])
debug = sys.argv[4]
metric = sys.argv[5]

if metric == 'loadavg':
    max_load = int(sys.argv[6])

    while True:
        load = os.getloadavg()[1]

        # Weight must range from 1 - 256
        if load < 0.001:
            load = 0.001
        if load > max_load:
            load = max_load

        weight = int(((255 / max_load) * ((max_load + 0.001) - load)) + 1)

        if debug == 'True':
            print 'Declaring weight of %s for %s for %ss' % (weight, server_address, 60 * 2)

        mc.set('%s-weight' % server_address, weight, time=60 * 2)  # Set a two minute expiry
        time.sleep(timeout)

elif metric == 'cpu':
    alpha_value = float(sys.argv[6])
    inv_alpha_value = 1 - alpha_value


    def get_stats():
        _stats = psutil.cpu_times()
        _idle = _stats.idle
        _total = _idle + (_stats.user + _stats.system + _stats.nice + _stats.irq + _stats.softirq)
        return _idle, _total


    last_idle, last_total = get_stats()
    util = 100 - psutil.cpu_percent(interval=0.1)
    weight = int(util)

    while True:
        idle, total = get_stats()

        if (total - last_total) != 0:
            util = 100.0 * (idle - last_idle) / (total - last_total)

        weight = int((alpha_value * util) + (inv_alpha_value * weight))
        if weight == 0:
            weight = 1
        # else: weight = XXX

        if debug == 'True':
            print 'Declaring weight of %s for %s for %ss' % (weight, server_address, 60 * 2)

        last_idle, last_total = idle, total

        mc.set('%s-weight' % server_address, weight, time=60 * 2)  # Set a two minute expiry
        time.sleep(timeout)
