#!/usr/bin/env python
import socket
from datetime import datetime

ENCODING = 'UTF-8'      # The method for encoding and decoding all messages (UTF-8 allows 4 bytes max per char)
LINE_ENDINGS = '\r\n'   # This is appended to all messages sent by the socket (should always be CRLF)
CONNECTION_TIMEOUT = 30 # The socket will timeout after this many seconds when trying to initialize the connection
RECV_TIMEOUT = 180      # The socket will timeout after this many seconds when trying to receive data
SEND_TIEMOUT = 30       # The socket will timeout after this many seconds when trying to send data
MAX_RECV_BYTES = 4096   # The maximum amount of bytes to be received by the socket at a time
DEBUG_MODE = True       # Allows printing of socket debug info (ERROR level messages ignore this flag)


class IrcSocket:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._is_connected = False

    def connect(self, host, port):
        if not self.is_connected():
            self._set_timeout(CONNECTION_TIMEOUT)
            self._print_debug('Connecting to {}:{}...'.format(host, port))

            try:
                self._socket.connect((host, port))

            except socket.herror as err:
                error_message = 'Connection failed: {}'.format(err)
                self._print_debug(error_message, 'ERROR')
                raise SocketConnectFailed(error_message)

            except socket.gaierror as err:
                error_message = 'Connection failed: {}'.format(err)
                self._print_debug(error_message, 'ERROR')
                raise SocketConnectFailed(error_message)

            except socket.timeout:
                error_message = 'Connection failed: Socket operation timed out'
                self._print_debug(error_message, 'ERROR')
                raise SocketTimeout(error_message)

            except socket.error as err:
                error_message = 'Connection failed: {}'.format(err)
                self._print_debug(error_message, 'ERROR')
                raise SocketConnectFailed(error_message)

            else:
                self._print_debug('Connection successful')
                self._is_connected = True

        else:
            error_message = 'Connection failed: Socket is already connected to something'
            self._print_debug(error_message, 'ERROR')
            raise SocketAlreadyConnected(error_message)

    def disconnect(self):
        self._print_debug('Shutting down the connection')
        self._is_connected = False

        try:
            self._socket.shutdown(socket.SHUT_RDWR)

        except socket.error as err:
            error_message = 'Shutdown failed: {}'.format(err)
            self._print_debug(error_message, 'WARN', True)

        finally:
            self._print_debug('Cleaning up')
            self._socket.close()

    def reset(self):
        self._print_debug('Resetting socket...')
        self.disconnect()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._print_debug('Socket reset')

    def send_raw_text(self, raw_text):
        if self.is_connected():
            if raw_text != '':
                encoded_msg = '{}{}'.format(raw_text, LINE_ENDINGS).encode(ENCODING)
                msg_len = len(encoded_msg)
                bytes_sent = 0

                self._set_timeout(SEND_TIEMOUT)

                # NOTE: This loop wrapping send() ensures the socket actually sends the whole message
                while bytes_sent < msg_len:
                    try:
                        num_bytes = self._socket.send(encoded_msg[bytes_sent:])

                    except socket.timeout:
                        error_message = 'Send failed: Operation timed out after {} second(s)'.format(SEND_TIEMOUT)
                        self._print_debug(error_message, 'ERROR')
                        raise SocketTimeout(error_message)

                    except socket.error as err:
                        error_message = 'Send failed: {}'.format(err)
                        self._print_debug(error_message, 'ERROR')
                        self._is_connected = False # self.disconnect()
                        raise SocketConnectionBroken(error_message)

                    else:
                        # NOTE: If send() works but returns 0 bytes, it means the connection was terminated
                        if num_bytes == 0:
                            error_message = 'Send failed: Socket connection was closed unexpectedly'
                            self._print_debug(error_message, 'ERROR')
                            self._is_connected = False # self.disconnect()
                            raise SocketConnectionBroken(error_message)

                        bytes_sent += num_bytes

                self._print_debug('>> SENT / {} Bytes: {}'.format(bytes_sent, raw_text))

        else:
            error_message = 'Send failed: Socket connection has not been established'
            self._print_debug(error_message, 'ERROR')
            raise SocketConnectionNotEstablished(error_message)

    def recv_raw_text(self):
        if self.is_connected():
            self._set_timeout(RECV_TIMEOUT)

            try:
                encoded_msg = self._socket.recv(MAX_RECV_BYTES)

            except socket.timeout:
                error_message = 'Receive failed: Operation timed out after {} second(s)'.format(RECV_TIMEOUT)
                self._print_debug(error_message, 'ERROR')
                raise SocketTimeout(error_message)

            except socket.error as err:
                error_message = 'Receive failed: {}'.format(err)
                self._print_debug(error_message, 'ERROR')
                self._is_connected = False # self.disconnect()
                raise SocketConnectionBroken(error_message)

            else:
                # NOTE: If recv() works but returns a 0-byte message, it means the connection was terminated
                if encoded_msg == b'':
                    error_message = 'Receive failed: Socket connection was closed unexpectedly'
                    self._print_debug(error_message, 'ERROR')
                    self._is_connected = False # self.disconnect()
                    raise SocketConnectionBroken(error_message)

                else:
                    bytes_recd = len(encoded_msg)

                    # TODO: Need to remove the -2 offset when the server omits line endings from its messages...
                    # -
                    raw_text = encoded_msg.decode(ENCODING)[:-2]
                    # -
                    # END TODO

                    self._print_debug('<< RECV / {} Bytes: {}'.format(bytes_recd, raw_text))

                    # TODO: Responding to PING messages should probably be the responsibility of the caller?
                    # -
                    for line in raw_text.split(LINE_ENDINGS):
                        # NOTE: We have to echo the server's "PING <a string>" messages with "PONG <same string>"
                        if line.startswith('PING'):
                            try:
                                self.send_raw_text('PONG {}'.format(line.split()[1]))
                            except SocketTimeout:
                                raise
                            except SocketConnectionBroken:
                                raise
                            except SocketConnectionNotEstablished:
                                raise
                    # -
                    # END TODO

                    return (raw_text, LINE_ENDINGS)

        else:
            error_message = 'Receive failed: Socket connection has not been established'
            self._print_debug(error_message, 'ERROR')
            raise SocketConnectionNotEstablished(error_message)

    def is_connected(self):
        return self._is_connected

    def _set_timeout(self, new_timeout):
        if float(new_timeout) != self._socket.gettimeout():
            self._print_debug('Timeout set to {} second(s)'.format(new_timeout))
            self._socket.settimeout(new_timeout)

    def _print_debug(self, message, level='NORMAL', ignore_debug_flag=False):
        if level == 'ERROR':
            ignore_debug_flag = True

        if DEBUG_MODE or ignore_debug_flag:
            timestamp = datetime.now().strftime('%H:%M:%S')

            if level == 'NORMAL' or level == '':
                print('[{}] [ircsocket.py] {}'.format(timestamp, message))
            else:
                print('[{}] [ircsocket.py] [{}] {}'.format(timestamp, level, message))


class SocketError(OSError):
    """A socket error occurred"""
    def __init__(self, message='A socket error occurred', errors=None):
        self.message = message
        self.errors = errors
        super().__init__(message)


class SocketTimeout(SocketError):
    """Socket operation timed out"""
    def __init__(self, message='Operation timed out', errors=None):
        super().__init__(message, errors)


class SocketConnectFailed(SocketError):
    """Socket connection attempt failed"""
    def __init__(self, message='Socket connection attempt failed', errors=None):
        super().__init__(message, errors)


class SocketConnectionBroken(SocketError):
    """Socket connection was closed unexpectedly"""
    def __init__(self, message='Socket connection was closed unexpectedly', errors=None):
        super().__init__(message, errors)


class SocketConnectionNotEstablished(SocketError):
    """Socket connection has not been established"""
    def __init__(self, message='Socket connection has not been established', errors=None):
        super().__init__(message, errors)


class SocketAlreadyConnected(SocketError):
    """Socket is already connected to something"""
    def __init__(self, message='Socket is already connected to something', errors=None):
        super().__init__(message, errors)
