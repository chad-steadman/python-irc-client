#!/usr/bin/env python
import socket

ENCODING = 'UTF-8'      # The default method for encoding and decoding messages (UTF-8 allows 4 bytes max per char)
LINE_ENDINGS = '\r\n'   # The default line endings for all messages sent by the socket (should always be CRLF)
CONNECTION_TIMEOUT = 30 # The socket will time out after 30 seconds when trying to initialize the connection
RECV_TIMEOUT = 180      # The socket will time out after 3 minutes of inactivity after initializing the connection
SEND_TIEMOUT = 30       # The socket will time out after 30 seconds when trying to send data
MAX_RECV_BYTES = 4096   # The maximum amount of bytes to be received by the socket at a time
DEBUG_MODE = True       # Allows printing of socket debug info to STDOUT


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
                self._set_timeout(RECV_TIMEOUT)
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
                        self.disconnect()
                        raise SocketConnectionBroken(error_message)

                    else:
                        if num_bytes == 0:
                            error_message = 'Send failed: Socket connection was closed unexpectedly'
                            self._print_debug(error_message, 'ERROR')
                            self.disconnect()
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
                self.disconnect()
                raise SocketConnectionBroken(error_message)

            else:
                if encoded_msg == b'':
                    error_message = 'Receive failed: Socket connection was closed unexpectedly'
                    self._print_debug(error_message, 'ERROR')
                    self.disconnect()
                    raise SocketConnectionBroken(error_message)

                else:
                    bytes_recd = len(encoded_msg)
                    raw_text = encoded_msg.decode(ENCODING)[:-2]

                    self._print_debug('<< RECV / {} Bytes: {}'.format(bytes_recd, raw_text))

                    for line in raw_text.split(LINE_ENDINGS):
                        if line.startswith('PING'):
                            try:
                                self.send_raw_text('PONG {}'.format(line.split()[1]))
                            except SocketError as err:
                                self._print_debug(err, 'ERROR')

                    return (raw_text, LINE_ENDINGS)

        else:
            error_message = 'Receive failed: Socket connection has not been established'
            self._print_debug(error_message, 'ERROR')
            raise SocketConnectionNotEstablished(error_message)

    def is_connected(self):
        return self._is_connected

    def _set_timeout(self, new_timeout):
        self._print_debug('Timeout set to {} second(s)'.format(new_timeout))
        self._socket.settimeout(new_timeout)

    def _print_debug(self, message, level='NORMAL', ignore_debug_flag=False):
        if level == 'ERROR':
            ignore_debug_flag = True

        if DEBUG_MODE or ignore_debug_flag:
            if level == 'NORMAL' or level == '':
                print('[IrcSocket] {}'.format(message))
            else:
                print('[IrcSocket] [{}] {}'.format(level, message))


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
