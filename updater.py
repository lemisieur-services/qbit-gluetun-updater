#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Original source: https://gist.github.com/stumpylog/5dc8f19460459c455d67a03485132187
"""
import enum
import logging
import sys
import os
from typing import Dict
from typing import Final

import qbittorrentapi
import requests


@enum.unique
class ToolExitCodes(enum.IntEnum):
    ALL_GOOD = 0
    BASE_ERROR = 1
    QBIT_AUTH_FAILURE = 2
    HTTP_ERROR = 3
    INVALID_PORT = 4
    QBIT_PREF_MISSING = 5


class VpnServerException(BaseException):
    CODE = ToolExitCodes.BASE_ERROR


class VpnServerHttpCodeException(VpnServerException):
    CODE = ToolExitCodes.HTTP_ERROR


class VpnServerInvalidPortException(VpnServerException):
    CODE = ToolExitCodes.INVALID_PORT


class VpnControlServerApi(object):
    def __init__(self,
                 host: str,
                 port: int):
        self._log = logging.getLogger(__name__)
        self._host: Final[str] = host
        self._port: Final[int] = port

        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json"
        })

        self._API_BASE: Final[str] = f"http://{self._host}:{self._port}/v1"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def _query(self, endpoint) -> Dict:
        uri = self._API_BASE + endpoint
        self._log.debug(f"Query to {uri}")
        r = self._session.get(uri)
        if r.status_code == 200:
            self._log.debug("API query completed")
            return r.json()
        else:
            self._log.error(f"API returned {r.status_code} for {endpoint} endpoint")
            raise VpnServerHttpCodeException()

    @property
    def forwarded_port(self) -> int:
        endpoint = "/openvpn/portforwarded"
        data = self._query(endpoint)
        if "port" in data:
            vpn_forwarded_port: int = int(data["port"])
            self._log.info(f"VPN Port is {vpn_forwarded_port}")
            if 1023 < vpn_forwarded_port < 65535:
                return vpn_forwarded_port
            else:
                self._log.info(f"VPN Port invalid: {vpn_forwarded_port}")
                raise VpnServerInvalidPortException()
        else:
            self._log.info("Missing port data")
            raise VpnServerInvalidPortException()


if __name__ == "__main__":
    # Torrent host and WebUI port
    _TORRENT_HOST: Final[str] = os.environ.get('QBIT_HOST')
    _TORRENT_USERNAME: Final[str] = os.environ.get('QBIT_USERNAME')
    _TORRENT_PASSWORD: Final[str] = os.environ.get('QBIT_PASSWORD')

    # VPN host and control server port
    _VPN_FQDN: Final[str] = os.environ.get('GLUETUN_FQDN')
    _VPN_CTRL_PORT: Final[int] = os.environ.get('GLUETUN_CTRL_PORT')

    __EXIT_CODE = ToolExitCodes.ALL_GOOD

    logging.basicConfig(level=logging.INFO,
                        datefmt="%Y-%m-%d %H:%M:%S",
                        format='%(asctime)s %(name)-10s %(levelname)-8s %(message)s')

    logger = logging.getLogger("port-tool")

    qbit_port: int = -1
    vpn_port: int = -1

    # Gather the qBittorent _port
    try:

        qbt_client = qbittorrentapi.Client(host=f'{_TORRENT_HOST}',
                                           username={_TORRENT_USERNAME},
                                           password={_TORRENT_PASSWORD})

        qbt_client.auth_log_in()

        logger.info(f'qBittorrent: {qbt_client.app.version}')
        logger.info(f'qBittorrent Web API: {qbt_client.app.web_api_version}')

        if "listen_port" in qbt_client.app.preferences:
            qbit_port: int = int(qbt_client.app.preferences["listen_port"])
            logger.info(f"Torrent Port is {qbit_port}")
        else:
            logger.error("Preference listen_port not found")
            __EXIT_CODE = ToolExitCodes.QBIT_PREF_MISSING

        # Gather the VPN _port
        if __EXIT_CODE == ToolExitCodes.ALL_GOOD:
            try:
                api = VpnControlServerApi(_VPN_FQDN, _VPN_CTRL_PORT)
                vpn_port = api.forwarded_port
                logger.info(f"VPN port: {vpn_port}")
            except VpnServerException as e:
                logger.error(str(e))
                __EXIT_CODE = e.CODE

        # Change prefs if needed
        if __EXIT_CODE == ToolExitCodes.ALL_GOOD:
            if vpn_port != qbit_port:
                qbt_client.app.preferences = dict(listen_port=vpn_port)
                logger.info(f"Updated qBittorrent port to {vpn_port}")
            else:
                logger.info(f"Ports matched, no change ({vpn_port} == {qbit_port})")

    except qbittorrentapi.LoginFailed as e:
        logger.error(str(e))
        __EXIT_CODE = ToolExitCodes.QBIT_AUTH_FAILURE

    sys.exit(__EXIT_CODE)
