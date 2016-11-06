#!/bin/bash

port=$1
echo $port
python tcp_server.py $port
