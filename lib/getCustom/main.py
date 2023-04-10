from lib.helenalibs.main import helenacustom
import os

OUTPUT_PATH = "out/getCustom/"
LOG_PATH = "log/getCustom.log"


def getCustom(testbed):
    helenacustom(OUTPUT_PATH, LOG_PATH)