#!/usr/bin/env/python
# -*- encoding: utf-8 -*-

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
#print(sys.path)
from main.__main__ import main
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))