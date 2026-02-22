import sys
import os

# Make the project root importable so `scrapers.*` resolves without Django setup
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
