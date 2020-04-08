""" show_card_detail.py
    supports commands:
        * show lag detail
"""

# Python
import re

# Metaparser
from genie.metaparser import MetaParser
from genie.metaparser.util.schemaengine import Schema, Any, Optional

# parser utils
from genie.libs.parser.utils.common import Common

# =============================================
# Parser for 'show lag detail'
# =============================================


class ShowLagDetailSchema(MetaParser):
    """Schema for show lag detail"""
    schema = {
    }


class ShowLagDetail(ShowLagDetailSchema):
    """ Parser for show lag detail"""

    cli_command = 'show lag detail'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # ===============================================================================
        # LAG Details
        # ===============================================================================
        # -------------------------------------------------------------------------------
        # LAG 7
        # -------------------------------------------------------------------------------
        # Description        : To CR02-Nokia-NGCore LAG 7
        # -------------------------------------------------------------------------------
        # Details
        # -------------------------------------------------------------------------------
        # Lag-id              : 7                     Mode                 : network
        # Adm                 : up                    Opr                  : up
        # Thres. Last Cleared : 02/10/2020 08:01:04   Thres. Exceeded Cnt  : 0
        # Dynamic Cost        : false                 Encap Type           : null
        # Configured Address  : 10:e8:78:3e:51:48     Lag-IfIndex          : 1342177287
        # Hardware Address    : 10:e8:78:3e:51:48
        # Per-Link-Hash       : disabled
        # Include-Egr-Hash-Cfg: disabled              Forced               : -
        # Per FP Ing Queuing  : disabled              Per FP Egr Queuing   : disabled
        # Per FP SAP Instance : disabled
        # Access Bandwidth    : N/A                   Access Booking Factor: 100
        # Access Available BW : 0
        # Access Booked BW    : 0
        # LACP                : enabled               Mode                 : active
        # LACP Transmit Intvl : fast                  LACP xmit stdby      : enabled
        # Selection Criteria  : highest-count         Slave-to-partner     : disabled
        # MUX control         : coupled
        # Subgrp hold time    : 0.0 sec               Remaining time       : 0.0 sec
        # Subgrp selected     : 1                     Subgrp candidate     : -
        # Subgrp count        : 1
        # System Id           : 10:e8:78:3e:50:01     System Priority      : 32768
        # Admin Key           : 7                     Oper Key             : 7
        # Prtr System Id      : 10:e8:78:3e:40:01     Prtr System Priority : 32768
        # Prtr Oper Key       : 7
        # Standby Signaling   : lacp
        # Port hashing        : port-speed            Port weight speed    : 0 gbps
        # Ports Up            : 1
        # Weights Up          : 1                     Hash-Weights Up      : 100
        # Monitor oper group  : N/A
        #
        # -------------------------------------------------------------------------------
        # Port-id        Adm     Act/Stdby Opr     Primary   Sub-group     Forced  Prio
        # -------------------------------------------------------------------------------
        # 1/1/c10/1      up      active    up      yes       1             -       32768
        #
        # -------------------------------------------------------------------------------
        # Port-id        Role      Exp   Def   Dist  Col   Syn   Aggr  Timeout  Activity
        # -------------------------------------------------------------------------------
        # 1/1/c10/1      actor     No    No    Yes   Yes   Yes   Yes   Yes      Yes
        # 1/1/c10/1      partner   No    No    Yes   Yes   Yes   Yes   Yes      Yes

        parsed = {}

        for line in out.splitlines():
            m = re.search(r'^LAG (\d+)$', line)
            if m:
                lagd = parsed[m.group(1)] = {}
                lpid = lagd['Port-id'] = {}
                continue

            m = re.search(r'^Description +: +\b(.*)$', line)
            if m:
                lagd['Description'] = m.group(1)
                continue

            m = re.search(r'^(.{20}): (.{21}) (.{21}): +(\S+)$', line)
            if m:
                lagd[m.group(1).strip()] = m.group(2).strip()
                lagd[m.group(3).strip()] = m.group(4)
                continue

            m = re.search(r'^(.{20}): (\S+)\s*?$', line)
            if m:
                lagd[m.group(1).strip()] = m.group(2)

            m = re.search(r'^(\d\S+) +(\S+) +(\S+) +(\S+)'
                          r' +(\S+)? +(\S+) +(\S+) +(\S+)$', line)
            if m:
                lpid[m.group(1)] = {
                    'Adm': m.group(2), 'Act/Stdby': m.group(3),
                    'Opr': m.group(4), 'Primary': m.group(5),
                    'Sub-group': m.group(6), 'Forced': m.group(7),
                    'Prio': m.group(8)}

            m = re.search(r'^(\d\S+) +(actor|partner) +(\S+) +(\S+)'
                          r' +(\S+) +(\S+) +(\S+) +(\S+) +(\S+) +(\S+)$', line)
            if m:
                lpid[m.group(1)][m.group(2)] = {
                    'Exp': m.group(3), 'Def': m.group(4),
                    'Dist': m.group(5), 'Col': m.group(6),
                    'Syn': m.group(7), 'Aggr': m.group(8),
                    'Timeout': m.group(9), 'Activity': m.group(10)}

        return parsed
