import os
import logging

from dispersionreticle.settings import copy, deleteEmptyFolderSafely
from dispersionreticle.settings.config_file import g_configFiles

logger = logging.getLogger(__name__)


class ConfigVersion(object):

    V2_0_X = 0
    V2_1_X = 1
    V2_2_X = 2
    V2_3_X = 3
    V2_4_X = 4
    V2_6_X = 5
    V3_0_X = 6

    CURRENT = V3_0_X


def performConfigMigrations():
    v2_0_2_migrateConfigFileLocation()

    anyExecuted = False
    anyExecuted |= performMainConfigMigrations()

    if anyExecuted:
        g_configFiles.writeConfigDicts()


def performMainConfigMigrations():
    if not g_configFiles.config.exists():
        return False

    g_configFiles.config.loadConfigDict()
    configDict = g_configFiles.config.configDict

    if configDict is None:
        return False

    if isVersion(configDict, ConfigVersion.CURRENT):
        return False

    v2_1_0_addOptionLatencyReticleHideStandardReticle()
    v2_2_0_addSimpleServerReticle()
    v2_3_0_addNewSimpleServerReticleFeatures()
    v2_4_0_addSupportForModsSettingsAPI()
    v2_6_0_addDrawCenterDotToSimpleServerReticle()

    v3_0_0_splitConfigFile()

    return True


def v2_0_2_migrateConfigFileLocation():
    legacyConfigDir = os.path.join("mods", "config")
    legacyConfigFileDir = os.path.join("mods", "config", "DispersionReticle")
    legacyConfigFilePath = os.path.join("mods", "config", "DispersionReticle", "config.json")

    # handle config folder name that differs from other mod configs folder
    if not os.path.isfile(legacyConfigFilePath):
        return

    logger.info("Legacy config location detected, moving file to new location ...")

    newConfigFilePath = g_configFiles.config.configFilePath

    # move copy config to new location
    copy(legacyConfigFilePath, newConfigFilePath)

    # remove previous config
    os.remove(legacyConfigFilePath)

    # remove previous folders if they are empty
    deleteEmptyFolderSafely(legacyConfigFileDir)
    deleteEmptyFolderSafely(legacyConfigDir)

    logger.info("Finished moving config file to new location.")


def v2_1_0_addOptionLatencyReticleHideStandardReticle():
    configDict = g_configFiles.config.configDict

    if not isVersion(configDict, ConfigVersion.V2_0_X):
        return

    logger.info("Migrating config file from version 2.0.x to 2.1.x ...")

    configDict["dispersion-reticle"] = {}
    configDict["dispersion-reticle"]["enabled"] = configDict["dispersion-reticle-enabled"]
    configDict["latency-reticle"] = {}
    configDict["latency-reticle"]["enabled"] = configDict["latency-reticle-enabled"]
    configDict["latency-reticle"]["hide-standard-reticle"] = False
    configDict["server-reticle"] = {}
    configDict["server-reticle"]["enabled"] = configDict["server-reticle-enabled"]

    del configDict["dispersion-reticle-enabled"]
    del configDict["latency-reticle-enabled"]
    del configDict["server-reticle-enabled"]

    progressVersion(configDict)

    logger.info("Migration finished.")


def v2_2_0_addSimpleServerReticle():
    configDict = g_configFiles.config.configDict
    if not isVersion(configDict, ConfigVersion.V2_1_X):
        return

    logger.info("Migrating config file from version 2.1.x to 2.2.x ...")

    configDict["simple-server-reticle"] = {}
    configDict["simple-server-reticle"]["enabled"] = False
    configDict["simple-server-reticle"]["color"] = (255, 0, 255)
    configDict["simple-server-reticle"]["alpha"] = 1.0
    progressVersion(configDict)

    logger.info("Migration finished.")


def v2_3_0_addNewSimpleServerReticleFeatures():
    configDict = g_configFiles.config.configDict
    if not isVersion(configDict, ConfigVersion.V2_2_X):
        return

    logger.info("Migrating config file from version 2.2.x to 2.3.x ...")

    configDict["simple-server-reticle"]["shape"] = "pentagon"
    configDict["simple-server-reticle"]["draw-outline"] = False
    configDict["simple-server-reticle"]["blend"] = 0.0
    progressVersion(configDict)

    logger.info("Migration finished.")


def v2_4_0_addSupportForModsSettingsAPI():
    configDict = g_configFiles.config.configDict
    if not isVersion(configDict, ConfigVersion.V2_3_X):
        return

    logger.info("Migrating config file from version 2.3.x to 2.4.x ...")

    configDict["enabled"] = True
    progressVersion(configDict)

    logger.info("Migration finished.")


def v2_6_0_addDrawCenterDotToSimpleServerReticle():
    configDict = g_configFiles.config.configDict
    if not isVersion(configDict, ConfigVersion.V2_4_X):
        return

    logger.info("Migrating config file from version 2.4.x to 2.6.x ...")

    configDict["simple-server-reticle"]["draw-center-dot"] = False
    progressVersion(configDict)

    logger.info("Migration finished.")


def v3_0_0_splitConfigFile():
    configDict = g_configFiles.config.configDict
    if not isVersion(configDict, ConfigVersion.V2_6_X):
        return

    logger.info("Migrating config file from version 2.6.x to 3.0.x ...")

    # progress version prior to copying
    progressVersion(g_configFiles.config.configDict)

    # focused reticle
    g_configFiles.configFocusedReticle.configDict = {}
    focusedReticleConfigDict = g_configFiles.configFocusedReticle.configDict
    focusedReticleConfigDict["__version__"] = configDict["__version__"]

    # standard focused reticle
    focusedReticleConfigDict["standard-focused-reticle"] = {}
    focusedReticleConfigDict["standard-focused-reticle"]["enabled"] = configDict["dispersion-reticle"]["enabled"]
    del configDict["dispersion-reticle"]

    # custom focused reticle
    focusedReticleConfigDict["custom-focused-reticle"] = {}
    focusedReticleConfigDict["custom-focused-reticle"]["enabled"] = False
    focusedReticleConfigDict["custom-focused-reticle"]["shape"] = "circle"
    focusedReticleConfigDict["custom-focused-reticle"]["color"] = (255, 0, 255)
    focusedReticleConfigDict["custom-focused-reticle"]["draw-center-dot"] = False
    focusedReticleConfigDict["custom-focused-reticle"]["draw-outline"] = False
    focusedReticleConfigDict["custom-focused-reticle"]["blend"] = 0.5
    focusedReticleConfigDict["custom-focused-reticle"]["alpha"] = 1.0

    # hybrid reticle
    g_configFiles.configHybridReticle.configDict = {}
    hybridReticleConfigDict = g_configFiles.configHybridReticle.configDict
    hybridReticleConfigDict["__version__"] = configDict["__version__"]

    # standard hybrid reticle
    hybridReticleConfigDict["standard-hybrid-reticle"] = {}
    hybridReticleConfigDict["standard-hybrid-reticle"]["enabled"] = configDict["latency-reticle"]["enabled"]
    hybridReticleConfigDict["standard-hybrid-reticle"]["hide-standard-reticle"] = configDict["latency-reticle"]["hide-standard-reticle"]
    del configDict["latency-reticle"]

    # custom hybrid reticle
    hybridReticleConfigDict["custom-hybrid-reticle"] = {}
    hybridReticleConfigDict["custom-hybrid-reticle"]["enabled"] = False
    hybridReticleConfigDict["custom-hybrid-reticle"]["shape"] = "circle"
    hybridReticleConfigDict["custom-hybrid-reticle"]["color"] = (255, 0, 255)
    hybridReticleConfigDict["custom-hybrid-reticle"]["draw-center-dot"] = False
    hybridReticleConfigDict["custom-hybrid-reticle"]["draw-outline"] = False
    hybridReticleConfigDict["custom-hybrid-reticle"]["blend"] = 0.5
    hybridReticleConfigDict["custom-hybrid-reticle"]["alpha"] = 1.0

    # server reticle
    g_configFiles.configServerReticle.configDict = {}
    serverReticleConfigDict = g_configFiles.configServerReticle.configDict
    serverReticleConfigDict["__version__"] = configDict["__version__"]

    # standard server reticle
    serverReticleConfigDict["standard-server-reticle"] = {}
    serverReticleConfigDict["standard-server-reticle"]["enabled"] = configDict["server-reticle"]["enabled"]
    del configDict["server-reticle"]

    # custom server reticle
    serverReticleConfigDict["custom-server-reticle"] = {}
    serverReticleConfigDict["custom-server-reticle"]["enabled"] = configDict["simple-server-reticle"]["enabled"]
    serverReticleConfigDict["custom-server-reticle"]["shape"] = configDict["simple-server-reticle"]["shape"]
    serverReticleConfigDict["custom-server-reticle"]["color"] = configDict["simple-server-reticle"]["color"]
    serverReticleConfigDict["custom-server-reticle"]["draw-center-dot"] = configDict["simple-server-reticle"]["draw-center-dot"]
    serverReticleConfigDict["custom-server-reticle"]["draw-outline"] = configDict["simple-server-reticle"]["draw-outline"]
    serverReticleConfigDict["custom-server-reticle"]["blend"] = configDict["simple-server-reticle"]["blend"]
    serverReticleConfigDict["custom-server-reticle"]["alpha"] = configDict["simple-server-reticle"]["alpha"]
    del configDict["simple-server-reticle"]

    logger.info("Migration finished.")


def progressVersion(configDict):
    if "__version__" not in configDict:
        configDict["__version__"] = ConfigVersion.V2_1_X
        return

    configDict["__version__"] = int(configDict["__version__"]) + 1


def isVersion(configDict, version):
    if "__version__" not in configDict:
        return ConfigVersion.V2_0_X == version

    return int(configDict["__version__"]) == version
