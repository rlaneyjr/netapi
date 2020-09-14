import pytest
import re
import netapi.probe as probe
from netapi.probe.ping import PingBase, PingResult
from netaddr import IPAddress
from pydantic import ValidationError
from textwrap import dedent


MODULE_MAPPING = {
    "EOS-PYEAPI": probe.eos.pyeapier,
    "LINUX-SUBPROCESS": probe.linux.subprocesser,
    "LINUX-PARAMIKO": probe.linux.paramikoer,
    "JUNOS-PYEZ": probe.junos.pyezer,
    "IOS-NETMIKO": probe.ios.netmikoer,
    "XE-NETMIKO": probe.xe.netmikoer,
    "NXOS-NXAPI": probe.nxos.nxapier,
    "XR-NETMIKO": probe.xr.netmikoer,
}
PING_RESULT_ARGS = {
    "ok": {
        "probes_sent": 5,
        "probes_received": 5,
        "packet_loss": 0.0,
        "rtt_min": 164.0,
        "rtt_avg": 165.0,
        "rtt_max": 166.0,
        "warning_thld": None,
        "critical_thld": None,
        "status": "ok",
        "status_code": 0,
        "status_up": True,
        "apply_analysis": False,
    },
    "warning": {
        "probes_sent": 10,
        "probes_received": 5,
        "packet_loss": 0.5,
        "rtt_min": 174.0,
        "rtt_avg": 175.0,
        "rtt_max": 176.0,
        "warning_thld": None,
        "critical_thld": None,
        "status": "warning",
        "status_code": 1,
        "status_up": True,
        "apply_analysis": False,
    },
    "critical": {
        "probes_sent": 5,
        "probes_received": 0,
        "packet_loss": 1.0,
        "rtt_min": None,
        "rtt_avg": None,
        "rtt_max": None,
        "warning_thld": None,
        "critical_thld": None,
        "status": "critical",
        "status_code": 2,
        "status_up": False,
        "apply_analysis": False,
    },
    "custom_thld_critical": {
        "probes_sent": 10,
        "probes_received": 3,
        "packet_loss": 0.7,
        "rtt_min": 2.1,
        "rtt_avg": 2.2,
        "rtt_max": 2.3,
        "warning_thld": None,
        "critical_thld": 65,
        "status": "critical",
        "status_code": 2,
        "status_up": False,
        "apply_analysis": True,
    },
    "custom_thld_warning": {
        "probes_sent": 10,
        "probes_received": 3,
        "packet_loss": 0.7,
        "rtt_min": 2.1,
        "rtt_avg": 2.2,
        "rtt_max": 2.3,
        "warning_thld": 60,
        "critical_thld": 80,
        "status": "warning",
        "status_code": 1,
        "status_up": True,
        "apply_analysis": True,
    },
    "invalid_packet_loss": dict(probes_sent=2, probes_received=0, packet_loss=1.5),
}

PING_RESULT_REPR = {
    "ok": (
        "PingResult(probes_sent=5, probes_received=5, packet_loss=0.0, rtt_min="
        "164.0, rtt_avg=165.0, rtt_max=166.0, warning_thld=None, critical_thld="
        "None, status='ok', status_up=True, status_code=0, apply_analysis=False)"
    ),
    "warning": (
        "PingResult(probes_sent=10, probes_received=5, packet_loss=0.5, rtt_min="
        "174.0, rtt_avg=175.0, rtt_max=176.0, warning_thld=None, critical_thld="
        "None, status='warning', status_up=True, status_code=1, apply_analysis=False)"
    ),
    "critical": (
        "PingResult(probes_sent=5, probes_received=0, packet_loss=1.0, rtt_min="
        "None, rtt_avg=None, rtt_max=None, warning_thld=None, critical_thld="
        "None, status='critical', status_up=False, status_code=2, apply_analysis=False)"
    ),
    "custom_thld_critical": (
        "PingResult(probes_sent=10, probes_received=3, packet_loss=0.7, rtt_min="
        "2.1, rtt_avg=2.2, rtt_max=2.3, warning_thld=None, critical_thld="
        "65, status='critical', status_up=False, status_code=2, apply_analysis=True)"
    ),
    "custom_thld_warning": (
        "PingResult(probes_sent=10, probes_received=3, packet_loss=0.7, rtt_min="
        "2.1, rtt_avg=2.2, rtt_max=2.3, warning_thld=60, critical_thld="
        "80, status='warning', status_up=True, status_code=1, apply_analysis=True)"
    ),
}

PING_BASE_ARGS = {
    "ok": dict(target="10.77.77.1", result=PING_RESULT_ARGS["ok"]),
    "warning": dict(
        target="some.random.test",
        target_ip=IPAddress("10.77.77.7"),
        target_name="some.random.test",
        source=None,
        source_ip="10.0.0.1",
        instance="TEST-INSTANCE",
        count=10,
        timeout=1,
        size=1000,
        df_bit=True,
        interval=0.5,
        ttl=4,
        result=PING_RESULT_ARGS["warning"],
    ),
    "critical": dict(
        target="10.77.77.77",
        source="Vlan177",
        interval=0.5,
        size=777,
        timeout=7,
        count=5,
        df_bit=True,
        instance="LUCKY7",
        ttl=700,
        result=PING_RESULT_ARGS["critical"],
    ),
    "resolve_target": dict(target="localhost", resolve_target=True),
    "invalid_target_ip": dict(target="10.77.77.77", target_ip="10.77.77.77.77"),
    "invalid_source_ip": dict(target="10.77.77.77", source_ip="10.77.77.77.77"),
}
PING_BASE_REPR = {
    "ok": (
        "PingBase(target='10.77.77.1', target_ip=None, target_name="
        "None, resolve_target=False, source=None, source_ip=None, instance=None, "
        "count=5, timeout=2, size=692, df_bit=False, interval=1.0, ttl="
        "None, result=PingResult(probes_sent=5, probes_received=5, packet_loss="
        "0.0, rtt_min=164.0, rtt_avg=165.0, rtt_max=166.0, warning_thld="
        "None, critical_thld=None, status='ok', status_up=True, status_code="
        "0, apply_analysis=False))"
    ),
    "warning": (
        "PingBase(target='some.random.test', target_ip=IPAddress('10.77.77.7')"
        ", target_name='some.random.test', resolve_target=False, source="
        "None, source_ip=IPAddress('10.0.0.1'), instance='TEST-INSTANCE', count="
        "10, timeout=1, size=1000, df_bit=True, interval=0.5, ttl=4, result="
        "PingResult(probes_sent=10, probes_received=5, packet_loss=0.5, rtt_min="
        "174.0, rtt_avg=175.0, rtt_max=176.0, warning_thld=None, critical_thld="
        "None, status='warning', status_up=True, status_code=1, apply_analysis=False))"
    ),
    "critical": (
        "PingBase(target='10.77.77.77', target_ip=None, target_name="
        "None, resolve_target=False, source='Vlan177', source_ip=None, instance"
        "='LUCKY7', count=5, timeout=7, size=777, df_bit=True, interval=0.5, ttl="
        "700, result=PingResult(probes_sent=5, probes_received=0, packet_loss="
        "1.0, rtt_min=None, rtt_avg=None, rtt_max=None, warning_thld="
        "None, critical_thld=None, status='critical', status_up=False, "
        "status_code=2, apply_analysis=False))"
    ),
    "resolve_target": (
        "PingBase(target='localhost', target_ip=IPAddress('127.0.0.1')"
        ", target_name='localhost', resolve_target=True, source=None, source_ip="
        "None, instance=None, count=5, timeout=2, size=692, df_bit=False, interval="
        "1.0, ttl=None, result=None)"
    ),
}
PING_METADATA_REPR = (
    "Metadata(name='ping', type='entity', implementation='<IMPLEMENTATION>', "
    "created_at=<CREATED_AT>, id=<UUID>, updated_at=None, collection_count=0, "
    "parent=None)"
)
PING_BASE_ASDICT = {
    "ok": {
        "target": "10.77.77.1",
        "target_ip": None,
        "target_name": None,
        "resolve_target": False,
        "source": None,
        "source_ip": None,
        "instance": None,
        "count": 5,
        "timeout": 2,
        "size": 692,
        "df_bit": False,
        "interval": 1.0,
        "ttl": None,
        "result": {
            "probes_sent": 5,
            "probes_received": 5,
            "packet_loss": 0.0,
            "rtt_min": 164.0,
            "rtt_avg": 165.0,
            "rtt_max": 166.0,
            "warning_thld": None,
            "critical_thld": None,
            "status": "ok",
            "status_up": True,
            "status_code": 0,
            "apply_analysis": False,
        },
        "metadata": None,
    },
    "warning": {
        "target": "some.random.test",
        "target_ip": "10.77.77.7",
        "target_name": "some.random.test",
        "resolve_target": False,
        "source": None,
        "source_ip": "10.0.0.1",
        "instance": "TEST-INSTANCE",
        "count": 10,
        "timeout": 1,
        "size": 1000,
        "df_bit": True,
        "interval": 0.5,
        "ttl": 4,
        "result": {
            "probes_sent": 10,
            "probes_received": 5,
            "packet_loss": 0.5,
            "rtt_min": 174.0,
            "rtt_avg": 175.0,
            "rtt_max": 176.0,
            "warning_thld": None,
            "critical_thld": None,
            "status": "warning",
            "status_up": True,
            "status_code": 1,
            "apply_analysis": False,
        },
        "metadata": None,
    },
    "critical": {
        "target": "10.77.77.77",
        "target_ip": None,
        "target_name": None,
        "resolve_target": False,
        "source": "Vlan177",
        "source_ip": None,
        "instance": "LUCKY7",
        "count": 5,
        "timeout": 7,
        "size": 777,
        "df_bit": True,
        "interval": 0.5,
        "ttl": 700,
        "result": {
            "probes_sent": 5,
            "probes_received": 0,
            "packet_loss": 1.0,
            "rtt_min": None,
            "rtt_avg": None,
            "rtt_max": None,
            "warning_thld": None,
            "critical_thld": None,
            "status": "critical",
            "status_up": False,
            "status_code": 2,
            "apply_analysis": False,
        },
        "metadata": None,
    },
}
PING_COMMANDS = {
    "ok": {
        "ios": "ping 10.77.77.1 size 692 repeat 5 timeout 2",
        "xe": "ping 10.77.77.1 size 692 repeat 5 timeout 2",
        "xr": "ping 10.77.77.1 size 692 repeat 5 timeout 2",
        "nxos": "ping 10.77.77.1 packet-size 692 count 5 timeout 2 interval 1.0",
        "junos": "ping 10.77.77.1 size 692 count 5 wait 2 interval 1.0",
        "eos": "ping 10.77.77.1 size 692 repeat 5 timeout 2 interval 1.0",
        "linux": "ping 10.77.77.1 -s 692 -c 5 -W 2 -i 1.0",
    },
    "warning": {
        "ios": (
            "ping vrf TEST-INSTANCE some.random.test size 1000 repeat 10 timeout 1 "
            "source 10.0.0.1 df-bit"
        ),
        "xe": (
            "ping vrf TEST-INSTANCE some.random.test size 1000 repeat 10 timeout 1 "
            "source 10.0.0.1 df-bit"
        ),
        "xr": (
            "ping some.random.test vrf TEST-INSTANCE size 1000 repeat 10 timeout 1 "
            "source 10.0.0.1 donotfrag"
        ),
        "nxos": (
            "ping some.random.test vrf TEST-INSTANCE packet-size 1000 count 10 timeout "
            "1 source 10.0.0.1 df-bit interval 0.5"
        ),
        "junos": (
            "ping some.random.test routing-instance TEST-INSTANCE size 1000 count 10 "
            "wait 1 source 10.0.0.1 do-not-fragment interval 0.5 ttl 4"
        ),
        "eos": (
            "ping vrf TEST-INSTANCE some.random.test size 1000 repeat 10 timeout 1 "
            "source 10.0.0.1 df-bit interval 0.5"
        ),
        "linux": (
            "ip netns exec TEST-INSTANCE ping some.random.test -s 1000 -c 10 -W 1 "
            "-I 10.0.0.1 -i 0.5 -t 4"
        ),
    },
}
# PING_PARSED_RESULTS = {
#     "ok": {
#         "probes_sent": 5,
#         "probes_received": 5,
#         "packet_loss": 0.0,
#         "rtt_min": 164.0,
#         "rtt_avg": 165.0,
#         "rtt_max": 166.0,
#         "flag": "green",
#         "alert": False,
#         "status_code": 0,
#         "status_up": True,
#     },
#     "not-so-ok": {
#         "probes_sent": 10,
#         "probes_received": 5,
#         "packet_loss": 0.5,
#         "rtt_min": 174.0,
#         "rtt_avg": 175.0,
#         "rtt_max": 176.0,
#         "flag": "yellow",
#         "alert": True,
#         "status_code": 1,
#         "status_up": True,
#     },
#     "bad": {
#         "probes_sent": 5,
#         "probes_received": 0,
#         "packet_loss": 1.0,
#         "flag": "red",
#         "status_code": 2,
#         "status_up": False,
#         "alert": True,
#     },
#     "custom": {  # For cases where analysis is manually set
#         "probes_sent": 5,
#         "probes_received": 5,
#         "packet_loss": 0.0,
#         "rtt_min": 164.0,
#         "rtt_avg": 165.0,
#         "rtt_max": 166.0,
#         "flag": "yellow",
#         "alert": True,
#         "status_code": 1,
#         "status_up": True,
#     },
# }
PING_DATA = {
    "ios": {
        "ok": [
            dedent(
                """\
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 201.222.0.1, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 164/165/166 ms"""
            )
        ],
        "warning": [
            dedent(
                """\
Type escape sequence to abort.
Sending 10, 100-byte ICMP Echos to 201.222.0.1, timeout is 2 seconds:
!.!.!.!.!.
Success rate is 50 percent (10/5), round-trip min/avg/max = 174/175/176 ms"""
            )
        ],
        "critical": [
            dedent(
                """\
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 7.7.7.7, timeout is 2 seconds:
.....
Success rate is 0 percent (5/0)"""
            )
        ],
    },
    "xe": {
        "ok": [
            dedent(
                """\
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.193.7.35, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 164/165/166 ms"""
            )
        ],
        "warning": [
            dedent(
                """\
Type escape sequence to abort.
Sending 10, 100-byte ICMP Echos to 10.193.7.35, timeout is 2 seconds:
!.!.!.!.!.
Success rate is 50 percent (10/5), round-trip min/avg/max = 174/175/176 ms"""
            )
        ],
        "critical": [
            dedent(
                """\
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 201.222.0.0, timeout is 2 seconds:
.....
Success rate is 0 percent (5/0)"""
            )
        ],
    },
    "xr": {
        "ok": [
            dedent(
                """\
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 192.168.7.27, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 164/165/166 ms"""
            )
        ],
        "warning": [
            dedent(
                """\
Type escape sequence to abort.
Sending 10, 100-byte ICMP Echos to 201.222.0.1, timeout is 2 seconds:
!.!.!.!.!.
Success rate is 50 percent (10/5), round-trip min/avg/max = 174/175/176 ms"""
            )
        ],
        "critical": [
            dedent(
                """\
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 7.7.7.7, timeout is 2 seconds:
.....
Success rate is 0 percent (5/0)"""
            )
        ],
    },
    "nxos": {
        "ok": [
            dedent(
                """\
PING 201.222.0.1 (201.222.0.1): 56 data bytes
64 bytes from 201.222.0.1: icmp_seq=0 ttl=54 time=156.473 ms
64 bytes from 201.222.0.1: icmp_seq=1 ttl=54 time=155.678 ms
64 bytes from 201.222.0.1: icmp_seq=2 ttl=54 time=156.833 ms
64 bytes from 201.222.0.1: icmp_seq=3 ttl=54 time=159.921 ms
64 bytes from 201.222.0.1: icmp_seq=4 ttl=54 time=164.076 ms

--- 201.222.0.1 ping statistics ---
5 packets transmitted, 5 packets received, 0.00% packet loss
round-trip min/avg/max = 164.000/165.000/166.000 ms"""
            )
        ],
        "warning": [
            dedent(
                """\
PING 201.222.0.1 (201.222.0.1): 56 data bytes
64 bytes from 201.222.0.1: icmp_seq=0 ttl=54 time=156.473 ms
64 bytes from 201.222.0.1: icmp_seq=1 ttl=54 time=155.678 ms
64 bytes from 201.222.0.1: icmp_seq=2 ttl=54 time=156.833 ms
64 bytes from 201.222.0.1: icmp_seq=3 ttl=54 time=159.921 ms
64 bytes from 201.222.0.1: icmp_seq=4 ttl=54 time=164.076 ms

--- 201.222.0.1 ping statistics ---
10 packets transmitted, 5 packets received, 50.00% packet loss
round-trip min/avg/max = 174.000/175.000/176.000 ms"""
            )
        ],
        "critical": [
            dedent(
                """\
PING 201.222.0.1 (201.222.0.1): 56 data bytes
Request 0 timed out
Request 1 timed out

--- 201.222.0.1 ping statistics ---
5 packets transmitted, 0 packets received, 100.00% packet loss"""
            )
        ],
    },
    "junos": {
        "ok": [
            dedent(
                """\
PING 201.222.0.1 (201.222.0.1): 56 data bytes
64 bytes from 201.222.0.1: icmp_seq=0 ttl=57 time=144.163 ms
64 bytes from 201.222.0.1: icmp_seq=1 ttl=57 time=146.907 ms
64 bytes from 201.222.0.1: icmp_seq=2 ttl=57 time=145.691 ms
64 bytes from 201.222.0.1: icmp_seq=3 ttl=57 time=145.562 ms
64 bytes from 201.222.0.1: icmp_seq=4 ttl=57 time=146.194 ms

--- 201.222.0.1 ping statistics ---
5 packets transmitted, 5 packets received, 0% packet loss
round-trip min/avg/max/stddev = 164.00/165.000/166.000/0.827 ms"""
            )
        ],
        "warning": [
            dedent(
                """\
PING 201.222.0.1 (201.222.0.1): 56 data bytes
64 bytes from 201.222.0.1: icmp_seq=0 ttl=57 time=144.163 ms
64 bytes from 201.222.0.1: icmp_seq=1 ttl=57 time=146.907 ms
64 bytes from 201.222.0.1: icmp_seq=2 ttl=57 time=145.691 ms
64 bytes from 201.222.0.1: icmp_seq=3 ttl=57 time=145.562 ms
64 bytes from 201.222.0.1: icmp_seq=4 ttl=57 time=146.194 ms

--- 201.222.0.1 ping statistics ---
10 packets transmitted, 5 packets received, 50% packet loss
round-trip min/avg/max/stddev = 174.00/175.000/176.000/0.827 ms"""
            )
        ],
        "critical": [
            dedent(
                """\
PING 201.222.0.0 (201.222.0.0): 56 data bytes

--- 201.222.0.0 ping statistics ---
5 packets transmitted, 0 packets received, 100% packet loss"""
            )
        ],
    },
    "eos": {
        "ok": [
            dedent(
                """\
PING 10.193.0.1 (10.193.0.1) 72(100) bytes of data.
80 bytes from 10.193.0.1: icmp_seq=1 ttl=64 time=2.06 ms
80 bytes from 10.193.0.1: icmp_seq=2 ttl=64 time=0.102 ms
80 bytes from 10.193.0.1: icmp_seq=3 ttl=64 time=0.115 ms
80 bytes from 10.193.0.1: icmp_seq=4 ttl=64 time=0.098 ms
80 bytes from 10.193.0.1: icmp_seq=5 ttl=64 time=0.085 ms

--- 10.193.0.1 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 7ms
rtt min/avg/max/mdev = 164.000/165.000/166.000/0.787 ms, ipg/ewma 1.798/1.252 ms"""
            )
        ],
        "warning": [
            dedent(
                """\
PING 10.193.0.1 (10.193.0.1) 72(100) bytes of data.
80 bytes from 10.193.0.1: icmp_seq=1 ttl=64 time=2.06 ms
80 bytes from 10.193.0.1: icmp_seq=2 ttl=64 time=0.102 ms
80 bytes from 10.193.0.1: icmp_seq=3 ttl=64 time=0.115 ms
80 bytes from 10.193.0.1: icmp_seq=4 ttl=64 time=0.098 ms
80 bytes from 10.193.0.1: icmp_seq=5 ttl=64 time=0.085 ms

--- 10.193.0.1 ping statistics ---
10 packets transmitted, 5 received, 50% packet loss, time 7ms
rtt min/avg/max/mdev = 174.000/175.000/176.000/0.787 ms, ipg/ewma 1.798/1.252 ms"""
            )
        ],
        "critical": [
            dedent(
                """\
PING 1.1.1.1 (1.1.1.1) 72(100) bytes of data.

--- 1.1.1.1 ping statistics ---
5 packets transmitted, 0 received, 100% packet loss, time 40ms"""
            )
        ],
    },
    "linux": {
        "ok": [
            dedent(
                """\
PING 10.193.47.1 (10.193.47.1) 1400(1428) bytes of data.
1408 bytes from 10.193.47.1: icmp_seq=1 ttl=64 time=0.202 ms
1408 bytes from 10.193.47.1: icmp_seq=2 ttl=64 time=0.367 ms

--- 10.193.47.1 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 1000ms
rtt min/avg/max/mdev = 164.000/165.000/166.000/0.084 ms"""
            )
        ],
        "warning": [
            dedent(
                """\
PING 10.193.47.1 (10.193.47.1) 1400(1428) bytes of data.
1408 bytes from 10.193.47.1: icmp_seq=1 ttl=64 time=0.202 ms
1408 bytes from 10.193.47.1: icmp_seq=2 ttl=64 time=0.367 ms

--- 10.193.47.1 ping statistics ---
10 packets transmitted, 5 received, 50% packet loss, time 1000ms
rtt min/avg/max/mdev = 174.000/175.000/176.000/0.084 ms"""
            )
        ],
        "critical": [
            dedent(
                """\
PING 172.30.17.57 (172.30.17.57) 56(84) bytes of data.
From 172.30.17.32 icmp_seq=1 Destination Host Unreachable
From 172.30.17.32 icmp_seq=2 Destination Host Unreachable
From 172.30.17.32 icmp_seq=3 Destination Host Unreachable
From 172.30.17.32 icmp_seq=4 Destination Host Unreachable
From 172.30.17.32 icmp_seq=5 Destination Host Unreachable

--- 172.30.17.57 ping statistics ---
5 packets transmitted, 0 received, +5 errors, 100% packet loss, time 4000ms"""
            ),
            dedent(
                """\
PING 185.10.117.77 (185.10.117.77) 692(720) bytes of data.
From 10.193.66.129 icmp_seq=1 Time to live exceeded

--- 185.10.117.77 ping statistics ---
5 packets transmitted, 0 received, +5 errors, 100% packet loss, time 17ms"""
            ),
        ],
    },
}


@pytest.fixture
def ping_parameters(request):
    return PING_BASE_ARGS[request.getfixturevalue("ping_type")]


# @pytest.fixture
# def ping_base_obj(ping_parameters):
#     return PingBase(**ping_parameters)


@pytest.fixture
def module(get_implementation):
    return MODULE_MAPPING[get_implementation]


@pytest.fixture
def ping_imp_obj(module, ping_parameters):
    return module.Ping(**ping_parameters)


@pytest.fixture
def ping_imp_parser(module):
    return module.ParsePing


# @pytest.fixture
# def ping_command(request, get_os):
#     # Tries to get the command based on ping_type and os
#     try:
#         return PING_COMMANDS[request.getfixturevalue("ping_type")][get_os]
#     except KeyError as err:
#         pytest.skip(f"Unsupported commmand configuration for {str(err)}")


# @pytest.fixture
# def ping_obj(request, ping_parameters, get_implementation):
#     return MODULE_MAPPING[get_implementation].Ping(**ping_parameters)


# @pytest.fixture
# def ping_parser(get_implementation):
#     return MODULE_MAPPING[get_implementation].PingParser()


# @pytest.fixture
# def raw_outputs(request, get_os):
#     result_type = request.getfixturevalue("result_type")
#     return PING_DATA[get_os][result_type]


# @pytest.fixture
# def expected_result(request):
#     result_type = request.getfixturevalue("result_type")
#     return PING_PARSED_RESULTS[result_type]


def metadata_processor(metadata_obj, implementation, representation):
    # Retrieving UUID from instantiated object
    uid = repr(metadata_obj.id)

    # Retrieving timestamp from instantiated object
    created = repr(metadata_obj.created_at)

    if metadata_obj.updated_at:
        updated_at = repr(metadata_obj.updated_at)
        count = "1"
    else:
        updated_at = "None"
        count = "0"

    # Make the respective replacement on the expected output
    expected_metadata = re.sub(r"<CREATED_AT>", created, representation)
    expected_metadata = re.sub(r"<UUID>", uid, expected_metadata)
    expected_metadata = re.sub(r"<UPDATED_AT>", updated_at, expected_metadata)
    expected_metadata = re.sub(r"<COUNT>", count, expected_metadata)
    expected_metadata = re.sub(r"<IMPLEMENTATION>", implementation, expected_metadata)

    return expected_metadata


# class PingTester:
#     # TODO: Pending function to verify PingBuilder
#     @pytest.mark.init
#     @pytest.mark.parametrize(
#         "ping_type", ["default", "custom", "resolve_target", "no_resolve_target"]
#     )
#     def test_ping_obj_instatiation(self, ping_type, ping_obj, get_implementation):
#         # Retrieving UUID from instantiated object
#         uid = repr(ping_obj.metadata.id)

#         # Retrieving timestamp from instantiated object
#         created = repr(ping_obj.metadata.created_at)

#         # Make the respective replacement on the expected output
#         expected_metadata = re.sub(r"<CREATED_AT>", created, PING_METADATA_REPR)
#         expected_metadata = re.sub(r"<UUID>", uid, expected_metadata)
#         expected_metadata = re.sub(
#             r"<IMPLEMENTATION>", get_implementation, expected_metadata
#         )
#         assert repr(ping_obj) == PING_REPR[ping_type]
#         assert repr(ping_obj.metadata) == expected_metadata

#     @pytest.mark.init
#     @pytest.mark.parametrize("ping_type", ["invalid1"])
#     def test_ping_obj_instatiation_prohibition(self, ping_type, get_implementation):
#         with pytest.raises(TypeError):
#             MODULE_MAPPING[get_implementation].Ping(**PING_ARGS[ping_type])

#     @pytest.mark.command
#     @pytest.mark.parametrize(
#         "ping_type", ["default", "custom", "resolve_target", "no_resolve_target"]
#     )
#     def test_ping_obj_command(self, ping_type, ping_obj, ping_command):
#         assert ping_obj.command() == ping_command

#     @pytest.mark.pytest_result
#     @pytest.mark.parametrize("result_type", ["ok", "not-so-ok", "bad"])
#     def test_ping_obj_parse_result(
#         self, result_type, ping_parser, raw_outputs, expected_result
#     ):
#         for raw_output in raw_outputs:
#             output = ping_parser.data_parser(data=raw_output)
#             assert output == expected_result

#     @pytest.mark.parse_result
#     def test_ping_obj_parse_result_custom_analysis(self, get_os, ping_parser):
#         # It sends a good ping an analysis that is always warning
#         raw_output = PING_DATA[get_os]["ok"][0]
#         output = ping_parser.data_parser(
#             data=raw_output, warning_threshold=-1, critical_threshold=20
#         )
#         assert output == PING_PARSED_RESULTS["custom"]

#     #  TODO: Need to mock the execution of the tests. to be added at a later date...
#     # @pytest.mark.parse_result
#     # def test_ping_obj_custom_analysis_on_execute(self, get_os, ping_parser):
#     #     # For mocking I need to already specify the result when
#     #     raw_output = PING_DATA[get_os]["ok"][0]
#     #     output = ping_parser.data_parser(
#     #         data=raw_output, warning_threshold=-1, critical_threshold=20
#     #     )
#     #     assert output == PING_PARSED_RESULTS["custom"]

#     @pytest.mark.slow
#     @pytest.mark.network_run
#     @pytest.mark.parametrize("ping_type", ["resolve_target"])
#     def test_ping_obj_execution(self, dev_connector, ping_type, ping_obj):
#         ping_obj.connector = dev_connector
#         ping_obj.execute()
#         assert ping_obj.result["probes_sent"] == 5
#         assert ping_obj.result["probes_received"] == 5
#         assert ping_obj.result["packet_loss"] == 0.0
#         assert 0.0 <= ping_obj.result["rtt_min"] <= 3000.0
#         assert 0.0 <= ping_obj.result["rtt_avg"] <= 3000.0
#         assert 0.0 <= ping_obj.result["rtt_max"] <= 3000.0
#         assert ping_obj.result["flag"] == "green"
#         assert ping_obj.result["alert"] is False
#         assert ping_obj.result["status_code"] == 0
#         assert ping_obj.result["status_up"] is True


class TestPingResult:
    @pytest.mark.parametrize(
        "ping_result_type",
        ["ok", "warning", "critical", "custom_thld_critical", "custom_thld_warning"],
    )
    def test_instation(self, ping_result_type):
        ping_result_dict = PING_RESULT_ARGS[ping_result_type]
        assert (
            repr(PingResult(**ping_result_dict)) == PING_RESULT_REPR[ping_result_type]
        )

    def test_invalid_packet_loss(self):
        with pytest.raises(
            ValidationError, match="Packet loss must be between 0.0 and 1.0"
        ):
            PingResult(**PING_RESULT_ARGS["invalid_packet_loss"])


class TestPingBase:
    @pytest.mark.parametrize(
        "ping_type", ["ok", "warning", "critical", "resolve_target"]
    )
    def test_instatiation(self, ping_type):
        ping_dict = PING_BASE_ARGS[ping_type]
        assert repr(PingBase(**ping_dict)) == PING_BASE_REPR[ping_type]

    @pytest.mark.parametrize(
        "ping_type,expected",
        [
            (
                "invalid_target_ip",
                "failed to detect a valid IP address from '10.77.77.77.77'",
            ),
            (
                "invalid_source_ip",
                "failed to detect a valid IP address from '10.77.77.77.77'",
            ),
        ],
    )
    def test_invalid(self, ping_type, expected):
        with pytest.raises(ValidationError, match=expected):
            PingBase(**PING_BASE_ARGS[ping_type])

    @pytest.mark.parametrize("ping_type", ["ok", "warning", "critical"])
    def test_asdict(self, ping_type):
        ping = PingBase(**PING_BASE_ARGS[ping_type])
        del ping.metadata
        assert ping.to_dict() == PING_BASE_ASDICT[ping_type]


class PingTester:
    "Performs checks on the interface object of each implementation"

    @pytest.mark.parametrize("ping_type", ["ok", "warning", "critical"])
    def test_meta_attrs(self, ping_imp_obj, ping_type, get_implementation):
        assert "ping" == ping_imp_obj.metadata.name
        assert "entity" == ping_imp_obj.metadata.type
        assert get_implementation == ping_imp_obj.metadata.implementation

    @pytest.mark.parametrize("ping_type", ["ok", "warning"])
    def test_command(self, get_os, ping_type, ping_imp_obj):
        assert ping_imp_obj.ping_cmd is None
        # Now verify the command when generated
        ping_imp_obj.generate_ping_cmd()
        assert ping_imp_obj.ping_cmd == PING_COMMANDS[ping_type][get_os]

    # TODO: Implement `execute` method test - need mock

    @pytest.mark.parametrize("ping_type", ["ok", "warning", "critical"])
    def test_result_data_parse(self, get_os, ping_type, ping_imp_obj, ping_imp_parser):
        raw_data = PING_DATA[get_os][ping_type]

        parsed_dict = ping_imp_parser.data_constructor(raw_data[0])
        expected_dict = PING_RESULT_ARGS[ping_type]
        expected_dict.pop("apply_analysis", None)
        expected_dict.pop("critical_thld", None)
        expected_dict.pop("warning_thld", None)
        expected_dict.pop("status", None)
        expected_dict.pop("status_code", None)
        expected_dict.pop("status_up", None)
        for x in ("rtt_min", "rtt_avg", "rtt_max"):
            if expected_dict.get(x) is None:
                expected_dict.pop(x, None)
        assert parsed_dict == PING_RESULT_ARGS[ping_type]

    #  TODO: Implement parse (the overall)


@pytest.mark.eos
class TestPingEos(PingTester):
    net_os = "eos"
    implementation = "pyeapi"


@pytest.mark.ios
class TestPingIos(PingTester):
    net_os = "ios"
    implementation = "netmiko"


@pytest.mark.xe
class TestPingXe(PingTester):
    net_os = "xe"
    implementation = "netmiko"


@pytest.mark.xr
class TestPingXr(PingTester):
    net_os = "xr"
    implementation = "netmiko"


@pytest.mark.nxos
class TestPingNxos(PingTester):
    net_os = "nxos"
    implementation = "nxapi"


@pytest.mark.junos
class TestPingJunos(PingTester):
    net_os = "junos"
    implementation = "pyez"


@pytest.mark.linux
class TestPingLinuxLocal(PingTester):
    net_os = "linux"
    implementation = "subprocess"


@pytest.mark.linux
class TestPingLinuxRemote(PingTester):
    net_os = "linux"
    implementation = "paramiko"
