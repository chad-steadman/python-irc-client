#!/usr/bin/env python
import configparser


class Config:
    def __init__(self, filename=''):
        self._filename = filename
        self._config = configparser.ConfigParser()

    def set_filename(self, filename):
        # sets the filename for saving/loading
        self._filename = filename

    def get_filename(self):
        # returns the set filename
        return self._filename

    def save_to_file(self):
        # saves the configuration to a file
        try:
            # file saved successfully -- return 1
            with open(self._filename, 'w') as configfile:
                self._config.write(configfile)
                return 1
        except IOError:
            # there was an error saving the file -- return 0
            return 0

    def load_from_file(self):
        # loads a configuration from an existing file
        try:
            # file loaded successfully -- return 1
            with open(self._filename, 'r') as configfile:
                self._config.read_file(configfile)
            return 1
        except IOError:
            # there was an error loading the file -- return 0
            return 0

    def add_section(self, section):
        # adds a new section to the configparser
        try:
            self._config.add_section(section)
            return 1
        except configparser.Error:
            return 0

    def add_key(self, section, key, value):
        # adds a new key/value pair under the specified section header
        try:
            self._config[section][key] = value
            return 1
        except configparser.Error:
            return 0

    def remove_key(self, section, key):
        # removes a key/value pair from the specified section header
        try:
            self.remove_key(section, key)
            return 1
        except configparser.Error:
            return 0

    def get_key(self, section, key):
        # retrieves a key/value pair from the specified section header
        try:
            value = self._config[section][key]
            return value
        except configparser.Error:
            return 0

    def get_sections(self):
        # retrieves a list of all the sections in the configparser object
        return self._config.sections()

    def get_options(self, section):
        # retrieves a list of all the options under the specified section
        return self._config.options(section)
