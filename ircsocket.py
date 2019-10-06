#!/usr/bin/env python
import socket

ENCODING = 'UTF-8'      # The default method for encoding and decoding messages (UTF-8 allows 4 bytes max per char)
LINE_ENDINGS = '\r\n'   # The default line endings for all messages sent by the socket (should always be CRLF)
CONNECTION_TIMEOUT = 30 # The socket will time out after 30 seconds when trying to initialize the connection
TIMEOUT = 180           # The socket will time out after 3 minutes of inactivity after initializing the connection
MAX_RECV_BYTES = 4096   # The maximum amount of bytes to be received by the socket at a time
DEBUG_MODE = True       # Allows printing of socket debug info to STDOUT


class IrcSocket:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._is_connected = False

    def connect(self, host, port):
        if not self._is_connected:
            self._print_debug('Timeout set to {} seconds'.format(CONNECTION_TIMEOUT))
            self._socket.settimeout(CONNECTION_TIMEOUT)

            self._print_debug('Connecting to {}:{}...'.format(host, port))

            try:
                self._socket.connect((host, port))

            except socket.error:
                self._print_debug('ERROR: Connection failed')
                self.disconnect()
                raise OSError('ERROR: Socket failed to connect')

            else:
                self._print_debug('Connection successful')
                self._print_debug('Timeout set to {} seconds'.format(TIMEOUT))
                self._socket.settimeout(TIMEOUT)
                self._is_connected = True

        else:
            self._print_debug('WARNING: Cannot connect -- This socket is already connected to something!')

    def disconnect(self):
        if self._is_connected:
            self._print_debug('Gracefully shutting down the connection')
            self._is_connected = False

            try:
                self._socket.shutdown(socket.SHUT_RDWR)

            except socket.error:
                raise OSError('ERROR: Cannot shutdown socket')

            self._socket.close()

        else:
            self._print_debug('Something went wrong! Shutting down the connection')
            self._socket.close()

    def send_raw_text(self, raw_text):
        if self._is_connected:
            bytes_sent = 0

            if raw_text != '':
                encoded_msg = '{}{}'.format(raw_text, LINE_ENDINGS).encode(ENCODING)
                msg_len = len(encoded_msg)

                while bytes_sent < msg_len:
                    num_bytes = self._socket.send(encoded_msg[bytes_sent:])

                    if num_bytes == 0:
                        self._is_connected = False
                        self.disconnect()
                        raise OSError('ERROR: Socket connection broken')

                    bytes_sent += num_bytes

            self._print_debug('>> SENT / {} Bytes: {}'.format(bytes_sent, raw_text))

        else:
            self._print_debug('WARNING: Cannot send -- This socket is not connected to anything!')

    def recv_raw_text(self):
        if self._is_connected:
            encoded_msg = self._socket.recv(MAX_RECV_BYTES)

            if encoded_msg == b'':
                self._is_connected = False
                self.disconnect()
                raise OSError('Socket connection broken')

            else:
                bytes_recd = len(encoded_msg)
                raw_text = encoded_msg.decode(ENCODING)[:-2]

                self._print_debug('<< RECV / {} Bytes: {}'.format(bytes_recd, raw_text))

                for line in raw_text.split(LINE_ENDINGS):
                    if line.startswith('PING'):
                        self.send_raw_text('PONG {}'.format(line.split()[1]))

                return (raw_text, LINE_ENDINGS)

        else:
            self._print_debug('WARNING: Cannot receive -- This socket is not connected to anything!')

    def is_connected(self):
        return self._is_connected

    def _print_debug(self, msg):
        if DEBUG_MODE:
            print('[DEBUG] {}'.format(msg))
