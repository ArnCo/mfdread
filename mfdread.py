#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  mfdread.py - Mifare dumps parser in human readable format
#  Pavel Zhovner <pavel@zhovner.com>
#  https://github.com/zhovner/mfdread
#  Arnaud Cordier arnaud*at<*>cordier.work
#  Partial rewrite and implementation of MifareUltralight parser

import argparse
import sys
from cards import MifareCardFactory
from collections import defaultdict

from bitstring import BitArray


class Options:
    FORCE_1K = False


def main(args):
    if args.force_1k:
        Options.FORCE_1K = True

    filename = args.card_dump
    with open(filename, "rb") as f:
        data = f.read()
        mifare_card = MifareCardFactory.create(data)
        if mifare_card:
            mifare_card.print_info()
        else:
            sys.exit("Card not supported. You can try to implement your own module and submit a pull request :)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mifare dumps reader.")
    parser.add_argument('-c', '--card-dump', help='Card dump', required=True)
    parser.add_argument('-f', '--force-1k', help='Force Mifare 1k', required=False)
    args = parser.parse_args()

    main(args)
