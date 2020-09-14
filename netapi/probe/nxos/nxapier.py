import re
import pendulum
from netapi.probe import ping

PATTERNS = {
    "ping": re.compile(
        r"(?P<tx>\d+) packets transmitted, (?P<rx>\d+) packets received, "
        r"(?P<loss>\d+\.\d+)% packet loss\nround-trip min/avg/max = "
        r"(?P<min>\d+(\.\d+)?)/(?P<avg>\d+(\.\d+)?)/(?P<max>\d+(\.\d+)?).*",
        re.MULTILINE,
    )
}

TIMEOUT_PATTERNS = {
    "ping": re.compile(
        r"(?P<tx>\d+) packets transmitted, (?P<rx>\d+) packets received, "
        r"(?P<loss>\d+\.\d+)% packet loss"
    )
}


class Ping(ping.PingBase):
    def __post_init__(self, **_ignore):
        super().__post_init__()
        self.metadata.implementation = "NXOS-NXAPI"

    def _ping_parameters(self):
        "Ping Parameters for nxos"
        params = []
        if self.size:
            params.append(f"packet-size {self.size}")
        if self.count:
            params.append(f"count {self.count}")
        if self.timeout:
            params.append(f"timeout {self.timeout}")
        if self.source:
            # NOTE: On older versions of NXOS is parent-interface...
            params.append(f"source-interface {self.source}")
        if self.source_ip:
            params.append(f"source {self.source_ip}")
        if self.df_bit:
            params.append(f"df-bit")
        if self.interval:
            params.append(f"interval {self.interval}")
        return params

    def _ping_base_cmd(self):
        "Ping base command for nxos"
        # If resolve_target was selected it will use the target IP for the ping
        if self.resolve_target:
            target = str(self.target_ip)
        else:
            target = self.target
        ping_base_cmd = ["ping", target]
        if self.instance is not None:
            ping_base_cmd.append(f"vrf {self.instance}")

        return ping_base_cmd

    def generate_ping_cmd(self, **_ignore):
        self.ping_cmd = " ".join(self._ping_base_cmd() + self._ping_parameters())

    def execute(self, warning_thld=None, critical_thld=None, **_ignore):
        """
        Automatic execution of entity to retrieve results. Also applies warning/critical
        thresholds for the analysis if given.

        - `warning_thld`: Packet loss above this value is flagged as `warning`
        - `critical_thld`: Packet loss above this value is flagged as `critical`

        NOTE: If `warning_thld` was set and paket loss is below the percentage value,
        it is then flagged as `ok`

        By default it uses the built-in analysis:
        `packet_loss` >= 100 -> `critical`
        `packet_loss` == 0   -> `ok`
        `packet_loss` != 0   -> `warning`
        """
        if self.connector is None:
            raise NotImplementedError("Need to have the connector defined")

        # Generate exec command
        if not self.ping_cmd:
            self.generate_ping_cmd()

        #  Executed flag
        _executed = False
        if self.result:
            _executed = True

        self.result = ParsePing.parse(
            self.connector.run(self.ping_cmd),
            warning_thld=warning_thld,
            critical_thld=critical_thld,
        )

        if _executed:
            self.metadata.updated_at = pendulum.now()
            self.metadata.collection_count += 1

        return True


class ParsePing(ping.CommonParser):
    UNREACHABLE_MESSAGES = ["Name or service not known"]

    @staticmethod
    def matched_obj(data):
        return re.search(PATTERNS["ping"], data)

    @staticmethod
    def matched_timeout_obj(data):
        return re.search(TIMEOUT_PATTERNS["ping"], data)

    @staticmethod
    def matched_data(regex_obj):
        return dict(
            probes_sent=int(regex_obj.group("tx")),
            probes_received=int(regex_obj.group("rx")),
            packet_loss=float("{:.4f}".format(float(regex_obj.group("loss")) / 100)),
            rtt_min=float(regex_obj.group("min")),
            rtt_avg=float(regex_obj.group("avg")),
            rtt_max=float(regex_obj.group("max")),
        )

    @staticmethod
    def matched_timeout_data(regex_obj):
        return dict(
            probes_sent=int(regex_obj.group("tx")),
            probes_received=int(regex_obj.group("rx")),
            packet_loss=float("{:.4f}".format(float(regex_obj.group("loss")) / 100)),
        )

    @staticmethod
    def extraction_operation(data):
        pass  # TODO: Needs to be developed
