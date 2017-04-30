#!/usr/bin/python
# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use('Agg')

import os
import sys
import json
import re
import time
import spur

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from collections import namedtuple
from datetime import datetime

from boom import boom

server="palvelin"
ports = ( 8083, 8081, 8082 )
concurrencies = (1, 10, 100)
n = 100

shell = spur.SshShell(
    hostname=server,
    username="tester",
    password="qwertyuiop",
    missing_host_key=spur.ssh.MissingHostKey.accept,
)

def run_stats(filesize):
    stats = []
    duration_stats = []

    for p in ports:
        # raw_input("Going to bench port {0}. Press Enter to continue...".format(p))
        try:
            print("Benching port {0}...".format(p))
            logger = shell.spawn(["/home/tester/{0}.sh".format(p), filesize],  store_pid=True)

            time.sleep(5)

            for c in concurrencies:
                result = boom.run("http://{0}:{1}/{2}.html".format(server, p, filesize), n, None, c)
                stats.append(boom.calc_stats(result, n, c))
                duration_stats += [
                    {
                        'server': result.server,
                        'duration': d,
                        'concurrency': c,
                    }
                    for d in result.all_res
                ]

            time.sleep(1)

        finally:
            logger.send_signal(9)

    print("Done benching.")

    df1 = pd.DataFrame(stats)
    df2 = pd.DataFrame(duration_stats)
    return df1, df2

def plot_stats(data, fig_path, title=None):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    bar = sns.barplot(
        x="server",
        y="rps",
        hue="concurrency",
        data=data,
    )

    ax.set_xlabel('Palvelinohjelman  nimi')
    ax.set_ylabel('Vastausta sekunissa')

    if title:
        ax.set_title(title)

    fig.savefig(fig_path)

def plot_durations(data, fig_path, title=None):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    swarm = sns.swarmplot(
        x="server",
        y="duration",
        hue="concurrency",
        data=data,
        size=4,
    )

    ax.set_xlabel('Palvelinohjelman  nimi')
    ax.set_ylabel('Vastausaika (s)')

    if title:
        ax.set_title(title)

    fig.savefig(fig_path)

def plot_usage(data, fig_path):
    fig = plt.figure()

    ax1 = fig.add_subplot(121)
    bar1 = sns.barplot(
        x="server",
        y="cpu",
        data=data
    )

    for item in bar1.get_xticklabels():
        item.set_rotation(20)

    ax1.set_xlabel('Palvelinohjelman  nimi')
    ax1.set_ylabel(u'Prosessorin käyttö (%)')

    ax2 = fig.add_subplot(122)

    bar2 = sns.barplot(
        x="server",
        y="mem",
        data=data
    )

    for item in bar2.get_xticklabels():
        item.set_rotation(20)

    ax2.set_xlabel('Palvelinohjelman  nimi')
    ax2.set_ylabel(u'Muistin käyttö (%)')

    fig.savefig(fig_path)

# stats4k, durations4k = run_stats('4k')
# stats72k, durations72k = run_stats('72k')

# plot_stats(stats4k, 'run_4k_stats.png')
# plot_stats(stats72k, 'run_72k_stats.png')

# plot_durations(durations4k, 'run_4k_durations.png')
# plot_durations(durations72k, 'run_72k_durations.png')

# usage_data = pd.read_json('cpu_mem.json')
# plot_usage(usage_data, 'run_72k_usage.png')