"""
10 Arquétipos Emocionais - SignalCut Hybrid
"""

ARCHETYPES = {
    "curiosidade": {
        "id": "curiosidade",
        "nome": "Curiosidade",
        "emoção": "Omissão de informação",
        "peso": 0.30,
        "gancho_template": [
            "Você não vai acreditar no que descobri sobre {tema}",
            "O segredo de {tema} que mudou minha vida"
        ],
        "cores": ["#FFD700", "#FF6B6B"],
        "emoji": "⚠️"
    },
    "medo": {
        "id": "medo", 
        "nome": "Medo/Urgência",
        "emoção": "Perda iminente",
        "peso": 0.28,
        "gancho_template": [
            "Se você não souber isso, {consequência}",
            "Alerta: {tema} pode destruir seus resultados"
        ],
        "cores": ["#FF0000", "#000000"],
        "emoji": "⏰"
    },
    "transformacao": {
        "id": "transformacao",
        "nome": "Transformação", 
        "emoção": "Superação",
        "peso": 0.25,
        "gancho_template": [
            "De {estado_negativo} para {estado_positivo}",
            "Minha transformação com {tema}"
        ],
        "cores": ["#FF69B4", "#00FF7F"],
        "emoji": "🦋"
    }
}

def get_archetype(archetype_id: str):
    return ARCHETYPES.get(archetype_id, ARCHETYPES["curiosidade"])
