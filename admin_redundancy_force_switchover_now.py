""" admin_redundancy_force_switchover_now.py
    supports commands:
        * admin redundancy force-switchover now 
"""

# Python
import re

# Metaparser
from genie.metaparser import MetaParser
from genie.metaparser.util.schemaengine import Schema, Any, Optional

# parser utils
from genie.libs.parser.utils.common import Common

# =============================================
# Parser for 'admin redundancy force-switchover now'
# =============================================


class  AdminRedundancyForceSwitchoverNowSchema(MetaParser):
    """admin redundancy force-switchover now"""
    schema = {
    }


class AdminRedundancyForceSwitchoverNow(AdminRedundancyForceSwitchoverNowSchema):
    """ Parser for admin redundancy force-switchover now"""

    cli_command = 'admin redundancy force-switchover now'

    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # ==============================================================================
        # No Output
        # ==============================================================================

        parsed = {}

        for line in out.splitlines():
            m = re.search(r'^(\S+)', line)

            if m:
                # there should be no character output
                parsed = m

        return parsed
