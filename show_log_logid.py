""" show_log_syslog_id.py
    supports commands:
        * show log log-id
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


class ShowLogLogidSchema(MetaParser):
    """Schema for show log log-id"""
    schema = {
    }


class ShowLogLogid(ShowLogLogidSchema):
    """ Parser for show log log-id"""

    cli_command = 'show log log-id'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # ==============================================================================
        # Event Logs
        # ==============================================================================
        # Log Source    Filter Admin Oper       Logged     Dropped Dest       Dest Size
        # Id            Id     State State                         Type       Id
        # ------------------------------------------------------------------------------
        #   1 M S C     none   up    up            961           1 syslog     1     N/A
        #   2 M S C     none   up    up            955           1 syslog     2     N/A
        #  10 M S C     none   up    up            979           0 file       10    N/A
        #  66 D         none   up    up              0           0 memory           100
        #  75 D         none   up    up              0           0 file       75    N/A
        #  97 M S C     none   up    up            973           0 file       97    N/A
        #  98 M S C     none   up    up            969           0 file       98    N/A
        #  99 M         none   up    up            424           0 memory           500
        # 100 M         1001   up    up             20         404 memory           500
        # 101 M S C     none   up    up           1161           1 netconf          500

        parsed = {}

        for line in out.splitlines():
            m = re.search(r'^(.{3}) (.{9}) +(\S+) +(\S+) +(\S+)'
                          r' +(\d+) +(\d+) +(\S+) +(\d+)? +(\S+)$', line)
            if m:
                # use 'Dest Type' as major key
                if m.group(8) in parsed:
                    td = parsed[m.group(8)]
                else:
                    td = parsed[m.group(8)] = {}
                # use 'Log Id' as secondary key
                td[m.group(1).lstrip()] = {
                    'Source': m.group(2).rstrip(), 'Filter Id': m.group(3),
                    'Admin State': m.group(4), 'Oper State': m.group(5),
                    'Logged': m.group(6), 'Dropped': m.group(7),
                    'Dest Id': m.group(9), 'Size': m.group(10)}

        return parsed
