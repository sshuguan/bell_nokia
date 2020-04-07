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
from genie.libs.parser.sros.show_router_routetable import ShowRouterRoutetable
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
            if ntpd['clock_state']['system_status']['oper_status'] == 'up'\
                and ntpd['peer']['172.16.1.82']['local_mode']['client']['state'] == 'chosen'\
                and ntpd['peer']['172.16.1.78']['local_mode']['client']['state'] == 'candidate':
                logger.info('Device %s NTP up & chosen/candidate state good!' % dev.name)
            else:
                logger.error('Device %s NTP NOT up or chosen/candidate error!' % dev.name)
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
            r1 = dev.execute("show card detail | match '^Card|Trap'")
            r2 = dev.execute("show mda detail | match '^MDA|Trap'")
            for r in [r1, r2]:
                if "Trap" in r:
                    logger.error("%s has Card/Trap errors!" % dev.name)
                    testpass = False
                else:
                    logger.info("%s all card/mda good" % dev.name)
        
        # set test result
        self.passed() if testpass else self.failed('Card error')


class Test_FlashNotFull(aetest.Testcase):

    @aetest.test
    def check_Flash_health(self, testbed):

        testpass = True
        cf3 = 'Flash - cf3'
        for dev in testbed:
            # parse output of "show card A|B detail"
            for cpm in ["A", "B"]:
                cpmd = ShowCardDetail(device=dev).parse(output=cpm)

                if cpm not in cpmd:
                    logger.info("CPM %s not equipped!" % cpm)
                    continue  # cpm A|B not equipped

                # check flash-cf3 card not full
                if cf3 in cpmd[cpm] and \
                    cpmd[cpm][cf3]['Operational state'] == "up" and \
                    s2i(cpmd[cpm][cf3]['Percent Used']) <= 90:
                    logger.info("CPM %s, %s up and not full" % (cpm, cf3))
                else:
                    logger.error("CPM %s, %s almost full!" % (cpm, cf3))
                    testpass = False

        # set test result
        self.passed() if testpass else self.failed('Flash full!')

class Test_P2pIp_NotIn_IsisRoute(aetest.Testcase):

    @aetest.test
    def check_ip_notin_isis_routes(self, testbed):

        testpass = True
        cmd = 'show router isis routes | match %s'
        p2p = {'CR01-Nokia-NGCore': ['172.16.1.116/31', '172.16.3.209/31'],
               'CR02-Nokia-NGCore': ['172.16.3.140/31', '172.16.3.207/31']}
        for dev in testbed:
            for ip in p2p[dev.name]:
                cout = dev.execute(cmd % ip)
                if not cout:
                    logger.info('%s isis route does not have %s. Good!'
                                % (dev.name, ip))
                else:
                    logger.info('%s isis route have %s!' % (dev.name, ip))
                    testpass = False
 
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
        verifyIps = ['67.70.219.13/32', '67.70.219.14/32']
        for dev in testbed:
            # parse output of "show router isis prefix-sids"
            isispfxd = ShowRouterIsisPrefixSids(device=dev).parse()
            for ip in verifyIps:
                if ip in isispfxd['0']:
                    logger.info('%s in isis prefix-sids. Good!' % ip)
                else:
                    logger.error('%s NOT in isis prefix-sids' % ip)
                    testpass = False

        # set test result
        self.passed() if testpass else self.failed()

class Test_RoutetableWithSidLabel(aetest.Testcase):

    @aetest.test
    def check_routetable_sidLabel(self, testbed):

        testpass = True
        for dev in testbed:
            rtabled = ShowRouterRoutetable(device=dev).parse()
            pfxsidd = ShowRouterIsisPrefixSids(device=dev).parse()
            # collect all /32 prefixes with isis-proto
            pfx32 = [x for x in rtabled if x.endswith('/32')
                     and rtabled[x]['Proto'] == 'ISIS']
            # verify /32 prefix in isis-prefix-sid table
            err = 0
            for pfx in pfx32:
                if pfx not in pfxsidd['0']:
                    logger.error('%s NOT in isis-prefix-sid table' % pfx)
                    err += 1

            logger.info("%s /32 isis prefix found in route-table" % len(pfx32))
            if err:
                logger.error("%s /32 prefix NOT in isis-prefix-sid table" % err)
                testpass = False
            else:
                logger.info("all /32 prefix in isis-prefix-sid table")

        # set test result
        self.passed() if testpass else self.failed()

class Test_Bfd_Lag_up(aetest.Testcase):

    @aetest.test
    def check_bfd_lag_up(self, testbed):

        testpass = True
        for dev in testbed:
            # verify bfd session up
            bfdd = ShowRouterBfdSession(device=dev).parse()
            for b, bd in bfdd.items():
                if bd['State'] == 'Up':
                    logger.info('Bfd session %s up. Good!' % b)
                else:
                    logger.error('Bfd session %s NOT up!' % b)
                    testpass = False
            # verify lag up/active
            lagd = ShowLagDetail(device=dev).parse()
            for l, ld in lagd.items():
                if ld['Opr'] == 'up' and\
                    ld['LACP'] == 'enabled' and\
                    ld['Mode'] == 'active':
                    logger.info('Lag %s up/active. Good!' % l)
                    for p in ld['Port-id']:
                        if ld[p]['Opr'] == 'up' and\
                            ld[p]['Act/Stdby'] == 'active':
                            logger.info("%s up/active. Good!" % p)
                        else:
                            logger.error("%s NOT up/active" % p)
                            testpass = False
                else:
                    logger.error('Lag %s NOT up/active!' % l)
                    testpass = False

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
            mplslbld = ShowRouterMplsLabelsSummary(device=dev).parse()
            if mplslbld['Segment Routing Start Label'] == '16000' and\
                mplslbld['Segment Routing End Label'] == '81534':
                logger.info("SRGB label range allocated properply. Good!")
            else:
                logger.error("SRGB label range NOT in 16000~81534!")
                testpass = False

        # set test result
        self.passed() if testpass else self.failed()

# class Test_Admin_Redundancy_Force_Switchover_Now(aetest.Testcase):
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
