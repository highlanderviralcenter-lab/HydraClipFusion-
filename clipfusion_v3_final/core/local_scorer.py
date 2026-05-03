"""Score local por palavras-chave dos arquétipos — roda sem IA externa."""
import re

KEYWORDS = {
    "curiosidade":   ["segredo","descobri","nao vai acreditar","surpreendente","revelacao","escondido","verdade sobre"],
    "medo":          ["alerta","cuidado","perigo","erro","evite","nunca","destruir","pior","urgente","falha"],
    "transformacao": ["mudou","antes e depois","transformacao","virei","consegui","do zero","resultado"],
    "controversia":  ["polemico","discordo","errado","mentira","mito","fake","ninguem fala"],
    "utilidade":     ["como fazer","passo a passo","tutorial","dica","aprenda","facil","rapido","gratis"],
    "emocao":        ["chorei","emocional","incrivel","impressionante","nunca vi","melhor","inacreditavel"],
}

HIGH_IMPACT = {"segredo","alerta","nunca","transformacao","inacreditavel","urgente","revelacao"}


def score_text(text: str) -> dict:
    """Retorna dict com score 0-10 e arquétipo dominante."""
    t = re.sub(r'[^\w\s]', ' ', text.lower())
    hits = {}
    for arch, kws in KEYWORDS.items():
        count = 0
        for kw in kws:
            if kw in t:
                mult = 2 if any(w in HIGH_IMPACT for w in kw.split()) else 1
                count += mult
        if count:
            hits[arch] = count
    total = sum(hits.values())
    raw   = min(total / 5.0 * 10, 10.0)
    n_words = max(len(t.split()), 1)
    bonus = min(total / n_words * 20, 1.5)
    final = min(round(raw + bonus, 2), 10.0)
    dominant = max(hits, key=hits.get) if hits else "neutro"
    return {"score": final, "archetype": dominant, "hits": hits}
