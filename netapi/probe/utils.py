import re
import time
from socket import gethostbyname, gaierror, gethostbyaddr
from netaddr import IPNetwork, IPAddress, AddrFormatError


def is_it_valid_ip(ip):
    """
    Determines if the IP address passed is a valid IPv4 or IPv6 address
    Returns True or False
    """
    try:
        IPAddress(ip)
    except (ValueError, AddrFormatError) as err:
        if "IPAddress() does not support netmasks" in str(err):
            try:
                IPNetwork(ip)
            except (ValueError, AddrFormatError):
                return False
        else:
            return False
    return True


def is_valid_hostname(hostname):
    """
    Method from (http://stackoverflow.com/questions/2532053/validate-a-hostname-string)
    that helps determine hostname name validity
    """

    if hostname[-1] == ".":
        # strip exactly one dot from the right, if present
        hostname = hostname[:-1]
    if len(hostname) > 253:
        return False
    # must be not all-numeric, so that it can't be confused with an ip-address
    if re.match(r"[\d.]+$", hostname):
        return False

    allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def get_ip_by_name(name):
    "Return IP and True if name resolved. Return Err and False if not"
    try:
        ip = gethostbyname(name)
    except gaierror as err:
        return str(err), False
    return ip, True


def host_validity(host, dns_query_attempt=1):
    """
    Determines hostname or IP is valid and returns IP
    """
    # Verification if agent is local
    if host == "local" or host == "localhost":
        return "127.0.0.1"

    if is_it_valid_ip(host):
        # Return IP address
        return host

    if is_valid_hostname(host):
        # Determine IP from DNS:
        while dns_query_attempt:
            try:
                # This will get the first IP if there are multiple
                print(f"Resolving locally host {host} - attempt {dns_query_attempt}")
                ip = gethostbyname(host)
                return ip
            except gaierror as err:
                if any(
                    x in str(err)
                    for x in (
                        "Name or service not known",
                        "getaddrinfo failed",
                        "nodename nor servname provided, or not known",
                        "Temporary failure in name resolution",
                    )
                ):
                    dns_query_attempt -= 1
                    if dns_query_attempt <= 0:
                        raise ValueError(f"Could not resolve name")
                    time.sleep(5)
                else:
                    raise err
            except Exception as err:
                raise err

    raise ValueError("Could not retrieve IP")


def addresser(address, **kwargs):
    """ Determines the address_ip and address_name """
    if address:
        if is_valid_hostname(address):
            address_name = address
            address_ip = host_validity(address, **kwargs)

        else:
            address_ip = host_validity(address, **kwargs)
            try:
                address_name = gethostbyaddr(address_ip)[0]

            except Exception:
                address_name = address_ip
    else:
        address_ip = None
        address_name = None

    return address_ip, address_name
