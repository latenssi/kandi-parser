#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
import matplotlib
matplotlib.use('Agg')

import os
import sys
import json
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import namedtuple

Plot = namedtuple('Plot', ['id', 'label', 'y_factor'])

plots = [
    Plot('avg', u'Keskimääräinen viive (ms)', 1000),
    Plot('max', u'Suurin viive (ms)', 1000),
    Plot('min', u'Pienin viive (ms)', 1000),
    Plot('rps', u'Vastausta sekunissa', 1),
    Plot('failed', u'Saapumattomat vastaukset', 1),
]

x_label = u'Samanaikaisten kyselyiden määrä'
label_fontsize = 12

with open(sys.argv[1], "r") as f:
    results = f.readlines()

results = map(str.strip, results)
results = map(json.loads, results)

x = sorted(set([r['concurrency'] for r in results]))
servers = sorted(set([r['server'] for r in results]))

path = "img/{0}".format(datetime.now().strftime("%Y-%m-%d_%H%M"))
os.makedirs(path)

for p in plots:
    legend = []
    plt.ylabel(p.label, fontsize=label_fontsize)
    plt.xlabel(x_label, fontsize=label_fontsize)

    for s in servers:
        server_results = sorted(filter(lambda r: r['server'] == s, results), key=lambda r: r['concurrency'])
        y = [r[p.id] * p.y_factor for r in server_results]
        # plt.plot(x, y)
        plt.semilogx(x, y)
        legend.append(s)

    plt.legend(legend, loc='best')
    plt.savefig("{0}/{1}.png".format(path, p.id))
    plt.close()