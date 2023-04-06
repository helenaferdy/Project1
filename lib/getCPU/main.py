from lib.helenalibs.main import helenamain
import os

OUTPUT_PATH = "out/getCPU/"
LOG_PATH = "log/getCPU.log"
COMMAND = "show processes cpu"


def getCPUUtils(testbed):
    helenamain(COMMAND, OUTPUT_PATH, LOG_PATH)