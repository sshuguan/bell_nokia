#!/usr/bin/env python
from genie.libs.parser.sros.show_system_cpu import ShowSystemCpu
from genie.libs.parser.sros.show_system_memory import ShowSystemMemory
from genie.libs.parser.sros.show_card_detail import ShowCardDetail
from genie.libs.parser.sros.show_router_isis_database import ShowRouterIsisDatabase
import sys
from pprint import pprint
from genie.testbed import load
testbed = load("/home/jcoulter/pyats_tests/sam_tb.yaml")

dev = testbed.devices["CR01-Nokia-NGCore"]

dev.connect(log_stdout=True, via="cli")

# For now until this is added to the connector
dev.mdcli_execute("environment more false")

# parser of "show system memory-pools
memd = ShowSystemMemory(device=dev).parse()
print('Total In Use      :', memd['Total']['Total In Use'])

# parser of "show system memory-pools
cpud = ShowSystemCpu(device=dev).parse()
print('Usage: ', cpud['Summary']['Usage']['Cpu Time'])

# parser of "show card detail"
cardd = ShowCardDetail(device=dev).parse()
print("slot 1 card type:", cardd['1']['provisioned type'])
print("slot A card type:", cardd['A']['provisioned type'])
print("slot A software version:", cardd['A']['Hardware Data']['Software version'])
print("slot B Hardware Resources Amperage Current:",
      cardd['B']['Hardware Resources (Power-Zone 1)']['Amperage']['Current'])

# parser of "show system ntp all"
from genie.libs.parser.sros.show_system_ntp_all import ShowSystemNtpAll
sysntpd = ShowSystemNtpAll(device=dev).parse()
print("system ntp oper-state:", sysntpd['clock_state']['system_status']['oper_status'])
for peer in sysntpd['peer']:
    print("ntp peer %s refid: %s" %(peer, sysntpd['peer'][peer]['local_mode']['client']['refid']))

# parser of "show router isis database"
isisd = ShowRouterIsisDatabase(device=dev).parse()
for instance in isisd:
    for level in isisd[instance]:
        if isisd[instance][level]['LSP Count'] != '0':
            for lspid in isisd[instance][level]:
                if lspid != 'LSP Count':
                    print("%s %s %s %s" % (instance, level, lspid, isisd[instance][level][lspid]['sequence']))
