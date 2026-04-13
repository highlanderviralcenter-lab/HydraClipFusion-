"""
ClipFusion Viral Engine v3.0
Motor de viralização com 10 arquétipos emocionais
"""

from .hook_engine import ViralHookEngine
from .archetypes import ARCHETYPES, get_archetype
from .audience_analyzer import AudienceAnalyzer
from .platform_optimizer import PlatformOptimizer

__all__ = [
    "ViralHookEngine",
    "ARCHETYPES",
    "get_archetype",
    "AudienceAnalyzer", 
    "PlatformOptimizer"
]
