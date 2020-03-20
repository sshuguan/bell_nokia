""" show_card_detail.py
    supports commands:
        * show card detail
"""

# Python
import re

# Metaparser
from genie.metaparser import MetaParser
from genie.metaparser.util.schemaengine import Schema, Any, Optional

# parser utils
from genie.libs.parser.utils.common import Common

# =============================================
# Parser for 'show system memory-pools'
# =============================================


class ShowCardDetailSchema(MetaParser):
    """Schema for show card detail"""
    schema = {
    }


class ShowCardDetail(ShowCardDetailSchema):
    """ Parser for show system cpu"""

    cli_command = 'show card detail'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        elif re.search(r'^[\dAB]$', output):
            self.cli_command = 'show card %s detail' % output
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # ===============================================================================
        # Card A
        # ===============================================================================
        # Slot      Provisioned Type                         Admin Operational   Comments
        #               Equipped Type (if different)         State State
        # -------------------------------------------------------------------------------
        # A         cpm-v                                    up    up/active
        # BOF last modified                 : N/A
        # Config file version               : TUE FEB 11 14:36:42 2020 UTC
        # Config file last modified         : N/A
        # Config file last saved            : N/A
        # M/S clocking ref state            : not initialized
        # Universally unique identifier     : 2923e95c-b5b2-4562-929b-05a4808b3d61
        #
        # Flash - cf1:
        #     Administrative State          : up
        #     Operational state             : not equipped
        #
        # Flash - cf2:
        #     Administrative State          : up
        #     Operational state             : not equipped
        #
        # Flash - cf3:
        #     Administrative State          : up
        #     Operational state             : up
        #     Serial number                 : serial-3
        #     Firmware revision             : v1.0
        #     Model number                  : PC HD 3
        #     Size                          : 1,189 MB
        #     Free space                    : 791,508 KB
        #     Percent Used                  : 35 %
        #
        # Virtual Machine Card Specific Data
        #     Hypervisor                    : KVM/QEMU
        #     CPU                           : Intel Core Processor (Skylake)
        #     Number of cores               : 4
        #
        # Hardware Data
        #     Platform type                 : 7750
        #     Administrative state          : up
        #     Operational state             : up
        #     Software version              : TiMOS-B-19.10.R2 both/x86_64 Nokia 7750 SR
        #                                     Copyright (c) 2000-2019 Nokia.
        #                                     All rights reserved. All use subject to
        #                                     applicable license agreements.
        #                                     Built on Mon Dec 16 15:37:51 PST 2019 by
        #                                     builder in /builds/c/1910B/R2/panos/main
        #     Time of last boot             : 2020/02/13 21:01:51
        #     Base MAC address              : 00:00:02:00:00:00
        #     Firmware revision status      : acceptable
        #     Memory capacity               : 16,384 MB

        parsed = {}
        if re.search(r'MINOR: MGMT_CORE #2301', out):
            return parsed

        # split <out> into list
        s0 = re.compile(r'\r?\n=+\r?\nCard \w+\r?\n=+\r?\n')
        cardL = s0.split(out)

        for card in cardL:
            slot = None
            if not card:
                continue

            tmpL = card.splitlines()
            # deal with card state line
            # A         cpm-v                up    up/active
            m = re.search(r'(\w+) +(\S+) +(\S+) +(\S+)',tmpL[3])
            if m:
                slot = m.group(1)
                slotd = parsed[slot] = {
                    'provisioned type': m.group(2),
                    'admin state': m.group(3),
                    'operational state': m.group(4)}

            # deal with rest data started from 4th line
            subkey = subkey2 = None
            for line in tmpL[4:]:
                # add key:value in dict when hitting line such as
                # "Config file version    : TUE FEB 11 14:36:42 2020 UTC"
                # "M/S clocking ref state : not initialized"
                m = re.search(r'^\b(.+)\b +: +\b(.+)\b$', line)
                if slot and m:
                    parsed[slot][m.group(1)] = m.group(2)
                    continue
                # create sub-dict when hitting line such as
                # "Hardware Data"
                # "Flash -cf3:"
                m = re.search(r'^\b([\w\-() ]+):?$', line)
                if m:
                    subkey = m.group(1)
                    sub1d = slotd[subkey] = {}
                    continue
                # create sub-sub-dict when hitting line
                # "    Voltage"
                # "    Wattage"
                # "    Amperage"
                m = re.search(r'^\s{4}\b(\w+)\b$', line)
                if 'subkey' and m:
                    subkey2 = m.group(1)
                    sub2d = sub1d[subkey2] = {}
                    continue
                # add key:value when hitting line such as
                # "    Platform type                 : 7750"
                m = re.search(r'^\s{4}\b(.+)\b +: +\b(.+)$', line)
                if m and slot and subkey:
                    sub1d[m.group(1)] = m.group(2)
                    continue
                # add key:value when hitting line such as
                # "        Minimum : 54.56 Volts  (02/21/2020 16:21:40)"
                m = re.search(r'^\s{8}\b(.+)\b +: +\b(.+)$', line)
                if m and slot and subkey and subkey2:
                    sub2d[m.group(1)] = m.group(2)

        return parsed
