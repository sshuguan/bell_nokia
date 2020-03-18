""" show_card_detail.py
    supports commands:
        * show router isis routes
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


class ShowRouterIsisRoutesSchema(MetaParser):
    """Schema for show card detail"""
    schema = {
    }


class ShowRouterIsisRoutes(ShowRouterIsisRoutesSchema):
    """ Parser for show system cpu"""

    cli_command = 'show router isis routes'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # ===============================================================================
        # Rtr Base ISIS Instance 0 Route Table
        # ===============================================================================
        # Prefix[Flags]                     Metric     Lvl/Typ     Ver.  SysID/Hostname
        #   NextHop                                                MT     AdminTag/SID[F]
        # -------------------------------------------------------------------------------
        # 10.55.93.144/31                   2485       2/Int.      4     CR02-Cisco-
        #                                                                NGCore
        #    172.16.1.206                                            0       0
        # 10.55.93.152/31                   2485       2/Int.      4     CR02-Cisco-
        #                                                                NGCore
        #    172.16.1.206                                            0       0
        # 10.55.93.164/31                   2485       2/Int.      4     CR02-Cisco-
        #                                                                NGCore
        #    172.16.1.206                                            0       0
        # 10.55.93.166/31                   2485       2/Int.      4     CR02-Cisco-

        parsed = {}

        for line in out.splitlines():
            m = re.search(r'^Rtr Base ISIS Instance (\d) Route Table', line)
            if m:
                instanced = parsed[m.group(1)] = {}
                continue

            m = re.search(r'^(\d\S+) +(\S+) +(\S+) +(\d) +(\S+)$', line)
            if m:
                prefixd = instanced[m.group(1)] = {
                    'Metric': m.group(2),
                    'Lvl/Typ': m.group(3),
                    'Ver': m.group(4),
                    'SysID/Hostname': m.group(5)}
                continue

            m = re.search(r'^\s{63}(\S+)$', line)
            if m:
                prefixd['SysID/Hostname'] += m.group(1)
                continue

            m = re.search(r'^\s{3}(\d\S+) +(\S+) +(\S+)$', line)
            if m:
                prefixd['NextHop'] = m.group(1)
                prefixd['MT'] = m.group(2)
                prefixd['AdminTag/SID'] = m.group(3)

        return parsed
