""" show_lag_flowdistribution.py
    supports commands:
        * show lag <log-id> flow-distribution
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


class ShowLagFlowdistributionSchema(MetaParser):
    """Schema for show lag <log-id> flow-distribution"""
    schema = {
    }


class ShowLagFlowdistribution(ShowLagFlowdistributionSchema):
    """ Parser for show lag <log-id> flow-distribution"""

    cli_command = 'show lag %s flow-distribution'

    def cli(self, output):
        if type(output) == int:
            out = self.device.execute(self.cli_command % output)
        else:
            out = output

        # ===============================================================================
        # Distribution of allocated flows
        # ===============================================================================
        # Port                        Bandwidth (Gbps) Hash-weight  Flow-share (%)
        # -------------------------------------------------------------------------------
        # 1/1/c13/1                   100.000          100          50.00
        # 1/1/c14/1                   100.000          100          50.00
        # -------------------------------------------------------------------------------
        # Total operational bandwidth: 200.000
        # ===============================================================================

        parsed = {}

        for line in out.splitlines():
            m = re.search(r'^(\d\S+) +(\d\S+) +(\d+) +(\d\S+)$', line)
            if m:
                parsed[m.group(1)] = {
                    'Bandwidth': int(m.group(2).split('.')[0]),
                    'Hash-weight': m.group(3),
                    'Flow-share': int(m.group(4).split('.')[0])}
                continue
            m = re.search(r'^Total operational bandwidth: *(\d\S+)$', line)
            if m:
                parsed['Total operational bandwidth'] = int(
                    m.group(1).split('.')[0])

        return parsed
