#!/bin/bash

sudo service apache2 stop
sudo service lighttpd stop
sudo service nginx start

while true; do (echo "%CPU %MEM ARGS $(date)" && ps -C nginx -o pcpu,pmem,args --sort=pcpu) >> /tmp/nginx_"$1".log; sleep 1; done
