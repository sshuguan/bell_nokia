""" show_log_syslog_id.py
    supports commands:
        * show log syslog <id>
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


class ShowLogSyslogIdSchema(MetaParser):
    """Schema for show log syslog <id>"""
    schema = {
    }


class ShowLogSyslogId(ShowLogSyslogIdSchema):
    """ Parser for show log syslog <id>"""

    cli_command = 'show log syslog %d'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command % 1)
        elif re.search(r'^\d$', output):
            out = self.device.execute(self.cli_command % output)
        else:
            out = output

        # ===============================================================================
        # Syslog Target 1
        # ===============================================================================
        # IP Address       : 192.168.132.69
        # Port             : 514
        # Log-ids          : 1
        # Prefix           : CR02-Nokia-NGCore
        # Facility         : local7
        # Severity Level   : info
        # Prefix Level     : yes
        # Below Level Drop : 0
        # Description      : COVE VM

        parsed = {}

        for line in out.splitlines():
            m = re.search(r'^(Syslog Target) (\d+)$', line)
            if m:
                parsed[m.group(1)] = m.group(2)
            m = re.search(r'^\b(.+)\b +: +\b(.+)\b$', line)
            if m:
                parsed[m.group(1)] = m.group(2)

        return parsed
