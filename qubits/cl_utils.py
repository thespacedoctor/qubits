#!/usr/local/bin/python
# encoding: utf-8
"""
*Documentation for qubits can be found here: https://github.com/thespacedoctor/qubits*

Usage:
    qubits init <pathToWorkspace>
    qubits run -s <pathToSettingsFile> -o <pathToOutputDirectory> -d <pathToSpectralDatabase>

    COMMANDS
    --------
    init            setup a qubits settings file and a test spectral database
    run             run the qubits simulation according to the setup given in the settings file

    ARGUMENTS
    ---------
    pathToSettingsFile    path to the yaml settings file
    pathToWorkspace       path to a directory within which to setup an example qubit workspace
    
    FLAGS
    -----
    -h, --help      show this help message
    -s, --settings  provide a path to the settings file
    -d, --database  provide the path to the root directory containing your nested-folders and files spectral database
    -o, --output    provide a path to an output directory for the results of the simulations*
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
import readline
import glob
import pickle
import yaml
from docopt import docopt
from fundamentals import tools, times
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime, date, time
from . import commonutils as cu
from . import surveysim as ss
from . import datagenerator as dg
from . import results as r
import dryxPython.commonutils as dcu
from . import universe as u
import dryxPython.mmd.mmd as dmd
# from ..__init__ import *


def main(arguments=None):
    """
    *The main function used when ``cl_utils.py`` is run as a single script from the cl, or when installed as a cl command*
    """
    # setup the command-line util settings
    su = tools(
        arguments=arguments,
        docString=__doc__,
        logLevel="WARNING",
        options_first=False,
        projectName="qubits"
    )
    arguments, settings, log, dbConn = su.setup()

    # unpack remaining cl arguments using `exec` to setup the variable names
    # automatically
    for arg, val in arguments.iteritems():
        if arg[0] == "-":
            varname = arg.replace("-", "") + "Flag"
        else:
            varname = arg.replace("<", "").replace(">", "")
        if varname == "import":
            varname = "iimport"
        if isinstance(val, str) or isinstance(val, unicode):
            exec(varname + " = '%s'" % (val,))
        else:
            exec(varname + " = %s" % (val,))
        if arg == "--dbConn":
            dbConn = val
        log.debug('%s = %s' % (varname, val,))

    ## START LOGGING ##
    startTime = times.get_now_sql_datetime()
    log.info(
        '--- STARTING TO RUN THE cl_utils.py AT %s' %
        (startTime,))

    if init:
        from . import workspace
        ws = workspace(
            log=log,
            pathToWorkspace=pathToWorkspace
        )
        ws.setup()
        return

    # IMPORT THE SIMULATION SETTINGS
    (allSettings,
     programSettings,
     limitingMags,
     sampleNumber,
     peakMagnitudeDistributions,
     explosionDaysFromSettings,
     extendLightCurveTail,
     relativeSNRates,
     lowerRedshiftLimit,
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
     logLevel) = cu.read_in_survey_parameters(
        log,
        pathToSettingsFile=pathToSettingsFile
    )

    logFilePath = pathToOutputDirectory + "/qubits.log"
    del log
    log = _set_up_command_line_tool(
        level=str(logLevel),
        logFilePath=logFilePath
    )

    # dbConn, log = cu.settings(
    #     pathToSettingsFile=pathToSettingsFile,
    #     dbConn=False,
    #     log=True
    # )

    ## START LOGGING ##
    startTime = dcu.get_now_sql_datetime()
    log.info('--- STARTING TO RUN THE qubits AT %s' % (startTime,))

    resultsDict = {}

    pathToOutputPlotDirectory = pathToOutputDirectory + "/plots/"
    dcu.dryx_mkdir(
        log,
        directoryPath=pathToOutputPlotDirectory
    )

    pathToResultsFolder = pathToOutputDirectory + "/results/"
    dcu.dryx_mkdir(
        log,
        directoryPath=pathToResultsFolder
    )

    if not programSettings['Extract Lightcurves from Spectra'] and not programSettings['Generate KCorrection Database'] and not programSettings['Run the Simulation'] and not programSettings['Compile and Plot Results']:
        print "All stages of the simulatation have been switched off. Please switch on at least one stage of the simulation under the 'Programming Settings' in the settings file `%(pathToSettingsFile)s`" % locals()

    # GENERATE THE DATA FOR SIMULATIONS
    if programSettings['Extract Lightcurves from Spectra']:
        log.info('generating the Lightcurves')
        dg.generate_model_lightcurves(
            log=log,
            pathToSpectralDatabase=pathToSpectralDatabase,
            pathToOutputDirectory=pathToOutputDirectory,
            pathToOutputPlotDirectory=pathToOutputPlotDirectory,
            explosionDaysFromSettings=explosionDaysFromSettings,
            extendLightCurveTail=extendLightCurveTail,
            polyOrder=lightCurvePolyOrder
        )
        print "The lightcurve file can be found here: %(pathToOutputDirectory)stransient_light_curves.yaml" % locals()
        print "The lightcurve plots can be found in %(pathToOutputPlotDirectory)s" % locals()

    if programSettings['Generate KCorrection Database']:
        log.info('generating the kcorrection data')
        dg.generate_kcorrection_listing_database(
            log,
            pathToOutputDirectory=pathToOutputDirectory,
            pathToSpectralDatabase=pathToSpectralDatabase,
            restFrameFilter=restFrameFilter,
            temporalResolution=kCorrectionTemporalResolution,
            redshiftResolution=redshiftResolution,
            redshiftLower=lowerRedshiftLimit,
            redshiftUpper=upperRedshiftLimit + redshiftResolution)
        log.info('generating the kcorrection polynomials')
        dg.generate_kcorrection_polynomial_database(
            log,
            pathToOutputDirectory=pathToOutputDirectory,
            restFrameFilter=restFrameFilter,
            kCorPolyOrder=kCorPolyOrder,  # ORDER OF THE POLYNOMIAL TO FIT
            kCorMinimumDataPoints=kCorMinimumDataPoints,
            redshiftResolution=redshiftResolution,
            redshiftLower=lowerRedshiftLimit,
            redshiftUpper=upperRedshiftLimit + redshiftResolution,
            plot=programSettings['Generate KCorrection Plots'])

        print "The k-correction database has been generated here: %(pathToOutputDirectory)sk_corrections" % locals()
        if programSettings['Generate KCorrection Plots']:
            print "The k-correction polynomial plots can also be found in %(pathToOutputDirectory)sk_corrections" % locals()

    if programSettings['Run the Simulation']:
        # CREATE THE OBSERVABLE UNIVERSE!
        log.info('generating the redshift array')
        redshiftArray = u.random_redshift_array(
            log,
            sampleNumber,
            lowerRedshiftLimit,
            upperRedshiftLimit,
            redshiftResolution=redshiftResolution,
            pathToOutputPlotDirectory=pathToOutputPlotDirectory,
            plot=programSettings['Plot Simulation Helper Plots'])
        resultsDict['Redshifts'] = redshiftArray.tolist()

        log.info('generating the SN type array')
        snTypesArray = u.random_sn_types_array(
            log,
            sampleNumber,
            relativeSNRates,
            pathToOutputPlotDirectory=pathToOutputPlotDirectory,
            plot=programSettings['Plot Simulation Helper Plots'])
        resultsDict['SN Types'] = snTypesArray.tolist()

        log.info('generating peak magnitudes for the SNe')
        peakMagnitudesArray = u.random_peak_magnitudes(
            log,
            peakMagnitudeDistributions,
            snTypesArray,
            plot=programSettings['Plot Simulation Helper Plots'])

        log.info('generating the SN host extictions array')
        hostExtinctionArray = u.random_host_extinction(
            log,
            sampleNumber,
            extinctionType,
            extinctionConstant,
            hostExtinctionDistributions,
            plot=programSettings['Plot Simulation Helper Plots'])

        log.info('generating the SN galactic extictions array')
        galacticExtinctionArray = u.random_galactic_extinction(
            log,
            sampleNumber,
            extinctionType,
            extinctionConstant,
            galacticExtinctionDistribution,
            plot=programSettings['Plot Simulation Helper Plots'])

        log.info('generating the raw lightcurves for the SNe')
        rawLightCurveDict = u.generate_numpy_polynomial_lightcurves(
            log,
            snLightCurves=snLightCurves,
            pathToOutputDirectory=pathToOutputDirectory,
            pathToOutputPlotDirectory=pathToOutputPlotDirectory,
            plot=programSettings['Plot Simulation Helper Plots'])

        log.info('generating the k-correction array for the SNe')
        kCorrectionArray = u.build_kcorrection_array(
            log,
            redshiftArray,
            snTypesArray,
            snLightCurves,
            pathToOutputDirectory=pathToOutputDirectory,
            plot=programSettings['Plot Simulation Helper Plots'])

        log.info('generating the observed lightcurves for the SNe')
        observedFrameLightCurveInfo, peakAppMagList = u.convert_lightcurves_to_observered_frame(
            log,
            snLightCurves=snLightCurves,
            rawLightCurveDict=rawLightCurveDict,
            redshiftArray=redshiftArray,
            snTypesArray=snTypesArray,
            peakMagnitudesArray=peakMagnitudesArray,
            kCorrectionArray=kCorrectionArray,
            hostExtinctionArray=hostExtinctionArray,
            galacticExtinctionArray=galacticExtinctionArray,
            restFrameFilter=restFrameFilter,
            pathToOutputDirectory=pathToOutputDirectory,
            pathToOutputPlotDirectory=pathToOutputPlotDirectory,
            polyOrder=lightCurvePolyOrder,
            plot=programSettings['Plot Simulation Helper Plots'])

        log.info('generating the survey observation cadence')
        cadenceDictionary = ss.survey_cadence_arrays(
            log,
            surveyCadenceSettings,
            pathToOutputDirectory=pathToOutputDirectory,
            pathToOutputPlotDirectory=pathToOutputPlotDirectory,
            plot=programSettings['Plot Simulation Helper Plots'])

        log.info('determining if the SNe are discoverable by the survey')
        discoverableList = ss.determine_if_sne_are_discoverable(
            log,
            redshiftArray=redshiftArray,
            limitingMags=limitingMags,
            observedFrameLightCurveInfo=observedFrameLightCurveInfo,
            pathToOutputDirectory=pathToOutputDirectory,
            pathToOutputPlotDirectory=pathToOutputPlotDirectory,
            plot=programSettings['Plot Simulation Helper Plots'])

        log.info(
            'determining the day (if and) when each SN is first discoverable by the survey')
        ripeDayList = ss.determine_when_sne_are_ripe_for_discovery(
            log,
            redshiftArray=redshiftArray,
            limitingMags=limitingMags,
            discoverableList=discoverableList,
            observedFrameLightCurveInfo=observedFrameLightCurveInfo,
            plot=programSettings['Plot Simulation Helper Plots'])

        # log.info('determining the day when each SN is disappears fainter than the survey limiting mags')
        # disappearDayList = determine_when_discovered_sne_disappear(
        #     log,
        #     redshiftArray=redshiftArray,
        #     limitingMags=limitingMags,
        #     ripeDayList=ripeDayList,
        #     observedFrameLightCurveInfo=observedFrameLightCurveInfo,
        #     plot=programSettings['Plot Simulation Helper Plots'])

        log.info('determining if and when each SN is discovered by the survey')
        lightCurveDiscoveryDayList, surveyDiscoveryDayList, snCampaignLengthList = ss.determine_if_sne_are_discovered(
            log,
            limitingMags=limitingMags,
            ripeDayList=ripeDayList,
            cadenceDictionary=cadenceDictionary,
            observedFrameLightCurveInfo=observedFrameLightCurveInfo,
            extraSurveyConstraints=extraSurveyConstraints,
            plot=programSettings['Plot Simulation Helper Plots'])

        resultsDict[
            'Discoveries Relative to Peak Magnitudes'] = lightCurveDiscoveryDayList
        resultsDict[
            'Discoveries Relative to Survey Year'] = surveyDiscoveryDayList
        resultsDict['Campaign Length'] = snCampaignLengthList
        resultsDict['Cadence Dictionary'] = cadenceDictionary
        resultsDict['Peak Apparent Magnitudes'] = peakAppMagList

        now = datetime.now()
        now = now.strftime("%Y%m%dt%H%M%S")
        fileName = pathToOutputDirectory + \
            "/simulation_results_%s.yaml" % (now,)
        stream = file(fileName, 'w')
        yamlContent = dict(allSettings.items() + resultsDict.items())
        yaml.dump(yamlContent, stream, default_flow_style=False)
        stream.close()

        print "The simulation output file can be found here: %(fileName)s. Remember to update your settings file 'Simulation Results File Used for Plots' parameter with this filename before compiling the results." % locals()
        if programSettings['Plot Simulation Helper Plots']:
            print "The simulation helper-plots found in %(pathToOutputPlotDirectory)s" % locals()

    # COMPILE AND PLOT THE RESULTS
    if programSettings['Compile and Plot Results']:
        pathToYamlFile = pathToOutputDirectory + "/" + \
            programSettings['Simulation Results File Used for Plots']
        result_log = r.log_the_survey_settings(log, pathToYamlFile)
        snSurveyDiscoveryTimes, lightCurveDiscoveryTimes, snTypes, redshifts, cadenceDictionary, peakAppMagList, snCampaignLengthList = r.import_results(
            log, pathToYamlFile)
        snRatePlotLink, totalRate, tooFaintRate, shortCampaignRate = r.determine_sn_rate(
            log,
            lightCurveDiscoveryTimes,
            snSurveyDiscoveryTimes,
            redshifts,
            surveyCadenceSettings=surveyCadenceSettings,
            lowerRedshiftLimit=lowerRedshiftLimit,
            upperRedshiftLimit=upperRedshiftLimit,
            redshiftResolution=redshiftResolution,
            surveyArea=surveyArea,
            CCSNRateFraction=CCSNRateFraction,
            transientToCCSNRateFraction=transientToCCSNRateFraction,
            peakAppMagList=peakAppMagList,
            snCampaignLengthList=snCampaignLengthList,
            extraSurveyConstraints=extraSurveyConstraints,
            pathToOutputPlotFolder=pathToOutputPlotDirectory)
        result_log += """
## Results ##

This simulated survey discovered a total of **%s** transients per year. An extra **%s** transients were detected but deemed too faint to constrain a positive transient identification and a further **%s** transients where detected but an observational campaign of more than **%s** days could not be completed to ensure identification. See below for the various output plots.

        """ % (totalRate, tooFaintRate, shortCampaignRate, extraSurveyConstraints["Observable for at least ? number of days"])
        cadenceWheelLink = r.plot_cadence_wheel(
            log,
            cadenceDictionary,
            pathToOutputPlotFolder=pathToOutputPlotDirectory)
        result_log += """%s""" % (cadenceWheelLink,)
        discoveryMapLink = r.plot_sn_discovery_map(
            log,
            snSurveyDiscoveryTimes,
            peakAppMagList,
            snCampaignLengthList,
            redshifts,
            extraSurveyConstraints,
            pathToOutputPlotFolder=pathToOutputPlotDirectory)
        result_log += """%s""" % (discoveryMapLink,)
        ratioMapLink = r.plot_sn_discovery_ratio_map(
            log,
            snSurveyDiscoveryTimes,
            redshifts,
            peakAppMagList,
            snCampaignLengthList,
            extraSurveyConstraints,
            pathToOutputPlotFolder=pathToOutputPlotDirectory)
        result_log += """%s""" % (ratioMapLink,)
        result_log += """%s""" % (snRatePlotLink,)

        now = datetime.now()
        now = now.strftime("%Y%m%dt%H%M%S")
        mdLogPath = pathToResultsFolder + \
            "simulation_result_log_%s.md" % (now,)
        mdLog = open(mdLogPath, 'w')
        mdLog.write(result_log)
        mdLog.close()

        dmd.convert_to_html(
            log=log,
            pathToMMDFile=mdLogPath,
            css="amblin"
        )

        print "Results can be found here: %(pathToResultsFolder)s" % locals()
        html = mdLogPath.replace(".md", ".html")
        print "Open this file in your browser: %(html)s" % locals()

    if "dbConn" in locals() and dbConn:
        dbConn.commit()
        dbConn.close()
    ## FINISH LOGGING ##
    endTime = times.get_now_sql_datetime()
    runningTime = times.calculate_time_difference(startTime, endTime)
    log.info('-- FINISHED ATTEMPT TO RUN THE cl_utils.py AT %s (RUNTIME: %s) --' %
             (endTime, runningTime, ))

    return


def _set_up_command_line_tool(
    level="DEBUG",
        logFilePath="/tmp/tmp.log"):
    import logging
    import logging.config
    import yaml

    logging.shutdown()
    reload(logging)

    loggerConfig = """
    version: 1
    formatters:
        file_style:
            format: '* %(asctime)s - %(name)s - %(levelname)s (%(filename)s > %(funcName)s > %(lineno)d) - %(message)s  '
            datefmt: '%Y/%m/%d %H:%M:%S'
        console_style:
            format: '* %(asctime)s - %(levelname)s: %(filename)s:%(funcName)s:%(lineno)d > %(message)s'
            datefmt: '%H:%M:%S'
        html_style:
            format: '<div id="row" class="%(levelname)s"><span class="date">%(asctime)s</span>   <span class="label">file:</span><span class="filename">%(filename)s</span>   <span class="label">method:</span><span class="funcName">%(funcName)s</span>   <span class="label">line#:</span><span class="lineno">%(lineno)d</span> <span class="pathname">%(pathname)s</span>  <div class="right"><span class="message">%(message)s</span><span class="levelname">%(levelname)s</span></div></div>'
            datefmt: '%Y-%m-%d <span class= "time">%H:%M <span class= "seconds">%Ss</span></span>'
    handlers:
        console:
            class: logging.StreamHandler
            level: """ + level + """
            formatter: console_style
            stream: ext://sys.stdout
        development_logs:
            class: logging.FileHandler
            level: """ + level + """
            formatter: file_style
            filename: """ + logFilePath + """
            mode: w
    root:
        level: DEBUG
        handlers: [console,development_logs]"""

    logging.config.dictConfig(yaml.load(loggerConfig))
    log = logging.getLogger(__name__)

    return log


if __name__ == '__main__':
    main()
