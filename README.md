

# Queen's University Belfast Imitation Transient Surveys (QUBITS)

[![](https://zenodo.org/badge/12975788.svg)](https://zenodo.org/badge/latestdoi/12975788) 



## Abstract:

QUBITS is a python package and command-line tool used to simulate various flavours of astronomical transient surveys. The simulations are designed to be easy to use and tailor without having to hack any code, and many of the simulation parameters can be found in one settings file.

Although recoded from scratch, the [second chapter of my thesis](qubits/assets/dry_thesis_ch2.pdf) describes most of the details used to build these transient survey simulations.

## Installation and Setting Up Your Environment

QUBITS relies heavily on [`pysynphot`](http://pysynphot.readthedocs.io/en/latest/index.html) which no longer supports a PyPI distribution. Therefore the easiest way to get QUBITS running is to install [Anaconda](https://docs.continuum.io/anaconda/install/) and then use the [STScI's AstroConda channel to install their Standard Software Stack](https://astroconda.readthedocs.io/en/latest/installation.html#configure-conda-to-use-the-astroconda-channel) (which includes pysynphot). Once this stack is installed, create/activate a conda environment that includes the stack and run:

    pip install qubits

This should install the QUBITS code and all of its dependencies. If this doesn't work, or you want to tinker with the code by installing QUBITS as a development package, then clone the project using this command:

    git clone git@github.com:thespacedoctor/qubits.git <folder_name>

and then `cd <folder_name>` and:

    python setup.py install

or

    python setup.py develop

### `PYSYN_CDBS` The STScI Calibration Reference Data System

Note that the data files required by *pysynphot*, and hence QUBITS, are distributed separately by [STScI Calibration Reference Data System](http://www.stsci.edu/hst/observatory/crds/throughput.html). Before starting you will need to download of the calibration data from the FTP area linked from the [STScI webpage](http://www.stsci.edu/hst/observatory/crds/throughput.html), unpack them somewhere appropriate and organise them into a single nested folder structure like so:

![PYSYN_CDBS][pysyn_cdbs 36852357776]

[PYSYN_CDBS 36852357776]: https://farm5.staticflickr.com/4374/36852357776_03eeaaf8a2_o.png

Finally, you need to make sure the `PYSYN_CDBS` environment variable is set so *pysynphot* knows where these data live. Add the following to your `.bashrc` file and don't forget to open a new terminal window before you begin to use QUBITS:

```bash
export PYSYN_CDBS=/path/to/cdbs/
```

I haven't tested this on many other machines so let me know what goes wrong with the installation!

## Usage

    Usage:
        qubits init <pathToWorkspace>
        qubits run -s <pathToSettingsFile> -o <pathToOutputDirectory> -d <pathToSpectralDatabase>

        COMMANDS
        --------
        init            setup a qubits settings file and a test spectral database

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

## Quick Start

If you're using QUBITS for the first time, or have not used it in a while, the best way to start is to use the `qubits init` command to generate a template workspace for yourself. Running the command:

```bash
qubits init ~/Desktop/qubits_workspace
```

creates a template workspace on your desktop with:

1.  a template spectral database `qubits_spectral_database`,
2.  a default qubits settings file `qubits_settings.yaml`,
3.  an empty output directory `qubits_output`

![qubits template workspace][qubits template workspace 36868827172]

[qubits template workspace 36868827172]: https://farm5.staticflickr.com/4403/36868827172_3eaec29a82_o.png

Once you familiarise yourself with running QUBITS you can move this workspace elsewhere and tailor the spectral database and settings file to your needs.

### Building a Spectral Database

Within the folder you choose to place your spectral database, create appropriately named folders for each of the specific transient objects you would like to include in the simulations. Note these are the names to be included in the settings file (see below) and that will appear in results files, plots and logs. Your database might look like this:

    qubits_spectral_database/
        SNIa/
            t-021.00.spec
            t-012.00.spec
            t+003.00.spec
            t+015.00.spec
            t+024.00.spec
            t+068.00.spec
            t+098.00.spec
            t+134.00.spec
        SNIIp/
            ...
        SLSN/
            ...

Name your spectral files with times relative to some epoch within the transient's evolution (e.g. peak magnitude or explosion date). QUBITS will determine the time of peak magnitude when generating the lightcurves from the spectra and recalibrate the time scale relative to this point. The files should contain two space separated columns containing wavelength (Å) and flux (ergs/s/cm^2/Å). Have a look in the template database supplied by the `qubits init` command.

### Settings File

A template simulation settings file is provided by the `qubits init` command and should look something like this:

    version: 1

    ##### PROGRAM EXECUTION SETTINGS #####
    Program Settings:
        # STAGE 1 - LIGHTCURVES
        Extract Lightcurves from Spectra: True
        # STAGE 2 - KCORRECTION DATABASE
        Generate KCorrection Database: True
        Generate KCorrection Plots: True  # ONLY SET TO TRUE IF ONLY A FEW KCORRECTIONS ARE TO BE CALCULATED
        # STAGE 3 - RUNNING SIMULATION
        Run the Simulation: True
        Plot Simulation Helper Plots: True  #  ONLY PLOT IF DEBUGGING
        # STAGE 4 - COMPILING RESULTS
        Compile and Plot Results: True
        Simulation Results File Used for Plots: simulation_results_20130919t131758.yaml

    ###### SIMULATED SURVEY CONSTRAINTS ######
    Extra Survey Constraints:
        Faint-Limit of Peak Magnitude: 21.50 # The lower-limit of the apparent peak magnitude so that the transient can be distinguished from other flavours of transients. Set this to 99.9 for this setting to be disregarded.
        Observable for at least ? number of days: 100 # Set this to 1 for this setting to be distregarded
    Lower Redshift Limit: 0.00 ## Usually set to 0.0
    Upper Redshift Limit: 1.0
    Redshift Resolution: 0.05 ## Higher resolution (lower number) means the simulations are more accuate but the code shall take long to run, especially for the k-correction database generation.
    Sky Area of the Survey (square degrees): 70
    Limiting Magnitudes:
        g : 23.3
        r : 23.3
        i : 23.3
        z : 21.7
    Survey Cadence:
        # YEAR MINUS FRACTION LOST DUE TO OBJECTS BEING LOCATED BEHIND THE SUN
        Observable Fraction of Year: 0.5
        Fraction of Year Lost to Weather etc: 0.4
        Filters:
            - band: g
              day of year of first scheduled observation: 1
              repeat every ? days: 3
              Fraction of Lunar Month Lost to Moon: 0.27
            - band: r
              day of year of first scheduled observation: 1
              repeat every ? days: 3
              Fraction of Lunar Month Lost to Moon: 0.27
            - band: i
              day of year of first scheduled observation: 2
              repeat every ? days: 3
              Fraction of Lunar Month Lost to Moon: 0.27
            - band: z
              day of year of first scheduled observation: 3
              repeat every ? days: 3
              Fraction of Lunar Month Lost to Moon: 0.27

    ###### K-CORRECTION GENERATION ######
    Rest Frame Filter for K-corrections: g # This is the filter that the k-corrections are anchored to. The simulations will convert from this observed band magnitude to the rest frame magnitudes to calculate the k-correction.
    K-correction temporal resolution (days): 1.0 # Only increase the resolution here if you have many spectra in your database and k-corrections are taking too long to generate.
    Order of polynomial used to fits k-corrections: 18 # Check the k-correction polynomial plots and tweak this value as needed.
    Minimum number of datapoints used to generate k-correction curve: 3 # If the are not enough spectra or too many spectra have been redshifted out of the range of the observed frame band-pass, then there are few points to generate a polynomial k-correction lightcurve. 3 is probably the barely-passable minimum.

    ###### SIMULATED UNIVERSE CONSTRAINTS ######
    CCSN Progenitor Population Fraction of IMF: 0.007
    Transient to CCSN Ratio: 10e-5
    Simulation Sample: 50 # Number of transients to include in simulations. More = more accurate but sims take longer to run. 100 good for testing & 10,000 good for science.
    Extinctions:
        constant or random: constant # Parameter not yet implemented - leave as `constant`
        constant E(b-v): 0.023 # 0.023 is the mean for the PS1-MD fields
        host: # Parameter not yet implemented
        galactic: # Parameter not yet implemented
    Relative Rate Set to Use: SLSNe
    Relative SN Rates:
        SLSNe:
            SN2007bi: 0.5 # make sure transient names correspond to folder names containing thier spectral data-sets
            SLSN: 0.5
    SN Absolute Peak-Magnitude Distributions:
        magnitude:
            SN2007bi: -17.08
            SLSN: -20.21
        sigma:
            SN2007bi: 0.001
            SLSN: 0.001

    ###### LIGHTCURVE GENERATION & CONSTRAINTS
    Lightcurves:
        SN2007bi:
            End of lightcurve relative to peak: 300 # Constrain the end of the lightcurve so polynomial fits don't go awal
        SLSN:
            End of lightcurve relative to peak: 220
    Order of polynomial used to fits lightcurves: 6 # Check the extracted lightcurve plots and tweak this value as needed.
    # Often it is useful to set a an explosion day (relative to the timescale used in naming the files in the spectral database).
    # This helps constrain the polynomials of the light- and K-correction- curves generated in the simulations.
    # SET TO `None` TO DISREGARD THIS SETTING
    Explosion Days:
        SLSN: -70
        SN2007bi: -70
    # You can also extend the tail of the lightcurve to better constrain the polynomial. Set to `True` or `False`
    Extend lightcurve tail?:
        SLSN: True
        SN2007bi: True

    ###### LOGGING
    Level of logging required: WARNING # DEBUG, INFO, WARNING, ERROR or CRITICAL

## The QUBITS Simulation Stages

The four stages of the simulation are:

1.  Extracting the Lightcurves from Spectra
2.  Generating a K-Correction Database
3.  Running the Simulation, and
4.  Compiling and Plotting Results

At the top of this settings file you turn the various stages of the simulation build on and off:

    Program Settings:
            # STAGE 1 - LIGHTCURVES
            Extract Lightcurves from Spectra: True
            # STAGE 2 - KCORRECTION DATABASE
            Generate KCorrection Database: True
            Generate KCorrection Plots: True  # ONLY SET TO TRUE IF ONLY A FEW KCORRECTIONS ARE TO BE CALCULATED
            # STAGE 3 - RUNNING SIMULATION
            Run the Simulation: True
            Plot Simulation Helper Plots: True  #  ONLY PLOT IF DEBUGGING
            # STAGE 4 - COMPILING RESULTS
            Compile and Plot Results: True
            Simulation Results File Used for Plots: simulation_results_20130919t131758.yaml

When you first use the simulations it's best to set all stages of the simulation to *False*, then incrementally run the code through each stage. You will always run the code with the `qubits run` command with the following syntax:

```bash
qubits run -s <pathToSettingsFile> -o <pathToOutputDirectory> -d <pathToSpectralDatabase>
```

So to run QUBITS with our template workspace we setup in the quick start workspace above, we run:

```bash
qubits run -s ~/Desktop/qubits_workspace/qubits_settings.yaml -o ~/Desktop/qubits_workspace/qubits_output -d ~/Desktop/qubits_workspace/qubits_spectral_database
```

Below you will find details of each build stage of the simulation - read the settings file comments to determine which settings you need to tailor for the simulation you are trying to run.

### 1. Extracting the Lightcurves from Spectra

This stage generates the `z=0` lightcurves. Lightcurve plots are created in the *plots* folder in the output directory. Please note QUBITS' ability to generate decent lightcurves relies heavily on the quality of your spectral database; it needs good wavelength coverage to be able to synthesize the photometry and good temporal coverage to build an entire lightcurve. The extracted lightcurves are stored as python objects in the a file called *transient_light_curves.yaml* in `<pathToOutputDirectory>`.

Once you've generated the lightcurves, have a look at the lightcurve plots (some may be blank if temporal/wavelength coverage was deemed too poor to create a lightcurve for the given band-pass at `z=0`). You may want to tweak some lightcurve parameters in the settings file and rebuild the lightcurve plots. Once you're happy move onto the next stage.

![example lightcurve](qubits/assets/SNOne_-_i-band.png)

Current filters are the PS1 *g*, *r*, *i*, *z* filters.

Note *pysynphot* can be very chatty and prints log messages straight to stdout which can't be turned off easily. Don't worry if you see something like this:

> ... does not have a defined binset in the wavecat table. The waveset of the spectrum will be used instead.

### 2. Generate K-Correction Database

The code will use the spectra to generate a database of K-corrections with the given settings. They will be created in the `k_corrections` directory of your output folder. For each redshift and k-correction filter-set, a dataset is generated which is used to create a polynomial for *rest frame epoch* vs *kcorrection*. Note the k-corrections also act as colour-transformations between filters at low-redshift.

By setting `Generate K-Correction Plots` to `True` a plot for each K-correction dataset will be generated. Set this to true if only a few k-corrections are to be calculated, i.e. when you are testing/debugging the simulation - otherwise the k-correction generation will take forever!

![example k-correction polynomial](qubits/assets/k_ir_at_z_=_0.3.png)

### 3. Run the Simulation

Here the simulation is run using the settings found in the settings file (cadence of observation, limiting-magnitudes, survey volume, loss due to weather etc). This stage is a two part process:

1.  **Simulating the Universe** - placing SNe throughout the volume requested at random redshifts, with the relative-rate supplied and with the peak magnitude distributions given.
2.  **Simulating the Survey** - simulates the survey with the setup supplied in the settings files with cadence of observation, limiting-magnitudes, survey volume, loss due to weather etc.

The results of the simulation are place in a (large) date-time stamped yaml file in the output folder named something similar to `simulation_results_20130425t053500.yaml`. The date-time appended to the filename will be the time the simulation was run so you can run many simulations without worrying about overwriting previous outputs. The settings used to run the simulation are also recorded in this file.

The `Plot Simulation Helper Plots` setting should only be set to *True* if you are trying to debug the code and work out how the input data is being manipulated to create the simulations.

### 4. Compile and Plot Results

Use the `Simulation Results File Used for Plots` setting to set the simulation results file used to generate the result plots and log:

    Simulation Results File Used for Plots: simulation_results_20130425t053500.yaml

This compiles the results into a markdown file (plain text with minimal markup) and a styled HTML file into the `<pathToOutputDirectory>/results` folder with names similar to:

    simulation_result_log_20130426t110856.md
    simulation_result_log_20130426t110856.html

Here is an example of the output log file:

![example results file](qubits/assets/example_results.png)

[^cdbs]: http://www.stsci.edu/institute/software_hardware/stsdas/synphot

## WARNINGS

QUBITS can return many warnings, usually related the limitations of your spectral databases. Here are some:

-   **'does not have a defined binset in the wavecat table. The waveset of the spectrum will be used instead.'**: This is a pysynphot message and not a QUBITS log. Don't worry.
-   **' failed with this error: Spectrum and bandpass are disjoint'**: This generally means the spectrum quoted doesn't cover the wavelength range of the band-pass and therefore a magnitude can't be synthesised.
-   **'Spectrum and bandpass do not fully overlap. You may use force=[extrap|taper] to force this Observation anyway.'**: As above but the spectral wavelength range does partially cover the band-pass
-   **'could not find the magnitude from spectrum /\*\*\*/t+601.00.spec using the filter sdss,g - failed with this error: Integrated flux is <= 0'**: This generally means the spectrum quoted doesn't entirely cover the wavelength range of the band-pass and therefore a magnitude can't be synthesised.
-   **'the k-correction file z0pt30.yaml contains less than 3 datapoints to convert from g restframe to z observed frame for the SNOne model - polynomial shall not be generated'**: The was not enough temporal/wavelength coverage to generate k-corrections for the quoted rest/observed frame filter-set at this redshift

## Issues

Please report any issues [here](https://github.com/thespacedoctor/qubits/issues).

[Pull requests](https://github.com/thespacedoctor/qubits/pulls) are welcomed!

## License

Copyright (c) 2018 David Young

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


## How to cite qubits

If you use `qubits` in your work, please cite using the following BibTeX entry: 

```bibtex
@software{Young_qubits,
    author = {Young, David R.},
    doi = {10.5281/zenodo.8037739},
    license = {GPL-3.0-only},
    title = {{qubits}},
    url = {https://github.com/thespacedoctor/qubits}
}
```
 
