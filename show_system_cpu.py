""" show_system_cpu.py
    supports commands:
        * show system cpu
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
    """Schema for show system cpu"""
    schema = {
    }


class ShowSystemCpu(ShowSystemMemorySchema):
    """ Parser for show system cpu"""

    cli_command = 'show system cpu'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

            # ===============================================================================
            # CPU Utilization (Sample period: 1 second)
            # ===============================================================================
            # Name                                   CPU Time       CPU Usage        Capacity
            #                                          (uSec)                           Usage
            # -------------------------------------------------------------------------------
            # BFD                                       1,133           0.01%           0.04%
            # BGP                                      15,239           0.15%           0.23%
            # BGP PE-CE                                     0           0.00%           0.00%
            # BIER                                          0           0.00%           0.00%
            # CALLTRACE                                 2,428           0.02%           0.23%
            # CFLOWD                                    2,560           0.02%           0.25%
            # Cards & Ports                            50,312           0.50%           2.46%
            # DHCP Server                                  64          ~0.00%          ~0.00%
            # ETH-CFM                                   3,043           0.03%           0.30%
            # HQoS Algorithm                                0           0.00%           0.00%
            # -------------------------------------------------------------------------------
            # Total                                 9,974,226         100.00%
            #    Idle                               9,497,074          95.21%
            #    Usage                                477,152           4.78%
            # Busiest Core Utilization                 88,374           8.85%

        parsed = {'Process': {}, 'Summary': {}}
        p0 = re.compile(r'^\b(.+)\b +([\d,]+) +([~\d\.%]+) +([~\d\.%]+)')
        p1 = re.compile(r'^\b(.+)\b +([\d,]+) +([\d\.%]+)')

        for line in out.splitlines():
            line = line.strip()

            m = p0.match(line)
            if m:
                parsed['Process'][m.group(1)] = {
                    'Cpu Time': m.group(2),
                    'Cpu Usage': m.group(3),
                    'Capacity Usage': m.group(4)}
                continue

            m = p1.match(line)
            if m:
                parsed['Summary'][m.group(1)] = {
                    'Cpu Time': m.group(2),
                    'Cpu Usage': m.group(3)}

        return parsed
