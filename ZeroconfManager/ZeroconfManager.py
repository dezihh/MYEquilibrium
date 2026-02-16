import logging
import socket

from zeroconf.asyncio import AsyncServiceInfo, AsyncZeroconf
from zeroconf import IPVersion

class ZeroconfManager:

    info: AsyncServiceInfo|None = None
    zeroconf: AsyncZeroconf|None = None

    async def register_service(self, name: str, description=None):
        if description is None:
            description = {}

        fqdn = socket.gethostname()
        ip_addr = socket.gethostbyname(fqdn)
        hostname = fqdn.split('.')[0]

        service_type = "_myequilibrium._tcp.local."
        service_name = f"{name}.{service_type}"
        server_name = f"{hostname}.local."

        self.info = AsyncServiceInfo(
            service_type,
            service_name,
            addresses=[socket.inet_aton(ip_addr)],
            port=8000,
            properties=description,
            server=server_name,
        )

        # Restrict to IPv4 to avoid failures on hosts without IPv6 routing
        self.zeroconf = AsyncZeroconf(ip_version=IPVersion.V4Only)
        await self.zeroconf.async_register_service(info=self.info)

    async def unregister_service(self):
        await self.zeroconf.async_unregister_service(self.info)
        await self.zeroconf.async_close()
