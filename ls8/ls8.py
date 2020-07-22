#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

if len(sys.argv) < 2:
    sys.exit("ERROR: No CL Input")

cpu = CPU()

cpu.load(sys.argv[1])
cpu.run()
