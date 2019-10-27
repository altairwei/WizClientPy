import os
import platform
from pathlib import Path

# Setup the home directory of WizQTClient database
WIZNOTE_HOME_DIR = os.getenv('WIZNOTE_HOME_DIR', str(Path.home()))
if platform.system() == "Windows":
    WIZNOTE_HOME = str(Path(WIZNOTE_HOME_DIR).joinpath("WizNote"))
elif platform.system() == "Darwin":
    WIZNOTE_HOME = str(Path(WIZNOTE_HOME_DIR).joinpath(".wiznote"))
elif platform.system() == "Linux":
    WIZNOTE_HOME = str(Path(WIZNOTE_HOME_DIR).joinpath(".wiznote"))

# use 10 minutes locally, server use 20 minutes
TOKEN_TIMEOUT_INTERVAL = 600
