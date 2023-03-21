import sys
from lib.Apps import init,MainMenu

############ Program Start here ############
if __name__ == '__main__':
    if init() != False:
        MainMenu()
    else:
        sys.exit()
