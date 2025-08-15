#!/bin/bash

make -j$(nproc)
cp ./tcp_stream /output
