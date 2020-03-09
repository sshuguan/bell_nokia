""" show_system_memory.py
    supports commands:
        * show system memory-pools
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


class ShowSystemMemorySchema(MetaParser):
    """Schema for show system memory"""
    schema = {
    }


class ShowSystemMemory(ShowSystemMemorySchema):
    """ Parser for show system memory-pools"""

    cli_command = 'show system memory-pools'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

            # ===============================================================================
            # Memory Pools
            # ===============================================================================
            # Name                Max Allowed    Current Size      Max So Far          In Use
            # -------------------------------------------------------------------------------
            # BFD                    No limit       5,242,880       5,242,880       4,937,856
            # BGP                    No limit       5,242,880       5,242,880       4,103,128
            # BIER                   No limit       1,048,576       1,048,576         673,600
            # CFLOWD                 No limit       1,048,576       1,048,576          26,384
            # Cards & Ports          No limit      15,728,640      15,728,640      11,652,400
            # DHCP Server            No limit       1,048,576       1,048,576         126,720
            # ETH-CFM                No limit       5,242,880       5,242,880       4,430,048
            # ICC                  37,748,736       2,097,152       2,097,152       1,730,152
            # -------------------------------------------------------------------------------
            # Current Total Size :    5,085,593,600 bytes
            # Total In Use       :    4,933,805,656 bytes
            # Available Memory   :   11,031,019,520 bytes
            # ===============================================================================

        parsed = {"Pools": {}, "Total": {}}
        p0 = re.compile(
            r'^\b(.+)\b +(No limit|[\d,]+) +([\d,]+) +([\d,]+) +([\d,]+)')
        p1 = re.compile(r'^\b(.+)\b +: +([0-9,]+) bytes')

        for line in out.splitlines():
            line = line.strip()

            m = p0.match(line)
            if m:
                parsed['Pools'][m.group(1)] = {
                    'Max Allowed': m.group(2),
                    'Current Size': m.group(3),
                    'Max So Far': m.group(4),
                    'In Use': m.group(5)}
                continue

            m = p1.match(line)
            if m:
                parsed['Total'][m.group(1)] = m.group(2)

        return parsed
