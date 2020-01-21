#!/usr/bin/env python
import ircsocket
import clientconfig
import tools

DEBUG_MODE = False  # Allows printing of socket debug messages


class IrcClient:
    def __init__(self):
        client_socket = ircsocket.IrcSocket()
        client_config = clientconfig.ClientConfig()
