from lib.helenalibs.main import helenamain
import os

OUTPUT_PATH = "out/getEnvi/"
LOG_PATH = "log/getEnvironment.log"
COMMAND = "show environment"

def getEnvi(testbed):
    helenamain(COMMAND, OUTPUT_PATH, LOG_PATH)