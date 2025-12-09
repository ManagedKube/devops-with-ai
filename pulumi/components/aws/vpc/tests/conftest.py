import pytest
import sys
import os

# Add the parent directory to the Python path so tests can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
