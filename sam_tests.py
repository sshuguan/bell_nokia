import logging
from pyats import aetest
from genie.testbed import load
from genie.libs.parser.sros.show_system_cpu import ShowSystemCpu
from genie.libs.parser.sros.show_card_detail import ShowCardDetail
from genie.libs.parser.sros.show_system_memory import ShowSystemMemory


logger = logging.getLogger(__name__)


def s2i(s):
    if s.endswith('C'):
        # convert "56C" to 56
        return int(''.join(s.split('C')))
    # convert "123,456,789" to 123456789
    return int(''.join(s.split(',')))


class CommonSetup(aetest.CommonSetup):
    'common setup section always runs first within the script'

    @aetest.subsection
    def connect_tb_devices(self, testbed):
        self.parent.parameters['testbed'] = testbed = load(testbed)

        # connect testbed devices
        for dev in testbed.devices.values():
            dev.connect()
            dev.mdcli_execute("environment more false")
            logger.info('Device %s connected!' % dev.name)


class Test_SysMem(aetest.Testcase):

    @aetest.test
    def check_system_memory(self, testbed):
        testpass = True
        for dev in testbed.devices.values():
            logger.info('Check %s system memory' % dev.name)
            # parse output of "show system memory-pools"
            memd = ShowSystemMemory(device=dev).parse()
            # sum up all pool memory
            isum = csum = 0
            for poold in memd['Pools'].values():
                isum += s2i(poold['In Use'])
                csum += s2i(poold['Current Size'])
            logger.info("Current Size sum: %d" % csum)
            logger.info("In Use sum      : %d" % isum)
            # check total equal to sum
            itot = s2i(memd['Total']['Total In Use'])
            ctot = s2i(memd['Total']['Current Total Size'])
            if isum == itot and csum == ctot:
                logger.info("%s memory counts looks good!" % dev.name)
            else:
                logger.error(
                    "%s Memory pool sum NOT match totol count!" % dev.name)
                testpass = testpass and False

        # set test result
        self.passed() if testpass else self.failed()


class Test_SysCpu(aetest.Testcase):

    @aetest.test
    def check_system_cpu(self, testbed):

        testpass = True
        for dev in testbed.devices.values():
            logger.info('Check %s system cpu' % dev.name)
            # parse output of "show system cpu"
            cpud = ShowSystemCpu(device=dev).parse()
            # sum up all process cpu time
            tsum = 0
            for prcd in cpud['Process'].values():
                tsum += s2i(prcd['Cpu Time'])
            logger.info('Process usage time sum: %d' % tsum)
            # check total equal to sum
            ttot = s2i(cpud['Summary']['Usage']['Cpu Time'])
            if tsum == ttot:
                logger.info("%s cpu usage time looks good!" % dev.name)
            else:
                logger.error(
                    "%s cpu usage time sum NOT match totol count!" % dev.name)
                testpass = testpass and False

        # set test result
        self.passed() if testpass else self.failed()


class Test_CardNoError(aetest.Testcase):

    @aetest.test
    def check_card_health(self, testbed):

        testpass = True
        for dev in testbed.devices.values():
            # parse output of "show card detail"
            cardd = ShowCardDetail(device=dev).parse()
            for s, cd in cardd.items():
                hd = cd['Hardware Data']
                admin = hd['Administrative state']
                oper = hd['Operational state']
                cardinfo = "{0} card {1} ({2})".format(
                    dev.name, s, cd['provisioned type'])
                # check card state
                cardpass = True
                err = ""
                if admin != "up":
                    err += "Admin state: %s (Not up);" % admin
                    cardpass = cardpass and False
                if oper != "up":
                    err += "Oper state: %s (Not up)" % oper
                    cardpass = cardpass and False
                # log card info
                if cardpass:
                    logger.info(cardinfo + ' OK')
                else:
                    logger.error(cardinfo + ' ERROR')
                    logger.error('  ' + err)
                # update test result
                testpass = testpass and cardpass

        # set test result
        self.passed("No hardware error") if testpass \
            else self.failed('Hardware errors')
