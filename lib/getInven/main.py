from lib.helenalibs.main import helenamain
import os

OUTPUT_PATH = "out/getInven/"
COMMAND = "show inventory"



def getInven(testbed):
    helenamain(COMMAND, OUTPUT_PATH)