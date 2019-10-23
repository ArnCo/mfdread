#!/usr/bin/env python
# -*- coding: utf-8 -*-
from cards import mifarecard
import codecs
from bitstring import BitArray
from commons.tools import *
import copy


class MifareUltralight(mifarecard.MifareCard):

    def __init__(self, data):
        super(MifareUltralight, self).__init__(data)
        self.initial_page_matrix = []
        self.page_matrix = []
        self.page_number = 0
        self.lock_bytes = {}

    def extract_data(self):
        data = self.data

        # read all pages
        start = 0
        end = 4
        while True:
            page = data[start:end]
            page = codecs.encode(page, 'hex')
            if not isinstance(page, str):
                page = str(page, 'ascii')

            page = [page[x:x + 2] for x in range(0, len(page), 2)]

            start += 4
            end += 4

            self.page_number += 1
            self.page_matrix.append(page)

            if start == len(data):
                break

        return self.page_matrix

    def print_general_info(self):
        print("File size: %d bytes. Expected %d pages" % (self.data_size, self.page_number))
        print("\n\tUID:  " + " ".join(self.page_matrix[0][0:3]) + " " + " ".join(self.page_matrix[1][0:4]))
        print("\tBCC0:  " + self.page_matrix[0][3])
        print("\tBCC1:  " + self.page_matrix[2][0])
        print("\tINT:  " + self.page_matrix[2][1])
        print("\tLOCK:  " + " ".join(self.page_matrix[2][2:4]) + "\n")

    @staticmethod
    def description_for_page(page):
        # Description for given page
        if page == 0:
            description = "%s              ║ %s    " % (
                colorize("UID part 1", BashColors.BLUE),
                colorize("BCC0", BashColors.WARNING))
        elif page == 1:
            description = "%s                        " % (
                colorize("UID part 2", BashColors.BLUE))
        elif page == 2:
            description = "%s ║ %s ║ %s      " % (
                colorize("BCC1", BashColors.WARNING),
                colorize("Internal", BashColors.BLUE),
                colorize("Lock bytes", BashColors.WARNING))
        elif page == 3:
            description = "OTP (One Time Programmable)"
        elif page < 16:
            description = "User Memory pages"
        elif page == 16:
            description = "CFG0 (Configuration page)"
        elif page == 17:
            description = "CFG1 (Configuration page)"
        elif page == 18:
            description = "PWD (Password)"
        elif page == 19:
            description = "PACK | RFUI (PWD ACK)"

        return description

    def extract_lock_bytes(self):
        raw_lock_bytes = [BitArray("0x" + self.initial_page_matrix[2][2], 8),
                          BitArray("0x" + self.initial_page_matrix[2][3], 8)]

        # Init lock pages VP4 to P7
        for i in range(0, 4):
            desc = "P" + str(7 - i)
            self.lock_bytes[desc] = raw_lock_bytes[0][i]

        # Initialize lock bits
        self.lock_bytes["OTP"] = raw_lock_bytes[0][4]

        self.lock_bytes["BL15-10"] = raw_lock_bytes[0][5]

        self.lock_bytes["BL9-4"] = raw_lock_bytes[0][6]

        self.lock_bytes["BLOTP"] = raw_lock_bytes[0][7]

        for i in range(0, 8):
            desc = "P" + str(15 - i)
            self.lock_bytes[desc] = raw_lock_bytes[1][i]

    def colorize_lock_byte(self, desc, format, color=None):
        if not color:

            if self.lock_bytes[desc]:
                color = BashColors.RED
            else:
                color = BashColors.GREEN

        if format == "desc":
            return colorize(desc, color) + " "
        else:
            return colorize(str(int(self.lock_bytes[desc])), color)

    def print_lock_bytes(self, lock_byte, format):
        to_print = ""

        if lock_byte == 0:
            # Print lock pages VP4 to P7
            for i in range(0, 4):
                color = None
                desc = "P" + str(7 - i)
                if self.lock_bytes["BL9-4"]:
                    color = BashColors.RED

                to_print += self.colorize_lock_byte(desc, format, color)

            # Print lock bits
            if self.lock_bytes["BLOTP"]:
                to_print += self.colorize_lock_byte("OTP", format, BashColors.RED)
            else:
                to_print += self.colorize_lock_byte("OTP", format)

            to_print += self.colorize_lock_byte("BL15-10", format)

            to_print += self.colorize_lock_byte("BL9-4", format)

            to_print += self.colorize_lock_byte("BLOTP", format)

        if lock_byte == 1:
            # Init lock pages 8 to P15
            for i in range(0, 8):
                color = None
                desc = "P" + str(15 - i)
                if self.lock_bytes["BL9-4"] and i > 4:
                    color = BashColors.RED
                if self.lock_bytes["BL15-10"] and i <= 3:
                    color = BashColors.RED
                to_print += self.colorize_lock_byte(desc, format, color)

        return to_print

    def colorize_page(self, page_index, byte):
        if page_index == 3:
            if self.lock_bytes["OTP"]:
                return colorize(byte, BashColors.RED)
            else:
                return colorize(byte, BashColors.GREEN)

        if self.lock_bytes["P" + str(page_index)]:
            return colorize(byte, BashColors.RED)
        else:
            return colorize(byte, BashColors.GREEN)

    def print_info(self):
        #Extract data as a matrix
        self.initial_page_matrix = self.extract_data()
        self.page_matrix = copy.deepcopy(self.page_matrix)
        self.extract_lock_bytes()

        #Print general info from two first pages
        self.print_general_info()

        print("%s %s" % (
            colorize("Locked bytes", BashColors.RED),
            colorize("Modifiable bytes", BashColors.GREEN)))
        print("╔═════════╦═══════════════════════════════════════════════╦═════════════════════════════════════╗")
        print("║  Page   ║                     Data                      ║               Description           ║")
        print("╠════╦════╬═══════════╦═══════════╦═══════════╦═══════════╬═════════════════════════════════════╣")
        print("║Dec ║Hex ║     0     ║     1     ║     2     ║     3     ║                                     ║")

        for page in range(0, len(self.page_matrix)):
            print("╠════╬════╬═══════════╬═══════════╬═══════════╬═══════════╬═════════════════════════════════════╣")

            description = self.description_for_page(page)

            # UID part 1 + BCC0 + UID part 2
            for i in range(0, 4):
                color = None
                if page <= 1:
                    if page == 0 and i == 3:
                        color = BashColors.WARNING
                    else:
                        color = BashColors.BLUE
                    self.page_matrix[page][i] = colorize(self.page_matrix[page][i], color)

                # BCC1 + Internal + Lock bytes
                elif page == 2:
                    if i == 1:
                        color = BashColors.BLUE
                    else:
                        color = BashColors.WARNING
                    self.page_matrix[page][i] = colorize(self.page_matrix[page][i], color)

                elif page < 16:
                    self.page_matrix[page][i] = self.colorize_page(page, self.page_matrix[page][i])

            print("║ %02d ║ %02x ║     %s    ║     %s    ║     %s    ║     %s    ║  %-34s ║"
                  % (page, page, self.page_matrix[page][0], self.page_matrix[page][1], self.page_matrix[page][2],
                     self.page_matrix[page][3], description))
            if page == 2:
                print("║    ║    ║           ║           ║  %s ║  %s ║ %-34s║"
                      % (self.print_lock_bytes(0, "bin"),
                         self.print_lock_bytes(1, "bin"),
                         self.print_lock_bytes(0, "desc")))
                print("║    ║    ║           ║           ║           ║           ║ %-34s      ║"
                      % (self.print_lock_bytes(1, "desc")))

        print("╚════╩════╩═══════════╩═══════════╩═══════════╩═══════════╩═════════════════════════════════════╝")
