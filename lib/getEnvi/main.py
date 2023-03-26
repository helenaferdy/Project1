from lib.helenalibs.main import helenamain
import os

OUTPUT_PATH = "out/getEnvi/"
COMMAND = "show environment"

def getEnvi(testbed):
    helenamain(COMMAND, OUTPUT_PATH)