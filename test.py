#!/usr/bin/env python
import ircsocket

class IrcClient:
    def __init__(self):
        self.ircsocket = ircsocket.IrcSocket()

    def connect(self, host, port):
        self.ircsocket.connect(host, port)

    def register(self, nickname, username, realname, server_pwd=''):
        if server_pwd != '':
            self.ircsocket.send_msg('PASS {}'.format(server_password))
        self.ircsocket.send_msg('NICK {}'.format(nickname))
        self.ircsocket.send_msg('USER {} 0 * {}'.format(username, realname))

    def mainloop(self):
        while self.ircsocket.is_connected:
            self.ircsocket.recv_msg()


HOST = 'irc.rizon.net'
PORT = 6667

ircclient = IrcClient()
ircclient.connect(HOST, PORT)
ircclient.register('Namdaets', 'namdaets', 'namdaets')
ircclient.mainloop()
