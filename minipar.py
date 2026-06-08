"""
Minipar Compiler - Main Entry Point
Simple wrapper for backward compatibility
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from compiler import main

if __name__ == '__main__':
    main()
