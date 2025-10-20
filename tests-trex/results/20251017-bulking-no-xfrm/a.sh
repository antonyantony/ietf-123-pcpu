#!/bin/bash
SUBDIR=results/20251017-bulking-no-xfrm
mkdir -p $SUBDIR
./u1.py --pps 16M --flows-end 15 --frame-size 128 --duration 30 --csvfile $SUBDIR/both-bulk
./u1.py --pps 16M --flows-end 15 --frame-size 128 --duration 30 --csvfile $SUBDIR/sender-bulk
./u1.py --pps 16M --flows-end 15 --frame-size 128 --duration 30 --csvfile $SUBDIR/receiver-bulk
./u1.py --pps 16M --flows-end 15 --frame-size 128 --duration 30 --csvfile $SUBDIR/no-bulk
