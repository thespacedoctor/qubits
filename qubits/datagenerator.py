#!/usr/bin/python
# encoding: utf-8
"""
datagenerator
============================
:Summary:
    Partial for the main MCS simulation. This module will generate lightcurves and K-corrections
    for the SN models given multiple epoch spectra and filter throughputs as a function of wavelength.

:Author:
    David Young

:Date Created:
    March 20, 2013

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
## LAST MODIFIED : April 16, 2013
## CREATED : April 16, 2013
## AUTHOR : DRYX
def generate_model_lightcurves(
        log,
        pathToSpectralDatabase,
        pathToOutputDirectory,
        pathToOutputPlotDirectory,
        explosionDaysFromSettings,
        extendLightCurveTail,
        polyOrder
    ):
    """Generate the lightcurve plots and polynomials by extracting the data from the provided spectra.

    **Key Arguments:**
        - ``log`` -- logger
        - ``pathToSpectralDatabase`` -- path to the nested-folders and files spectral database (provided by the user)
        - ``pathToOutputDirectory`` -- path to the output directory (provided by the user)
        - ``pathToOutputPlotDirectory`` -- path to add plots to
        - ``explosionDaysFromSettings`` -- explosion days for transients as set by the user in the settings file
        - ``extendLightCurveTail`` -- extend the tail of the lightcurve by extrapolating last two data points
        - ``polyOrder`` -- order of the polynomial used to fit the lightcurve

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    import glob
    import os
    ## THIRD PARTY ##
    import yaml
    ## LOCAL APPLICATION ##

    ################ >ACTION(S) ################
    ## WRITE CODE HERE
    pwd = os.getcwd()
    pathToSpectralDatabase

    spectralDatabase = {}

    basePath = pathToSpectralDatabase
    for d in os.listdir(basePath):
        if os.path.isdir(os.path.join(basePath, d)):
            spectralDatabase[d] = os.path.join(basePath, d)+"/"

    # spectralDatabase = {"he130": he130}
    filters = ['g', 'r', 'i', 'z']
    # filters = ['g']

    extractedLightCurveDict = {}
    for model, path in spectralDatabase.iteritems():
        extractedLightCurveDict[model] = {}
        os.chdir(path)
        spectrumFiles = []
        for thisFile in glob.glob("*.spec"):
            thisFile = path + thisFile
            spectrumFiles.append(thisFile)

        os.chdir(pwd)

        # LIGHTCURVES PLOTTING CODE
        peakDict = {}
        for ffilter in filters:
            extractedLightCurveDict[model][ffilter] = {}
            title = "%s - %s-band" % (model, ffilter)
            # EXTRACT LIGHTCURVES FROM SPECTRA

            magnitudes, times = extract_lightcurve(
                log,
                spectrumFiles,
                userExplosionDay=explosionDaysFromSettings[model],
                extendLightCurveTail=extendLightCurveTail[model],
                obsmode="sdss,%s" % (ffilter,)
            )

            filterDict = {}

            # CREATE A FIRST POLY LIGHTCURVE TO EXTRACT MAX PEAK AND TIME
            lightCurveList = [[magnitudes, times, '%s-band data' % (ffilter,), ffilter, model, title],]
            curveDict = plotLightCurves(
                log,
                lightCurves=lightCurveList,
                polyOrder=polyOrder,
                pathToOutputDirectory=pathToOutputPlotDirectory
            )

            # log.debug('lightCurveList: %s' % (lightCurveList,))

            wavelengthArray, fluxArray = extract_spectra_from_file(log, pathToSpectrum=thisFile)
            for k, v in curveDict.iteritems():
                poly = v

                if poly is None:
                    log.warning('could not generate a polynomial for %s in %s-band - enough data could not be extracted from spectra' % (model,ffilter))
                    continue
                start=int(min(times))
                end=int(max(times))
                log.debug('times: %s' % (times,))
                log.debug('model, start, end: %s, %s, %s' % (model, start, end,))

                if poly is not None:
                    peakMag, peakTime, explosionMag, explosionDay = find_peak_magnitude(
                        log,
                        poly=poly,
                        model=model,
                        start=int(min(times)),
                        end=int(max(times))
                    )
                else:
                    peakMag, peakTime, explosionMag, explosionDay = None, None, None, None

                if peakTime is not None:
                    extractedLightCurveDict[model][ffilter]['Peak Magnitude'] = peakMag
                    extractedLightCurveDict[model][ffilter]['Peak Time in Spectra'] = peakTime
                    extractedLightCurveDict[model][ffilter]['Explosion Day Relative to Peak'] = - peakTime + explosionDay
                    for i in range(len(times)):
                        times[i] = times[i] - peakTime
                else:
                    extractedLightCurveDict[model][ffilter]['Peak Magnitude'] = None
                    extractedLightCurveDict[model][ffilter]['Peak Time in Spectra'] = None
                    extractedLightCurveDict[model][ffilter]['Explosion Day Relative to Peak'] = None



            # CREATE A SECOND POLY LIGHTCURVE NORMALISED TO PEAK MAG AND TIME
            lightCurveList = [[magnitudes, times, '%s-band data' % (ffilter,), ffilter, model, title],]
            curveDict = plotLightCurves(
                log,
                lightCurves=lightCurveList,
                polyOrder=polyOrder,
                pathToOutputDirectory=pathToOutputPlotDirectory
            )

            for k, v in curveDict.iteritems():
                extractedLightCurveDict[model][ffilter][k] = v

    yamlDict = extractedLightCurveDict
    fileName = pathToOutputDirectory + "transient_light_curves.yaml"
    stream = file(fileName, 'w')
    yaml.dump(yamlDict, stream, default_flow_style=False)
    stream.close()

    return extractedLightCurveDict


## LAST MODIFIED : March 20, 2013
## CREATED : March 20, 2013
## AUTHOR : DRYX
def extract_spectra_from_file(
        log,
        pathToSpectrum,
        convertLumToFlux=False):
    """Given a spectrum file this function shall convert the two columns (wavelength and luminosity) to a wavelegnth (wavelengthArray) and flux (fluxArray) array

    **Key Arguments:**
        - ``log`` -- logger
        - ``pathToSpectrum`` -- absolute path the the spectrum file

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    import os
    ## THIRD PARTY ##
    import numpy as np
    ## LOCAL APPLICATION ##
    import dryxPython.astrotools as at


    ################ > VARIABLE SETTINGS ######
    ################ >ACTION(S) ################
    # USE numPy TO EXTRACT THE DATA FROM FILE
    pwd = os.getcwd()
    log.debug('pwd %s' % (pwd,))
    log.debug('pathToSpectrum %s' % (pathToSpectrum,))
    data = np.genfromtxt(pathToSpectrum, skip_header=0, usecols=(0, 1))
    wavelengthArray = data[:, 0]
    # minWl = wavelengthArray.min()
    # maxWl = wavelengthArray.max()
    luminosityArray = data[:, 1]
    ## CONVERT TO FLUX:  F = L / 4*pi*(r**2)
    if convertLumToFlux:
        fluxArray = at.luminosity_to_flux(luminosityArray, 1e-5)
    else:
        fluxArray = luminosityArray

    ## DEBUG BLOCK
    log.debug('pathToSpectrum: %s' % (pathToSpectrum,))
    # for i in range(len(fluxArray)):
    #     print """%s\t%s\t%s""" % (wavelengthArray[i], luminosityArray[i], fluxArray[i] )
    # print "\n\n\n"
    return wavelengthArray, fluxArray


## LAST MODIFIED : March 22, 2013
## CREATED : March 22, 2013
## AUTHOR : DRYX
def plot_filter_transmissions(log, filterList):
    """Plot the filters on a single plot

    **Key Arguments:**
        - ``log`` -- logger
        - ``filterList`` -- list of absolute paths to plain text files containing filter transmission profiles

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import matplotlib.pyplot as plt
    import numpy as np
    ## LOCAL APPLICATION ##


    ################ > VARIABLE SETTINGS ######
    ################ >ACTION(S) ################
    for filterFile in filterList:
        data = np.genfromtxt(filterFile)
        plt.plot(data[:, 0], data[:, 1])

    plt.show()
    return


## LAST MODIFIED : March 24, 2013
## CREATED : March 24, 2013
## AUTHOR : dryx
# def calcphot(log, spectrum, filter):
def calcphot(log, wavelengthArray, fluxArray, obsmode):
    """Run calcphot on single spectrum and filter.

    **Key Arguments:**
        - ``log`` -- logger
        - ``wavelengthArray`` -- the array containing the wavelength range of the spectrum
        - ``fluxArray`` -- the array contain the respective spectrum flux (as function of wavelength)
        - ``obsmode`` -- the observation mode (generally a filter system and filter type, e.g. "sdss,g")

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import pysynphot as syn
    ## LOCAL APPLICATION ##

    ################ > VARIABLE SETTINGS ######
    # Read in a spectrum from a file
    sp = syn.ArraySpectrum(wave=wavelengthArray, flux=fluxArray, waveunits='angstrom', fluxunits='flam')
    bp = syn.ObsBandpass(obsmode)
    obs = syn.Observation(sp, bp)
    abMag = obs.effstim('abmag')

    return abMag


## LAST MODIFIED : March 25, 2013
## CREATED : March 25, 2013
## AUTHOR : DRYX
def plotLightCurves(
        log,
        lightCurves,
        polyOrder,
        pathToOutputDirectory):
    """plot lightcurve(s) given an list of magnitude, time pairs

    **Key Arguments:**
        - ``log`` -- logger
        - ``lightCurves`` -- list of magnitude, time numPy arrays
        - ``polyOrder`` -- order of polynomial used to fit the model lightcurves extracted from spectra
        - ``pathToOutputDirectory`` -- path to the output directory

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import matplotlib.pyplot as plt
    import numpy as np
    ## LOCAL APPLICATION ##

    resultsDict = {}
    ################ > VARIABLE SETTINGS ######
    ################ >ACTION(S) ################
    ax = plt.subplot(111)
    curveDict = {}
    for curve in lightCurves:
        x = curve[1]
        y = curve[0]

        ## CAUSE LIGHTCURVE GENERATION TO FAIL IF LESS THAN 5 POINTS EXTRACTED FROM THE SPECTRA
        if len(x) <= 4:
            curveDict['poly'] = None
            continue

        order = polyOrder
        poly = np.polyfit(x, y, order)
        curveDict['poly'] = poly
        pOrder = np.poly1d(poly)
        polyString = "mxxx[i] = "
        polyStringMd = "\\\\(mag = "
        for i in range(0, order+1):
            if i > 0 and poly[i] > 0:
                polyString += "+"
                polyStringMd += "+"
            polyString += """%s*pow(i,%s) """ % (poly[i], order-i)
            polyStringMd += """%s*time^{%s} """ % (poly[i], order-i)
        polyStringMd += "\\\\)"

        ax.plot(x, y, '.', label='%s' % (curve[2],))
        i = np.arange(int(min(x)), int(max(x)), 1)
        ax.plot(i, pOrder(i), label='polynomial fit')

    title = curve[5]
    # Shink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size':8})
    ax.titlesize = 'medium'   # fontsize of the axes title
    ax.labelsize = 'medium'  # fontsize of the x any y labels
    plt.xlabel("Days Relative to Peak")
    plt.ylabel("Magnitude")
    plt.title(title, fontsize='small', verticalalignment = 'bottom', linespacing = 0.2)
    ax.invert_yaxis()

    fileName = pathToOutputDirectory + title.replace(" ", "_") + ".png"
    # mdPlotLink = """![%s_plot]\n\n[%s_plot]: %s\n\n""" % (title.replace(" ", "_"), title.replace(" ", "_"), fileName,)
    # curveDict['mdLink'] = mdPlotLink
    plt.savefig(fileName)
    plt.clf()  # clear figure

    return curveDict


## LAST MODIFIED : March 25, 2013
## CREATED : March 25, 2013
## AUTHOR : DRYX
def extract_lightcurve(
        log,
        spectrumFiles,
        userExplosionDay,
        extendLightCurveTail,
        obsmode):
    """Extract the requested lightcurve from list of spectrum files

    **Key Arguments:**
        - ``log`` -- logger
        - ``spectrumFiles`` -- list of the spectrum files
        - ``userExplosionDay`` -- explosion day for transient as set by the user in the settings file
        - ``extendLightCurveTail`` -- extend the tail of the lightcurve by extrapolating last two data points
        - ``obsmode`` -- the observation mode (generally a filter system and filter type, e.g. "sdss,g")

    **Return:**
        - ``magnitudes`` -- numpy array of the magnitudes
        - ``times`` -- numpy array of the corresponding times
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    import re
    ## THIRD PARTY ##
    import numpy as np
    ## LOCAL APPLICATION ##

    ################ > VARIABLE SETTINGS ######
    reTime = re.compile(r't((\+|\-)\d{3}\.\d{2})')
    magnitudes = []
    times = []
    fileNameTimes = []

    # log.info('spectrumFiles[-1] %s' % (spectrumFiles[-1],))
    ################ >ACTION(S) ################
    for thisFile in spectrumFiles:
        # log.warning('here is the file %s' % (thisFile,))
        # mul = 1.
        # if reTime.search(thisFile).group(2) == "-":
        #     mul = -1.
        thisTime = float(reTime.search(thisFile).group(1))
        fileNameTimes.append(thisTime)
        log.debug('time in %s is: %s' % (thisFile,thisTime))
        wavelengthArray, fluxArray = extract_spectra_from_file(log, thisFile)
        try:
            log.debug("attempting to find the magnitude from spectrum")
            magnitudes.append(
                calcphot(
                    log,
                    wavelengthArray=wavelengthArray,
                    fluxArray=fluxArray,
                    obsmode=obsmode
                )
            )
            times.append(thisTime)
        except Exception, e:
            log.warning("could not find the magnitude from spectrum %s using the filter %s - failed with this error: %s " % (thisFile,obsmode,str(e),))
            pass

    ## APPEND AN EXPLOSION DAY AND MAG
    if len(magnitudes) > 3:
        finalTime = max(times)
        firstTime = min(times)
        firstMag=magnitudes[times.index(firstTime)]
        lastMag=magnitudes[times.index(finalTime)]
        log.debug('times: %s' % (times,))
        log.debug('magnitudes: %s' % (magnitudes,))
        sortedTime = times[:]
        sortedTime.sort()
        log.debug('sortedTime: %s' % (sortedTime,))
        secondLastTime=sortedTime[-2]
        secondLastMag=magnitudes[times.index(secondLastTime)]

        minMag = max(magnitudes)
        iterations = 4
        magDrop = 4

        if userExplosionDay is not None:
            x2=firstTime
            x1=userExplosionDay
            y2=firstMag
            y1=minMag+magDrop

            m = (y1-y2)/(x1-x2)
            c = y1-m*x1
            upperTimeLimit = (minMag-c)/m

            thisRange = upperTimeLimit-userExplosionDay
            delta = 0
            magDropNow = magDrop
            # log.debug('firstTime, userExplosionDay, increment: %s, %s, %s' % (firstTime, userExplosionDay))
            log.debug('range: %s' % (np.arange(userExplosionDay, upperTimeLimit, thisRange/iterations+1),))
            for t in np.arange(userExplosionDay,upperTimeLimit, thisRange/iterations):
                log.debug('new time: %s' % (t,))
                magDropNow -= delta
                delta = magDrop/iterations
                log.debug('magDrop, delta : %s, %s' % (magDropNow, delta,))
                times.append(t)
                magnitudes.append(minMag+magDropNow)
                log.debug('new mag: %s' % (minMag+magDropNow,))

        if extendLightCurveTail:
            x2=secondLastTime
            x1=finalTime
            y2=secondLastMag
            y1=lastMag

            log.debug('finalTime, lastMag: %s, %s' % (finalTime, lastMag,))
            log.debug('secondLastTime, secondLastMag: %s, %s' % (secondLastTime, secondLastMag))

            m = (y1-y2)/(x1-x2)
            c = y1-m*x1
            upperTimeLimit = (lastMag+4-c)/m

            thisRange = upperTimeLimit-finalTime
            delta = 0
            magDrop = 4
            magDropNow = 0
            for t in np.arange(finalTime, upperTimeLimit, thisRange/iterations):
                magDropNow += delta
                delta = magDrop/iterations
                times.append(t)
                magnitudes.append(lastMag+magDropNow)

    log.debug('finding magnitudes and times from spectrum : %s' % (thisFile ,))
    log.debug('magnitudes, times: %s, %s' % (magnitudes,times))
    print magnitudes, times
    return magnitudes, times


## LAST MODIFIED : March 25, 2013
## CREATED : March 25, 2013
## AUTHOR : DRYX
def find_peak_magnitude(
        log,
        poly,
        model,
        start,
        end):
    """Determine peakMag and time from an initial polynomial lightcurve

    **Key Arguments:**
        - ``log`` -- logger
        - ``poly`` -- initial polynomial lightcurve
        - ``model`` -- the transient being considered
        - ``start`` -- lower time bound of spectrum
        - ``end`` -- upper time bound of spectrum

    **Return:**
        - ``peakMag``
        - ``peakTime``
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import numpy as np
    ## LOCAL APPLICATION ##

    ################ > VARIABLE SETTINGS ######

    ################ >ACTION(S) ################
    timeList = []
    magnitudeList = []

    # wavelengthArray, fluxArray, minWl, maxWl = extract_spectra_from_file(log, thisFile)
    for time in range(start, end, 1):
        thisTime = time - 20.
        flatPoly = np.poly1d(poly)
        magnitude = flatPoly(thisTime)
        timeList.append(thisTime)
        magnitudeList.append(magnitude)

    magnitudeArray = np.array(magnitudeList)
    timeArray = np.array(timeList)
    magIndexMin=magnitudeArray.argmin()
    magIndexMax=magnitudeArray.argmax()
    timeIndexMin=timeArray.argmin()
    timeIndexMax=timeArray.argmax()

    peakMag = float(magnitudeArray[magIndexMin])
    peakTime = float(timeList[magIndexMin])
    explosionMag = float(magnitudeArray[timeIndexMin])
    explosionDay = float(timeList[timeIndexMin])

    log.debug('start, end: %s, %s' % (start, end,))
    log.debug('timeList: %s' % (timeList,))
    log.debug('magnitudeArray: %s' % (magnitudeArray,))
    log.info('MODEL: %s ... peakMag %s, peakTime %s, explosionMag %s, explosionDay %s' % (model, peakMag, peakTime, explosionMag, explosionDay))
    return peakMag, peakTime, explosionMag, explosionDay

## LAST MODIFIED : March 25, 2013
## CREATED : March 25, 2013
## AUTHOR : DRYX
def generate_kcorrection_listing_database(
        log,
        restFrameFilter,
        pathToOutputDirectory,
        pathToSpectralDatabase,
        temporalResolution=4.0,
        redshiftResolution=0.1,
        redshiftLower=0.0,
        redshiftUpper=1.0):
    """Generate the Kg* k-corrections for a range of redshifts given a list of spectra

    **Key Arguments:**
        - ``log`` -- logger
        - ``restFrameFilter`` -- the filter to generate the K-corrections against
        - ``pathToOutputDirectory`` -- path to the output directory (provided by the user)
        - ``pathToSpectralDatabase`` -- path to the directory containing the spectral database
        - ``temporalResolution`` -- temporal resolution at which to calculate the k-correcions
        - ``redshiftResolution`` -- resolution of the k-correction database (at what redshift points do you want the k-corrections calculated)
        - ``redshiftLower`` -- lower redshift in range of k-corrections to be calculated
        - ``redshiftUpper`` -- upper redshift in range of k-corrections to be calculated

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    import re
    import os
    import shutil
    ## THIRD PARTY ##
    import pysynphot as syn
    import yaml
    ## LOCAL APPLICATION ##

    mul = 1000
    div = 1000.

    fileName = pathToOutputDirectory + "transient_light_curves.yaml"
    stream = file(fileName, 'r')
    generatedLCs = yaml.load(stream)

    ## REMOVE OLD DATABASE
    try:
        shutil.rmtree(pathToOutputDirectory+"k_corrections")
    except:
        pass

    models = generatedLCs.keys()
    for model in models:

        for redshift in range(int(redshiftLower*mul), int(redshiftUpper*mul), int(redshiftResolution*mul)):
            redshift = redshift/div

            generate_single_kcorrection_listing(
                log,
                pathToOutputDirectory=pathToOutputDirectory,
                pathToSpectralDatabase=pathToSpectralDatabase,
                model=model,
                redshift=redshift,
                restFrameFilter=restFrameFilter,
                temporalResolution=4.0)
    return


## LAST MODIFIED : April 15, 2013
## CREATED : April 15, 2013
## AUTHOR : DRYX
def generate_single_kcorrection_listing(
        log,
        pathToOutputDirectory,
        pathToSpectralDatabase,
        model,
        restFrameFilter,
        redshift,
        temporalResolution=4.0):
    """Given a redshift generate a dictionary of k-correction polynomials for the MCS.

    **Key Arguments:**
        - ``log`` -- logger
        - ``pathToOutputDirectory`` -- path to the output directory (provided by the user)
        - ``pathToSpectralDatabase`` -- path to the directory containing the spectral database
        - ``model`` -- name of the object/model required
        - ``restFrameFilter`` -- the filter to generate the K-corrections against
        - ``redshift`` -- the redshift at which to generate the k-corrections for
        - ``temporalResolution`` -- temporal resolution at which to calculate the k-correcions

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    import re
    import os
    import glob

    ## THIRD PARTY ##
    import yaml
    import pysynphot as syn
    ## LOCAL APPLICATION ##


    ################ >ACTION(S) ################
    # GET THE PEAK MAGNITUDE DETAILS FROM YAML FILE
    fileName = pathToOutputDirectory + "transient_light_curves.yaml"
    stream = file(fileName, 'r')
    generatedLCs = yaml.load(stream)
    filterData = generatedLCs[model]
    peakMag = generatedLCs[model][restFrameFilter]['Peak Magnitude']
    peakTime = generatedLCs[model][restFrameFilter]['Peak Time in Spectra']
    stream.close()

    pwd = os.getcwd()
    path = pathToSpectralDatabase + "/" + model + "/"

    title = "%s Objects" % (model,)
    os.chdir(path)
    spectrumFiles = []
    for thisFile in glob.glob("*.spec"):
        thisFile = path + thisFile
        spectrumFiles.append(thisFile)

    os.chdir(pwd)

    ################ > VARIABLE SETTINGS ######
    reTime = re.compile(r't((\+|\-)\d{3}\.\d{2})')

    ################ >ACTION(S) ################
    # CREATE THE REQUIRED DIRECTORIES

    filters = ["g", "i", "r", "z"]
    for thisFilter in filters:
        strRed = "%0.2f" % (redshift,)
        try:
            log.debug("attempting to create directories")
            dataDir = pathToOutputDirectory + "k_corrections/%s/%s" % (model, thisFilter)
            os.makedirs(dataDir)
        except Exception, e:
            log.debug("could not create directories - failed with this error: %s " % (str(e),))

        try:
            log.debug("attempting to clear the k-correction yaml file")
            fileName = dataDir + "/z"+str(strRed).replace(".", "pt")+".yaml"
            stream = file(fileName, 'w')
            stream.close()
        except Exception, e:
            log.critical("could not clear the k-correction yaml file - failed with this error: %s " % (str(e),))
            return -1

    nextTime = 0.0
    for thisFile in spectrumFiles:
        # mul = 1
        # if reTime.search(thisFile).group(2) == "-":
        #     mul = -1
        thisTime = float(reTime.search(thisFile).group(1))
        if thisTime < nextTime:
            continue
        else:
            nextTime = thisTime + temporalResolution
            thisTime -= peakTime
            wavelengthArray, fluxArray = extract_spectra_from_file(log, thisFile)
            spRest = syn.ArraySpectrum(wave=wavelengthArray, flux=fluxArray, waveunits='angstrom', fluxunits='flam')
            try:
                log.debug("attempting to determine the rest %s-magnitude" % (restFrameFilter,))
                gRest = calcphot(
                    log,
                    wavelengthArray=wavelengthArray,
                    fluxArray=fluxArray,
                    obsmode="sdss,%s" % (restFrameFilter,)
                )
            except Exception, e:
                if "Integrated flux is <= 0" in str(e):
                    log.warning("could not determine the rest-magnitude using calcphot - filter, model, time, file %s, %s, %s, %s - failed with this error: %s " % (restFrameFilter, model, thisTime, thisFile, str(e),))
                    continue
                elif "Spectrum and bandpass do not fully overlap" in str(e):
                    log.warning("could not determine the rest-magnitude using calcphot - filter, model, time, file %s, %s, %s, %s - failed with this error: %s " % (restFrameFilter, model, thisTime, thisFile, str(e),))
                    continue
                else:
                    log.warning("could not determine the rest-magnitude using calcphot - filter, model, time, file %s, %s, %s, %s - failed with this error: %s " % (restFrameFilter, model, thisTime, thisFile, str(e),))
                pass

            for thisFilter in filters:
                strRed = "%0.2f" % (redshift,)
                spObs = spRest.redshift(redshift)
                dataDir = pathToOutputDirectory + "k_corrections/%s/%s" % (model, thisFilter)
                try:
                    log.debug("attempting to open the yaml file to append k-correction data")
                    fileName = dataDir + "/z"+str(strRed).replace(".", "pt")+".yaml"
                    stream = file(fileName, 'a')
                except Exception, e:
                    log.critical("could not open the yaml file to append k-correction data - failed with this error: %s " % (str(e),))
                    return -1

                try:
                    log.debug("attempting to determine the magnitude of the object using calcphot - redshift, filter, model %s, %s, %s" % (strRed,thisFilter, model))
                    filterObs = calcphot(
                        log,
                        wavelengthArray=spObs.wave,
                        fluxArray=spObs.flux,
                        obsmode="sdss,%s" % (thisFilter,)
                    )
                except Exception, e:
                    if "Integrated flux is <= 0" in str(e):
                        log.warning("could not determine the magnitude of the object using calcphot - redshift, filter, model %s, %s, %s - failed with this error: %s " % (strRed,thisFilter, model,str(e),))
                        continue
                    elif "Spectrum and bandpass do not fully overlap" in str(e):
                        log.warning("could not determine the magnitude of the object using calcphot - redshift, filter, model %s, %s, %s - failed with this error: %s " % (strRed,thisFilter, model,str(e),))
                        continue
                    else:
                        log.warning("could not determine the magnitude of the object using calcphot - redshift, filter, model %s, %s, %s - failed with this error: %s " % (strRed,thisFilter, model,str(e),))
                    pass
                kCor = gRest-filterObs
                kcName = 'K_%s%s' % (restFrameFilter, thisFilter,)
                thisKcor = {}
                thisKcor["Rest Frame Days"] = thisTime
                thisKcor[kcName] = kCor
                yamlList = [thisKcor]
                yaml.dump(yamlList, stream, default_flow_style=False)
                stream.close()

    return


## LAST MODIFIED : April 16, 2013
## CREATED : April 16, 2013
## AUTHOR : DRYX
def generate_single_kcorrection_polynomial(
        log,
        model,
        pathToOutputDirectory,
        redshift,
        ffilter,
        restFrameFilter,
        kCorPolyOrder=3,
        kCorMinimumDataPoints=3,
        plot=False):
    """Given a the k-correction lightcurve, convert it to a polynomial, plot if requested and dump to a separate file.

    **Key Arguments:**
        - ``log`` -- logger
        - ``model`` -- the transient model name
        - ``pathToOutputDirectory`` -- path to the output directory (provided by the user)
        - ``redshift`` -- the redshift of the k-correction listing to plot
        - ``ffilter`` -- the k-correction rest frame filter
        - ``restFrameFilter`` -- the observed frame filter
        - ``kCorPolyOrder`` -- the order of the polynomial to fit
        - ``kCorMinimumDataPoints`` -- Minimum number of datapoints used to generate k-correction curve
        - ``plot`` -- plot the polynomial?

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    ## THIRD PARTY ##
    import numpy as np
    import yaml
    ## LOCAL APPLICATION ##
    import dryxPython.plotting as dp

    ################ >ACTION(S) ################
    strRed = "%0.2f" % (redshift,)
    dataDir = pathToOutputDirectory + "k_corrections/%s/%s" % (model, ffilter)
    pathToYaml = dataDir + "/z"+str(strRed).replace(".", "pt")+".yaml"
    fileName = pathToYaml
    stream = file(fileName, 'r')
    yamlList = yaml.load(stream)
    thisKcor = 'K_%s%s' % (restFrameFilter, ffilter)
    stream.close()

    kCor = []
    time = []
    try:
        log.debug("attempting to generate a k-correction polynomial plot from the file: %s" % (fileName,))
        for item in yamlList:
            kCor.append(item[thisKcor])
            time.append(item['Rest Frame Days'])
    except Exception, e:
        log.warning("could not generate a k-correction polynomial plot from the file %s:  - failed with this error: %s " % (fileName, str(e),))
        return -1

    if len(kCor) < kCorMinimumDataPoints:
        basename = os.path.basename(fileName)
        log.warning('the k-correction file %s contains less than %s datapoints - polynomial shall not be generated' % (basename,kCorMinimumDataPoints))
        return

    kCorArray = np.array(kCor)
    timeArray = np.array(time)
    xMin = np.min(timeArray)
    xMax = np.max(timeArray)

    timeDist = 200
    timeDelta = 40
    for i in range(4):
        timeArray = np.append(timeArray,xMin-timeDist-i*timeDelta)
        timeArray = np.append(timeArray,xMax+timeDist+i*timeDelta)
        kCorArray = np.append(kCorArray,[0,0])

    log.debug('timeArray: %s' % (timeArray,))
    log.debug('kCorArray: %s' % (kCorArray,))

    expand = 20
    xMin -= expand
    xMax += expand

    thisPoly = np.polyfit(timeArray, kCorArray, kCorPolyOrder)
    flatPoly = np.poly1d(thisPoly)
    polyDict = {}
    dataDict = {}
    polyDict[redshift] = flatPoly
    dataDict[redshift] = [timeArray, kCorArray]

    title = "k_%s%s at z = %s" % (restFrameFilter, ffilter, redshift)

    if plot:
        fileName = dp.plot_polynomial(
                        log,
                        title=title,
                        polynomialDict=polyDict,
                        orginalDataDictionary=dataDict,
                        pathToOutputPlotsFolder=dataDir+"/",
                        xRange=[xMin, xMax],
                        xAxisLimits=False,
                        yAxisLimits=False,
                        yAxisInvert=False,
                        prependNum=False)

        # mdLog.write("""![%s_plot]\n\n[%s_plot]: %s\n\n""" % (title.replace(" ", "_"), title.replace(" ", "_"), fileName,))

    newFileName = dataDir + "/z"+str(strRed).replace(".", "pt")+"_poly.yaml"
    stream = file(newFileName, 'w')
    yamlContent = {'polyCoeffs' : flatPoly.coeffs}
    #log.debug('flatPoly.coeffs %s' % (flatPoly.coeffs,))
    yaml.dump(yamlContent, stream, default_flow_style=True)
    stream.close()

    return


## LAST MODIFIED : March 25, 2013
## CREATED : March 25, 2013
## AUTHOR : DRYX
def generate_kcorrection_polynomial_database(
        log,
        restFrameFilter,
        pathToOutputDirectory,
        kCorPolyOrder=3,
        kCorMinimumDataPoints=3,
        redshiftResolution=0.1,
        redshiftLower=0.0,
        redshiftUpper=1.0,
        plot=False):
    """Generate the Kg* k-correction polynoimal for a range of redshifts given a list of spectra

    **Key Arguments:**
        - ``log`` -- logger
        - ``restFrameFilter`` -- the observed frame filter with which to calculate k-crrections with
        - ``pathToOutputDirectory`` -- path to the output directory (provided by the user)
        - ``kCorPolyOrder`` -- the order of the polynomials to fit
        - ``kCorMinimumDataPoints`` -- Minimum number of datapoints used to generate k-correction curve
        - ``redshiftResolution`` -- resolution of the k-correction database (at what redshift points do you want the k-corrections calculated)
        - ``redshiftLower`` -- lower redshift in range of k-corrections to be calculated
        - ``redshiftUpper`` -- upper redshift in range of k-corrections to be calculated
        - ``plot`` -- plot the polynomial?

    **Return:**
        - None
    """
    ################ > IMPORTS ################
    ## STANDARD LIB ##
    import re
    import os
    ## THIRD PARTY ##
    import pysynphot as syn
    import yaml
    ## LOCAL APPLICATION ##

    mul = 1000
    div = 1000.

    fileName = pathToOutputDirectory + "transient_light_curves.yaml"
    stream = file(fileName, 'r')
    generatedLCs = yaml.load(stream)
    models = generatedLCs.keys()
    filters = ['g', 'r', 'i', 'z']
    # models = ["he130",]
    for model in models:

        for redshift in range(int(redshiftLower*mul), int(redshiftUpper*mul), int(redshiftResolution*mul)):
            redshift = redshift/div

            for ffilter in filters:
                generate_single_kcorrection_polynomial(
                    log,
                    model=model,
                    pathToOutputDirectory=pathToOutputDirectory,
                    redshift=redshift,
                    ffilter=ffilter,
                    restFrameFilter=restFrameFilter,
                    kCorPolyOrder=kCorPolyOrder,
                    kCorMinimumDataPoints=kCorMinimumDataPoints,
                    plot=plot)

    return



###################################################################
# PRIVATE (HELPER) FUNCTIONS                                      #
###################################################################

if __name__ == '__main__':
    main()


###################################################################
# TEMPLATE FUNCTIONS                                              #
###################################################################
