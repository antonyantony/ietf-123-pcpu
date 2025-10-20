from trex_stl_lib.api import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, UDP

class STLUdpProfile:
    def get_streams(self, **kwargs):
        base_mac = "10:70:fd:23:2b:59"
        src_ip = "10.25.2.2"
        dst_ip = "10.25.0.1"
        base_sport = 4501
        base_dport = 5201
        payload_size = 1420
        nflows = 3
        tp = 30.0e9

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

