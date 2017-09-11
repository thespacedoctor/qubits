#!/usr/bin/python
# encoding: utf-8
"""
commonutils

Created by David Young on xxxxx
If you have any questions requiring this script please email me: davidrobertyoung@gmail.com

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


##########################################################################
# CLASSES                                                                                   #
##########################################################################


############################################
# PUBLIC FUNCTIONS                         #
############################################
def set_python_path():
    """
    *Used simply to set the python path for the project modules
    - note, the Apache pythonpath is not the same as the users path so this function is particularly usful if the project is a web-based.*

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
    # READ THE ABSOLUTE PATH TO THE ROOT DIRECTORY OF THIS PROJECT
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
            sys.path.append(svnroot + pythonpaths[k])
            print """%s""" % (svnroot + pythonpaths[k],)

    return


# LAST MODIFIED : April 12, 2013
# CREATED : April 12, 2013
# AUTHOR : DRYX
def read_in_survey_parameters(
    log,
    pathToSettingsFile
):
    """
    *First reads in the mcs_settings.yaml file to determine the name of the settings file to read in the survey parameters.*

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
    # READ THE NAME OF THE SETTINGS FILE FOR THIS SIMULATION
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

    peakMagnitudeDistributions = thisDict[
        "SN Absolute Peak-Magnitude Distributions"]
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
    lightCurvePolyOrder = thisDict[
        "Order of polynomial used to fits lightcurves"]
    #log.debug('snlightCurves %s' % (snlightCurves,))

    surveyArea = thisDict["Sky Area of the Survey (square degrees)"]
    CCSNRateFraction = thisDict["CCSN Progenitor Population Fraction of IMF"]
    transientToCCSNRateFraction = thisDict["Transient to CCSN Ratio"]
    extraSurveyConstraints = thisDict["Extra Survey Constraints"]
    restFrameFilter = thisDict["Rest Frame Filter for K-corrections"]
    kCorrectionTemporalResolution = thisDict[
        "K-correction temporal resolution (days)"]
    kCorPolyOrder = thisDict["Order of polynomial used to fits k-corrections"]
    kCorMinimumDataPoints = thisDict[
        "Minimum number of datapoints used to generate k-correction curve"]
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
# LAST MODIFIED : December 5, 2012
# CREATED : December 5, 2012
# AUTHOR : DRYX


def settings(
    pathToSettingsFile,
    dbConn=True,
    log=True
):
    """
    *Create a connector to the database if required & setup logging*

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
    # READ THE PATH OF THIS MODULE TO - SANDBOX OR MARSHALL?
    if dbConn:
        dbConn = m.set_db_connection(pathToDBSettings)
    if log:
        log = l.setup_dryx_logging(pathToLoggingSettings)

    return dbConn, log


def plot_polynomial(
        log,
        title,
        polynomialDict,
        orginalDataDictionary=False,
        pathToOutputPlotsFolder="~/Desktop",
        xRange=False,
        xlabel=False,
        ylabel=False,
        xAxisLimits=False,
        yAxisLimits=False,
        yAxisInvert=False,
        prependNum=False,
        legend=False):
    """
    *Plot a dictionary of numpy lightcurves polynomials*

    **Key Arguments:**
        - ``log`` -- logger
        - ``title`` -- title for the plot
        - ``polynomialDict`` -- dictionary of polynomials { label01 : poly01, label02 : poly02 }
        - ``orginalDataDictionary`` -- the orginal data points {name: [x, y]}
        - ``pathToOutputPlotsFolder`` -- path the the output folder to save plot to
        - ``xRange`` -- the x-range for the polynomial [xmin, xmax, interval]
        - ``xlabel`` -- xlabel
        - ``ylabel`` -- ylabel
        - ``xAxisLimits`` -- the x-limits for the axes [xmin, xmax]
        - ``yAxisLimits`` -- the y-limits for the axes [ymin, ymax]
        - ``yAxisInvert`` -- invert the y-axis? Useful for lightcurves
        - ``prependNum`` -- prepend this number to the output filename
        - ``legend`` -- plot a legend?

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    import sys
    ## THIRD PARTY ##
    import matplotlib.pyplot as plt
    import numpy as np
    ## LOCAL APPLICATION ##

    ################ >ACTION(S) ################
    colors = {
        'green': '#859900',
        'blue': '#268bd2',
        'red': '#dc322f',
        'gray': '#D2D1D1',
        'orange': '#cb4b16',
        'violet': '#6c71c4',
        'cyan': '#2aa198',
        'magenta': '#d33682',
        'yellow': '#b58900'
    }

    if not xRange:
        log.error('please provide an x-range')
        sys.exit(1)

    ax = plt.subplot(111)

    if len(xRange) == 2:
        x = np.arange(xRange[0] * 4, xRange[1] * 4, 1)
        x = x / 4.
    else:
        x = np.arange(xRange[0], xRange[1], xRange[2])

    if xAxisLimits:
        ax.set_xlim(xAxisLimits[0], xAxisLimits[1])
    else:
        overShoot = (xRange[1] - xRange[0]) / 10.
        ax.set_xlim(xRange[0] - overShoot, xRange[1] + overShoot)
    if yAxisLimits:
        ax.set_ylim(yAxisLimits[0], yAxisLimits[1])

    theseColors = [colors['blue'], colors[
        'green'], colors['red'], colors['violet']]

    count = 0
    if orginalDataDictionary:
        for name, data in orginalDataDictionary.iteritems():
            ax.plot(data[0], data[1], '.', label=name,
                    color=theseColors[count])
            count += 1
            if count == 4:
                count = 0

    count = 0
    for snType, poly in polynomialDict.iteritems():
        log.debug('x: %s' % (x,))
        ax.plot(x, poly(x), label='%s' % (snType,), color=theseColors[count])
        count += 1
        if count == 4:
            count = 0

    # Shink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    # Put a legend to the right of the current axis
    if legend:
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})
    ax.titlesize = 'medium'   # fontsize of the axes title
    ax.labelsize = 'medium'  # fontsize of the x any y labels

    if xlabel:
        plt.xlabel(xlabel, fontsize='small')
    if ylabel:
        plt.ylabel(ylabel, fontsize='small')
    if title:
        plt.title(title, fontsize='small',
                  verticalalignment='bottom', linespacing=0.2)

    if yAxisInvert:
        ax.invert_yaxis()

    # fileName = pathToOutputPlotsFolder + title.replace(" ", "_") + ".ps"
    # plt.savefig(fileName)
    if prependNum:
        title = "%02d_%s" % (prependNum, title)
    thisTitle = title.replace(" ", "_")
    thisTitle = thisTitle.replace("-", "_")
    fileName = pathToOutputPlotsFolder + thisTitle + ".png"
    imageLink = """
![%s_plot](%s)

""" % (thisTitle, fileName)
    plt.savefig(fileName)
    plt.clf()  # clear figure

    return imageLink


# LAST MODIFIED : April 15, 2013
# CREATED : April 15, 2013
# AUTHOR : DRYX
def plot_polar(
        log,
        title,
        dataDictionary,
        pathToOutputPlotsFolder="~/Desktop",
        dataRange=False,
        ylabel=False,
        radius=False,
        circumference=True,
        circleTicksRange=(0, 360, 60),
        circleTicksLabels=".",
        prependNum=False):
    """
    *Plot a dictionary of numpy lightcurves polynomials*

    **Key Arguments:**
        - ``log`` -- logger
        - ``title`` -- title for the plot
        - ``dataDictionary`` -- dictionary of data to plot { label01 : dataArray01, label02 : dataArray02 }
        - ``pathToOutputPlotsFolder`` -- path the the output folder to save plot to
        - ``dataRange`` -- the range for the data [min, max]
        - ``ylabel`` -- ylabel
        - ``radius`` -- the max radius of the plot
        - ``circumference`` -- draw the circumference of the plot?
        - ``circleTicksRange``
        - ``circleTicksLabels``
        - ``prependNum`` -- prepend this number to the output filename

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    import sys
    ## THIRD PARTY ##
    import matplotlib.pyplot as plt
    import numpy as np
    ## LOCAL APPLICATION ##

    ################ >ACTION(S) ################
    colors = [
        {'green': '#859900'},
        {'blue': '#268bd2'},
        {'red': '#dc322f'},
        {'gray': '#D2D1D1'},
        {'orange': '#cb4b16'},
        {'violet': '#6c71c4'},
        {'cyan': '#2aa198'},
        {'magenta': '#d33682'},
        {'yellow': '#b58900'}
    ]

    # FORCE SQUARE FIGURE AND SQUARE AXES LOOKS BETTER FOR POLAR
    fig = plt.figure(
        num=None,
        figsize=(8, 8),
        dpi=None,
        facecolor=None,
        edgecolor=None,
        frameon=True)

    ax = fig.add_axes(
        [0.1, 0.1, 0.8, 0.8],
        polar=True,
        frameon=circumference)

    ax.set_ylim(0, radius)
    # ax.get_xaxis().set_visible(circumference)

    if circleTicksRange:
        circleTicks = np.arange(circleTicksRange[0], circleTicksRange[
                                1], circleTicksRange[2])
    tickLabels = []
    for tick in circleTicks:
        tickLabels.append(".")

    plt.xticks(2 * np.pi * circleTicks / 360., tickLabels)

    count = 0
    for k, v in dataDictionary.iteritems():
        if count <= len(colors):
            colorDict = colors[count]
            count += 1
        else:
            count = 0
            colorDict = colors[count]

        thetaList = []
        twoPi = 2. * np.pi
        for i in range(len(v)):
            thetaList.append(twoPi * np.random.rand())
        thetaArray = np.array(thetaList)

        x = thetaArray
        y = v

        plt.scatter(
            x,
            y,
            label=k,
            s=50,
            c=colorDict.values(),
            marker='o',
            cmap=None,
            norm=None,
            vmin=None,
            vmax=None,
            alpha=0.5,
            linewidths=None,
            edgecolor='#657b83',
            verts=None,
            hold=True)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(0.7, -0.1), prop={'size': 8})
    plt.grid(True)
    plt.title(title)
    if prependNum:
        title = "%02d_%s" % (prependNum, title)
    thisTitle = title.replace(" ", "_")
    thisTitle = thisTitle.replace("-", "_")
    fileName = pathToOutputPlotsFolder + thisTitle + ".png"
    imageLink = """
![%s_plot](%s)

""" % (thisTitle, fileName)
    plt.savefig(fileName)
    plt.clf()  # clear figure

    return imageLink

if __name__ == '__main__':
    main()
