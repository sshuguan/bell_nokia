""" show_router_routetable.py
    supports commands:
        * show router route-table
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


class ShowRouterRoutetableSchema(MetaParser):
    """Schema for show router route-table"""
    schema = {
    }


class ShowRouterRoutetable(ShowRouterRoutetableSchema):
    """ Parser for show router route-table"""

    cli_command = 'show router route-table'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # ===============================================================================
        # Route Table (Router: Base)
        # ===============================================================================
        # Dest Prefix[Flags]                            Type    Proto     Age        Pref
        #       Next Hop[Interface Name]                                    Metric
        # -------------------------------------------------------------------------------
        # 10.10.10.0/30                                 Local   Local     01d23h50m  0
        #        to-ixia-4/7                                                  0
        # 10.55.93.144/31                               Remote  ISIS      22h17m22s  18
        #        172.16.3.117                                                 2485
        # 10.55.93.150/31                               Remote  ISIS      22h17m22s  18
        #        172.16.3.117                                                 2485

        parsed = {}

        for line in out.splitlines():
            m = re.search(r'^(\d\S+) +(\S+) +(\S+) +(\S+) +(\S+)$', line)
            if m:
                prefixd = parsed[m.group(1)] = {
                    'Type': m.group(2), 'Proto': m.group(3),
                    'Age': m.group(4), 'Pref': m.group(5)}
                continue

            m = re.search(r'^\s{7}(\S+) +(\S+)$', line)
            if m:
                prefixd['Next Hop'] = m.group(1)
                prefixd['Metric'] = m.group(2)

        return parsed
