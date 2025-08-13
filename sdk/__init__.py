"""
M2ARM Python SDK

A comprehensive toolkit for migrating and modernizing applications
from x86 to ARM architecture while maintaining cross-platform compatibility.
"""

__version__ = "0.1.0"
__author__ = "M2ARM Team"
__email__ = "team@m2arm.dev"

from .core import M2ARMCore
from .scanner import CodeScanner
from .migrator import Migrator
from .compiler import CrossCompiler
from .tester import ARMTester
from .optimizer import PerformanceOptimizer

__all__ = [
    "M2ARMCore",
    "CodeScanner", 
    "Migrator",
    "CrossCompiler",
    "ARMTester",
    "PerformanceOptimizer"
]
