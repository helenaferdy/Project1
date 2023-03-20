# from lib.config.createTestbed import File,generateDeviceList
import sys
import pandas as pd
from lib.apps import init,MainMenu

############ Program Start here ############
if __name__ == '__main__':
    if init() != False:
        MainMenu()
    else:
        sys.exit()
