from lib.helenalibs.main import helenamain
import os

OUTPUT_PATH = "out/getInven/"
LOG_PATH = "log/getInventory.log"
COMMAND = "show inventory"



def getInven(testbed):
    helenamain(COMMAND, OUTPUT_PATH, LOG_PATH)