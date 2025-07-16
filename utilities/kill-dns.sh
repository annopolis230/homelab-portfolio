#!/bin/bash

PIDS=$(lsof -i :53 -t 2>/dev/null)

for PID in $PIDS; do
    kill $PID && echo "Killed $PID"
done