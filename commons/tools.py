#!/usr/bin/env python
# -*- coding: utf-8 -*-


import codecs


class BashColors:
    BLUE = '\033[34m'
    RED = '\033[91m'
    GREEN = '\033[32m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'


def decode(bytes_to_decode):
    decoded = codecs.decode(bytes_to_decode, "hex")
    try:
        return str(decoded, "utf-8").rstrip(b'\0')
    except:
        return ""


def colorize(text, color):
    return color + text + BashColors.ENDC

