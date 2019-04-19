#!/usr/bin/env python
import configparser


class Config:
    def __init__(self, filename):
        self.filename = filename
        self.config = configparser.ConfigParser()

    def set_filename(self, filename):
        # sets the filename for saving/loading
        self.filename = filename

    def get_filename(self):
        # returns the set filename
        return self.filename

    def save_to_file(self):
        # saves the configuration to a file
        try:
            # file saved successfully -- return 1
            with open(self.filename, 'w') as configfile:
                self.config.write(configfile)
                return 1
        except IOError:
            # there was an error saving the file -- return 0
            return 0

    def load_from_file(self):
        # loads a configuration from an existing file
        try:
            # file loaded successfully -- return 1
            with open(self.filename, 'r') as configfile:
                self.config.read_file(configfile)
            return 1
        except IOError:
            # there was an error loading the file -- return 0
            return 0

    def add_section(self, section):
        # adds a new section to the configparser
        try:
            self.config.add_section(section)
            return 1
        except configparser.Error:
            return 0

    def add_key(self, section, key, value):
        # adds a new key/value pair under the specified section header
        try:
            self.config[section][key] = value
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
            value = self.config[section][key]
            return value
        except configparser.Error:
            return 0

    def get_sections(self):
        # retrieves a list of all the sections in the configparser object
        return self.config.sections()

    def get_options(self, section):
        # retrieves a list of all the options under the specified section
        return self.config.options(section)
