#!/usr/bin/python
# encoding: utf-8
"""
commonutils

Created by David Young on xxxxx
If you have any questions requiring this script please email me: d.r.young@qub.ac.uk

dryx syntax:
xxx = come back here and do some more work
_someObject = a 'private' object that should only be changed for debugging

notes:
    - Dave started work on this file on December 5, 2012
    - Dave 'completed' this code on ... not complete yet!
"""

import sys
import os
from datetime import datetime, date, time

now = datetime.now()
now = now.strftime("%Y%m%dt%H%M%S")

########## THE GLOBAL VARIABLES ############
pathToRoot = os.path.dirname(__file__) + "/"
pathToArchiveFolder = pathToRoot + ".archive/"
pathToCodeFolder = pathToRoot + "code/"
pathToDependenciesFolder = pathToRoot + "dependencies/"
pathToDocumentationFolder = pathToRoot + "documentation/"
pathToInputFolder = pathToRoot + "input/"
pathToStaticInputFolder = pathToInputFolder + 'static/'
pathToDynamicInputFolder = pathToInputFolder + 'dynamic/'
pathToLogsFolder = pathToRoot + "logs/"
pathToAsciiLogsFolder = pathToLogsFolder + "ascii/"
pathToHtmlLogsFolder = pathToLogsFolder + "html/"
pathToOutputFolder = pathToRoot + "output/"
pathToOutputDataFolder = pathToOutputFolder + 'data/'
pathToOutputPlotsFolder = pathToOutputFolder + 'plots/'
pathToOutputResultsFolder = pathToOutputFolder + 'results/'
pathToSettingsFolder = pathToRoot + 'settings/'
pathToYamlFile = pathToSettingsFolder + 'python_path.yaml'
pathToDBSettings = pathToSettingsFolder + 'database_credentials.yaml'
pathToLoggingSettings = pathToSettingsFolder + 'logging.yaml'
mdLogPath = pathToOutputResultsFolder + "simulation_result_log_%s.md" % (now,)


#############################################################################################
# CLASSES                                                                                   #
#############################################################################################


############################################
# PUBLIC FUNCTIONS                         #
############################################
def set_python_path():
    """Used simply to set the python path for the project modules
    - note, the Apache pythonpath is not the same as the users path so this function is particularly usful if the project is a web-based.

    **Key Arguments:**
        - ``None``

    **Return:**
        - ``None``
    """
    ################ > IMPORTS ################
    import yaml

    ## IMPORT THE YAML PYTHONPATH DICTIONARY ##
    path = os.getcwd()

    ################ >ACTION(S) ################
    ## READ THE ABSOLUTE PATH TO THE ROOT DIRECTORY OF THIS PROJECT
    try:
        stream = file(pathToYamlFile, 'r')
        ppDict = yaml.load(stream)
    except Exception, e:
        print str(e)

    # READ THE KEYS FROM THE YAML DICTIONARY AND APPEND TO PYTHONPATH
    svnroot = ppDict["project_root"]
    pythonpaths = ppDict["python_path"]
    print "Here's what has been appended to your pythonpath:"
    for k, v in pythonpaths.iteritems():
        if v:
            sys.path.append(svnroot+pythonpaths[k])
            print """%s""" % (svnroot+pythonpaths[k],)

    return


## LAST MODIFIED : April 12, 2013
## CREATED : April 12, 2013
## AUTHOR : DRYX
def read_in_survey_parameters(
        log,
        pathToSettingsFile
    ):
    """First reads in the mcs_settings.yaml file to determine the name of the settings file to read in the survey parameters.

    **Key Arguments:**
        - ``log`` -- logger
        - ``pathToSettingsFile`` -- path to the settings file for the simulation

    **Return:**
        - a tuple of settings lists and dictionaries
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import yaml
    ## LOCAL APPLICATION ##

    ############### VARIABLE ATTRIBUTES #############
    ################ >ACTION(S) ################
    ## READ THE NAME OF THE SETTINGS FILE FOR THIS SIMULATION
    try:
        stream = file(pathToSettingsFile, 'r')
        thisDict = yaml.load(stream)
        stream.close()
    except Exception, e:
        print str(e)

    # NOW READ IN THE USER SET MCS SETTINGS
    try:
        stream = file(pathToSettingsFile, 'r')
        thisDict = yaml.load(stream)
        stream.close()
    except Exception, e:
        print str(e)

    allSettings = thisDict
    programSettings = thisDict["Program Settings"]

    limitingMags = thisDict["Limiting Magnitudes"]
    # for key in limitingMags:
        # log.debug('filter: %s, limit: %s' % (key, limitingMags[key]))

    sampleNumber = thisDict["Simulation Sample"]

    peakMagnitudeDistributions = thisDict["SN Absolute Peak-Magnitude Distributions"]
    #log.debug('snDistributions[magnitude] %s' % (snDistributions["magnitude"],))
    #log.debug('snDistributions[sigma] %s' % (snDistributions["sigma"],))

    relativeRatesSet = thisDict["Relative Rate Set to Use"]
    relativeSNRates = thisDict["Relative SN Rates"][relativeRatesSet]
    #log.debug('relativeSNRates %s' % (relativeSNRates,))
    lowerReshiftLimit = thisDict["Lower Redshift Limit"]
    upperRedshiftLimit = thisDict["Upper Redshift Limit"]
    #log.debug('upperRedshiftLimit %s' % (upperRedshiftLimit,))
    redshiftResolution = thisDict["Redshift Resolution"]

    extinctionSettings = thisDict["Extinctions"]
    extinctionType = extinctionSettings["constant or random"]
    extinctionConstant = extinctionSettings["constant E(b-v)"]

    hostExtinctionDistributions = extinctionSettings["host"]
    #log.debug('hostExtinctionDistributions %s' % (hostExtinctionDistributions,))
    galacticExtinctionDistribution = extinctionSettings["galactic"]
    #log.debug('galacticExtinctionDistribution %s' % (galacticExtinctionDistribution,))

    surveyCadenceSettings = thisDict["Survey Cadence"]
    #log.debug('surveyCadenceSettings %s' % (surveyCadenceSettings,))

    explosionDaysFromSettings = thisDict["Explosion Days"]
    extendLightCurveTail = thisDict["Extend lightcurve tail?"]

    snLightCurves = thisDict["Lightcurves"]
    lightCurvePolyOrder = thisDict["Order of polynomial used to fits lightcurves"]
    #log.debug('snlightCurves %s' % (snlightCurves,))

    surveyArea = thisDict["Sky Area of the Survey (square degrees)"]
    CCSNRateFraction = thisDict["CCSN Progenitor Population Fraction of IMF"]
    transientToCCSNRateFraction = thisDict["Transient to CCSN Ratio"]
    extraSurveyConstraints = thisDict["Extra Survey Constraints"]
    restFrameFilter = thisDict["Rest Frame Filter for K-corrections"]
    kCorrectionTemporalResolution = thisDict["K-correction temporal resolution (days)"]
    kCorPolyOrder = thisDict["Order of polynomial used to fits k-corrections"]
    kCorMinimumDataPoints = thisDict["Minimum number of datapoints used to generate k-correction curve"]
    logLevel = thisDict["Level of logging required"]

    return (
        allSettings,
        programSettings,
        limitingMags,
        sampleNumber,
        peakMagnitudeDistributions,
        explosionDaysFromSettings,
        extendLightCurveTail,
        relativeSNRates,
        lowerReshiftLimit,
        upperRedshiftLimit,
        redshiftResolution,
        restFrameFilter,
        kCorrectionTemporalResolution,
        kCorPolyOrder,
        kCorMinimumDataPoints,
        extinctionType,
        extinctionConstant,
        hostExtinctionDistributions,
        galacticExtinctionDistribution,
        surveyCadenceSettings,
        snLightCurves,
        surveyArea,
        CCSNRateFraction,
        transientToCCSNRateFraction,
        extraSurveyConstraints,
        lightCurvePolyOrder,
        logLevel)

############################################
# PRIVATE (HELPER) FUNCTIONS               #
############################################
## LAST MODIFIED : December 5, 2012
## CREATED : December 5, 2012
## AUTHOR : DRYX
def settings(
        pathToSettingsFile,
        dbConn=True,
        log=True
    ):
    """
    Create a connector to the database if required & setup logging

    **Key Arguments:**
        - ``pathToOutputDirectory`` -- path to the outpur directory
        - ``dbConn`` -- want a dbConn?
        - ``logger`` -- want a logger?

    **Return:**
        - dbConn - database connection
        - log - logger
    """
    ################ > IMPORTS ################
    # set_python_path()
    import os
    import dryxPython.mysql as m
    import dryxPython.logs as l

    ################ >SETTINGS ################
    path = os.getcwd()

    ################ >ACTION(S) ################
    ## READ THE PATH OF THIS MODULE TO - SANDBOX OR MARSHALL?
    if dbConn:
        dbConn = m.set_db_connection(pathToDBSettings)
    if log:
        log = l.setup_dryx_logging(pathToLoggingSettings)

    return dbConn, log

if __name__ == '__main__':
    main()


