#!/bin/bash
: ${SUBDIR=results/20251017-bulking-no-xfrm}
mkdir -p $SUBDIR
./u1.py --pps 16M --flows-end 10 --frame-size 128 --duration 30 --csvfile $SUBDIR/both-bulk-1
./u1.py --pps 25M --flows-start 11 --flows-end 15 --frame-size 128 --duration 30 --csvfile $SUBDIR/both-bulk-2
./u1.py --pps 16M --flows-end 15 --frame-size 128 --duration 30 --csvfile $SUBDIR/sender-bulk
./u1.py --pps 16M --flows-end 15 --frame-size 128 --duration 30 --csvfile $SUBDIR/receiver-bulk
./u1.py --pps 16M --flows-end 15 --frame-size 128 --duration 30 --csvfile $SUBDIR/no-bulk
