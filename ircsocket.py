#!/usr/bin/env python
import socket

DEFAULT_ENCODING = 'UTF-8'       # UTF-8 allows up to 4 bytes per char
DEFAULT_LINE_ENDINGS = '\r\n'    # The specified line ending will automatically be appended to text sent
DEFAULT_CONNECTION_TIMEOUT = 30  # Socket will time out after 30 seconds when initializing the connection
DEFAULT_TIMEOUT = 180            # Socket will time out after 3 minutes of inactivity
MAX_RECV_BYTES = 4096            # The max amount of bytes to be received
DEBUG_MODE = True                # Causes printing of socket debug info to standard out


class IrcSocket:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_connected = False
    
    def connect(self, host, port):
        if not self.is_connected:
            self._print_debug_msg('Timeout set to {} seconds'.format(DEFAULT_CONNECTION_TIMEOUT))
            self.socket.settimeout(DEFAULT_CONNECTION_TIMEOUT)

            self._print_debug_msg('Connecting to {}:{}...'.format(host, port))
            self.socket.connect((host, port))
            self._print_debug_msg('Connection successful')

            self._print_debug_msg('Timeout set to {} seconds'.format(DEFAULT_TIMEOUT))
            self.socket.settimeout(DEFAULT_TIMEOUT)
            
            self.is_connected = True
        
    def disconnect(self):
        if self.is_connected:
            self._print_debug_msg('Shutting down the connection')
            self.is_connected = False
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
    
    def send_msg(self, raw_text, line_endings=DEFAULT_LINE_ENDINGS, encoding=DEFAULT_ENCODING):
        if self.is_connected:
            encoded_msg = '{}{}'.format(raw_text, line_endings).encode(encoding)
            msg_len = len(encoded_msg)
            
            bytes_sent = 0
            while raw_text != '' and bytes_sent < msg_len:
                num_bytes = self.socket.send(encoded_msg[bytes_sent:])
                if num_bytes == 0:
                    self.is_connected = False
                    raise RuntimeError('Socket connection broken')
                bytes_sent += num_bytes
            
            self._print_debug_msg('>> SENT / {} Bytes: {}'.format(bytes_sent, raw_text))
    
    def recv_msg(self, line_endings=DEFAULT_LINE_ENDINGS, encoding=DEFAULT_ENCODING):
        if self.is_connected:
            encoded_msg = self.socket.recv(MAX_RECV_BYTES)
            
            if encoded_msg == b'':
                self.is_connected = False
                raise RuntimeError('Socket connection broken')
            else:
                bytes_recd = len(encoded_msg)
                raw_text = encoded_msg.decode(encoding)[:-2]
                
                self._print_debug_msg('<< RECV / {} Bytes: {}'.format(bytes_recd, raw_text))
                
                for line in raw_text.split(line_endings):
                    if line.startswith('PING'):
                        self.send_msg('PONG {}'.format(line.split()[1]))
                
                return raw_text.split(line_endings)

    def _print_debug_msg(self, msg):
        if DEBUG_MODE:
            print('[DEBUG] {}'.format(msg))
