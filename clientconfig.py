#!/usr/bin/env python
import os
import config

DEFAULT_PORT = '6667'
DEFAULT_AUTO_RECONNECT = 'True'
DEFAULT_ENABLE_LOGGING = 'True'
DEFAULT_CONFIG_FILE = 'config.cfg'
DEFAULT_LOG_FILE = 'server.log'


class ClientConfig(config.Config):
    def __init__(self, filename=DEFAULT_CONFIG_FILE):
        super().__init__(filename)

        # initialize default key/value pairs
        self.add_section('IDENTITY')
        self.add_key('IDENTITY', 'nickname', '')
        self.add_key('IDENTITY', 'username', '')
        self.add_key('IDENTITY', 'realname', '')
        self.add_key('IDENTITY', 'nickserv_password', '')

        self.add_section('CONNECTION')
        self.add_key('CONNECTION', 'server_address', '')
        self.add_key('CONNECTION', 'server_port', DEFAULT_PORT)
        self.add_key('CONNECTION', 'server_password', '')
        self.add_key('CONNECTION', 'auto_reconnect', DEFAULT_AUTO_RECONNECT)
        self.add_key('CONNECTION', 'enable_logging', DEFAULT_ENABLE_LOGGING)
        self.add_key('CONNECTION', 'autojoin_channels', '')

        self.add_section('PATHS')
        self.add_key('PATHS', 'config_file', DEFAULT_CONFIG_FILE)
        self.add_key('PATHS', 'log_file', DEFAULT_LOG_FILE)

    def save_client_config(self):
        # save existing configuration to a file
        print('Saving client configuration to {}... '.format(self.get_filename()), end='')
        if not self.save_to_file():
            # failed to save file -- check for errors
            print('Failed!')

            # check if file exists
            if os.path.isfile(self.get_filename()):
                # file exists but can't be written to
                print('[ERROR] Cannot write to file. Check directory and/or file permissions.')

            else:
                # file doesn't exist but can't be created
                print('[ERROR] Could not save configuration file. Check the path and/or directory permissions.')

            raise IOError

        else:
            # successfully saved configuration to file
            print('Success!')

    def load_client_config(self, first_load=False):
        # load existing configuration from a file
        print('Loading client configuration from {}... '.format(self.get_filename()), end='')
        if not self.load_from_file():
            # failed to load file -- check for errors
            print('Failed!')

            # check if file exists
            if os.path.isfile(self.get_filename()):
                # file exists but can't be accessed
                print('[ERROR] Cannot access file. Check directory and/or file permissions.')
                raise IOError

            elif first_load:
                # file doesn't exist on startup -- make a new, empty configuration file then exit program
                print('File not found. Creating new empty configuration file... ', end='')
                if not self.save_to_file():
                    # failed to save new configuration file
                    print('Failed!\n[ERROR] Could not save new configuration file. Check the path and/or directory permissions.')
                    raise IOError

                else:
                    # successfully saved new configuration file
                    print('Success!')

            else:
                # file doesn't exist on subsequent loads --
                print('[ERROR] File not found. Check the path and/or filename.')
                raise IOError

        else:
            # successfully loaded configuration from file
            print('Success!')

    def get_nickname(self):
        # return the value of 'nickname' stored in the IDENTITY section
        return self.get_key('IDENTITY', 'nickname')

    def get_username(self):
        # return the value of 'username' stored in the IDENTITY section
        return self.get_key('IDENTITY', 'username')

    def get_realname(self):
        # return the value of 'realname' stored in the IDENTITY section
        return self.get_key('IDENTITY', 'realname')

    def get_nickservpass(self):
        # return the value of 'nickserv_password' stored in the IDENTITY section
        return self.get_key('IDENTITY', 'nickserv_password')

    def get_serveraddress(self):
        # return the value of 'server_address' stored in the CONNECTION section
        return self.get_key('CONNECTION', 'server_address')

    def get_serverport(self):
        # return the value of 'server_port' stored in the CONNECTION section
        return self.get_key('CONNECTION', 'server_port')

    def get_serverpass(self):
        # return the value of 'server_password' stored in the CONNECTION section
        return self.get_key('CONNECTION', 'server_password')

    def get_autoreconnect(self):
        # return the value of 'auto_reconnect' stored in the CONNECTION section
        return self.get_key('CONNECTION', 'auto_reconnect')

    def get_enablelogging(self):
        # return the value of 'enable_logging' stored in the CONNECTION section
        return self.get_key('CONNECTION', 'enable_logging')

    def get_autojoinchans(self):
        # return the value of 'autojoin_channels' stored in the CONNECTION section
        return self.get_key('CONNECTION', 'autojoin_channels')

    def get_configfile(self):
        # return the value of 'config_file' stored in the PATHS section
        return self.get_key('PATHS', 'config_file')

    def get_logfile(self):
        # return the value of 'log_file' stored in the PATHS section
        return self.get_key('PATHS', 'log_file')

    def set_nickname(self, nickname):
        # sets the value of 'nickname'
        return self.add_key('IDENTITY', 'nickname', str(nickname))

    def set_username(self, username):
        # sets the value of 'username'
        return self.add_key('IDENTITY', 'username', str(username))

    def set_realname(self, realname):
        # sets the value of 'realname'
        return self.add_key('IDENTITY', 'realname', str(realname))

    def set_nickservpass(self, nickserv_password):
        # sets the value of 'nickserv_password'
        return self.add_key('IDENTITY', 'nickserv_password', str(nickserv_password))

    def set_serveraddress(self, server_address):
        # sets the value of 'server_address'
        return self.add_key('CONNECTION', 'server_address', str(server_address))

    def set_serverport(self, server_port):
        # sets the value of 'server_port'
        return self.add_key('CONNECTION', 'server_port', str(server_port))

    def set_serverpass(self, server_password):
        # sets the value of 'server_password'
        return self.add_key('CONNECTION', 'server_password', str(server_password))

    def set_autoreconnect(self, auto_reconnect):
        # sets the value of 'auto_reconnect'
        return self.add_key('CONNECTION', 'auto_reconnect', str(auto_reconnect))

    def set_enablelogging(self, enable_logging):
        # sets the value of 'enable_logging'
        return self.add_key('CONNECTION', 'enable_logging', str(enable_logging))

    def set_autojoinchans(self, autojoin_channels):
        # sets the value of 'autojoin_channels'
        return self.add_key('CONNECTION', 'autojoin_channels', str(autojoin_channels))

    def set_configfile(self, config_file):
        # sets the value of 'config_file'
        return self.add_key('PATHS', 'config_file', str(config_file))

    def set_logfile(self, log_file):
        # sets the value of 'log_file'
        return self.add_key('PATHS', 'log_file', str(log_file))
