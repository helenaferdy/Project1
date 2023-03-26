from lib.helenalibs.main import helenamain
import os

OUTPUT_PATH = "out/getCPU/"
COMMAND = "show processes cpu"


def getCPUUtils(testbed):
    helenamain(COMMAND, OUTPUT_PATH)