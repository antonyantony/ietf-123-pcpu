# TRex Testing
TRex v3.06, as of July of 2025, requires an older Python (3.8-3.9) than what is shipped in Ubuntu 25.04. TRex on Mellanox NICs needs DOCA-OFED installed. See the end for DOCA-OFED details.

## Install TRex v3.06 with Python3.9
TRex has two parts: server and user scripts. Initially, I am running stateless user scripts. We can run one script at a time. TRex probably can do more. I am doing basic.


## Start TRex server
Start the server once and leave it running inside a screen session. You can access it vis "screen -x". The server should be started in Python 3.9 venv.

## Login to sunset and start Python 3.9 venv

cd /root; source ./venv/bin/activate

To verify: type python3.9; python3.9 is hashed (/root/venv/bin/python3.9)

I usually start "screen bash" in this virtual environment. Inside the screen, start the TRex server.

## Start the TRex server
./t-rex-64 -i --no-scapy --cfg /etc/trex_cfg.yaml -c 8

It will take a few seconds, and this will run in the foreground.

## Run TRex script

cd /root/ietf-123-pcpu/tests-trex;
./u1.py --src-ip 192.0.1.253 --dst-ip 192.0.2.253 --pps 1M --frame-size 1518 --flows 2 --duration 10 --flows-end 2 --runs 2

u1.py is my script. A simple UDP send and collect results in JSON. Then I use panda plots to generate plots.

## Mellanox NICs -- install DOCA-OFED from Mellanox
run mst start once.
 mst status --v
MST modules:
------------
    MST PCI module is not loaded
    MST PCI configuration module loaded
    -E- Unknown argument "--v"
root@sunset:~/ietf-123-pcpu/tests-trex# mst status -v
MST modules:
------------
    MST PCI module is not loaded
    MST PCI configuration module loaded
PCI devices:
------------
DEVICE_TYPE             MST                           PCI       RDMA            NET                                     NUMA
ConnectX5(rev:0)        /dev/mst/mt4121_pciconf0.1    01:00.1   mlx5_1          net-redwest                             0

ConnectX5(rev:0)        /dev/mst/mt4121_pciconf0      01:00.0   mlx5_0          net-redeast                             0


root@sunset:~/ietf-123-pcpu/tests-trex# mst --help
Usage:
    /usr/bin/mst {start|stop|status|remote|server|restart|save|load|rm|add|help|version|gearbox|cable}

Type "/usr/bin/mst help" for detailed help

