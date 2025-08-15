#!/var/tmp/trex-root/trex/trex-env/bin/python3.9
import sys
sys.path.append('/var/tmp/trex-root/v3.06/automation/trex_control_plane/interactive')
sys.path.append('/var/tmp/trex-root/v3.06/scripts')
sys.path.append('/var/tmp/trex-root/v3.06/automation/trex_control_plane/interactive/trex_stl_lib')
from trex_stl_lib.api import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, UDP
import csv
import time

class STLUdpProfile:
    def get_streams(self, **kwargs):
        base_mac = "10:70:fd:23:2b:59"
        src_ip = "10.25.2.2"
        dst_ip = "10.25.0.1"
        base_sport = 4501
        base_dport = 5201
        payload_size = 1420
        nflows = 1
        tp = 30.0e9
        # duration = 20
        # duration = kwargs.get("duration", duration)

        streams = []
        for i in range(nflows):
            sport = base_sport + i + 1
            dport = base_dport + i + 1
            pkt = Ether(dst=base_mac) / IP(src=src_ip, dst=dst_ip) / UDP(sport=sport, dport=dport)
            pad_len = payload_size - len(bytes(pkt))
            if pad_len < 0:
                raise ValueError("Packet too large")
            full_pkt = pkt / (b'X' * pad_len)
            pps = tp / nflows / (payload_size * 8)
            stream = STLStream(
                name=f"udp_stream_{i+1}",
                packet=STLPktBuilder(pkt=full_pkt),
                mode=STLTXCont(pps=pps)
            )
            streams.append(stream)

        return streams

def register():
    return STLUdpProfile()

if __name__ == '__main__':
#    from trex_stl_lib.stlapi import STLClient

    client = STLClient()
    client.connect()
    client.reset()

    profile = STLUdpProfile()

    csv_file = 'udp_test_stats.csv'
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["#<Flows>", "Run_1", "Run_2", "Run_3", "Run_4", "Run_5", "Avg"])

        flow_stats = []
        for run in range(5):
            client.reset()
            client.add_streams(profile.get_streams())
            client.start(ports=[0], force=True)
            client.wait_on_traffic(ports=[0])
            stats = client.get_stats()

            tx_bps = stats[0]['tx_bps']
            rx_bps = stats[0]['rx_bps']
            loss = (tx_bps - rx_bps) / tx_bps if tx_bps > 0 else 0
            gbps = rx_bps / 1e9
            flow_stats.append(gbps)
            print(f"Run {run+1}: {gbps:.2f} Gbps, Loss: {loss:.2%}")

        avg_gbps = sum(flow_stats) / len(flow_stats)
        writer.writerow(["Flows"] + [f"{s:.2f}" for s in flow_stats] + [f"{avg_gbps:.2f}"])
        print(f"Average Throughput: {avg_gbps:.2f} Gbps")

    client.disconnect()

