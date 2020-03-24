""" show_router_isis_database.py
    supports commands:
        * show router isis database
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


class ShowRouterIsisDatabaseSchema(MetaParser):
    """Schema for show router isis database"""
    schema = {
    }


class ShowRouterIsisDatabase(ShowRouterIsisDatabaseSchema):
    """ Parser for show router isis database"""

    cli_command = 'show router isis database'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

            # ===============================================================================
            # Rtr Base ISIS Instance 0 Database 
            # ===============================================================================
            # LSP ID                                  Sequence  Checksum Lifetime Attributes
            # -------------------------------------------------------------------------------
            # 
            # Displaying Level 1 database
            # -------------------------------------------------------------------------------
            # Level (1) LSP Count : 0
            # 
            # Displaying Level 2 database
            # -------------------------------------------------------------------------------
            # CR01-Nokia-NGCore.00-00                 0x133     0x7bb9   61280    L1L2
            # CR02-Nokia-NGCore.00-00                 0xb       0xe431   51659    L1L2
            # newbx1_RE0.00-00                        0xab      0x9bdd   60464    L1L2
            # core1-tatooine.00-00                    0xa54c    0xfed1   45926    L1L2
            # core2-tatooine.00-00                    0xa3bc    0x30d    60872    L1L2
            # vpce1-tatooine.00-00                    0x3d      0x11f9   44000    L1L2
            # tcore4-rohan.00-00                      0x5a62    0xf535   51390    L1L2
            # tcore4-rohan.00-01                      0x5f      0x48bd   48226    L1L2
            # tcore4-rohan.00-02                      0x9f      0x746d   52396    L1L2
            # vpce2-tatooine.00-00                    0x3c      0x78bf   43278    L1L2


        parsed = {}

        # split <out> into list
        s0 = re.compile(r'\r?\n=+\r?\nCard \w+\r?\n=+\r?\n')
        cardL = s0.split(out)

        for line in out.splitlines():
            line = line.strip()
            if not line or re.search(r'^(=+|-+|LSP ID.*)$', line):
                continue

            m = re.search(r'^Rtr Base ISIS Instance +(\d) Database$', line)
            if m:
                instance = m.group(1)
                parsed[instance] = {}
                continue
            
            m = re.search(r'^Displaying Level +(\d) database$', line)
            if m:
                level = m.group(1)
                parsed[instance][level] = {}
                continue
            
            m = re.search(r'^Level +\(\d\) (LSP Count) +: +(\d+)$', line)
            if m:
                parsed[instance][level][m.group(1)] = m.group(2)
                continue
            
            m = re.search(r'(\S+) +(0x\w+) +(0x\w+) +([\d()]+) *(\b.*)?$', line)
            if m:
                parsed[instance][level][m.group(1)] = {
                    'sequence':m.group(2), 'checksum':m.group(3),
                    'lifetime':m.group(4), 'attributes':m.group(5)}

        return parsed
