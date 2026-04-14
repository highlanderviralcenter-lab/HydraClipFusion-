#!/usr/bin/env python3
from __future__ import annotations

def segment_by_pauses(base_segments, min_duration=18.0, max_duration=35.0, pause_threshold=0.5):
    if not base_segments:
        return []

    grouped = []
    current = {
        "start": float(base_segments[0].get("start", 0.0)),
        "end": float(base_segments[0].get("end", 0.0)),
        "text": (base_segments[0].get("text", "") or "").strip(),
    }

    for seg in base_segments[1:]:
        seg_start = float(seg.get("start", current["end"]))
        seg_end = float(seg.get("end", seg_start))
        seg_text = (seg.get("text", "") or "").strip()

        current_duration = current["end"] - current["start"]
        gap = seg_start - current["end"]
        proposed_duration = seg_end - current["start"]

        should_close = False
        if current_duration >= min_duration and gap >= pause_threshold:
            should_close = True
        if proposed_duration > max_duration:
            should_close = True

        if should_close:
            grouped.append(current)
            current = {
                "start": seg_start,
                "end": seg_end,
                "text": seg_text,
            }
        else:
            current["end"] = seg_end
            if seg_text:
                current["text"] = (current["text"] + " " + seg_text).strip()

    grouped.append(current)

    normalized = []
    for item in grouped:
        dur = item["end"] - item["start"]
        if dur < min_duration and normalized:
            normalized[-1]["end"] = item["end"]
            normalized[-1]["text"] = (normalized[-1]["text"] + " " + item["text"]).strip()
        else:
            normalized.append(item)

    return normalized
