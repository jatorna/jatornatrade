import configparser
import sys
import subprojects.misc.LowLevelFuncions as llf
from subprojects.types.Common import *
import traceback


logger = llf.script_logger('DS CONFIG PARSER')


#################
# DATA SERVER CONFIG PARSER #
#################

def parse_config(config_path):
    config_file = configparser.ConfigParser()
    config_file.read(config_path)

    config = Config()

    try:
        config.general.mode = DataServerMode(config_file['GENERAL']['Mode'].upper())
        config.general.db_path = config_file['GENERAL']['DatabasePath']
        config.general.chromedriver_path = config_file['GENERAL']['ChromeDriverPath']
        config.general.market = Market(config_file['GENERAL']['Market'].upper())
        config.general.source = DataProviderSource(config_file['GENERAL']['Source'].upper())
        config.general.tgm_alerts = config_file.getboolean('GENERAL', 'TelegramAlerts')

        config.historical.alpha_key = config_file['HISTORICAL']['AlphaKey']
        config.historical.fhub_key = config_file['HISTORICAL']['FhbKey']
        config.historical.frequency = Frequency(config_file['HISTORICAL']['Frequency'].upper())

        config.realtime.hostname = config_file['REALTIME']['Hostname']
        config.realtime.port = config_file.getint('REALTIME', 'Port')
        config.realtime.rate = config_file.getint('REALTIME', 'Rate')

        config.mysqlconf.db_host = config_file['MYSQL']['Hostname']
        config.mysqlconf.db_port = config_file.getint('MYSQL', 'Port')
        config.mysqlconf.db_user = config_file['MYSQL']['User']
        config.mysqlconf.db_pass = config_file['MYSQL']['Password']
        config.mysqlconf.db_name = config_file['MYSQL']['DbName']

    except Exception as e:
        logger.error('Error parsing config')
        logger.error('Program interrumped')
        logger.error(traceback.format_exc())
        sys.exit()

    logger.log(5, 'Config parsed correctly')

    return config


class ConfigGeneral:
    mode = DataServerMode
    db_path = ''
    chromedriver_path = ''
    source = DataProviderSource
    market = Market
    tgm_alerts = False


class ConfigHistorical:
    alpha_key = ''
    fhub_key = ''
    frequency = Frequency
    resolution = 0


class ConfigRealTime:
    hostname = ''
    port = 0
    rate = ''


class ConfigMysql:
    db_host = ''
    db_port = 0
    db_user = ''
    db_pass = ''
    db_name = ''


class Config:
    general = ConfigGeneral()
    historical = ConfigHistorical()
    realtime = ConfigRealTime()
    mysqlconf = ConfigMysql()
