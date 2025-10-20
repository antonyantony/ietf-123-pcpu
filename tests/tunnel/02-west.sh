#!/bin/bash

sudo ip xfrm policy add src 192.1.10.0/24 dst 192.1.20.0/24 dir out \
    tmpl src 192.1.2.45 dst 192.1.2.23 \
    proto esp reqid 0xe1b41853 mode tunnel
sudo ip xfrm policy add src 192.1.20.0/24 dst 192.1.10.0/24 dir fwd \
    tmpl src 192.1.2.23 dst 192.1.2.45 \
    proto esp reqid 0xe1b41853 mode tunnel
sudo ip xfrm policy add src 192.1.20.0/24 dst 192.1.10.0/24 dir in \
    tmpl src 192.1.2.23 dst 192.1.2.45 \
    proto esp reqid 0xe1b41853 mode tunnel
