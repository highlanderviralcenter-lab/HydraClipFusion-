"""
Motor de geração de ganchos
"""

from .archetypes import get_archetype
from .audience_analyzer import AudienceAnalyzer

class ViralHookEngine:
    def __init__(self):
        self.analyzer = AudienceAnalyzer()

    def generate(self, tema: str, nicho: str, platform: str, archetype_id: str = None):
        audience = self.analyzer.analyze(nicho, platform)
        archetype = get_archetype(archetype_id or "curiosidade")

        template = archetype["gancho_template"][0]
        hook = template.format(tema=tema, estado_negativo="fracasso", estado_positivo="sucesso")

        return {
            "gancho_final": f"{archetype['emoji']} {hook}",
            "archetype": archetype,
            "hashtags": audience["hashtags_sugeridas"]
        }
