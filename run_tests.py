#!/usr/bin/env python3
"""
Run Minipar Compiler Tests
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

from test_compilerok import main

if __name__ == '__main__':
    main()
