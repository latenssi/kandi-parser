#!/bin/bash

sudo service apache2 start
sudo service lighttpd stop
sudo service nginx stop

while true; do (echo "%CPU %MEM ARGS $(date)" && ps -C apache2 -o pcpu,pmem,args --sort=pcpu ) >> /tmp/apache_"$1".log; sleep 1; done
