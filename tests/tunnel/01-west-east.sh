#!/bin/bash

sudo ip xfrm state add src 192.1.2.45 dst 192.1.2.23 \
    proto esp spi 0xe1b41853 \
    reqid 0xe1b41853 \
    mode tunnel \
    aead 'rfc4106(gcm(aes))' 0x5aafd8bd3f819c90a42f67e323b1e5b13d5ff08b 128
sudo ip xfrm state add src 192.1.2.23 dst 192.1.2.45 \
    proto esp spi 0xe1b41853 \
    reqid 0xe1b41853 \
    mode tunnel \
    aead 'rfc4106(gcm(aes))' 0x5aafd8bd3f819c90a42f67e323b1e5b13d5ff08b 128
