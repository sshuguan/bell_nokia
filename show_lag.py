""" show_lag.py
    supports commands:
        * show lag
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


class ShowLagSchema(MetaParser):
    """Schema for show lag"""
    schema = {
    }


class ShowLag(ShowLagSchema):
    """ Parser for show lag"""

    cli_command = 'show lag'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # ===============================================================================
        # Lag Data
        # ===============================================================================
        # Lag-id         Adm     Opr     Weighted Threshold Up-Count MC Act/Stdby
        # -------------------------------------------------------------------------------
        # 7              up      up      No       0         2        N/A
        # 52             up      down    No       0         0        N/A
        # 54             up      up      No       0         2        N/A
        # 102            up      up      No       0         2        N/A
        # 150            up      up      No       0         2        N/A
        # 151            up      up      No       0         2        N/A
        # 152            up      up      No       0         1        N/A
        # -------------------------------------------------------------------------------
        # Total Lag-ids: 7       Single Chassis: 7        MC Act: 0       MC Stdby: 0
        # ===============================================================================

        parsed = {}
        lagd = parsed['Lag-id'] = {}

        for line in out.splitlines():
            m = re.search(r'^(\d+) +(\S+) +(\S+) +(\S+)'
                          r' +(\d+) +(\d+) +(\S+)$', line)
            if m:
                lagd[m.group(1)] = {
                    'Adm': m.group(2), 'Opr': m.group(3),
                    'Weighted': m.group(4), 'Threshold': m.group(5),
                    'Up-Count': m.group(6), 'MC Act/Stdby': m.group(7)}
                continue
            m = re.search(r'^Total Lag-ids: *(\d+)'
                          r' +Single Chassis: *(\d+)'
                          r' +MC Act: *(\d+) +MC Stdby: *(\d+)$', line)
            if m:
                parsed['Total Lag-id'] = int(m.group(1))
                parsed['Single Chassis'] = int(m.group(2))
                parsed['MC Act'] = int(m.group(3))
                parsed['MC Stdby'] = int(m.group(4))

        return parsed
