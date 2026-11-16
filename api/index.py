import os
import sys

# Ensure root directory is on the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

# Vercel Serverless Function entry point
# 'app' is the Flask WSGI instance
