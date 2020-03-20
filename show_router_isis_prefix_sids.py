""" show_card_detail.py
    supports commands:
        * show router isis prefix-sids
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


class ShowRouterIsisPrefixSidsSchema(MetaParser):
    """Schema for show router isis prefix-sids"""
    schema = {
    }


class ShowRouterIsisPrefixSids(ShowRouterIsisPrefixSidsSchema):
    """ Parser for show router isis prefix-sids"""

    cli_command = 'show router isis prefix-sids'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # ===============================================================================
        # Rtr Base ISIS Instance 0 Prefix/SID Table
        # ===============================================================================
        # Prefix                            SID        Lvl/Typ    SRMS   AdvRtr
        #                                                          MT     Flags
        # -------------------------------------------------------------------------------
        # 67.70.219.13/32                   213        2/Int.      N     CR01-Nokia-
        #                                                                NGCore
        #                                                             0       NnP
        # 67.70.219.14/32                   214        2/Int.      N     CR02-Nokia-
        #                                                                NGCore
        #                                                             0       NnPm.
        # 67.70.219.15/32                   215        2/Int.      N     newbx1_RE0
        #                                                             0       N

        parsed = {}

        for line in out.splitlines():
            m = re.search(r'^Rtr Base ISIS Instance (\d) Prefix/SID Table', line)
            if m:
                instanced = parsed[m.group(1)] = {}
                continue

            m = re.search(r'^(\d\S+) +(\S+) +(\S+) +(\S) +(\S+)$', line)
            if m:
                prefixd = instanced[m.group(1)] = {
                    'SID': m.group(2),
                    'Lvl/Typ': m.group(3),
                    'SRMS': m.group(4),
                    'AdvRtr': m.group(5)}
                continue

            m = re.search(r'^\s{63}(\S+)$', line)
            if m:
                prefixd['AdvRtr'] += m.group(1)
                continue

            m = re.search(r'^\s{60}(\d) +(\S+)$', line)
            if m:
                prefixd['MT'] = m.group(1)
                prefixd['Flags'] = m.group(2)

        return parsed
