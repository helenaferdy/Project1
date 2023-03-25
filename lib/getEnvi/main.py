from lib.helenalibs.main import helenamain
import os

OUTPUT_PATH = "out/getEnvi/"
COMMAND = "show environment"

if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

def getEnvi(testbed):
    helenamain(COMMAND, OUTPUT_PATH)