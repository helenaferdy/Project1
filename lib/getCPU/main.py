from lib.helenalibs.main import helenamain
import os

OUTPUT_PATH = "out/getCPU/"
COMMAND = "show processes cpu"

if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

def getCPUUtils(testbed):
    helenamain(COMMAND, OUTPUT_PATH)