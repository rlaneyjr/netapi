from netapi.probe.linux import subprocesser


class Ping(subprocesser.Ping):
    def __post_init__(self, **_ignore):
        super().__post_init__()
        self.metadata.implementation = "LINUX-PARAMIKO"


class ParsePing(subprocesser.ParsePing):
    pass
