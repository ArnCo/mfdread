#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .mifareclassic import MifareClassic
from .mifareultralight import MifareUltralight


class MifareCardFactory:

    MIFARE_ULTRALIGHT_SIZES = {64, 80}
    MIFARE_CLASSIC_SIZES = {1024, 4096}

    def __init__(self):
        pass

    def create(data):
        data_size = len(data)
        if data_size in MifareCardFactory.MIFARE_CLASSIC_SIZES:
            return MifareClassic(data)
        elif data_size in MifareCardFactory.MIFARE_ULTRALIGHT_SIZES:
            return MifareUltralight(data)
        else:
            return None

