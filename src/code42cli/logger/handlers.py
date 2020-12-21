import logging
import socket
import ssl
from logging.handlers import SysLogHandler

from code42cli.cmds.search.enums import ServerProtocol


class NoPrioritySysLogHandlerWrapper:
    """
    Uses NoPrioritySysLogHandler but does not make the connection in the constructor. Instead,
    it connects the first time you access the handler property. This makes testing against
    a syslog handler easier.
    Args:
        hostname: The hostname of the syslog server to send log messages to.
        port: The port of the syslog server to send log messages to.
        protocol: The protocol over which to submit syslog messages. Accepts TCP, UDP, or TLS.
    """

    def __init__(self, hostname, port, protocol, certs):
        self.hostname = hostname
        self.port = port
        self.protocol = protocol
        self.certs = certs
        self._handler = None

    @property
    def handler(self):
        if not self._handler:
            self._handler = self._create_handler()
        return self._handler

    def _create_handler(self):
        return NoPrioritySysLogHandler(
            self.hostname, self.port, self.protocol, self.certs
        )


class NoPrioritySysLogHandler(SysLogHandler):
    """
    Overrides the default implementation of SysLogHandler to not send a `<PRI>` at the
    beginning of the message. Most CEF consumers seem to not expect the `<PRI>` to be
    present in CEF messages. Attach to a logger via `.addHandler` to use.
    Args:
        hostname: The hostname of the syslog server to send log messages to.
        port: The port of the syslog server to send log messages to.
        protocol: The protocol over which to submit syslog messages. Accepts TCP, UDP, or TLS.
    """

    def __init__(self, hostname, port, protocol, certs):
        self.address = (hostname, port)
        logging.Handler.__init__(self)
        use_insecure = protocol != ServerProtocol.TLS
        self.socktype = _try_get_socket_type_from_protocol(protocol)
        self.socket = self._create_socket(hostname, port, use_insecure, certs)

    def _create_socket(self, hostname, port, use_insecure, certs):
        socket_info = self._get_socket_address_info(hostname, port)
        err, sock = _create_socket_from_address_info_list(
            socket_info, use_insecure, certs
        )
        if err is not None:
            raise err
        return sock

    def _get_socket_address_info(self, hostname, port):
        info = socket.getaddrinfo(hostname, port, 0, self.socktype)
        if not info:
            raise OSError("getaddrinfo() returns an empty list")
        return info

    def emit(self, record):
        try:
            msg = self.format(record) + "\n"
            msg = msg.encode("utf-8")
            if self.socktype == socket.SOCK_DGRAM:
                self.socket.sendto(msg, self.address)
            else:
                self.socket.sendall(msg)
        except Exception:
            self.handleError(record)

    def close(self):
        self.socket.close()
        logging.Handler.close(self)


def _create_socket_from_address_info_list(socket_info, use_insecure, certs):
    err = sock = None
    for info in socket_info:
        err, sock = _try_create_socket_from_address_info(info, use_insecure, certs)
        if err:
            break
    return err, sock


def _try_create_socket_from_address_info(info, use_insecure, certs):
    af, sock_type, proto, _, sa = info
    err = sock = None
    try:
        sock = _create_socket_from_uncoupled_address_info(
            af, sock_type, proto, use_insecure, certs, sa
        )
    except OSError as exc:
        # reassign for returning outside except block
        err = exc
        if sock is not None:
            sock.close()
    return err, sock


def _create_socket_from_uncoupled_address_info(
    af, sock_type, proto, use_insecure, certs, sa
):
    sock = socket.socket(af, sock_type, proto)
    if not use_insecure:
        sock = _wrap_socket_for_ssl(sock, certs)
    if sock_type == socket.SOCK_STREAM:
        sock.connect(sa)
    return sock


def _wrap_socket_for_ssl(sock, certs):
    certs = certs or None
    cert_reqs = ssl.CERT_REQUIRED if certs else ssl.CERT_NONE
    return ssl.wrap_socket(sock, ca_certs=certs, cert_reqs=cert_reqs)


def _try_get_socket_type_from_protocol(protocol):
    socket_type = _get_socket_type_from_protocol(protocol)
    if socket_type is None:
        _raise_socket_type_error(protocol)
    return socket_type


def _get_socket_type_from_protocol(protocol):
    if protocol in [ServerProtocol.TCP, ServerProtocol.TLS]:
        return socket.SOCK_STREAM
    elif protocol == ServerProtocol.UDP:
        return socket.SOCK_DGRAM


def _raise_socket_type_error(protocol):
    msg = "Could not determine socket type. Expected one of {}, but got {}".format(
        list(ServerProtocol()), protocol
    )
    raise ValueError(msg)