""" show_card_detail.py
    supports commands:
        * show lag statistics
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


class ShowLagStatisticsSchema(MetaParser):
    """Schema for show lag statistics"""
    schema = {
    }


class ShowLagStatistics(ShowLagStatisticsSchema):
    """ Parser for show lag statistics"""

    cli_command = 'show lag statistics'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # ===============================================================================
        # LAG Statistics
        # ===============================================================================
        # -------------------------------------------------------------------------------
        # LAG 7
        # -------------------------------------------------------------------------------
        # Description        : To CR02-Nokia-NGCore LAG 7
        # Port-id       Input(Packets)                   Output(Packets)
        #               Input(Bytes)                     Output(Bytes)
        #               Input Errors                     Output Errors
        # -------------------------------------------------------------------------------
        # 1/1/c10/1     84634793                         58634263
        #               48245673755                      27005346688
        #               0                                0
        # -------------------------------------------------------------------------------
        # Totals        84634793                         58634263
        #               48245673755                      27005346688
        #               0                                0

        parsed = {}

        for line in out.splitlines():
            m = re.search(r'^LAG (\d+)$', line)
            if m:
                lagd = parsed[m.group(1)] = {}
                lpid = lagd['Port-id'] = list()
                continue

            m = re.search(r'^Description +: +\b(.*)$', line)
            if m:
                lagd['Description'] = m.group(1)
                continue

            m = re.search(r'^(\d\S+) +(\d+) +(\d+)$', line)
            if m:
                if m.group(1) not in lpid:
                    lpid.append(m.group(1))
                portd = lagd[m.group(1)] = {
                    'Input(Packets)': m.group(2),
                    'Output(Packets)': m.group(3)}
                portstat = True
                nextbyte = True

            m = re.search(r'^Totals +(\d+) +(\d+)$', line)
            if m:
                totald = lagd['Totals'] = {
                    'Input(Packets)': m.group(1),
                    'Output(Packets)': m.group(2)}
                totalstat = True
                nextbyte = True

            m = re.search(r'^\s{14}(\d+) +(\d+)$', line)
            if m:
                if portstat:
                    # deal with port stats lines
                    if nextbyte:
                        portd['Input(Bytes)'] = m.group(1)
                        portd['Output(Bytes)'] = m.group(2)
                        nextbyte = False
                    else:
                        portd['Input Error'] = m.group(1)
                        portd['Output Error'] = m.group(2)
                        portstat = False
                else:
                    # deal with lag total stats lines
                    if nextbyte:
                        totald['Input(Bytes)'] = m.group(1)
                        totald['Output(Bytes)'] = m.group(2)
                        nextbyte = False
                    else:
                        totald['Input Error'] = m.group(1)
                        totald['Output Error'] = m.group(2)
                        totalstat = False

        return parsed
