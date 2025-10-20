#!/bin/bash
: ${SUBDIR=results/20251017-ports/bulk-xfrm}
mkdir -p $SUBDIR
./u1.py --pps 3M --frame-size 128 --src-port 5000 --src-ports 1 --duration 30 --csvfile $SUBDIR/flows-1
./u1.py --pps 3M --frame-size 128 --src-port 5000 --src-ports 2 --duration 30 --csvfile $SUBDIR/flows-2
./u1.py --pps 3M --frame-size 128 --src-port 5000 --src-ports 4 --duration 30 --csvfile $SUBDIR/flows-4
./u1.py --pps 3M --frame-size 128 --src-port 5000 --src-ports 8 --duration 30 --csvfile $SUBDIR/flows-8
./u1.py --pps 3M --frame-size 128 --src-port 5000 --src-ports 16 --duration 30 --csvfile $SUBDIR/flows-16
./u1.py --pps 3M --frame-size 128 --src-port 5000 --src-ports 32 --duration 30 --csvfile $SUBDIR/flows-32
./u1.py --pps 3M --frame-size 128 --src-port 5000 --src-ports 64 --duration 30 --csvfile $SUBDIR/flows-64
./u1.py --pps 3M --frame-size 128 --src-port 5000 --src-ports 128 --duration 30 --csvfile $SUBDIR/flows-128
./u1.py --pps 3M --frame-size 128 --src-port 5000 --src-ports 256 --duration 30 --csvfile $SUBDIR/flows-256
./u1.py --pps 3M --frame-size 128 --src-port 5000 --src-ports 512 --duration 30 --csvfile $SUBDIR/flows-512
./u1.py --pps 3M --frame-size 128 --src-port 5000 --src-ports 1024 --duration 30 --csvfile $SUBDIR/flows-1024
./u1.py --pps 3M --frame-size 128 --src-port 5000 --src-ports 2048 --duration 30 --csvfile $SUBDIR/flows-2048
./u1.py --pps 3M --frame-size 128 --src-port 5000 --src-ports 4096 --duration 30 --csvfile $SUBDIR/flows-4096
./u1.py --pps 3M --frame-size 128 --src-port 5000 --src-ports 8192 --duration 30 --csvfile $SUBDIR/flows-8192
./u1.py --pps 3M --frame-size 128 --src-port 5000 --src-ports 16384 --duration 30 --csvfile $SUBDIR/flows-16384
