"""
Segmentação por pausas naturais - SignalCut
Janela de ouro: 18-35 segundos
"""

def segment_by_pauses(segments, min_duration=18, max_duration=35, pause_threshold=0.5):
    """
    Segmenta vídeo baseado em pausas naturais (VAD).
    Força quebra se: pausa > 0.5s OU duração > 35s
    Só aprova se: duração >= 18s
    """
    candidates = []
    current_start = None
    current_end = None
    current_text = []
    last_end = 0

    for seg in segments:
        if current_start is None:
            current_start = seg['start']
            current_end = seg['end']
            current_text = [seg['text']]
            last_end = seg['end']
            continue

        gap = seg['start'] - last_end

        # Força quebra se pausa grande ou excedeu duração máxima
        if gap > pause_threshold or (seg['end'] - current_start) > max_duration:
            dur = current_end - current_start
            if dur >= min_duration:
                candidates.append({
                    'start': current_start,
                    'end': current_end,
                    'text': ' '.join(current_text),
                    'duration': dur,
                    'word_count': len(' '.join(current_text).split())
                })
            current_start = seg['start']
            current_end = seg['end']
            current_text = [seg['text']]
        else:
            current_end = seg['end']
            current_text.append(seg['text'])

        last_end = seg['end']

    # Último segmento
    if current_start and (current_end - current_start) >= min_duration:
        candidates.append({
            'start': current_start,
            'end': current_end,
            'text': ' '.join(current_text),
            'duration': current_end - current_start,
            'word_count': len(' '.join(current_text).split())
        })

    return candidates
