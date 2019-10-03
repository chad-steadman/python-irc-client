# python-irc-client
A simple Internet Relay Chat (IRC) client created in Python

## Description
This project aims to create a basic IRC client with a GUI from scratch using Python sockets and wxPython. It is currently a work-in-progress.

[wxGlade](http://wxglade.sourceforge.net/) is the tool being used to create the wxPython GUI. The `gui.wxg` file can be opened in wxGlade in order to edit the GUI.

The protocols for properly communicating with IRC servers is laid out by [RFC 1459](https://tools.ietf.org/html/rfc1459) and [RFC 2812](https://tools.ietf.org/html/rfc2812). Great care has been taken to ensure the underlying socket programming conforms to the standards put forth by these documents.

## Requirements
- [Python 3.5+](https://www.python.org/downloads/)
- [wxPython](https://wxpython.org/) `pip install -U wxPython`
