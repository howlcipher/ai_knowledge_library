import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tools.library_statistics as ls
import tools.clean_backups as cb

def test_library_statistics():
    assert hasattr(ls, 'main')

def test_clean_backups():
    assert hasattr(cb, 'main')
