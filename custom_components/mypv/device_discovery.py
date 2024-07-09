import socket
from zeroconf import Zeroconf, ServiceBrowser, ServiceListener

class MypvDeviceListener(ServiceListener):
    """Service listener for mDNS."""

    def __init__(self):
        self.devices = []

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            address = socket.inet_ntoa(info.addresses[0])
            self.devices.append({"name": name, "address": address})

    def remove_service(self, zeroconf, type, name):
        pass

    def update_service(self, zeroconf, type, name):
        pass

def discover_devices():
    zeroconf = Zeroconf()
    listener = MypvDeviceListener()
    ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
    zeroconf.close()
    return listener.devices
