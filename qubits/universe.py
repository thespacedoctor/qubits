#!/usr/bin/python
# encoding: utf-8
"""
universe
=================================
:Summary:
    A partial of the ``SN_Survey_Simulator`` module.
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

###################################################################
# CLASSES                                                         #
###################################################################

###################################################################
# PUBLIC FUNCTIONS                                                #
###################################################################
## LAST MODIFIED : April 12, 2013
## CREATED : April 12, 2013
## AUTHOR : DRYX
def random_redshift_array(
        log,
        sampleNumber,
        lowerRedshiftLimit,
        upperRedshiftLimit,
        redshiftResolution,
        pathToOutputPlotDirectory,
        plot=False):
    """Generate a NumPy array of random distances given a sample number and distance limit

    **Key Arguments:**
        - ``log`` -- logger
        - ``sampleNumber`` -- the sample number, i.e. array size
        - ``lowerRedshiftLimit`` -- the lower redshift limit of the volume to be included
        - ``upperRedshiftLimit`` -- the upper redshift limit of the volume to be included
        - ``redshiftResolution`` -- the resolution of the redshift distribution
        - ``pathToOutputPlotDirectory`` -- path to the output directory (provided by the user)
        - ``plot`` -- generate plot?

    **Return:**
        - ``redshiftArray`` -- an array of random redshifts within the volume limit
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import matplotlib.pyplot as plt
    import numpy as np
    import numpy.random as npr
    ## LOCAL APPLICATION ##
    import dryxPython.astrotools as da

    redshiftDistribution = np.arange(0., upperRedshiftLimit, redshiftResolution)
    closestNumber=lambda n,l:min(l,key=lambda x:abs(x-n))

    # GIVEN THE REDSHIFT LIMIT - DETERMINE THE VOLUME LIMIT
    distanceDictionary = da.convert_redshift_to_distance(upperRedshiftLimit)
    upperMpcLimit = distanceDictionary["dl_mpc"]
    upperVolumeLimit = (4./3.)*np.pi*upperMpcLimit**3

    if lowerRedshiftLimit == 0.:
        lowerVolumeLimit = 0.
    else:
        distanceDictionary = da.convert_redshift_to_distance(lowerRedshiftLimit)
        lowerMpcLimit = distanceDictionary["dl_mpc"]
        lowerVolumeLimit = (4./3.)*np.pi*lowerMpcLimit**3

    volumeShell = upperVolumeLimit-lowerVolumeLimit

    # GENERATE A LIST OF RANDOM DISTANCES
    redshiftList = []
    for i in range(sampleNumber):
        randomVolume = lowerVolumeLimit+npr.random()*volumeShell
        randomDistance = (randomVolume*(3./4.)/np.pi)**(1./3.)
        randomRedshift = da.convert_mpc_to_redshift(randomDistance)
        randomRedshift = closestNumber(randomRedshift,redshiftDistribution)
        # log.debug('randomDistance %s' % (randomDistance,))
        redshiftList.append(randomRedshift)

    redshiftArray = np.array(redshiftList)
    # log.info('redshiftArray %s' % (redshiftArray,))

    if plot:
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
            polar=True)

        thetaList = []
        twoPi = 2.*np.pi
        for i in range(sampleNumber):
            thetaList.append(twoPi*npr.random())
        thetaArray = np.array(thetaList)

        plt.scatter(
            thetaArray,
            redshiftArray,
            s=10,
            c='b',
            marker='o',
            cmap=None,
            norm=None,
            vmin=None,
            vmax=None,
            alpha=None,
            linewidths=None,
            edgecolor='w',
            verts=None,
            hold=None)

        title = "SN Redshift Distribution"
        plt.title(title)
        fileName = pathToOutputPlotDirectory + title.replace(" ", "_") + ".png"
        plt.savefig(fileName)
        plt.clf()  # clear figure

    return redshiftArray


## LAST MODIFIED : April 12, 2013
## CREATED : April 12, 2013
## AUTHOR : DRYX
def random_sn_types_array(
        log,
        sampleNumber,
        relativeSNRates,
        pathToOutputPlotDirectory,
        plot=False):
    """Generate random supernova types from the weighted distributions set in the simulation settings file

    **Key Arguments:**
        - ``log`` -- logger
        - ``sampleNumber`` -- the sample number, i.e. array size
        - ``relativeSNRates`` -- dictionary of the rates
        - ``pathToOutputPlotDirectory`` -- path to the output directory (provided by the user)
        - ``plot`` -- generate plot?

    **Return:**
        - ``snTypesArray`` -- numpy array of the random SN types
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    ## LOCAL APPLICATION ##
    import numpy as np
    import matplotlib.pyplot as plt

    ################ > VARIABLE SETTINGS ######

    ################ >ACTION(S) ################
    randomSNTypeList = []
    # CREATE COUNTERS FOR PLOTTING
    counters = {}
    for k, v in relativeSNRates.iteritems():
        counters[k] = 0

    for i in range(sampleNumber):
        randNum = np.random.rand()
        cumulative = 0.
        for k, v in relativeSNRates.iteritems():
            cumulative = cumulative + v
            if (randNum <= cumulative):
                randType = k
                counters[k] += 1
                break
        randomSNTypeList.append(randType)

    # for k, v in relativeSNRates.iteritems():
    #     log.debug('%s = %s' % (k, counters[k]))

    snTypeArray = np.array(randomSNTypeList)

    if plot:
        numTypes = len(relativeSNRates)
        x = np.arange(1, numTypes+1, 1)

        heights = []
        xticks = []
        for k, v in relativeSNRates.iteritems():
            xticks.append(k)
            heights.append(counters[k])

        fig = plt.figure(
            num=None,
            figsize=(8,8),
            dpi=None,
            facecolor=None,
            edgecolor=None,
            frameon=True)

        ax = fig.add_axes(
            [0.1, 0.1, 0.8, 0.8])

        ax.bar(
            x,
            heights,
            width=0.8,
            bottom=0)

        plt.xticks( x + 0.5,  xticks )

        ax.set_xlabel('SN Type')
        ax.set_ylabel('Number of SNe')
        ax.grid(True)

        title = "Weighted SN Distribution"
        plt.title(title)
        fileName = pathToOutputPlotDirectory + title.replace(" ", "_") + ".png"
        plt.savefig(fileName)
        plt.clf()  # clear figure

    return snTypeArray


## LAST MODIFIED : April 12, 2013
## CREATED : April 12, 2013
## AUTHOR : DRYX
def random_host_extinction(
        log,
        sampleNumber,
        extinctionType,
        extinctionConstant,
        hostExtinctionDistributions,
        plot=False):
    """Generate a Numpy array of random host extinctions

    **Key Arguments:**
        - ``log`` -- logger
        - ``sampleNumber`` -- the sample number, i.e. array size
        - ``extinctionType`` -- constant or random?
        - ``extinctionConstant`` -- the constant value (when extinctionType is constant)
        - ``hostExtinctionDistributions`` -- the host extinction distribution (when extinctionType is random)
        - ``plot`` -- generate plot?

    **Return:**
        - ``hostExtinctionArray``
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import numpy as np
    ## LOCAL APPLICATION ##

    ################ > VARIABLE SETTINGS #######

    ################ >ACTION(S) ################
    ## xxx come back here and add in the random extinctions generation -- will need to account for what type of SN we have ##
    if extinctionType == "constant":
        hostExtinctionArray = np.zeros(sampleNumber)*extinctionConstant
    else:
        log.error('host extiction distributions not included yet')

    return hostExtinctionArray


## LAST MODIFIED : April 12, 2013
## CREATED : April 12, 2013
## AUTHOR : DRYX
def random_galactic_extinction(
        log,
        sampleNumber,
        extinctionType,
        extinctionConstant,
        galacticExtinctionDistributions,
        plot=False):
    """Generate a Numpy array of random galactic extinctions

    **Key Arguments:**
        - ``log`` -- logger
        - ``sampleNumber`` -- the sample number, i.e. array size
        - ``extinctionType`` -- constant or random?
        - ``extinctionConstant`` -- the constant value (when extinctionType is constant)
        - ``galacticExtinctionDistributions`` -- the galactic extinction distribution (when extinctionType is random)
        - ``plot`` -- generate plot?

    **Return:**
        - ``galacticExtinctionArray``
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import numpy as np
    ## LOCAL APPLICATION ##

    ################ > VARIABLE SETTINGS #######

    ################ >ACTION(S) ################
    ## xxx come back here and add in the random extinctions generation -- will need to account for what type of SN we have ##
    if extinctionType == "constant":
        galacticExtinctionArray = np.ones(sampleNumber)*extinctionConstant
    else:
        log.error('galactic extiction distributions not included yet')

    # log.debug('galacticExtinctionArray %s' % (galacticExtinctionArray,))

    return galacticExtinctionArray


## LAST MODIFIED : April 14, 2013
## CREATED : April 14, 2013
## AUTHOR : DRYX
def generate_numpy_polynomial_lightcurves(
        log,
        snLightCurves,
        pathToOutputDirectory,
        pathToOutputPlotDirectory,
        plot=False):
    """Given a the yaml input of the SN Lightcurves generate a numpy polynomial of the curves.

    **Key Arguments:**
        - ``log`` -- logger
        - ``snLightCurves`` -- some info on sn LightCurves
        - ``pathToOutputDirectory`` -- path to the output directory (provided by the user)
        - ``pathToOutputPlotDirectory`` -- path to the output plots directory
        - ``plot`` -- generate plot?

    **Return:**
        - ``polynomialDict`` -- { snType, polynomialLightcurve }
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import numpy as np
    import matplotlib.pyplot as plt
    import yaml
    ## LOCAL APPLICATION ##
    import dryxPython.plotting as dp

    ################ >ACTION(S) ################
    ## EXTRACT THE MODEL LIGHTCURVE POLYNOMIALS
    fileName = pathToOutputDirectory + "transient_light_curves.yaml"
    stream = file(fileName, 'r')
    yamlContent = yaml.load(stream)
    generatedLCs = yamlContent
    stream.close()

    log.critical('fileName: %s' % (fileName,))
    log.debug('generatedLCs: %s' % (generatedLCs,))

    rawLightCurveDict = {}
    for model, filterData in generatedLCs.iteritems():
        thisModel = model
        rawLightCurveDict[thisModel] = {}
        for ffilter, modelData in filterData.iteritems():
            rawLightCurveDict[thisModel][ffilter] = {}
            plotDict = {}

            if modelData["poly"] is None:
                log.error('cound not plot the raw lightcurve for the %s object in rest frame %s-band' % (modelData,ffilter))
                rawLightCurveDict[thisModel][ffilter]['poly'] = None
                rawLightCurveDict[thisModel][ffilter]['Explosion Day Relative to Peak'] = None
                rawLightCurveDict[thisModel][ffilter]['End of lightcurve relative to peak'] = None
                continue

            # explosionDay = snLightCurves[model]['Explosion Day Relative to Peak']
            endOfLightcurveDay = snLightCurves[model]['End of lightcurve relative to peak']
            explosionDay = modelData['Explosion Day Relative to Peak']
            log.warning('explosionDay, endOfLightcurveDay for raw Light Curve: %s, %s' % (explosionDay,endOfLightcurveDay))
            # endOfLightcurveDay = snLightCurves[model]['End of lightcurve relative to peak']
            # log.info('endOfLightcurveDay %s' % (endOfLightcurveDay,))
            # log.info('explosionDay %s' % (explosionDay,))
            poly = modelData['poly']
            peakMag = modelData['Peak Magnitude']
            peakMagPoly = np.poly1d([peakMag, ])
            polyLightCurve = np.poly1d(poly)
            polyLightCurve = polyLightCurve - peakMagPoly
            polyLightCurve = np.poly1d(polyLightCurve)
            rawLightCurveDict[thisModel][ffilter]['poly'] = polyLightCurve
            rawLightCurveDict[thisModel][ffilter]['Explosion Day Relative to Peak'] = explosionDay

            log.debug('rawLightCurveDict[thisModel][ffilter][Explosion Day Relative to Peak]: %s' % (rawLightCurveDict[thisModel][ffilter]['Explosion Day Relative to Peak'],))
            rawLightCurveDict[thisModel][ffilter]['End of lightcurve relative to peak'] = endOfLightcurveDay
            plotDict[model] = polyLightCurve

            if plot:
                dp.plot_polynomial(
                    log,
                    title="00 raw lightcurve for %s, filter %s" % (model, ffilter),
                    polynomialDict=plotDict,
                    orginalDataDictionary=False,
                    pathToOutputPlotsFolder=pathToOutputPlotDirectory,
                    xRange=[explosionDay, endOfLightcurveDay],
                    xlabel=False,
                    ylabel=False,
                    xAxisLimits=False,
                    yAxisLimits=False,
                    yAxisInvert=True,
                    prependNum=False)

    return rawLightCurveDict


## LAST MODIFIED : April 15, 2013
## CREATED : April 15, 2013
## AUTHOR : DRYX
def random_peak_magnitudes(
        log,
        peakMagnitudeDistributions,
        snTypesArray,
        plot=True):
    """Generate a numpy array of random (distribution weighted) peak magnitudes for the given sn types.

    **Key Arguments:**
        - ``log`` -- logger
        - ``peakMagnitudeDistributions`` -- yaml style dictionary of peak magnitude distributions
        - ``snTypesArray`` -- the pre-generated array of random sn types
        - ``plot`` -- generate plot?

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import matplotlib.pyplot as plt
    import numpy as np
    ## LOCAL APPLICATION ##

    ################ >ACTION(S) ################
    magDistributions = {}
    for snType, peakMag in peakMagnitudeDistributions['magnitude'].iteritems():
        sigma = peakMagnitudeDistributions['sigma'][snType]
        magDistributions[snType] = [peakMag, sigma]

    peakMagList = []
    for item in snTypesArray:
        thisPeak = magDistributions[item][1] * np.random.randn() + magDistributions[item][0]
        peakMagList.append(thisPeak)

    peakMagArray = np.array(peakMagList)
    # log.debug('peakMagArray %s' % (peakMagArray,))

    return peakMagArray


## LAST MODIFIED : April 15, 2013
## CREATED : April 15, 2013
## AUTHOR : DRYX
def build_kcorrection_array(
        log,
        redshiftArray,
        snTypesArray,
        snLightCurves,
        pathToOutputDirectory,
        plot=True):
    """Given the random redshiftArray and snTypeArray, generate a dictionary of k-correction polynomials (one for each filter) for every object.

    **Key Arguments:**
        - ``log`` -- logger
        - ``redshiftArray`` -- the pre-generated redshift array
        - ``snTypesArray`` -- the pre-generated array of random sn types
        - ``snLightCurves`` -- yaml style dictionary of SN lightcurve info
        - ``pathToOutputDirectory`` -- path to the output directory (provided by the user)
        - ``plot`` -- generate plot?

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import yaml
    import numpy as np
    ## LOCAL APPLICATION ##

    ################ >ACTION(S) ################
    dataDir = pathToOutputDirectory + "k_corrections/"
    filters = ['g', 'r', 'i', 'z']
    fileName = pathToOutputDirectory + "transient_light_curves.yaml"
    stream = file(fileName, 'r')
    generatedLCs = yaml.load(stream)
    models = generatedLCs.keys()
    kCorList = []

    for i in range(len(redshiftArray)):
        redshift = redshiftArray[i]
        kCorDict = {}
        for model in models:
            for ffilter in filters:
                filterDir = dataDir + model + "/" + ffilter
                strRed = "%0.2f" % (redshift,)
                fileName = filterDir + "/z"+str(strRed).replace(".", "pt")+"_poly.yaml"
                try:
                    stream = file(fileName, 'r')
                    yamlContent = yaml.load(stream)
                    # log.info('yamlContent %s' % (yamlContent,))
                    stream.close()
                    flatPoly = np.poly1d(yamlContent['polyCoeffs'])
                except:
                    flatPoly = None
                kCorDict[ffilter] = flatPoly
                kCorList.append(kCorDict)

    kCorArray = np.array(kCorList)
    return kCorArray


## LAST MODIFIED : April 15, 2013
## CREATED : April 15, 2013
## AUTHOR : DRYX
def convert_lightcurves_to_observered_frame(
        log,
        snLightCurves,
        rawLightCurveDict,
        redshiftArray,
        snTypesArray,
        peakMagnitudesArray,
        hostExtinctionArray,
        kCorrectionArray,
        galacticExtinctionArray,
        restFrameFilter,
        pathToOutputDirectory,
        pathToOutputPlotDirectory,
        polyOrder,
        plot=True):
    """Given all the randomly generated parameters of the survey, generate a dictionary of lightcurves for each object (one lightcurve per filter)

    **Key Arguments:**
        - ``log`` -- logger
        - ``snLightCurves`` -- the sn lightcurve dictionary (with explosion / extinction dates)
        - ``rawLightCurveDict`` -- dictionary of the raw lightcurves (all peaking at mag = 0)
        - ``redshiftArray`` -- array of random redshifts,
        - ``snTypesArray`` --  array of random sn types,
        - ``peakMagnitudesArray`` --  array of random peak mags,
        - ``kCorrectionArray`` -- array of k-corrections,
        - ``hostExtinctionArray`` --  array of random host extinctions,
        - ``galacticExtinctionArray`` --  array of random galactic extinctions,
        - ``restFrameFilter`` -- the observed frame filter with which to calculate k-crrections with
        - ``pathToOutputDirectory`` -- path to the output directory (provided by the user)
        - ``pathToOutputPlotDirectory`` -- path to the output plot directory
        - ``polyOrder`` -- order of the polynomial used to fit the lightcurve
        - ``plot`` -- generate plots?

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import numpy as np
    import matplotlib.pyplot as plt
    import math
    import yaml
    ## LOCAL APPLICATION ##
    import dryxPython.astrotools as da
    import dryxPython.plotting as dp

    ################ >ACTION(S) ################
    filters = ['g', 'r', 'i', 'z']
    fileName = pathToOutputDirectory + "transient_light_curves.yaml"
    stream = file(fileName, 'r')
    generatedLCs = yaml.load(stream)
    models = generatedLCs.keys()
    ebvConverters = {'g' : 3.793, 'r' : 2.751, 'i' : 2.086, 'z' : 1.479}
    stepNum = 0

    ###########################################################
    # STEP 1 - CONVERT RAW LIGHTCURVES TO ABSOLUTE MAG CURVES #
    ###########################################################
    stepNum += 1
    stepStr = "%02d" % stepNum
    # CONVERT PEAK MAGS TO POLYNOMIALS
    peakMagPolyList = []
    for item in peakMagnitudesArray:
        thisPoly = np.poly1d([item, ])
        peakMagPolyList.append(thisPoly)

    # CONVERT RAW LIGHTCURVES TO ABSOLUTE MAG CURVES
    absLightCurveList = []
    exampleDictionary = {}

    for item in range(len(snTypesArray)):
        thisModel = snTypesArray[item]
        # explosionDay = snLightCurves[thisModel]['Explosion Day Relative to Peak']
        log.debug('thisModel, restFrameFilter: %s, %s' % (thisModel,restFrameFilter ,))
        explosionDay = rawLightCurveDict[thisModel][restFrameFilter]['Explosion Day Relative to Peak']
        endOfLightcurveDay = snLightCurves[thisModel]['End of lightcurve relative to peak']
        log.warning('explosionDay, endOfLightcurveDay for absolute Light Curve: %s, %s' % (explosionDay,endOfLightcurveDay))
        absLightCurve = rawLightCurveDict[thisModel][restFrameFilter]['poly'] + peakMagPolyList[item]
        absLightCurve = np.poly1d(absLightCurve)
        absLightCurveList.append(absLightCurve)
        exampleDictionary['SN %02d @ z = %04.3f' % (item, redshiftArray[item])] = absLightCurve
    if plot:
        dp.plot_polynomial(
            log,
            title="Absoulte Magnitude Lightcurves - random sample",
            polynomialDict=exampleDictionary,
            orginalDataDictionary=False,
            pathToOutputPlotsFolder=pathToOutputPlotDirectory,
            xRange=[explosionDay, endOfLightcurveDay],
            xlabel="Days Relative to Peak (Rest Frame)",
            ylabel="Absolute Magnitude",
            xAxisLimits=False,
            yAxisLimits=False,
            yAxisInvert=True,
            prependNum=stepNum)

    ################################################################
    # STEP 2 - CONVERT ABSOLUTE LIGHTCURVES TO APPARENT MAG CURVES #
    ################################################################
    stepNum += 1
    stepStr = "%02d" % stepNum
    # CONVERT DISTANCE MOD TO POLYNOMIALS
    distanceModPolyList = []
    for item in redshiftArray:
        log.debug('redshift: %s' % (item,))
        if item == 0.0:
            item = 0.01
        distanceDictionary = da.convert_redshift_to_distance(item)
        distanceMpc = distanceDictionary["dl_mpc"]
        distanceModulus = distanceDictionary["dmod"]
        # log.debug('distanceMpc %s' % (distanceMpc,))
        # log.info('redshift %s = distanceModulus %s' % (item, distanceModulus,))
        thisPoly = np.poly1d([distanceModulus, ])
        distanceModPolyList.append(thisPoly)

    # CONVERT ABSOLUTE LIGHTCURVES TO APPARENT MAG CURVES
    apparentLightCurveList = []
    for item in range(len(snTypesArray)):
        thisModel = snTypesArray[item]
        # explosionDay = snLightCurves[thisModel]['Explosion Day Relative to Peak']
        explosionDay = rawLightCurveDict[thisModel][restFrameFilter]['Explosion Day Relative to Peak']
        endOfLightcurveDay = snLightCurves[thisModel]['End of lightcurve relative to peak']
        log.warning('explosionDay, endOfLightcurveDay for apparent Light Curve: %s, %s' % (explosionDay,endOfLightcurveDay))
        apparentLightCurve = absLightCurveList[item] + distanceModPolyList[item]
        # log.debug('apparentLightCurve %s' % (apparentLightCurve,))
        apparentLightCurve = np.poly1d(apparentLightCurve)
        apparentLightCurveList.append(apparentLightCurve)
        exampleDictionary['SN %02d @ z = %04.3f' % (item, redshiftArray[item])] = apparentLightCurve
        #log.info('absLightCurveDictionary %s' % (absLightCurveDictionary,))
    if plot:
        dp.plot_polynomial(
            log,
            title="Pre-KCorrection Apparent Magnitude Lightcurves - random sample",
            polynomialDict=exampleDictionary,
            orginalDataDictionary=False,
            pathToOutputPlotsFolder=pathToOutputPlotDirectory,
            xRange=[explosionDay, endOfLightcurveDay],
            xlabel="Days Relative to Peak (Rest Frame)",
            ylabel="Apparent Magnitude",
            xAxisLimits=False,
            yAxisLimits=False,
            yAxisInvert=True,
            prependNum=stepNum)

    ###########################################################
    # STEP 3 - (UN) K-CORRECT THE APPARENT LIGHTCURVES        #
    ###########################################################
    stepNum += 1
    stepStr = "%02d" % stepNum
    # (UN) K-CORRECT THE APPARENT LIGHTCURVES
    kCorApparentLightCurveList = []
    for i in range(len(apparentLightCurveList)):
        thisModel = snTypesArray[i]
        # explosionDay = snLightCurves[thisModel]['Explosion Day Relative to Peak']
        explosionDay = rawLightCurveDict[thisModel][restFrameFilter]['Explosion Day Relative to Peak']
        endOfLightcurveDay = snLightCurves[thisModel]['End of lightcurve relative to peak']
        log.warning('explosionDay, endOfLightcurveDay for unkcor apparent Light Curve: %s, %s' % (explosionDay,endOfLightcurveDay))
        kCorDict = kCorrectionArray[i]
        lcDict = {}
        plotLcDict = {}
        for ffilter, poly in kCorDict.iteritems():
            if poly is None:
                kcorLightCurve = None
            else:
                kcorLightCurve = apparentLightCurveList[i] - poly
                plotLcDict[ffilter] = kcorLightCurve
            lcDict[ffilter] = kcorLightCurve
            if plot:
                dp.plot_polynomial(
                    log,
                    title="K(un)corrected Apparent Magnitude Lightcurves - SN Number %s" % (i),
                    polynomialDict=plotLcDict,
                    orginalDataDictionary=False,
                    pathToOutputPlotsFolder=pathToOutputPlotDirectory,
                    xRange=[explosionDay, endOfLightcurveDay],
                    xlabel="Days Relative to Peak (Rest Frame)",
                    ylabel="Apparent Magnitude",
                    xAxisLimits=False,
                    yAxisLimits=False,
                    yAxisInvert=True,
                    prependNum=stepNum)

        kCorApparentLightCurveList.append(lcDict)

    ###########################################################
    # STEP 4 - INCLUDE GALACTIC EXTINCTION IN LIGHTCURVES     #
    ###########################################################
    stepNum += 1
    stepStr = "%02d" % stepNum
    # INCLUDE GALACTIC EXTINCTION
    # CONVERT EXT TO POLYNOMIALS
    galExtPolyList = []
    for ext in galacticExtinctionArray:
        extDict = {}
        for ffilter in filters:
            thisExt = ext*ebvConverters[ffilter]
            # log.info('ext %s, filter %s' % (thisExt, ffilter))
            thisPoly = np.poly1d([thisExt, ])
            extDict[ffilter] = thisPoly
        galExtPolyList.append(extDict)

    # INCLUDE GALAXTIC EXTINTION IN LIGHTCURVES
    galExtLightCurveList = []
    for item in range(len(kCorApparentLightCurveList)):
        thisModel = snTypesArray[item]
        # explosionDay = snLightCurves[thisModel]['Explosion Day Relative to Peak']
        explosionDay = rawLightCurveDict[thisModel][restFrameFilter]['Explosion Day Relative to Peak']
        endOfLightcurveDay = snLightCurves[thisModel]['End of lightcurve relative to peak']
        log.warning('explosionDay, endOfLightcurveDay for galatic extinction corr Frame Light Curve: %s, %s' % (explosionDay,endOfLightcurveDay))
        lcDict = {}
        plotLcDict = {}
        for ffilter in filters:
            if kCorApparentLightCurveList[item][ffilter] is not None:
                galExtLightCurve = kCorApparentLightCurveList[item][ffilter] + galExtPolyList[item][ffilter]
                # log.debug('apparentLightCurve %s' % (apparentLightCurve,))
                galExtPoly = np.poly1d(galExtLightCurve)
                plotLcDict[ffilter] = galExtPoly
            else:
                galExtPoly = None
            lcDict[ffilter] = galExtPoly
        if plot:
            dp.plot_polynomial(
                log,
                title="Galactic Extinction Corrected Lightcurves - SN Number %s" % (item),
                polynomialDict=plotLcDict,
                orginalDataDictionary=False,
                pathToOutputPlotsFolder=pathToOutputPlotDirectory,
                xRange=[explosionDay, endOfLightcurveDay],
                xlabel="Days Relative to Peak (Rest Frame)",
                ylabel="Apparent Magnitude",
                xAxisLimits=False,
                yAxisLimits=False,
                yAxisInvert=True,
                prependNum=stepNum)

        galExtLightCurveList.append(lcDict)

    ###########################################################
    # STEP 5 - TIME-DILATE LIGHTCURVES                        #
    ###########################################################
    stepNum += 1
    stepStr = "%02d" % stepNum
    observedFrameLightCurveInfo = []
    peakAppMagList = []
    for item in range(len(redshiftArray)):
        timeDilation = 1. + redshiftArray[item]
        thisModel = snTypesArray[item]
        # explosionDay = snLightCurves[thisModel]['Explosion Day Relative to Peak']*timeDilation
        explosionDay = rawLightCurveDict[thisModel][restFrameFilter]['Explosion Day Relative to Peak']*timeDilation
        endOfLightcurveDay = snLightCurves[thisModel]['End of lightcurve relative to peak']*timeDilation
        log.warning('explosionDay, endOfLightcurveDay for observed time dil Frame Light Curve: %s, %s' % (explosionDay,endOfLightcurveDay))
        polyDict = {}
        lcPolyDict = {}
        peakMagDict = {}
        floatPeakMagDict = {}

        for ffilter in filters:
            if galExtLightCurveList[item][ffilter] is not None:
                xList = []
                yList = []
                for x in range(int(explosionDay), int(endOfLightcurveDay)):
                    xList.append(x*timeDilation)
                    y = galExtLightCurveList[item][ffilter](x)
                    yList.append(y)

                x = np.array(xList)
                y = np.array(yList)
                thisPoly = np.polyfit(x, y, polyOrder)
                flatPoly = np.poly1d(thisPoly)
                peakMag = flatPoly(0)
                floatPeakMag = float(peakMag)
                polyDict[ffilter] = flatPoly
                peakMagDict[ffilter] = peakMag
                floatPeakMagDict[ffilter] = floatPeakMag
                lcPolyDict[ffilter] = flatPoly
            else:
                polyDict[ffilter] = None
                peakMagDict[ffilter] = None
                floatPeakMagDict[ffilter] = None

        if plot:
            dp.plot_polynomial(
                log,
                title="Observed Lightcurves - SN Number %s" % (item, ),
                polynomialDict=lcPolyDict,
                orginalDataDictionary=False,
                pathToOutputPlotsFolder=pathToOutputPlotDirectory,
                xRange=[explosionDay, endOfLightcurveDay],
                xlabel="Days Relative to Peak (Observed Frame)",
                ylabel="Apparent Magnitude",
                xAxisLimits=False,
                yAxisLimits=False,
                yAxisInvert=True,
                prependNum=stepNum,
                legend=True)

        thisData = {
                    'lightCurves' : polyDict,
                    'peakMags' : peakMagDict,
                    'explosionDay' : explosionDay,
                    'endOfLightcurveDay' : endOfLightcurveDay }
        # log.info('peakMagDict %s' % (peakMagDict,))
        observedFrameLightCurveInfo.append(thisData)
        peakAppMagList.append(floatPeakMagDict)

    return observedFrameLightCurveInfo, peakAppMagList


###################################################################
# PRIVATE (HELPER) FUNCTIONS                                      #
###################################################################

if __name__ == '__main__':
    main()


###################################################################
# TEMPLATE FUNCTIONS                                              #
###################################################################
