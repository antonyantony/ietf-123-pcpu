#!/root/venv/bin/python3.9
import sys
import json
import csv
import time
import ipaddress
import asyncio
import yaml
from interface_diag import InterfaceDiagnostics

sys.path.append('/var/tmp/trex-v3.06/automation/trex_control_plane/interactive')
sys.path.append('/var/tmp/trex-v3.06/scripts')
sys.path.append('/var/tmp/trex-v3.06/automation/trex_control_plane/interactive/trex_stl_lib')

from types import SimpleNamespace

import argparse
from trex.stl.api import (
    STLClient, STLStream, STLTXCont, STLPktBuilder, STLTXSingleBurst,
    STLScVmRaw, STLVmFlowVar, STLVmWrFlowVar, STLVmFixIpv4, STLVmFixChecksumHw
)
from scapy.all import Ether, IP, IPv6, UDP

def is_ipv4_address(ip):
    try:
        return isinstance(ipaddress.ip_address(ip), ipaddress.IPv4Address)
    except ValueError:
        return False

def is_ipv6_address(ip):
    try:
        return isinstance(ipaddress.ip_address(ip), ipaddress.IPv6Address)
    except ValueError:
        return False

def int_mac_low(macstr):
    # Returns integer value of lower 4 bytes
    return int(macstr.replace(":", "")[-8:], 16)


def create_pkt_udp_with_vm(src_mac, dst_mac, start_ip, src_ip_count, dst_ip, dst_ip_count, frame_size,
                       src_port, src_port_count, dst_port, dst_port_count, l4_proto="UDP"):
    '''
    Create a UDP packet with Scapy and TRex VM instructions to vary fields.
    Supports source and destination IP and port ranges.
    When src ip changes the src mac changes too.
    '''

    ip_ver = ipaddress.ip_address(start_ip).version
    min_mac_low = int_mac_low(src_mac)
    max_mac_low = min_mac_low + src_ip_count - 1
    l4_offset = 34 if ip_ver == 4 else 54
    l3_offset = 14  # Ethernet header size
    UDP_PROTO = 17  # UDP protocol number

    vm_instr = [
       STLVmFlowVar(name="src_mac_low", min_value=min_mac_low, max_value=max_mac_low, size=4, op="inc"),
       STLVmWrFlowVar(fv_name="src_mac_low", pkt_offset=8), # 8 because src MAC 6 + 2. increment lower 4 bytes

       STLVmFlowVar(name="src_port", min_value=src_port, max_value=src_port + src_port_count - 1, size=2, op="inc"),
       STLVmWrFlowVar(fv_name="src_port", pkt_offset="UDP.sport"),

       STLVmFlowVar(name="dst_port", min_value=dst_port, max_value=dst_port + dst_port_count - 1, size=2, op="inc"),
       STLVmWrFlowVar(fv_name="dst_port", pkt_offset="UDP.dport"),
       STLVmFixChecksumHw(l3_offset = l3_offset, l4_offset=l4_offset, l4_type=UDP_PROTO)

       ]

    if ip_ver == 4:
        vm_instr += [
            STLVmFlowVar(name="src_ipv4", min_value=int(ipaddress.IPv4Address(start_ip)),
                         max_value=int(ipaddress.IPv4Address(start_ip)) + src_ip_count - 1, size=4, op="inc"),
            STLVmWrFlowVar(fv_name="src_ipv4", pkt_offset="IP.src"),
            STLVmFlowVar(name="dst_ipv4", min_value=int(ipaddress.IPv4Address(dst_ip)),
                         max_value=int(ipaddress.IPv4Address(dst_ip)) + dst_ip_count - 1, size=4, op="inc"),
            STLVmWrFlowVar(fv_name="dst_ipv4", pkt_offset="IP.dst"),
            STLVmFixIpv4(offset="IP")
        ]
    else:
        vm_instr += [
            STLVmFlowVar(name="src_ipv6", min_value=int(ipaddress.IPv6Address(start_ip)),
                         max_value=int(ipaddress.IPv6Address(start_ip)) + src_ip_count - 1, size=16, op="inc"),
            STLVmWrFlowVar(fv_name="src_ipv6", pkt_offset="IPv6.src"),
            STLVmFlowVar(name="dst_ipv6", min_value=int(ipaddress.IPv6Address(dst_ip)),
                         max_value=int(ipaddress.IPv6Address(dst_ip)) + dst_ip_count - 1, size=16, op="inc"),
            STLVmWrFlowVar(fv_name="dst_ipv6", pkt_offset="IPv6.dst"),
        ]

    # this is the base packet, Scapy will build it and change fields via VM in STLPktBuilder.
    base_pkt = Ether(src=src_mac, dst=dst_mac) / (
                IP(src=start_ip, dst=dst_ip) if ip_ver == 4 else IPv6(src=start_ip, dst=dst_ip)
                ) / UDP(dport=dst_port, sport=src_port)

    vm = STLScVmRaw(vm_instr)
    pkt_len = len(base_pkt)
    pad = b'\0' * (frame_size - pkt_len) if pkt_len < frame_size else b''

    pkt = STLPktBuilder(pkt=base_pkt/pad, vm=vm)
    return pkt


def create_pkt_udp(src_mac, dst_mac, src_ip, dst_ip, frame_size, src_port, dst_port):

    if is_ipv6_address(src_ip) or is_ipv6_address(dst_ip):
        ip_layer = IPv6(src=src_ip, dst=dst_ip)
    elif is_ipv4_address(src_ip) or is_ipv4_address(dst_ip):
        ip_layer = IP(src=src_ip, dst=dst_ip)
    else:
        raise ValueError("Invalid IP address format")

    pkt_base = Ether(src=src_mac, dst=dst_mac)/ip_layer/UDP(dport=dst_port, sport=src_port)
    pkt_len = len(pkt_base)
    pad = b'\0' * (frame_size - pkt_len) if pkt_len < frame_size else b''

    return STLPktBuilder(pkt=pkt_base/pad)

def bits_to_gibps(bits_per_sec):
    return bits_per_sec / (1024**3)  # bits to GiB/sec

def run_priming(args, st, n=1, delay_ms=100):
    """
    Priming run to establish SA and avoid initial packet loss.
    Sends streams one by one.
    The first stream is sent twice.
    Delay (in milliseconds) between streams.
    """
    c = STLClient(server=args.server)
    try:
        c.connect()
        c.reset(ports=[0, 1])
        c.clear_stats()

        for flow_id in range(st.flows):
            src_port = args.src_port + flow_id
            pkt = create_pkt_udp(args.src_mac, args.dst_mac, args.src_ip,
                             args.dst_ip, st.frame_size, src_port,
                             args.dst_port)


            stream = STLStream(packet=pkt, mode=STLTXSingleBurst(total_pkts=n))

            # Add only current stream
            c.add_streams([stream], ports=[0])

            # Send first stream twice, others once; Jacob Two Two to get Fallback SA and per cpu SA
            send_times = 2 if flow_id == 0 else 1

            for i in range(send_times):
                c.start(ports=[0], mult="1")  # start sending current stream
                c.wait_on_traffic(ports=[0])  # wait until done
                # Wait delay between streams in seconds
                time.sleep(delay_ms / 1000.0)


                # Optionally clear stats after each send if desired
                # c.clear_stats()

            # Remove current stream before next loop iteration
            # Reset the client to clear streams on port 0
            c.reset(ports=[0, 1])

            # Wait delay between streams in seconds
            time.sleep(delay_ms / 1000.0)

    finally:
        c.disconnect()

def run_priming_delay(args, st):
    run_priming(args, st, n=1, delay_ms=100)
    # time.sleep(1)
    run_priming(args, st, n=1, delay_ms=100)

def run_test(args, st):
    c = STLClient(server=args.server)
    try:
        c.connect()
        c.reset(ports=[0, 1])
        c.clear_stats()

        streams = []

        for flow_id in range(st.flows):
            src_port = args.src_port + flow_id
            pkt = create_pkt_udp_with_vm(args.src_mac, args.dst_mac,
                       args.src_ip, args.src_ips,
                       args.dst_ip, args.dst_ips, st.frame_size, src_port, args.src_ports,
                       args.dst_port, args.dst_ports)

            stream = STLStream(packet=pkt, mode=STLTXCont(pps=st.pps))
            streams.append(stream)

        c.add_streams(streams, ports=[0])
        start_time = time.time()  # Record start

        c.start(ports=[0], mult="1", duration=args.duration)
        c.wait_on_traffic(ports=[0])  # wait on TX port until done (adjust if needed)
        end_time = time.time()  # Record end
        elapsed = end_time - start_time
        deviation = elapsed - args.duration

        if abs(deviation) > 0.2:
            runtime_deviation = deviation
        else:
            runtime_deviation = 0   # or "within tolerance"

        stats_ports = c.get_stats()
        stats_tx = stats_ports[0]
        stats_rx = stats_ports[1]

        #print("Port 0 stats:", stats_ports[0])
        #print("Port 1 stats:", stats_ports[1])

        # Gather stats per run, convert bps to GiB/s
        result = {
            "tx_pps": stats_tx.get("tx_pps", 0),
            "tx_bps": stats_tx.get("tx_bps", 0),
            "tx_throughput_gibps": bits_to_gibps(stats_tx.get("tx_bps_L1", 0)),
            "tx_errors": stats_tx.get("tx_err", 0),
            "tx_opackets": stats_tx.get("opackets", 0),
            "tx_obytes": stats_tx.get("obytes", 0),
            "tx_ipackets": stats_tx.get("ipackets", 0),
            "tx_ibytes": stats_tx.get("ibytes", 0),

            "rx_pps": stats_rx.get("rx_pps", 0),
            "rx_bps": stats_rx.get("rx_bps", 0),
            "rx_throughput_gibps": bits_to_gibps(stats_rx.get("rx_bps_L1", 0)),
            "rx_ipackets": stats_rx.get("ipackets", 0),
            "rx_ibytes": stats_rx.get("ibytes", 0),
            "rx_opackets": stats_rx.get("opackets", 0),
            "rx_obytes": stats_rx.get("obytes", 0),
            "rx_drops": stats_rx.get("rx_drops", 0),
            "l_pkts": stats_tx.get("opackets", 0) -  stats_rx.get("ipackets", 0),
            "l_bytes": stats_tx.get("obytes", 0) - stats_rx.get("ibytes", 0),
            "l_pkts_percent": ((stats_tx.get("opackets", 0) -  stats_rx.get("ipackets", 0))/stats_tx.get("opackets", 0)) * 100,
            "src_ips": args.src_ips,
            "dst_ips": args.dst_ips,
            "src_ports": args.src_ports,
            "dst_ports": args.dst_ports,
            "elapsed_runtime":  elapsed,
            "duration": args.duration,
            "runtime_deviation": runtime_deviation
        }

        stats = c.get_stats()
        global_stats = stats.get('global', {})
        cpu_usage = global_stats.get('cpu_util', None)

        if cpu_usage is not None:
            num_cpus = os.cpu_count()  # system cores count, for reference only

            # 'cpu_usage' is already a total/average CPU usage (percentage)
            avg_load = cpu_usage

            # print(f"Average CPU use per core (overall): {avg_load:.2f}% Number of CPUs on system: {num_cpus}")

            result.update({
                "cpu_load_total": cpu_usage,
                "cpu_load_avg": avg_load,
                "num_cpus": num_cpus
            })
        print (f"rx {result['rx_throughput_gibps']:.2f} Gbps loss {result['l_pkts_percent']:.2f} %", end="")
        print (f' transmission took {elapsed:.2f} seconds')
    finally:
        c.disconnect()

    return result

async def run_tests (args, st):
    all_runs_results = []  # To hold dicts per run

    # Run all test runs and collect results
    for run_id in range(1, args.runs + 1):
        print(f" run {run_id}/{args.runs} ",  end="")
        if not args.no_priming:
            run_priming_delay(args, st)
        if args.interface_stats:
            diag = InterfaceDiagnostics()
            await diag.collect_data(phase="start")

        run_result = run_test(args, st)

        if args.interface_stats:
            await diag.collect_data(phase="end")
            diag.compute_stats_diff()
            stats = diag.export_stats_rooted()
        else:
            stats = {}

        run_result.update({
            "frame_size": st.frame_size,
            "tx_pps_req": st.pps_req,
            "tx_pps_per_flow": st.pps,
            "tx_flow_throughput": args.throughput,
            "flows":  st.flows,
            "flows_start": args.flows_start,
            "flows_end": args.flows_end,
            "run": run_id,
            "runs": args.runs,
            "stats" : stats
            })
        all_runs_results.append(run_result)

    return all_runs_results

def compute_pps(args, frame_size):
    """
    Compute Ethernet PPS from throughput (bps) and IP packet size (bytes).
    This accounts for
    Ethernet Frame is IP packet + Ethernet overhead
    Ethernet header: header 14 bytes: (6 bytes destination MAC + 6 bytes source MAC + 2 bytes EtherType)

    Ethernet Overhead
        # Frame Check Sequence (FCS) 4 bytes: bytes CRC at the end

        preamble 7 bytes
        Start Frame Delimiter (SFD) 1 Byte
        Inter-frame gap (IFG): 12 bytes — a gap time between frames, treated as overhead on the wire
        = 20 bytes total.

    https://www.intel.com/content/www/us/en/docs/programmable/683338/22-1/performance-and-fmax-requirements-for.html
    Args:
        args: object with attribute 'throughput', throughput string parsed by parse_rate_value()
        frame_size: int, IP packet payload size in bytes (e.g., 1500 for full MTU)

    Returns:
        int: Packets per second (PPS) that fit in the given throughput with Ethernet overhead considered.
    """

    bps = parse_rate_value(args.throughput, "throughput")

    ethernet_overhead_bytes = 20
    frame_size_total = frame_size + ethernet_overhead_bytes

    bits_per_packet = frame_size_total * 8

    pps = int(bps / bits_per_packet)

    return pps

def parse_rate_value(s, option):
    """
    Parse a rate string with optional binary unit suffix into an integer value.
    K = 1 x 10^3, M = 1 x 10^6, G = 1 x 10^9

Assumptions:
    Link rate = 100 Gbps = 100,000,000,000 bits per second (decimal standard)

    Ethernet + physical overhead = 38 bytes total
    (Ethernet header 14 + FCS 4 + Preamble + SFD 8 + Inter-frame gap (IFG) 12)
    PPS calculated by dividing link rate by total bits per packet
    (IP packet size + 38 overhead bytes) × 8 (bits/byte)

    """

    if s is None:
        return 0

    s = s.strip().upper()

    try:
        if s.endswith('G'):
            num = float(s[:-1])
            return int(num * (10**9))
        elif s.endswith('M'):
            num = float(s[:-1])
            return int(num * (10**6))
        elif s.endswith('K'):
            num = float(s[:-1])
            return int(num * (10**3))
        else:
            # Assume raw integer rate (bps or pps)
            return int(s)
    except ValueError:
        raise ValueError(
            f"Invalid {option} value: '{s}'. "
            "Must be a number with optional G/M/K suffix."
        )

def run_test_frame_sizes(args, pps):
    all_results_frame_size = []  # To hold dicts all frame sizes results
    for frame_size in args.frame_sizes: #loop over --frame-sizes array

        if args.throughput:
            pps = compute_pps(args, frame_size)

        st = SimpleNamespace(pps=pps, pps_req = pps, frame_size=frame_size, flows=1, run=1)

        for flows in range(args.flows_start, args.flows_end + 1): # loop over flows
            st.flows = flows
            st.pps = pps/flows

            print(f"Setting flows {st.flows}/{args.flows_end} pps {st.pps:.2f}/{pps:.2f} per flow throughput {args.throughput} and frame-size {st.frame_size} runs {args.runs} duration {args.duration} sec")
            test_results = asyncio.run(run_tests(args, st))
            all_results_frame_size.extend(test_results)

            write_json(args.csvfile, all_results_frame_size)

    return all_results_frame_size

def write_json(csv_filename, all_results):

    base, ext = os.path.splitext(csv_filename)
    if ext.lower() == '.csv':
        json_filename = base + '.json'
    else:
        json_filename = csv_filename + '.json'

    # Dump JSON results to file
    with open(json_filename, 'w') as f:
        print(f"\nAll runs aggregated result as JSON: {json_filename}")
        json.dump(all_results, f, indent=2)

class Def:
  frame_sizes = [1440]
  pps = ["10K"]

class Def_v6:
  frame_sizes = [1440]
  pps = ["10K"]
  src_ip = "2001:db8:0:1::254"
  dst_ip = "2001:db8:0:2::254"

if __name__ == "__main__":

    d = Def()

    parser = argparse.ArgumentParser()
    parser.add_argument("--server", type=str, default="127.0.0.1")
    parser.add_argument("--dst-ip", type=str, default="192.0.2.253")
    parser.add_argument("--dst-ips", type=int, default=1)
    parser.add_argument("--src-ips", type=int, default=1)
    parser.add_argument("--src-ip", type=str, default="192.0.1.1")
    parser.add_argument("--dst-mac", type=str, default="10:70:fd:2f:b1:a1")
    parser.add_argument("--src-mac", type=str, default="1c:42:a1:f7:bf:c7")
    parser.add_argument("--src-port", type=int, default=4501)
    parser.add_argument("--src-ports", type=int, default=1)
    parser.add_argument("--dst-ports", type=int, default=1)
    parser.add_argument("--dst-port", type=int, default=5201)
    parser.add_argument("--flows-start", "--flows", type=int, default=1, help="Number of UDP flows to generate start")
    parser.add_argument("--flows-end", type=int, default=1, help="Number of UDP flows to generate end ")
    parser.add_argument("--frame-sizes", type=int, action='append', default=[],
                        help="Specify frame size in bytes; can be used multiple times. Default is 1440 bytes L1 1518 - IPsec.")
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--csvfile", type=str, default="trex_results.csv")
    parser.add_argument('--no-priming', action='store_true',
                        help='Disable priming', default=False)
    parser.add_argument('--interface-stats', action='store_true',
                        help='Collect interface diagnostics before and after each run', default=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--pps", type=str, action='append', default=None, help="Packets per second")
    group.add_argument("--throughput", "--tp", type=str,
                       default=None,
                       help="Target throughput with optional units: G for Gbps, M for Mbps, or bps if no unit, e.g., 10G, 500M, 10. ")

    # Two-pass parse: load --config first, then let CLI args override
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument('--config', type=str, default=None,
                            help='Path to YAML config file')
    pre_args, _ = pre_parser.parse_known_args()

    if pre_args.config:
        with open(pre_args.config) as f:
            config = yaml.safe_load(f) or {}
        # Translate positive 'priming' to argparse's 'no_priming'
        if 'priming' in config:
            config['no-priming'] = not config.pop('priming')
        # Validate config keys against known parser arguments
        valid_keys = {a.dest for a in parser._actions} | {'config'}
        unknown = {k for k in config if k.replace('-', '_') not in valid_keys}
        if unknown:
            parser.error(f"Unknown config file keys: {', '.join(sorted(unknown))}")
        parser.set_defaults(**{k.replace('-', '_'): v for k, v in config.items()})

    parser.add_argument('--config', type=str, default=None,
                        help='Path to YAML config file')
    args = parser.parse_args()
    all_results = []  # To hold dicts per run
    if args.flows_end <= args.flows_start:
        args.flows_end = args.flows_start

    if not args.frame_sizes :
        args.frame_sizes = d.frame_sizes

    if not args.throughput:
        if not args.pps:
            args.pps = d.pps

        for ppss in args.pps: #loop over --pps array
            pps = parse_rate_value(ppss, "pps")
            test_results = run_test_frame_sizes(args, pps)
            all_results.extend(test_results)
            write_json(args.csvfile, all_results)
