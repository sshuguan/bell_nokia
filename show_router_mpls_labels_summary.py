""" show_router_mpls-labels_summary.py
    supports commands:
        * show router mpls-labels summary
"""

# Python
import re

# Metaparser
from genie.metaparser import MetaParser
from genie.metaparser.util.schemaengine import Schema, Any, Optional

# parser utils
from genie.libs.parser.utils.common import Common

# =============================================
# Parser for 'show router mpls-labels summary'
# =============================================


class ShowRouterMplsLabelsSummarySchema(MetaParser):
    """Schema for show router mpls-labels summary"""
    schema = {
    }


class ShowRouterMplsLabelsSummary(ShowRouterMplsLabelsSummarySchema):
    """ Parser for show router mpls-labels summary"""

    cli_command = 'show router mpls-labels summary'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

            # ===============================================================================
            # Mpls-Labels Summary
            # ===============================================================================
            # Static Label Range             : 15968
            # Bgp Labels Hold Timer          : 0
            # Segment Routing Start Label    : 16000
            # Segment Routing End Label      : 81534
            # ===============================================================================

        parsed = {}

        for line in out.splitlines():
            # add key:value in dict when hitting line such as
            # "Static Label Range             : 15968"
            # "Segment Routing End Label      : 81534"
            m = re.search(r'^\b(.+)\b +: +\b(.+)\b$', line)
            if m:
                parsed[m.group(1)] = m.group(2)

        return parsed
