#!/usr/bin/python
# encoding: utf-8
"""
results
======================================
:Summary:
    Partial to comile and plot the results of the SN Survey Simulator

:Author:
    David Young

:Date Created:
    April 18, 2013

:dryx syntax:
    - ``xxx`` = come back here and do some more work
    - ``_someObject`` = a 'private' object that should only be changed for debugging

:Notes:
    - If you have any questions requiring this script please email me: d.r.young@qub.ac.uk
"""
################# GLOBAL IMPORTS ####################
from commonutils import *


###################################################################
# CLASSES                                                         #
###################################################################

###################################################################
# PUBLIC FUNCTIONS                                                #
###################################################################
## LAST MODIFIED : April 18, 2013
## CREATED : April 18, 2013
## AUTHOR : DRYX
def import_results(log, pathToYamlFile):
    """Import the results of the simulation (the filename is an argument of this models)

    **Key Arguments:**
        - ``log`` -- logger
        - ``pathToYamlFile`` -- the path to the yaml file to be imported

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import yaml
    ## LOCAL APPLICATION ##

    ################ >ACTION(S) ################
    fileName = pathToYamlFile
    stream = file(fileName, 'r')
    yamlContent = yaml.load(stream)
    snSurveyDiscoveryTimes = yamlContent['Discoveries Relative to Survey Year']
    lightCurveDiscoveryTimes = yamlContent['Discoveries Relative to Peak Magnitudes']
    snTypes = yamlContent['SN Types']
    redshifts = yamlContent['Redshifts']
    cadenceDictionary = yamlContent['Cadence Dictionary']
    peakAppMagList = yamlContent['Peak Apparent Magnitudes']
    snCampaignLengthList = yamlContent['Campaign Length']

    # log.info('yamlContent %s' % (yamlContent,))
    stream.close()

    return snSurveyDiscoveryTimes, lightCurveDiscoveryTimes, snTypes, redshifts, cadenceDictionary, peakAppMagList, snCampaignLengthList


## LAST MODIFIED : April 19, 2013
## CREATED : April 19, 2013
## AUTHOR : DRYX
def plot_cadence_wheel(
        log,
        cadenceDictionary,
        pathToOutputPlotFolder):
    """Generate the cadence wheel for the survey

    **Key Arguments:**
        - ``log`` -- logger
        - ``cadenceDictionary`` -- the cadence for the survey
        - ``pathToOutputPlotDirectory`` -- path to add plots to

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import numpy as np
    import matplotlib.pyplot as plt
    ## LOCAL APPLICATION ##
    import dryxPython.plotting as dp

    lunarMonth = 29.3
    surveyYear = 12.*lunarMonth

    ################ >ACTION(S) ################
    fig = plt.figure(
        num=None,
        figsize=(8,8),
        dpi=600,
        facecolor=None,
        edgecolor=None,
        frameon=True)

    ax = fig.add_axes(
        [0.1, 0.1, 0.8, 0.8],
        polar=True,
        frameon=False)
    # ax.set_xlabel('label')
    # ax.set_ylabel('label')
    # ax.set_title('title')
    # ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)

    for k, v in cadenceDictionary.iteritems():
        # log.debug('k %s' % (k,))
        x = 2*np.pi*np.array(v)/surveyYear
        y = np.ones(len(x))*10.

        if k in ['g', 'B']:
            color = '#268bd2'
        elif k in ['r', 'V']:
            color = '#859900'
        elif k in ['R', 'i']:
            color = '#cb4b16'
        elif k in ['I', 'z']:
            color = '#dc322f'
        # elif k in ['', '']
        #     color = ''
        else:
            color = '#b58900'

        plt.scatter(
            x,
            y,
            s=50,
            c=color,
            marker='o',
            cmap=None,
            label=k,
            norm=None,
            vmin=None,
            vmax=None,
            alpha=0.2,
            linewidths=None,
            edgecolor=color,
            verts=None,
            hold=True)

    circleTicks = np.arange(0, 350, 30)
    tickLabels = []
    for tick in circleTicks:
        tickLabels.append("%s days" % (tick,))

    plt.xticks(2*np.pi*circleTicks/surveyYear, tickLabels)
    plt.yticks([])

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(1.1, 0.5), prop={'size':8})

    title = "Cadence Wheel for Simulated Survey"
    plt.title(title, fontsize='small', verticalalignment = 'bottom', linespacing = 0.2)
    fileName = pathToOutputPlotFolder + title.replace(" ", "_") + ".png"
    imageLink = """
![%s_plot](%s)

""" % (title.replace(" ", "_"), fileName,)
    plt.savefig(fileName)
    plt.clf()  # clear figure

    return imageLink

## LAST MODIFIED : April 19, 2013
## CREATED : April 19, 2013
## AUTHOR : DRYX
def plot_sn_discovery_map(log,
        snSurveyDiscoveryTimes,
        peakAppMagList,
        snCampaignLengthList,
        redshifts,
        extraSurveyConstraints,
        pathToOutputPlotFolder):
    """Plot the SN discoveries in a polar plot as function of redshift & time

    **Key Arguments:**
        - ``log`` -- logger
        - ``snSurveyDiscoveryTimes`` --
        - ``peakAppMagList`` --
        - ``snCampaignLengthList`` -- a list of campaign lengths in each filter
        - ``redshifts`` --
        - ``extraSurveyConstraints`` --
        - ``pathToOutputPlotDirectory`` -- path to add plots to

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
    filters = ['g', 'r', 'i', 'z']
    lunarMonth = 29.3
    surveyYear = 12.*lunarMonth

    faintMagLimit = extraSurveyConstraints['Faint-Limit of Peak Magnitude']

    ################ >ACTION(S) ################
    discovered = []
    tooFaint = []
    shortCampaign = []
    discoveredRedshift = []
    tooFaintRedshift = []
    notDiscoveredRedshift = []
    shortCampaignRedshift = []
    #log.info('len(redshifts) %s' % (len(redshifts),))
    for item in range(len(redshifts)):
        if snSurveyDiscoveryTimes[item]['any'] is True:
            discoveryDayList = []
            faintDayList = []
            shortCampaignDayList = []
            for ffilter in filters:
                if snSurveyDiscoveryTimes[item][ffilter]:
                    if peakAppMagList[item][ffilter] < faintMagLimit:
                        if snCampaignLengthList[item]['max'] < extraSurveyConstraints['Observable for at least ? number of days']:
                            shortCampaignDayList.append(snSurveyDiscoveryTimes[item][ffilter])
                        else:
                            discoveryDayList.append(snSurveyDiscoveryTimes[item][ffilter])
                    else:
                        faintDayList.append(snSurveyDiscoveryTimes[item][ffilter])

            if len(discoveryDayList) > 0:
                discovered.append(min(discoveryDayList))
                discoveredRedshift.append(redshifts[item])
            elif len(shortCampaignDayList) > 0:
                shortCampaign.append(min(shortCampaignDayList))
                shortCampaignRedshift.append(redshifts[item])
            else:
                tooFaint.append(min(faintDayList))
                tooFaintRedshift.append(redshifts[item])
        else:
            notDiscoveredRedshift.append(redshifts[item])

    ################ >ACTION(S) ################
    colors = [
        {'red' : '#dc322f'},
        {'blue' : '#268bd2'},
        {'green' : '#859900'},
        {'orange' : '#cb4b16'},
        {'gray' : '#93a1a1'},
        {'violet' : '#6c71c4'},
        {'cyan' : '#2aa198'},
        {'magenta' : '#d33682'},
        {'yellow' : '#b58900'}
    ]

    # FORCE SQUARE FIGURE AND SQUARE AXES LOOKS BETTER FOR POLAR
    fig = plt.figure(
        num=None,
        figsize=(8,8),
        dpi=None,
        facecolor=None,
        edgecolor=None,
        frameon=True)

    ax = fig.add_axes(
        [0.1, 0.1, 0.8, 0.8],
        polar=True,
        frameon=False)

    ax.set_ylim(0, 1.1)
    # ax.get_xaxis().set_visible(False)

    circleTicks = np.arange(0, 350, 30)
    tickLabels = []
    for tick in circleTicks:
        tickLabels.append("%s days" % (tick,))

    plt.xticks(2*np.pi*circleTicks/360., tickLabels)

    discovered = 2*np.pi*np.array(discovered)/surveyYear
    discoveredRedshift = np.array(discoveredRedshift)

    tooFaint = 2*np.pi*np.array(tooFaint)/surveyYear
    tooFaintRedshift = np.array(tooFaintRedshift)

    shortCampaign = 2*np.pi*np.array(shortCampaign)/surveyYear
    shortCampaignRedshift = np.array(shortCampaignRedshift)

    plt.scatter(
        tooFaint,
        tooFaintRedshift,
        label="""Detected - too faint to constrain as transient""",
        s=50,
        c='#dc322f',
        marker='o',
        cmap=None,
        norm=None,
        vmin=None,
        vmax=None,
        alpha=0.2,
        linewidths=None,
        edgecolor='#657b83',
        verts=None,
        hold=True)

    plt.scatter(
        discovered,
        discoveredRedshift,
        label='Discovered transient',
        s=50,
        c='#859900',
        marker='o',
        cmap=None,
        norm=None,
        vmin=None,
        vmax=None,
        alpha=0.2,
        linewidths=None,
        edgecolor='#657b83',
        verts=None,
        hold=True)

    plt.scatter(
        shortCampaign,
        shortCampaignRedshift,
        label="""Detected - campaign to short to constrain as transient""",
        s=50,
        c='#268bd2',
        marker='o',
        cmap=None,
        norm=None,
        vmin=None,
        vmax=None,
        alpha=0.2,
        linewidths=None,
        edgecolor='#657b83',
        verts=None,
        hold=True)

    title = "transients Detected Within the Suvrey Year"
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(0.7, -0.1), prop={'size':8})
    plt.grid(True)
    plt.title(title, fontsize='small', verticalalignment = 'bottom', linespacing = 0.2)
    fileName = pathToOutputPlotFolder + title.replace(" ", "_") + ".png"
    imageLink = """
![%s_plot](%s)

""" % (title.replace(" ", "_"), fileName)
    plt.savefig(fileName)
    plt.clf()  # clear figure

    return imageLink


## LAST MODIFIED : April 19, 2013
## CREATED : April 19, 2013
## AUTHOR : DRYX
def plot_sn_discovery_ratio_map(log,
        snSurveyDiscoveryTimes,
        redshifts,
        peakAppMagList,
        snCampaignLengthList,
        extraSurveyConstraints,
        pathToOutputPlotFolder):
    """Plot the SN discoveries and non-discoveries in a polar plot as function of redshift

    **Key Arguments:**
        - ``log`` -- logger
        - ``snSurveyDiscoveryTimes`` --
        - ``redshifts`` --
        - ``peakAppMagList`` -- the list of peakmags for each SN in each filter
        - ``snCampaignLengthList`` -- a list of campaign lengths in each filter
        - ``extraSurveyConstraints`` --
        - ``pathToOutputPlotDirectory`` -- path to add plots to


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
    import dryxPython.plotting as dp
    filters = ['g', 'r', 'i', 'z']
    faintMagLimit = extraSurveyConstraints['Faint-Limit of Peak Magnitude']

    ################ >ACTION(S) ################
    discovered = []
    tooFaint = []
    shortCampaign = []
    discoveredRedshift = []
    tooFaintRedshift = []
    notDiscoveredRedshift = []
    shortCampaignRedshift = []
    #log.info('len(redshifts) %s' % (len(redshifts),))
    dataDictionary = {}
    for item in range(len(redshifts)):
        if snSurveyDiscoveryTimes[item]['any'] is True:
            discoveryDayList = []
            faintDayList = []
            shortCampaignDayList = []
            for ffilter in filters:
                if snSurveyDiscoveryTimes[item][ffilter]:
                    if peakAppMagList[item][ffilter] < faintMagLimit:
                        if snCampaignLengthList[item]['max'] < extraSurveyConstraints['Observable for at least ? number of days']:
                            shortCampaignDayList.append(snSurveyDiscoveryTimes[item][ffilter])
                        else:
                            discoveryDayList.append(snSurveyDiscoveryTimes[item][ffilter])
                    else:
                        faintDayList.append(snSurveyDiscoveryTimes[item][ffilter])

            if len(discoveryDayList) > 0:
                discovered.append(min(discoveryDayList))
                discoveredRedshift.append(redshifts[item])
            elif len(shortCampaignDayList) > 0:
                shortCampaign.append(min(shortCampaignDayList))
                shortCampaignRedshift.append(redshifts[item])
            else:
                tooFaint.append(min(faintDayList))
                tooFaintRedshift.append(redshifts[item])
        else:
            notDiscoveredRedshift.append(redshifts[item])

    if len(notDiscoveredRedshift) > 0:
        dataDictionary["Undiscovered"] = notDiscoveredRedshift
    if len(tooFaintRedshift) > 0:
        dataDictionary["Detected - too faint to constrain as transient"] = tooFaintRedshift
    if len(discoveredRedshift) > 0:
        dataDictionary["Discovered"] = discoveredRedshift
    if len(shortCampaignRedshift) > 0:
        dataDictionary["Detected - campaign to short to constrain as transient"] = shortCampaignRedshift

    ################ >ACTION(S) ################
    imageLink = dp.plot_polar(
       log,
       title="Redshift Map of transients Simulated within the Survey Volume",
       dataDictionary=dataDictionary,
       pathToOutputPlotsFolder=pathToOutputPlotFolder,
       dataRange=False,
       ylabel=False,
       radius=1.1,
       circumference=False,
       circleTicksRange=(0, 360, 60),
       circleTicksLabels=".",
       prependNum=False)

    return imageLink


## LAST MODIFIED : April 19, 2013
## CREATED : April 19, 2013
## AUTHOR : DRYX
def determine_sn_rate(
        log,
        lightCurveDiscoveryTimes,
        snSurveyDiscoveryTimes,
        redshifts,
        surveyCadenceSettings,
        surveyArea,
        CCSNRateFraction,
        transientToCCSNRateFraction,
        peakAppMagList,
        snCampaignLengthList,
        extraSurveyConstraints,
        pathToOutputPlotFolder,
        upperRedshiftLimit=1.0,
        redshiftResolution=0.1
        ):
    """Plot the SFR History as a function of redshift

    **Key Arguments:**
        - ``log`` -- logger
        - ``lightCurveDiscoveryTimes`` -- the lightcurve discovery times of the SN
        - ``snSurveyDiscoveryTimes`` -- the supernova discovery times relative to the survey year
        - ``redshifts`` -- the redshifts of the SN
        - ``surveyArea`` -- the area of the survey considered in square degree
        - ``surveyCadenceSettings`` -- the cadence settings for the survey
        - ``CCSNRateFraction`` -- the fraction of the IMF attributed to the progenitors of CCSN
        - ``transientToCCSNRateFraction`` -- the ratio of the transient rate to the rate of CCSNe
        - ``peakAppMagList`` -- a list of the peak magnitudes for each SN in each filter
        - ``snCampaignLengthList`` -- a list of campaign lengths in each filter
        - ``extraSurveyConstraints`` -- some extra survey constraints
        - ``pathToOutputPlotDirectory`` -- path to add plots to
        - ``upperRedshiftLimit`` -- the redshist limit out to which to determine the rate
        - ``redshiftResolution`` -- the redshist resolution ued to determine the rate

    **Return:**
        - ``imageLink`` -- MD link to the output plot
        - ``totalRate`` -- the final transient rate calculated
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import numpy as np
    ## LOCAL APPLICATION ##
    import dryxPython.astrotools as da
    import dryxPython.plotting as dp

    ################ >ACTION(S) ################
    filters = ['g', 'r', 'i', 'z']

    sdssArea = 5713.
    sdssSFRupperRedshiftLimit = 0.033
    sdssSFR = 14787.21
    CCSNRateFraction = 0.007
    transientToCCSNRateFraction = 1./10000.
    transientRateFraction = CCSNRateFraction*transientToCCSNRateFraction

    anchor = redshiftResolution/sdssSFRupperRedshiftLimit
    normaiseSFR = sdssSFR*anchor**3
    areaRatio = surveyArea/sdssArea
    #log.info('normaiseSFR %s' % (normaiseSFR,))

    anchorVolume = da.convert_redshift_to_distance(redshiftResolution)['dl_mpc']**3
    #log.info('anchorVolume %s' % (anchorVolume,))

    multiplier = int(1/redshiftResolution)
    redshiftResolution = int(redshiftResolution*multiplier)
    upperRedshiftLimit = int(upperRedshiftLimit*multiplier)

    shelltransientRateDensityList = []
    shellRedshiftList = []
    discoveryRedshiftList = []
    discoveryFractionList = []
    tooFaintRedshiftList = []
    tooFaintFractionList = []
    shortCampaignRedshiftList = []
    shortCampaignFractionList = []
    transientShellRateList = []
    tooFaintShellRateList = []
    shortCampaignShellRateList = []
    for shellRedshift in range(redshiftResolution, upperRedshiftLimit, redshiftResolution):
        shellRedshift = float(shellRedshift)/float(multiplier)
        shellWidth = float(redshiftResolution)/float(multiplier)
        shellMiddle = shellRedshift - shellWidth/2.
        shellRedshiftBottom = shellRedshift - shellWidth
        #log.info('shellMiddle %s' % (shellMiddle,))
        SFH = (1.+shellMiddle)**2.5
        if shellRedshift > shellWidth:
            shellVolume = da.convert_redshift_to_distance(shellRedshift)['dl_mpc']**3 - da.convert_redshift_to_distance(shellRedshift-shellWidth)['dl_mpc']**3
        else:
            shellVolume = da.convert_redshift_to_distance(shellRedshift)['dl_mpc']**3
        shellSFRDensity = (SFH/anchor)*normaiseSFR*(shellVolume/anchorVolume)
        shelltransientRateDensity = shellSFRDensity*transientRateFraction
        shelltransientRateDensity = shelltransientRateDensity*areaRatio
        timeDilation = 1./(1.+shellMiddle)
        shelltransientRateDensity = shelltransientRateDensity*timeDilation
        # log.info('shelltransientRateDensity %s' % (shelltransientRateDensity,))
        shelltransientRateDensityList.append(shelltransientRateDensity)
        shellRedshiftList.append(shellMiddle)

        discoveryFraction, tooFaintFraction, shortCampaignFraction = calculate_fraction_of_sn_discovered(log, surveyCadenceSettings, snSurveyDiscoveryTimes, redshifts, peakAppMagList, snCampaignLengthList, extraSurveyConstraints, shellRedshiftBottom, shellRedshift)
        # if discoveryFraction != 0.:
        discoveryRedshiftList.append(shellMiddle)
        discoveryFractionList.append(discoveryFraction)
        # log.info('shell redshift %s, discoveryFraction %s' % (shellMiddle, discoveryFraction))
        # if tooFaintFraction != 0.:
        tooFaintRedshiftList.append(shellMiddle)
        tooFaintFractionList.append(tooFaintFraction)
        # if shortCampaignFraction != 0.:
        shortCampaignRedshiftList.append(shellMiddle)
        shortCampaignFractionList.append(shortCampaignFraction)

        transientShellRate = discoveryFraction*shelltransientRateDensity
        tooFaintShellRate = tooFaintFraction*shelltransientRateDensity
        shortCampaignShellRate = shortCampaignFraction*shelltransientRateDensity
        transientShellRateList.append(transientShellRate)
        tooFaintShellRateList.append(tooFaintShellRate)
        shortCampaignShellRateList.append(shortCampaignShellRate)

    discoveryRedshiftListArray = np.array(discoveryRedshiftList)
    discoveryFractionListArray = np.array(discoveryFractionList)
    tooFaintRedshiftListArray = np.array(tooFaintRedshiftList)
    tooFaintFractionListArray = np.array(tooFaintFractionList)
    shortCampaignRedshiftListArray = np.array(shortCampaignRedshiftList)
    shortCampaignFractionListArray = np.array(shortCampaignFractionList)
    polynomialDict = {}
    orginalDataDictionary = {}
    pleasePlot = False
    if len(discoveryRedshiftListArray) > 0:
        pleasePlot = True
        thisPoly = np.polyfit(discoveryRedshiftListArray, discoveryFractionListArray, 12)
        discoveryRateCurve = np.poly1d(thisPoly)
        # polynomialDict["Discovery Rate"] = discoveryRateCurve
        orginalDataDictionary["Discovery Rate"] = [discoveryRedshiftListArray, discoveryFractionListArray]
    else:
        discoveryRateCurve = False
    if len(tooFaintRedshiftListArray) > 0:
        pleasePlot = True
        thisPoly = np.polyfit(tooFaintRedshiftListArray, tooFaintFractionListArray, 12)
        tooFaintRateCurve = np.poly1d(thisPoly)
        #polynomialDict["Detected - too faint to constrain as transient"] = tooFaintRateCurve
        orginalDataDictionary["Detected - too faint to constrain as transient"] = [tooFaintRedshiftListArray, tooFaintFractionListArray]
    else:
        tooFaintRateCurve = False
    if len(shortCampaignRedshiftListArray) > 0:
        pleasePlot = True
        thisPoly = np.polyfit(shortCampaignRedshiftListArray, shortCampaignFractionListArray, 12)
        shortCampaignRateCurve = np.poly1d(thisPoly)
        #polynomialDict["Detected - campaign to short to constrain as transient"] = shortCampaignRateCurve
        orginalDataDictionary["Detected - campaign to short to constrain as transient"] = [shortCampaignRedshiftListArray, shortCampaignFractionListArray]
    else:
        shortCampaignRateCurve = False

    if pleasePlot:
        imageLink = dp.plot_polynomial(
                log,
                title='PS1-transient Survey - Precentage of transient Detected',
                polynomialDict=polynomialDict,
                orginalDataDictionary=orginalDataDictionary,
                pathToOutputPlotsFolder=pathToOutputPlotFolder,
                xRange=[0.01, 1., 0.01],
                xlabel=False,
                ylabel=False,
                xAxisLimits=False,
                yAxisLimits=[-0.05, 1.05],
                yAxisInvert=False,
                prependNum=False,
                legend=True)
    else:
        imageLink = ""

    shelltransientRateDensityArray = np.array(shelltransientRateDensityList)
    shellRedshiftArray = np.array(shellRedshiftList)
    # log.info('shellRedshiftArray %s' % (shellRedshiftArray,))
    # log.info('shelltransientRateDensityArray %s' % (shelltransientRateDensityArray,))
    thisPoly = np.polyfit(shellRedshiftArray, shelltransientRateDensityArray, 3)
    transientRateCurve = np.poly1d(thisPoly)
    # log.info('flat %s' % (flatPoly,))
    polynomialDict = { "transient Rate" : transientRateCurve }
    orginalDataDictionary = { "transient Rate" : [shellRedshiftArray, shelltransientRateDensityArray] }
    imageLink = dp.plot_polynomial(
            log,
            title='PS1 MDF transient Rate Density',
            polynomialDict=polynomialDict,
            orginalDataDictionary=orginalDataDictionary,
            pathToOutputPlotsFolder=pathToOutputPlotFolder,
            xRange=[0.01, 1., 0.01],
            xlabel=False,
            ylabel=False,
            xAxisLimits=False,
            yAxisLimits=False,
            yAxisInvert=False,
            prependNum=False)

    polynomialDict = {}
    orginalDataDictionary = {}
    pleasePlot = False
    if discoveryRateCurve:
        pleasePlot = True
        discoveredtransientCurve = transientRateCurve*discoveryRateCurve
        discoveredtransientCurve = np.poly1d(discoveredtransientCurve)
        #polynomialDict['Discovered transient Rate'] = discoveredtransientCurve
        orginalDataDictionary['Discovered transient Rate'] = [shellRedshiftArray, shelltransientRateDensityArray*discoveryFractionListArray]
    if tooFaintRateCurve:
        pleasePlot = True
        tooFainttransientCurve = transientRateCurve*tooFaintRateCurve
        tooFainttransientCurve = np.poly1d(tooFainttransientCurve)
        #polynomialDict["Detected - too faint to constrain as transient"] = tooFainttransientCurve
        orginalDataDictionary["Detected - too faint to constrain as transient"] = [shellRedshiftArray, shelltransientRateDensityArray*tooFaintFractionListArray]
    if shortCampaignRateCurve:
        pleasePlot = True
        shortCampaigntransientCurve = transientRateCurve*shortCampaignRateCurve
        shortCampaigntransientCurve = np.poly1d(shortCampaigntransientCurve)
        #polynomialDict["Detected - campaign to short to constrain as transient"] = shortCampaigntransientCurve
        orginalDataDictionary["Detected - campaign to short to constrain as transient"] = [shellRedshiftArray, shelltransientRateDensityArray*shortCampaignFractionListArray]

    if pleasePlot:
        imageLink = dp.plot_polynomial(
                log,
                title='PS1-transient Survey - Relative Detected Rates',
                polynomialDict=polynomialDict,
                orginalDataDictionary=orginalDataDictionary,
                pathToOutputPlotsFolder=pathToOutputPlotFolder,
                xRange=[0.01, 1., 0.01],
                xlabel=False,
                ylabel=False,
                xAxisLimits=False,
                yAxisLimits=[-0.05, 3.5],
                yAxisInvert=False,
                prependNum=False,
                legend=True)
    else:
        imageLink = ""

    totalRate = 0.
    for item in transientShellRateList:
        totalRate += item

    tooFaintRate = 0.
    for item in tooFaintShellRateList:
        tooFaintRate += item

    shortCampaignRate = 0.
    for item in shortCampaignShellRateList:
        shortCampaignRate += item

    totalRate = "%1.0f" % (totalRate,)
    tooFaintRate = "%1.0f" % (tooFaintRate,)
    shortCampaignRate = "%1.0f" % (shortCampaignRate,)
    return imageLink, totalRate, tooFaintRate, shortCampaignRate


## LAST MODIFIED : April 19, 2013
## CREATED : April 19, 2013
## AUTHOR : DRYX
def log_the_survey_settings(
        log,
        pathToYamlFile):
    """Create a MD log of the survey settings

    **Key Arguments:**
        - ``log`` -- logger
        - ``pathToYamlFile`` -- yaml results file

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import yaml
    ## LOCAL APPLICATION ##
    from datetime import datetime, date, time
    now = datetime.now()
    now = now.strftime("%Y%m%dt%H%M%S")

    ################ >ACTION(S) ################
    ## IMPORT THE SIMULATION SETTINGS
    fileName = pathToYamlFile
    stream = file(fileName, 'r')
    yamlContent = yaml.load(stream)
    snSurveyDiscoveryTimes = yamlContent['Discoveries Relative to Survey Year']
    lightCurveDiscoveryTimes = yamlContent['Discoveries Relative to Peak Magnitudes']
    snTypes = yamlContent['SN Types']
    redshifts = yamlContent['Redshifts']
    cadenceDictionary = yamlContent['Cadence Dictionary']
    peakAppMagList = yamlContent['Peak Apparent Magnitudes']
    snCampaignLengthList = yamlContent['Campaign Length']

    programSettings = yamlContent["Program Settings"]

    limitingMags = yamlContent["Limiting Magnitudes"]
    # for key in limitingMags:
        # log.debug('filter: %s, limit: %s' % (key, limitingMags[key]))

    sampleNumber = yamlContent["Simulation Sample"]

    peakMagnitudeDistributions = yamlContent["SN Absolute Peak-Magnitude Distributions"]
    #log.debug('snDistributions[magnitude] %s' % (snDistributions["magnitude"],))
    #log.debug('snDistributions[sigma] %s' % (snDistributions["sigma"],))

    relativeRatesSet = yamlContent["Relative Rate Set to Use"]
    relativeSNRates = yamlContent["Relative SN Rates"][relativeRatesSet]
    #log.debug('relativeSNRates %s' % (relativeSNRates,))
    lowerRedshiftLimit = yamlContent["Lower Redshift Limit"]
    upperRedshiftLimit = yamlContent["Upper Redshift Limit"]
    #log.debug('upperRedshiftLimit %s' % (upperRedshiftLimit,))
    redshiftResolution = yamlContent["Redshift Resolution"]

    extinctionSettings = yamlContent["Extinctions"]
    extinctionType = extinctionSettings["constant or random"]


    hostExtinctionDistributions = extinctionSettings["host"]
    #log.debug('hostExtinctionDistributions %s' % (hostExtinctionDistributions,))
    galacticExtinctionDistribution = extinctionSettings["galactic"]
    #log.debug('galacticExtinctionDistribution %s' % (galacticExtinctionDistribution,))

    surveyCadenceSettings = yamlContent["Survey Cadence"]
    #log.debug('surveyCadenceSettings %s' % (surveyCadenceSettings,))

    snLightCurves = yamlContent["Lightcurves"]
    #log.debug('snlightCurves %s' % (snlightCurves,))

    surveyArea = yamlContent["Sky Area of the Survey (square degrees)"]

    extraSurveyConstraints = yamlContent["Extra Survey Constraints"]

    weatherLossFraction = surveyCadenceSettings["Fraction of Year Lost to Weather etc"]
    observableFraction = surveyCadenceSettings["Observable Fraction of Year"]
    extinctionConstant = extinctionSettings["constant E(b-v)"]
    CCSNRateFraction = yamlContent["CCSN Progenitor Population Fraction of IMF"]
    transientToCCSNRateFraction = yamlContent["Transient to CCSN Ratio"]
    restFrameFilter = yamlContent["Rest Frame Filter for K-corrections"]
    peakMagLimit = extraSurveyConstraints["Faint-Limit of Peak Magnitude"]
    campaignLengthLimit = extraSurveyConstraints["Observable for at least ? number of days"]

    # log.info('yamlContent %s' % (yamlContent,))
    stream.close()

    settings_log = """
# SN Survey Simulation Results - %s

The *%s*-band liming magnitudes of this simulated survey are:

| Filter | Magnitude |
|:---|:----|
""" % (now, restFrameFilter)
    for k, v in limitingMags.iteritems():
        settings_log += """| %s | %s |\n""" % (k,v,)
    settings_log += """

A total of **%s** transients where simulated in the survey, within a **redshift-range of %s-%s**. A constant galactic extinction of `E(B-V) = %s` is used (the mean extinction of the 10 PS1 Medimum Deep Fields). The MDFs are visible for a fraction of %s of the survey year and the typical fraction of survey time lost to weather of %s is accounted for. Here are the relative rates and peak magnitude distributions of the SN used in the survey:

| SN Type | Relative Rate | Peak Magnitude | Sigma Peak |
|:---|:---|:---|:---|
""" % (sampleNumber, lowerRedshiftLimit, upperRedshiftLimit, extinctionConstant, observableFraction, weatherLossFraction,)
    for k, v in peakMagnitudeDistributions['magnitude'].iteritems():
        settings_log += """| %s | %s | %s | %s |\n""" % (k, relativeSNRates[k], v, peakMagnitudeDistributions['sigma'][k])
    settings_log += """

If a transient is detected by the simulated survey, extra constraints are placed upon the detected object to secure positive identification as the object.

1. The peak apparent magnitude of the object must be brighter than **%s mag**
2. The object must be detectable for long enough to complete a follow-up campaign of longer than **%s days** within 1 survey year with any single filter.

The transient rate for the survey volume is estimated by assuming a rate of **%s** times that of the CCSN rate (itself a fraction of **%s** of the total SFR).

""" % (peakMagLimit, campaignLengthLimit, transientToCCSNRateFraction, CCSNRateFraction)
    return settings_log


###################################################################
# PRIVATE (HELPER) FUNCTIONS                                      #
###################################################################
## LAST MODIFIED : April 19, 2013
## CREATED : April 19, 2013
## AUTHOR : DRYX
def calculate_fraction_of_sn_discovered(
        log,
        surveyCadenceSettings,
        snSurveyDiscoveryTimes,
        redshifts,
        peakAppMagList,
        snCampaignLengthList,
        extraSurveyConstraints,
        zmin,
        zmax):
    """Given a list of the snSurveyDiscoveryTimes calculate the discovery/non-discovery ratio for a given redshift range

    **Key Arguments:**
        - ``log`` -- logger
        - ``surveyCadenceSettings`` -- the cadence settings for the survey
        - ``snSurveyDiscoveryTimes`` -- the discovery times of the SN relative to the survey year
        - ``redshifts`` -- redshifts of the sne
        - ``peakAppMagList`` -- list of the SN peak magnitude in each filter
        - ``snCampaignLengthList`` -- a list of campaign lengths in each filter
        - ``extraSurveyConstraints`` -- some extra survey constraints
        - ``zmin`` -- minimum redshift in the range
        - ``zmax`` -- maximum redshift in the range

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    ## LOCAL APPLICATION ##

    ################ >ACTION(S) ################
    filters = ['g', 'r', 'i', 'z']
    faintMagLimit = extraSurveyConstraints['Faint-Limit of Peak Magnitude']
    lunarMonth = 29.3
    surveyYear = 12.*lunarMonth
    observableFraction = surveyCadenceSettings["Observable Fraction of Year"]

    discovered = []
    tooFaint = []
    shortCampaign = []
    discoveredRedshift = []
    tooFaintRedshift = []
    notDiscoveredRedshift = []
    shortCampaignRedshift = []
    #log.info('len(redshifts) %s' % (len(redshifts),))
    dataDictionary = {}
    for item in range(len(redshifts)):
        if redshifts[item] > zmax or redshifts[item] <= zmin:
            continue
        if snSurveyDiscoveryTimes[item]['any'] is True:
            discoveryDayList = []
            faintDayList = []
            shortCampaignDayList = []
            for ffilter in filters:
                if snSurveyDiscoveryTimes[item][ffilter]:
                    if peakAppMagList[item][ffilter] < faintMagLimit:
                        if (snCampaignLengthList[item]['max'] < extraSurveyConstraints['Observable for at least ? number of days']):
                            shortCampaignDayList.append(snSurveyDiscoveryTimes[item][ffilter])
                        else:
                            if (surveyYear*observableFraction - snSurveyDiscoveryTimes[item][ffilter]) > extraSurveyConstraints['Observable for at least ? number of days']:
                                discoveryDayList.append(snSurveyDiscoveryTimes[item][ffilter])
                            # elif ((surveyYear*observableFraction - snSurveyDiscoveryTimes[item][ffilter]) < snSurveyDiscoveryTimes[item][ffilter] <  surveyYear*observableFraction):
                            elif (snCampaignLengthList[item][ffilter] - (surveyYear - snSurveyDiscoveryTimes[item][ffilter])) > extraSurveyConstraints['Observable for at least ? number of days']:
                                lcTail = snCampaignLengthList[item][ffilter] - (surveyYear - snSurveyDiscoveryTimes[item][ffilter])
                                discoveryDayList.append(snSurveyDiscoveryTimes[item][ffilter])
                            else:
                                shortCampaignDayList.append(snSurveyDiscoveryTimes[item][ffilter])
                                # log.info('item: %s. ffilter %s. too short due to going behind sun, discovery day %s, camp length %s' % (item, ffilter, snSurveyDiscoveryTimes[item][ffilter], snCampaignLengthList[item][ffilter]))
                    else:
                        faintDayList.append(snSurveyDiscoveryTimes[item][ffilter])

            if len(discoveryDayList) > 0:
                discovered.append(min(discoveryDayList))
                discoveredRedshift.append(redshifts[item])
            elif len(shortCampaignDayList) > 0:
                shortCampaign.append(min(shortCampaignDayList))
                shortCampaignRedshift.append(redshifts[item])
            else:
                tooFaint.append(min(faintDayList))
                tooFaintRedshift.append(redshifts[item])
        else:
            notDiscoveredRedshift.append(redshifts[item])

    if len(notDiscoveredRedshift) > 0:
        dataDictionary["Undiscovered"] = notDiscoveredRedshift
    if len(tooFaintRedshift) > 0:
        dataDictionary["Detected - too faint to constrain as transient"] = tooFaintRedshift
    if len(discoveredRedshift) > 0:
        dataDictionary["Discovered"] = discoveredRedshift
    if len(shortCampaignRedshift) > 0:
        dataDictionary["Detected - campaign to short to constrain as transient"] = shortCampaignRedshift

    totalWithinVolume = float(len(discoveredRedshift)+len(notDiscoveredRedshift)+len(tooFaintRedshift)+len(shortCampaignRedshift))

    if len(discoveredRedshift) == 0:
        discoveryFraction = 0.
    else:
        discoveryFraction = float(len(discoveredRedshift))/totalWithinVolume
    if len(tooFaintRedshift) == 0:
        tooFaintFraction = 0.
    else:
        tooFaintFraction = float(len(tooFaintRedshift))/totalWithinVolume
    if len(shortCampaignRedshift) == 0:
        shortCampaignFraction = 0.
    else:
        shortCampaignFraction = float(len(shortCampaignRedshift))/totalWithinVolume
    # log.info('len(discoveredRedshift) %s' % (len(discoveredRedshift),))
    # log.info('len(notDiscoveredRedshift) %s' % (len(notDiscoveredRedshift),))
    # log.info('discoveryFraction %s' % (discoveryFraction,))

    return discoveryFraction, tooFaintFraction, shortCampaignFraction

if __name__ == '__main__':
    main()


###################################################################
# TEMPLATE FUNCTIONS                                              #
###################################################################
