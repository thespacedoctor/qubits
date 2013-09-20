import os
import nose
from qubits import command_line as cl

## SETUP AND TEARDOWN FIXTURE FUNCTIONS FOR THE ENTIRE MODULE
def setUpModule():
    "set up test fixtures"
    moduleDirectory = os.path.dirname(__file__) + "/../tests"

    # SETUP PATHS TO COMMONG DIRECTORIES FOR TEST DATA
    global pathToOutputDir, pathToInputDir
    pathToInputDir = moduleDirectory+"/input/"
    pathToOutputDir = moduleDirectory+"/output/"

    # SETUP THE TEST LOG FILE
    global testlog
    testlog = open(pathToOutputDir + "tests.log", 'w')

    return None

def tearDownModule():
    "tear down test fixtures"
    # CLOSE THE TEST LOG FILE
    testlog.close()
    return None

class emptyLogger:
    info=None
    error=None
    debug=None
    critical=None
    warning=None


class TestCommandLine():
    def test_command_line_works_as_expected(self):
        clArgs = {}
        clArgs["<pathToOutputDirectory>"] = pathToOutputDir
        clArgs["<pathToSettingsFile>"] = pathToInputDir + "qubits_settings.yaml"
        clArgs["<pathToSpectralDatabase>"] = pathToInputDir + "test_spectral_database"
        cl.qubits(clArgs)
