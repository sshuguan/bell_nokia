#!/usr/bin/env python3
from genie.libs.parser.sros.show_system_cpu import ShowSystemCpu
from genie.libs.parser.sros.show_system_memory import ShowSystemMemory
from genie.libs.parser.sros.show_card_detail import ShowCardDetail
from genie.libs.parser.sros.show_router_isis_database import ShowRouterIsisDatabase
import sys
from pprint import pprint
from genie.testbed import load
testbed = load("/home/jcoulter/pyats_tests/sam_tb.yaml")

# convert "123,456,789" to 123456789
def s2i(s):
    return int(''.join(s.split(',')))

# connect device
dev = testbed.devices["CR01-Nokia-NGCore"]
dev.connect(log_stdout=True, via="cli")
dev.mdcli_execute("environment more false")

# parser of "show system memory-pools
memd = ShowSystemMemory(device=dev).parse()
# sum up pool memory
totalinuse = 0
totalcurrentsize = 0
for pool, poold in memd['Pools'].items():
    totalinuse += s2i(poold['In Use'])
    totalcurrentsize += s2i(poold['Current Size'])
# print sum and total
print(totalcurrentsize)
print(totalinuse)
print('Current Total Size:', memd['Total']['Current Total Size'])
print('Total In Use      :', memd['Total']['Total In Use'])

# parser of "show system memory-pools
cpud = ShowSystemCpu(device=dev).parse()
# sum up process cpu time
tsum = 0
for prc, prcd in cpud['Process'].items():
    tsum += s2i(prcd['Cpu Time'])
# print sum and total
print('Process usage time sum: %d' % tsum)
print('Total cpu usage time: %s' % cpud['Summary']['Usage']['Cpu Time'])

# parser of "show card detail"
cardd = ShowCardDetail(device=dev).parse()
# print certain retrieved values
for c, cd in cardd.items(): 
    print("card %s, admin/oper state: (%s)/(%s)" %
          (c, cd['admin state'], cd['operational state']))

##!! parser of "show card A detail"
# hack "output" as "card slot"
cardslot= ["A", "B"]
for slot in cardslot:
    sd = ShowCardDetail(device=dev).parse(output=slot)
    if slot in sd:
        # print certain retrieved values
        print("card %s, admin/oper state: (%s)/(%s);" %
            (slot, sd[slot]['admin state'], sd[slot]['operational state']))

# parser of "show router isis database"
isisd = ShowRouterIsisDatabase(device=dev).parse()
for instance in isisd:
    for level in isisd[instance]:
        if isisd[instance][level]['LSP Count'] != '0':
            for lspid in isisd[instance][level]:
                if lspid != 'LSP Count':
                    print("%s %s %s %s" % (instance, level, lspid, isisd[instance][level][lspid]['sequence']))
