#!/bin/bash

sudo service apache2 stop
sudo service lighttpd start
sudo service nginx stop

while true; do (echo "%CPU %MEM ARGS $(date)" && ps -C lighttpd -o pcpu,pmem,args --sort=pcpu) >> /tmp/lighttpd_"$1".log; sleep 1; done
