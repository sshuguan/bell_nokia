import re
import logging
from pyats import aetest
from genie.testbed import load
from genie.libs.parser.sros.show_system_cpu import ShowSystemCpu
from genie.libs.parser.sros.show_card_detail import ShowCardDetail
from genie.libs.parser.sros.show_system_memory import ShowSystemMemory
from genie.libs.parser.sros.show_router_isis_routes import ShowRouterIsisRoutes
from genie.libs.parser.sros.show_router_isis_database import ShowRouterIsisDatabase
from genie.libs.parser.sros.show_router_isis_prefix_sids import ShowRouterIsisPrefixSids
from genie.libs.parser.sros.show_router_bfd_session import ShowRouterBfdSession
from genie.libs.parser.sros.show_lag_detail import ShowLagDetail
from genie.libs.parser.sros.show_lag_statistics import ShowLagStatistics
from genie.libs.parser.sros.show_router_mpls_labels_summary import ShowRouterMplsLabelsSummary
from genie.libs.parser.sros.show_log_logid import ShowLogLogid
from genie.libs.parser.sros.admin_redundancy_force_switchover_now import AdminRedundancyForceSwitchoverNow
logger = logging.getLogger(__name__)

# convert "123,456,789" to 123456789
# convert "85 %" or "85%" to 85
# convert "75C" to 75
# convert "3,903 MB" to 3903
# convert "61,712 KB" to 61712


def s2i(s):
    m = re.search(r'^([\d,]+) ?(%|KB|MB|C)?', s)
    if m:
        return int(''.join(m.group(1).split(',')))
    # return original string if not match
    return s


class CommonSetup(aetest.CommonSetup):
    'common setup section always runs first within the script'

    @aetest.subsection
    def connect_tb_devices(self, testbed):
        self.parent.parameters['testbed'] = testbed = load(testbed)

        # connect testbed devices
        for dev in testbed:
            dev.connect()
            dev.mdcli_execute("environment more false")
            logger.info('Device %s connected!' % dev.name)


class Test_Ntp_Peer_Up(aetest.Testcase):

    @aetest.test
    def check_ntp_peer_up(self, testbed):
        testpass = True
        for dev in testbed:
            ntpd = dev.parse("show system ntp all")
            if ntpd['clock_state']['system_status']['oper_status'] == 'up' \
                and ntpd['peer']['172.16.1.82']['local_mode']['client']['state'] == 'chosen':
                logger.info('Device %s NTP up. Good!' % dev.name)
            else:
                logger.error('Device %s NTP NOT up' % dev.name)
                testpass = False
        # set test result
        self.passed() if testpass else self.failed()


class Test_Log_Syslog(aetest.Testcase):

    @aetest.test
    def check_log_syslog(self, testbed):

        testpass = True
        for dev in testbed:
            # parse output of "show log log-id"
            logd = ShowLogLogid(device=dev).parse()
            if 'syslog' in logd:
                for id in logd['syslog']:
                    if logd['syslog'][id]['Admin State'] == 'up':
                        logger.info('Device %s syslog %s up' % (dev.name, id))
                    else:
                        logger.error('Device %s syslog %s NOT up' % (dev.name, id))
                        testpass = False
            else:
                logger.error('Device %s has NO syslog configured!' % dev.name)
                testpass = False
        # set test result
        self.passed() if testpass else self.failed()


class Test_SysMem(aetest.Testcase):

    @aetest.test
    def check_system_memory(self, testbed):
        testpass = True
        for dev in testbed:
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
        for dev in testbed:
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
        for dev in testbed:
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


class Test_FlashNotFull(aetest.Testcase):

    @aetest.test
    def check_Flash_health(self, testbed):

        testpass = True
        for dev in testbed:
            # parse output of "show card A|B detail"
            for cpm in ["A", "B"]:
                cpmd = ShowCardDetail(device=dev).parse(output=cpm)

                if cpm not in cpmd:
                    logger.info("CPM %s not equipped!" % cpm)
                    continue  # cpm A|B not equipped

                # check flash card not full
                for k, kd in cpmd[cpm].items():
                    if re.search(r'^Flash', k) and \
                            kd['Operational state'] == "up":
                        if s2i(kd['Percent Used']) > 98:
                            logger.error("CPM %s, %s full" % (cpm, k))
                            testpass = testpass and False
                        else:
                            logger.info("CPM %s, %s has free space" % (cpm, k))

        # set test result
        self.passed("Flash has fress space") if testpass \
            else self.failed('Flash full !!!')

class Test_IsisDatabase(aetest.Testcase):

    @aetest.test
    def check_isis_database(self, testbed):

        testpass = True
        for dev in testbed:
            # parse output of "show router isis database"
            isisdbd = ShowRouterIsisDatabase(device=dev).parse()
            # TODO verify isis database

        # set test result
        self.passed() if testpass else self.failed()

class Test_IsisRoutes(aetest.Testcase):

    @aetest.test
    def check_isis_routes(self, testbed):

        testpass = True
        verifyIps = ['67.70.219.13/32', '67.70.219.14/32']
        for dev in testbed:
            # parse output of "show router isis routes"
            isisrtd = ShowRouterIsisRoutes(device=dev).parse()
            for ip in verifyIps:
                if ip in isisrtd['0']:
                    logger.info('%s in isis route table. Good!' % ip)
                else:
                    logger.error('%s NOT in isis route table.' % ip)
                    testpass = False
        # set test result
        self.passed() if testpass else self.failed()


class Test_IsisPrefixSids(aetest.Testcase):

    @aetest.test
    def check_isis_prefixsids(self, testbed):

        testpass = True
        for dev in testbed:
            # parse output of "show router isis prefix-sids"
            isispfxd = ShowRouterIsisPrefixSids(device=dev).parse()
            # TODO verify isis prefix-sids

        # set test result
        self.passed() if testpass else self.failed()

class Test_Bfd_Session(aetest.Testcase):

    @aetest.test
    def check_bfd_session(self, testbed):

        testpass = True
        for dev in testbed:
            # parse output of "show router bfd session"
            isispfxd = ShowRouterBfdSession(device=dev).parse()
            # TODO verify bfd session

        # set test result
        self.passed() if testpass else self.failed()

class Test_Ecmp_Over_lag(aetest.Testcase):

    @aetest.test
    def check_ecmp_over_lag(self, testbed):

        testpass = True
        for dev in testbed:
            # parse output of "show lag detail"
            # parse output of "show lag statistics"
            lagd = ShowLagDetail(device=dev).parse()
            lagstd = ShowLagStatistics(device=dev).parse()
            # TODO verify lag session

        # set test result
        self.passed() if testpass else self.failed()
        
        
class Test_Router_Mpls_Labels(aetest.Testcase):

    @aetest.test
    def check_router_mpls_labels(self, testbed):

        testpass = True
        for dev in testbed:
            # parse output of "show router mpls-labels summary"
            mplslabelsummary = ShowRouterMplsLabelsSummary(device=dev).parse()
            # TODO verify mpls labels

        # set test result
        self.passed() if testpass else self.failed()

#class Test_Admin_Redundancy_Force_Switchover_Now(aetest.Testcase):
#
#    @aetest.test
#    def check_admin_redundancy_force_switchover(self, testbed):
#
#        testpass = True
#        for dev in testbed:
#            # will include show card before and show card after
#
#            # parse output of "admin redundancy force-switchover now"
#            adminswitchover = AdminRedundancyForceSwitchoverNow(device=dev).parse()
#            # TODO verify "admin redundancy force-switchover now"
#
#        # set test result
#        self.passed() if testpass else self.failed()
