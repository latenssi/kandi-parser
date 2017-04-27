FROM ubuntu:14.04

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    ca-certificates unzip wget libtool autoconf automake make && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /usr/src

RUN wget https://github.com/httperf/httperf/archive/master.zip && \
    unzip master.zip

WORKDIR /usr/src/httperf-master

RUN mkdir build && \
    autoreconf -i && \
    ./configure && \
    make && \
    make install

WORKDIR /