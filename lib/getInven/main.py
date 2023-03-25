from lib.helenalibs.main import helenamain
import os

OUTPUT_PATH = "out/getInven/"
COMMAND = "show inventory"

if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

def getInven(testbed):
    helenamain(COMMAND, OUTPUT_PATH)