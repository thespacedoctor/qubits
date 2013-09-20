#!/usr/bin/python
# encoding: utf-8
"""
surveysim
=================================
:Summary:
    A partial of the ``qubits`` module.
    The functions in this partial are used to setup the simulated observable universe.

:Author:
    David Young

:Date Created:
    April 12, 2013

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
## LAST MODIFIED : April 12, 2013
## CREATED : April 12, 2013
## AUTHOR : DRYX
def survey_cadence_arrays(
        log,
        surveyCadenceSettings,
        pathToOutputDirectory,
        pathToOutputPlotDirectory,
        plot=False):
    """Generate the survey cadence arrays for each filter

    **Key Arguments:**
        - ``log`` -- logger
        - ``surveyCadenceSettings`` -- the survey cadence parameters as set in the simulation settings file
        - ``pathToOutputDirectory`` -- path to the output directory (provided by the user)
        - ``pathToOutputPlotDirectory`` -- path to add plots to
        - ``plot`` -- generate plot?

    **Return:**
        - ``cadenceDictionary`` -- a dictionary of { band : observedDayList }
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    ## LOCAL APPLICATION ##
    import numpy as np
    import matplotlib.pyplot as plt

    ################ > VARIABLE SETTINGS ######
    lunarMonth = 29.3
    surveyYear = 12.*lunarMonth
    ################ >ACTION(S) ################
    cadenceDictionary = {}
    obsFraction = surveyCadenceSettings['Observable Fraction of Year']
    lossFraction = surveyCadenceSettings['Fraction of Year Lost to Weather etc']
    for thisFilter in surveyCadenceSettings['Filters']:
        # READ THE CADENCE PARAMETERS
        band = thisFilter['band']
        firstDay = thisFilter['day of year of first scheduled observation']
        repeatEvery = thisFilter['repeat every ? days']
        moonFraction = thisFilter['Fraction of Lunar Month Lost to Moon']

        # DETERMINE DAYS LOST DUE TO MOON CYCLE
        finalObsDayOfMonth = lunarMonth*(1.-moonFraction)
        monthCount = 0
        day = 1
        monthDay = 1
        moonDayList = []
        while day < surveyYear:
            while monthDay < int(lunarMonth):
                if monthDay <= finalObsDayOfMonth:
                    moonDayList.append(day)
                monthDay += 1
                day += 1
            monthCount += 1
            day = int(lunarMonth*monthCount)
            #log.debug('month # %s starts on day %s' % (monthCount, day))
            monthDay = 0

        # DETERMINE THE DAYS THE TELESCOPE OBSERVES IN THIS FILTER
        day = firstDay
        nextObs = firstDay
        obsDaysList = []
        finalObsDayOfYear = obsFraction*surveyYear
        while day <= finalObsDayOfYear:
            randNum = np.random.rand()
            if day == nextObs:
                if day in moonDayList and randNum > lossFraction:
                    obsDaysList.append(day)
                nextObs = day + repeatEvery
            day += 1
            #log.debug('day # %s' % (day,))

        # ADD THE BAND & OBS ARRAY TO THE DICTIONARY
        cadenceDictionary[band] = obsDaysList

    if plot:
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
                norm=None,
                vmin=None,
                vmax=None,
                alpha=0.5,
                linewidths=None,
                edgecolor='w',
                verts=None,
                hold=True)

        circleTicks = np.arange(0, 350, 30)
        tickLabels = []
        for tick in circleTicks:
            tickLabels.append("%s days" % (tick,))

        plt.xticks(2*np.pi*circleTicks/surveyYear, tickLabels)
        plt.yticks([])

        title = "Cadence Wheel for Simulated Survey"
        plt.title(title)
        fileName = pathToOutputPlotDirectory + title.replace(" ", "_") + ".png"
        plt.savefig(fileName)
        plt.clf()  # clear figure

    return cadenceDictionary


## LAST MODIFIED : April 17, 2013
## CREATED : April 17, 2013
## AUTHOR : DRYX
def determine_if_sne_are_discoverable(
        log,
        redshiftArray,
        limitingMags,
        observedFrameLightCurveInfo,
        pathToOutputDirectory,
        pathToOutputPlotDirectory,
        plot=True):
    """Given the observe frame lightcurve, determine if the SNe are discoverable by the survey or not.

    **Key Arguments:**
        - ``log`` -- logger
        - ``redshiftArray`` -- the array of random redshifts
        - ``observedFrameLightCurveInfo`` -- the observed franme lightcurve info (dictionary)
        - ``pathToOutputDirectory`` -- path to the output directory (provided by the user)
        - ``pathToOutputPlotDirectory`` -- path to add plots to
        - ``plot`` -- generate plots?

    **Return:**
        - ``discoverableList`` -- a list of dictionaries describing if the object is discoverable in each filter and finally if it is discoverable in any filter.
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import numpy as np
    import matplotlib.pyplot as plt
    ## LOCAL APPLICATION ##
    import dryxPython.plotting as dp

    ################ >ACTION(S) ################
    filters = ['g', 'r', 'i', 'z']
    models = ['he80', 'he100', 'he130']

    discoverableList = []
    for i in range(len(observedFrameLightCurveInfo)):
        discoveryDict = {}
        for ffilter in filters:
            if observedFrameLightCurveInfo[i]['peakMags'][ffilter] > limitingMags[ffilter]:
                discoveryDict[ffilter] = False
            else:
                discoveryDict[ffilter] = True
        discoveryDict['any'] = False
        for k, v in discoveryDict.iteritems():
            if v is True:
                discoveryDict['any'] = True
                break

        discoverableList.append(discoveryDict)

    if plot:
        hitList = []
        missList = []
        faintList = []
        for i in range(len(discoverableList)):
            discoveryDict = discoverableList[i]
            if discoveryDict['any'] is True:
                hitList.append(redshiftArray[i])
            else:
                missList.append(redshiftArray[i])

        hitArray = np.array(hitList)
        missArray = np.array(missList)
        faintArray = np.array(faintList)

        dataDictionary =  { 'Discoverable' : hitArray, 'Undiscoverable' : missArray }
        dp.plot_polar(
            log,
            title="Discoverable SN Redshift Distribution",
            dataDictionary=dataDictionary,
            pathToOutputPlotsFolder=pathToOutputPlotDirectory,
            dataRange=False,
            ylabel=False,
            radius=1.1,
            circumference=False,
            prependNum=False)

    return discoverableList


## LAST MODIFIED : April 18, 2013
## CREATED : April 18, 2013
## AUTHOR : DRYX
def determine_when_sne_are_ripe_for_discovery(
        log,
        redshiftArray,
        limitingMags,
        observedFrameLightCurveInfo,
        discoverableList,
        plot=True):

    """Given the observe frame lightcurve, determine if the SNe are discoverable by the survey or not.

    **Key Arguments:**
        - ``log`` -- logger
        - ``redshiftArray`` -- the array of random redshifts
        - ``observedFrameLightCurveInfo`` -- the observed franme lightcurve info (dictionary)
        - ``discoverableList`` -- a list of dictionaries describing if the object is discoverable in each filter and finally if it is discoverable in any filter.
        - ``plot`` -- generate plots?

    **Return:**
        - ``ripeDayList`` -- a list of dictionaries describing the time relative to peak that the SN reaches the limiting mag of the survey
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    import math
    ## THIRD PARTY ##
    ## LOCAL APPLICATION ##

    ################ >ACTION(S) ################
    filters = ['g', 'r', 'i', 'z']
    models = ['he80', 'he100', 'he130']

    ripeDayList = []
    for item in range(len(redshiftArray)):
        #log.info("I AM HERE %s" % (item,))
        ripeDayDict = {}
        if not discoverableList[item]["any"]:
            ripeDayDict["any"] = False
            for ffilter in filters:
                ripeDayDict[ffilter] = False
        else:
            for ffilter in filters:
                if not discoverableList[item][ffilter]:
                    ripeDayDict[ffilter] = False
                else:
                    explosionDay = observedFrameLightCurveInfo[item]['explosionDay']
                    lowerLimit = explosionDay
                    upperLimit = 0.
                    ripeDay = lowerLimit
                    magGuess = observedFrameLightCurveInfo[item]['lightCurves'][ffilter](ripeDay)
                    magDiff = limitingMags[ffilter] - magGuess

                    if magGuess > limitingMags[ffilter]:
                        while math.fabs(magDiff) > 0.01:
                            if magGuess > limitingMags[ffilter]:
                                #log.info('item %s ripeDay %s magGuess %s - going higher' % (item, ripeDay, magGuess))
                                lowerLimit = ripeDay
                                ripeDay = lowerLimit + (upperLimit - lowerLimit)/2.
                                magGuess = observedFrameLightCurveInfo[item]['lightCurves'][ffilter](ripeDay)
                            elif magGuess < limitingMags[ffilter]:
                                #log.info('item %s ripeDay %s' % (item, ripeDay))
                                upperLimit = ripeDay
                                ripeDay = lowerLimit + (upperLimit - lowerLimit)/2.
                                magGuess = observedFrameLightCurveInfo[item]['lightCurves'][ffilter](ripeDay)
                            magDiff = limitingMags[ffilter] - magGuess

                    ripeDay = float("%5.3f" % (ripeDay,))
                    #log.info('SN#%s, filter %s, ripeDay %s' % (item, ffilter, ripeDay,))
                    ripeDayDict[ffilter] = ripeDay
            ripeDayDict["any"] = False
            for ffilter in filters:
                if ripeDayDict[ffilter]:
                    ripeDayDict["any"] = True
        ripeDayList.append(ripeDayDict)

    # log.info('ripeDayList %s' % (ripeDayList,))

    return ripeDayList


## LAST MODIFIED : April 18, 2013
## CREATED : April 18, 2013
## AUTHOR : DRYX
def determine_when_discovered_sne_disappear(
        log,
        redshiftArray,
        limitingMags,
        observedFrameLightCurveInfo,
        ripeDayList,
        plot=True):

    """Given the observed frame lightcurve, determine when the discovered SNe become too faint to be detected.

    **Key Arguments:**
        - ``log`` -- logger
        - ``redshiftArray`` -- the array of random redshifts
        - ``observedFrameLightCurveInfo`` -- the observed franme lightcurve info (dictionary)
        - ``ripeDayList`` -- a list of dictionaries describing if the object is discoverable in each filter and finally if it is discoverable in any filter.
        - ``plot`` -- generate plots?

    **Return:**
        - ``disappearDayList`` -- a list of dictionaries describing the time relative to peak that the SN reaches the limiting mag of the survey
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    import math
    ## THIRD PARTY ##
    ## LOCAL APPLICATION ##

    ################ >ACTION(S) ################
    filters = ['g', 'r', 'i', 'z']
    models = ['he80', 'he100', 'he130']

    disappearDayList = []
    for item in range(len(redshiftArray)):
        #log.info("I AM HERE %s" % (item,))
        disappearDayDict = {}
        if not ripeDayList[item]["any"]:
            disappearDayDict["any"] = False
            for ffilter in filters:
                disappearDayDict[ffilter] = False
        else:
            for ffilter in filters:
                if not ripeDayList[item][ffilter]:
                    disappearDayDict[ffilter] = False
                else:
                    lightCurveEndDay = observedFrameLightCurveInfo[item]['endOfLightcurveDay']
                    lowerLimit = 0.
                    upperLimit = lightCurveEndDay
                    disappearDay = upperLimit
                    magGuess = observedFrameLightCurveInfo[item]['lightCurves'][ffilter](disappearDay)
                    magDiff = limitingMags[ffilter] - magGuess
                    log.info('item %s disappearDay %s magGuess %s - going higher' % (item, disappearDay, magGuess))

                    if magGuess > limitingMags[ffilter]:
                        while math.fabs(magDiff) > 0.01:
                            if magGuess > limitingMags[ffilter]:
                                log.info('item %s disappearDay %s magGuess %s - going higher' % (item, disappearDay, magGuess))
                                upperLimit = disappearDay
                                disappearDay = lowerLimit + (upperLimit - lowerLimit)/2.
                                magGuess = observedFrameLightCurveInfo[item]['lightCurves'][ffilter](disappearDay)
                            elif magGuess < limitingMags[ffilter]:
                                log.info('item %s disappearDay %s' % (item, disappearDay))
                                lowerLimit = disappearDay
                                disappearDay = lowerLimit + (upperLimit - lowerLimit)/2.
                                magGuess = observedFrameLightCurveInfo[item]['lightCurves'][ffilter](disappearDay)
                            magDiff = limitingMags[ffilter] - magGuess
                    else:
                        disappearDay = "N.E.D."
                        log.warning("""not enough data to determine when the SN disappears fainter than the survey's limiting mag""")

                    if type(disappearDay) != str:
                        disappearDay = float("%5.3f" % (disappearDay,))
                    #log.info('SN#%s, filter %s, disappearDay %s' % (item, ffilter, disappearDay,))
                    disappearDayDict[ffilter] = disappearDay
            disappearDayDict["any"] = False
            for ffilter in filters:
                if disappearDayDict[ffilter] and disappearDayDict[ffilter] != "N.E.D.":
                    disappearDayDict["any"] = True
        disappearDayList.append(disappearDayDict)

    log.info('disappearDayList %s' % (disappearDayList,))

    return disappearDayList


## LAST MODIFIED : April 18, 2013
## CREATED : April 18, 2013
## AUTHOR : DRYX
def determine_if_sne_are_discovered(
        log,
        limitingMags,
        ripeDayList,
        cadenceDictionary,
        observedFrameLightCurveInfo,
        extraSurveyConstraints,
        plot=True):
    """Generate a list of dictionaries which describe if and when a SN is discovered in each and any filter.

    **Key Arguments:**
        - ``log`` -- logger
        - ``limitingMags`` -- the limiting magnitudes of the survey
        - ``ripeDayList`` -- a list of dictionaries describing the time relative to peak that the SN reaches the limiting mag of the survey
        - ``cadenceDictionary``  -- a dictionary of { band : observedDayList }
        - ``observedFrameLightCurveInfo`` -- the observed franme lightcurve info (dictionary)
        - ``extraConstraints`` -- some extra constraints
        - ``plot`` -- generate plots?

    **Return:**
        - ``discoveredList`` -- a list of dictionaries which describe if and when a SN is discovered in each and any filter.
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import numpy as np
    ## LOCAL APPLICATION ##

    ################ >ACTION(S) ################
    filters = ['g', 'r', 'i', 'z']
    models = ['he80', 'he100', 'he130']
    lunarMonth = 29.3
    surveyYear = 12.*lunarMonth


    surveyDiscoveryDayList = []
    lightCurveDiscoveryDayList = []
    snCampaignLengthList = []
    log.info('ripeDayList %s' % (len(ripeDayList),))
    for item in range(len(ripeDayList)):
        lightCurveEndDay = observedFrameLightCurveInfo[item]['endOfLightcurveDay']
        visibleDay = np.random.rand()*surveyYear
        surveyDiscoveryDayDict = {}
        lightCurveDiscoverDayDict = {}
        snCampaignLengthDict = {}
        if not ripeDayList[item]["any"]:
            surveyDiscoveryDayDict["any"] = False
            lightCurveDiscoverDayDict["any"] = False
            snCampaignLengthDict["any"] = False
            for ffilter in filters:
                lightCurveDiscoverDayDict[ffilter] = False
                surveyDiscoveryDayDict[ffilter] = False
                snCampaignLengthDict[ffilter] = False
            # log.info('NOTHING SEEN IN ANY FILTER FOR ITEM %s' % (item,))
            lightCurveDiscoveryDayList.append(lightCurveDiscoverDayDict)
            surveyDiscoveryDayList.append(surveyDiscoveryDayDict)
            snCampaignLengthList.append(snCampaignLengthDict)
        else:
            for ffilter in filters:
                if not ripeDayList[item][ffilter]:
                    surveyDiscoveryDayDict[ffilter] = False
                    lightCurveDiscoverDayDict[ffilter] = False
                    snCampaignLengthDict[ffilter] = False
                    # log.info('item %s, filter %s, NOT DISCOVERED' % (item, ffilter))
                else:
                    if visibleDay > max(cadenceDictionary[ffilter]):
                        waitingTime = surveyYear + min(cadenceDictionary[ffilter]) - visibleDay
                        surveyDiscoveryDayDict[ffilter] = min(cadenceDictionary[ffilter])
                        cdIndex = 0
                    else:
                        cdIndex = -1
                        for day in cadenceDictionary[ffilter]:
                            cdIndex += 1
                            if day > visibleDay:
                                waitingTime = day - visibleDay
                                surveyDiscoveryDayDict[ffilter] = day
                                break

                    lightCurveDiscoverDayDict[ffilter] = ripeDayList[item][ffilter] + waitingTime
                    if observedFrameLightCurveInfo[item]['lightCurves'][ffilter](lightCurveDiscoverDayDict[ffilter]) > limitingMags[ffilter]:
                        lightCurveDiscoverDayDict[ffilter] = False
                        surveyDiscoveryDayDict[ffilter] = False
                        snCampaignLengthDict[ffilter] = False
                    else:
                        snCampaignLengthDict[ffilter] = 0
                        lcDay = lightCurveDiscoverDayDict[ffilter]
                        cdIndex += 1
                        while 1 > 0:
                            if cdIndex >= len(cadenceDictionary[ffilter]):
                                log.info('item: %s. NEXT YEAR: cdIndex %s, len(cadenceDictionary[ffilter]) %s' % (item, cdIndex, len(cadenceDictionary[ffilter])))
                                nextLcDay = lcDay + surveyYear + min(cadenceDictionary[ffilter]) - max(cadenceDictionary[ffilter])
                                cdIndex = 1
                            else:
                                log.info('item: %s. SAME YEAR: cdIndex %s, len(cadenceDictionary[ffilter]) %s' % (item, cdIndex, len(cadenceDictionary[ffilter])))
                                nextLcDay = lcDay + cadenceDictionary[ffilter][cdIndex] - cadenceDictionary[ffilter][cdIndex-1]
                                cdIndex += 1
                            if observedFrameLightCurveInfo[item]['lightCurves'][ffilter](nextLcDay) < limitingMags[ffilter] and (lightCurveEndDay > nextLcDay):
                                snCampaignLengthDict[ffilter] += nextLcDay - lcDay
                                log.info('campaign length %s, filter %s' % (snCampaignLengthDict[ffilter], ffilter))
                                lcDay = nextLcDay
                            else:
                                break

            surveyDiscoveryDayDict['any'] = False
            lightCurveDiscoverDayDict['any'] = False
            snCampaignLengthDict['max'] = 0
            for ffilter in filters:
                if surveyDiscoveryDayDict[ffilter]:
                    surveyDiscoveryDayDict['any'] = True
                    lightCurveDiscoverDayDict['any'] = True
                if snCampaignLengthDict[ffilter] > snCampaignLengthDict['max']:
                    snCampaignLengthDict['max'] = snCampaignLengthDict[ffilter]
            lightCurveDiscoveryDayList.append(lightCurveDiscoverDayDict)
            surveyDiscoveryDayList.append(surveyDiscoveryDayDict)
            snCampaignLengthList.append(snCampaignLengthDict)

    # log.info('surveyDiscoveryDayList %s' % (len(surveyDiscoveryDayList),))
    # log.info('lightCurveDiscoveryDayList %s' % (len(lightCurveDiscoveryDayList),))
    # log.info('snCampaignLengthList %s' % (len(snCampaignLengthList),))

    return lightCurveDiscoveryDayList, surveyDiscoveryDayList, snCampaignLengthList

###################################################################
# PRIVATE (HELPER) FUNCTIONS                                      #
###################################################################

if __name__ == '__main__':
    main()


###################################################################
# TEMPLATE FUNCTIONS                                              #
###################################################################
