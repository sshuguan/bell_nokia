""" show_card_detail.py
    supports commands:
        * show router bfd session
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


class ShowRouterBfdSessionSchema(MetaParser):
    """Schema for show router bfd session"""
    schema = {
    }


class ShowRouterBfdSession(ShowRouterBfdSessionSchema):
    """ Parser for show router bfd session"""

    cli_command = 'show router bfd session'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # ===============================================================================
        # Legend:
        #   Session Id = Interface Name | LSP Name | Prefix | RSVP Sess Name | Service Id
        #   wp = Working path   pp = Protecting path
        # ===============================================================================
        # BFD Session
        # ===============================================================================
        # Session Id                                        State      Tx Pkts    Rx Pkts
        #   Rem Addr/Info/SdpId:VcId                      Multipl     Tx Intvl   Rx Intvl
        #   Protocols                                        Type     LAG Port     LAG ID
        # -------------------------------------------------------------------------------
        # N/A                                                  Up          N/A        N/A
        #   172.16.1.254                                        3          100        100
        #   lag                                            cpm-np    1/1/c10/1          7
        # N/A                                                  Up          N/A        N/A
        #   172.16.3.136                                        3          100        100
        #   lag                                            cpm-np    1/1/c13/1        101

        parsed = {}

        sessionId = 0
        for line in out.splitlines():
            m = re.search(r'^(N/A) +(Up|Down) +(\S+) +(\S+)$', line)
            if m:
                sessionId += 1
                sessiond = parsed[sessionId] = {
                    'State': m.group(2),
                    'Tx Pkts': m.group(3),
                    'Rx Pkts': m.group(4)}
                continue

            m = re.search(r'^ {2}([\d.]+) +(\d+) +(\d+) +(\d+)$', line)
            if m:
                sessiond['Rem Addr'] = m.group(1)
                sessiond['Multipl'] = m.group(2)
                sessiond['Tx Intvl'] = m.group(3)
                sessiond['Rx Intvl'] = m.group(4)
                continue

            m = re.search(r'^ {2}(\w+) +(\S+) +(\S+) +(\d+)$', line)
            if m:
                sessiond['Protocols'] = m.group(1)
                sessiond['Type'] = m.group(2)
                sessiond['LAG Port'] = m.group(3)
                sessiond['LAG ID'] = m.group(4)

        return parsed
