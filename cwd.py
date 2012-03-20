"""
Adds the current working directory's parent to the system paths,
allowing the current directory to be imported as a python module.

"""

import os
import sys

root_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(root_dir)
sys.path.append(parent_dir)
