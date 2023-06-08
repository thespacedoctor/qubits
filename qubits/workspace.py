#!/usr/local/bin/python
# encoding: utf-8
"""
*Tools to help setup an initial qubits workspace that can be tested and then tailored by the user*

:Author:
    David Young

:Date Created:
    September  5, 2017
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools
from os.path import expanduser
import shutil
import codecs


class workspace():
    """
    *Tools to help setup an initial qubits workspace that can be tested and then tailored by the user*

    **Key Arguments:**
        - ``log`` -- logger
        - ``pathToWorkspace`` -- path to the directory to setup the initial workspace within. Default *current working directory*.

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

        To initiate a qubits workspace, use the following:

        .. code-block:: python 

            from qubits import workspace
            ws = workspace(
                log=log,
                pathToWorkspace="~/Desktop/qubits_workspace"
            )
            ws.setup()
    """
    # Initialisation

    def __init__(
            self,
            log,
            pathToWorkspace
    ):
        self.log = log
        log.debug("instansiating a new 'workspace' object")
        self.pathToWorkspace = pathToWorkspace

        # MAKE PATH ABSOLUTE
        self.home = expanduser("~")
        if self.pathToWorkspace[0] == "~":
            self.pathToWorkspace[0] = self.home

        return None

    def setup(self):
        """
        *setup the workspace in the requested location*

        **Return:**
            - ``None``
        """
        self.log.debug('starting the ``setup`` method')

        # RECURSIVELY CREATE MISSING DIRECTORIES
        if not os.path.exists(self.pathToWorkspace):
            os.makedirs(self.pathToWorkspace)
        if not os.path.exists(self.pathToWorkspace + "/qubits_output"):
            os.makedirs(self.pathToWorkspace + "/qubits_output")

        # FIND RESOURCES
        spectralDB = os.path.dirname(
            __file__) + "/resources/qubits_spectral_database"
        qubitsSettings = os.path.dirname(
            __file__) + "/resources/qubits_settings.yaml"
        dstSettings = self.pathToWorkspace + "/qubits_settings.yaml"

        # CHECK FOR PRE-EXISTANCE
        if os.path.exists(self.pathToWorkspace + "/qubits_spectral_database") or os.path.exists(dstSettings):
            self.log.warning(
                "A qubits workspace seems to already exist in this location")
            sys.exit(0)

        # COPY ASSETS TO REQUESTED LOCATION
        shutil.copytree(spectralDB, self.pathToWorkspace +
                        "/qubits_spectral_database")
        shutil.copyfile(qubitsSettings, dstSettings)

        # ADD USER'S HOME FOLDER INTO SETTINGS
        pathToReadFile = dstSettings
        try:
            self.log.debug("attempting to open the file %s" %
                           (pathToReadFile,))
            readFile = codecs.open(pathToReadFile, encoding='utf-8', mode='r')
            thisData = readFile.read()
            readFile.close()
        except IOError, e:
            message = 'could not open the file %s' % (pathToReadFile,)
            self.log.critical(message)
            raise IOError(message)

        readFile.close()
        thisData = thisData.replace("/Users/XXXX", self.home)
        try:
            self.log.debug("attempting to open the file %s" %
                           (pathToReadFile,))
            writeFile = codecs.open(pathToReadFile, encoding='utf-8', mode='w')
        except IOError, e:
            message = 'could not open the file %s' % (pathToReadFile,)
            self.log.critical(message)
            raise IOError(message)
        writeFile.write(thisData)
        writeFile.close()

        self.log.debug('completed the ``setup`` method')
        return None

    # xt-class-method
