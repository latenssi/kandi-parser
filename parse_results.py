#!/usr/bin/python
# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use('Agg')

import os
import sys
import json
import re

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from collections import namedtuple
from datetime import datetime

from boom import boom

# Plot = namedtuple('Plot', ['id', 'label', 'y_factor'])

# plots = [
#     Plot('mean', u'Keskimääräinen viive (ms)', 1000),
#     Plot('median', u'Mediaani viive (ms)', 1000),
#     Plot('max', u'Suurin viive (ms)', 1000),
#     Plot('min', u'Pienin viive (ms)', 1000),
#     Plot('rps', u'Vastausta sekunissa', 1),
#     Plot('failed', u'Saapumattomat vastaukset', 1),
# ]

# x_label = u'Samanaikaisten kyselyiden määrä'
# label_fontsize = 12

def get_stats():
    server="palvelin"
    # ports = (8081, 8082, 8083)
    ports = (8081, 8082, 8083)
    concurrencies = (1,)
    request_nums = (10,)

    results = {}
    stats = []
    for p in ports:
        for c in concurrencies:
            for n in request_nums:
                result = boom.run("http://{0}:{1}".format(server, p), n, None, c)
                # stats.append(boom.calc_stats(result, "http://{0}:{1}".format(server, p), n, c))
                stats.append({
                    'server': result.server,
                    'durations': result.all_res,
                    'rps': len(result.all_res) / float(result.total_time),
                    'concurrency': c,
                    'number': n
                })

    df = pd.DataFrame(stats)
    df = df.apply(pd.to_numeric, errors='ignore')
    return df

stats = get_stats()
print stats

# Täytyy muuntaa niin, että yksi duraatio ja yksi serveri per rivi
plot = sns.stripplot(x="server", y="durations", data=stats)
fig = plot.get_figure()
fig.savefig("test.png")

# print(type(stats.iloc[0]['amp']))

# print(stats)

# with open(sys.argv[1], "r") as f:
#     results = f.readlines()

# results = pd.read_json(sys.argv[1])
# print(results)

# results = map(str.strip, results)
# results = map(json.loads, results)

# x = sorted(set([r['concurrency'] for r in results]))
# servers = sorted(set([r['server'] for r in results]))

# path = "img/{0}".format(datetime.now().strftime("%Y-%m-%d_%H%M"))
# os.makedirs(path)

# plt.bar([1, 1, 1], [2, 2 , 2], .02, [1, 0, 1])
# plt.savefig("test.png")
# plt.close()

# for p in plots:
#     legend = []
#     plt.ylabel(p.label, fontsize=label_fontsize)
#     plt.xlabel(x_label, fontsize=label_fontsize)

#     for s in servers:
#         server_results = sorted(filter(lambda r: r['server'] == s, results), key=lambda r: r['concurrency'])
#         y = [r[p.id] * p.y_factor for r in server_results]
#         # plt.plot(x, y)
#         plt.semilogx(x, y)
#         legend.append(s)

#     plt.legend(legend, loc='best')
#     plt.savefig("{0}/{1}.png".format(path, p.id))
#     plt.close()