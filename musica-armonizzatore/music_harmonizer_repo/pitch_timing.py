"""Map equal-tempered pitch intervals to tempo and rhythmic timing."""

import math
from numbers import Real
from typing import TypedDict


class PitchTimingResult(TypedDict):
    nota_midi: int
    semitoni_offset: float
    frequenza_hz: float
    bpm: float
    suddivisioni_ms: dict[str, float]
    offset_singolo_ms: float
    deriva_totale_ms: float


_SUBDIVISION_DIVISORS = {
    "1/4": 1.0,
    "1/8.": 4.0 / 3.0,
    "1/8": 2.0,
    "1/8T": 3.0,
    "1/16": 4.0,
    "1/32": 8.0,
}


def _positive_finite(value: Real, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} deve essere un numero reale positivo")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} deve essere un numero reale positivo e finito") from exc
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} deve essere un numero reale positivo")
    return result


def calculate_pitch_timing(
    semitones_offset: Real | None = None,
    *,
    midi_note: int | None = None,
    ref_hz: Real = 440.0,
    ref_bpm: Real = 100.3,
    beats_without_realign: int = 1,
) -> PitchTimingResult:
    """Return frequency, tempo, subdivisions, and drift for a MIDI pitch.

    Provide either a semitone offset from A4 (MIDI 69) or an absolute MIDI
    note. ``beats_without_realign`` controls how many master beats accumulate
    the single-beat timing offset.
    """
    if (semitones_offset is None) == (midi_note is None):
        raise ValueError("Specificare un solo valore tra semitones_offset e midi_note")

    if midi_note is not None:
        if isinstance(midi_note, bool) or not isinstance(midi_note, int):
            raise ValueError("midi_note deve essere un numero MIDI intero")
        if not 0 <= midi_note <= 127:
            raise ValueError("midi_note deve essere compreso tra 0 e 127")
        offset = float(midi_note - 69)
    else:
        if isinstance(semitones_offset, bool) or not isinstance(semitones_offset, Real):
            raise ValueError("semitones_offset deve essere un numero reale")
        try:
            offset = float(semitones_offset)
        except OverflowError as exc:
            raise ValueError("semitones_offset deve essere finito") from exc
        if not math.isfinite(offset):
            raise ValueError("semitones_offset deve essere finito")
        note_number = 69.0 + offset
        if not note_number.is_integer() or not 0 <= note_number <= 127:
            raise ValueError("L'offset deve corrispondere a una nota MIDI intera tra 0 e 127")
        midi_note = int(note_number)

    reference_frequency = _positive_finite(ref_hz, "ref_hz")
    reference_tempo = _positive_finite(ref_bpm, "ref_bpm")
    if isinstance(beats_without_realign, bool) or not isinstance(beats_without_realign, int):
        raise ValueError("beats_without_realign deve essere un intero non negativo")
    if beats_without_realign < 0:
        raise ValueError("beats_without_realign deve essere un intero non negativo")
    try:
        beat_count = float(beats_without_realign)
    except OverflowError as exc:
        raise ValueError("beats_without_realign è troppo grande") from exc

    factor = 2.0 ** (offset / 12.0)
    frequency_hz = reference_frequency * factor
    bpm = reference_tempo * factor
    if (
        not math.isfinite(frequency_hz)
        or frequency_hz <= 0.0
        or not math.isfinite(bpm)
        or bpm <= 0.0
    ):
        raise ValueError("I parametri producono una frequenza o un BPM non finito")

    try:
        master_quarter_ms = 60000.0 / reference_tempo
        note_quarter_ms = 60000.0 / bpm
    except OverflowError as exc:
        raise ValueError("I parametri producono una durata non rappresentabile") from exc
    if (
        not math.isfinite(master_quarter_ms)
        or not math.isfinite(note_quarter_ms)
        or master_quarter_ms <= 0.0
        or note_quarter_ms <= 0.0
    ):
        raise ValueError("I parametri producono una durata non rappresentabile")
    subdivisions_ms = {
        subdivision: note_quarter_ms / divisor
        for subdivision, divisor in _SUBDIVISION_DIVISORS.items()
    }
    offset_ms = note_quarter_ms - master_quarter_ms
    drift_ms = offset_ms * beat_count
    if not math.isfinite(drift_ms):
        raise ValueError("La deriva totale non è rappresentabile")

    return {
        "nota_midi": midi_note,
        "semitoni_offset": offset,
        "frequenza_hz": frequency_hz,
        "bpm": bpm,
        "suddivisioni_ms": subdivisions_ms,
        "offset_singolo_ms": offset_ms,
        "deriva_totale_ms": drift_ms,
    }


def validate_pitch_timing_reference_points() -> bool:
    """Check that the A3, A4, and A5 reference points match the specification."""
    expected_points = (
        (-12, 57, 220.0, 50.15),
        (0, 69, 440.0, 100.3),
        (12, 81, 880.0, 200.6),
    )
    for offset, expected_midi, expected_hz, expected_bpm in expected_points:
        result = calculate_pitch_timing(offset)
        if result["nota_midi"] != expected_midi:
            raise AssertionError(f"Nota MIDI errata per offset {offset}")
        if not math.isclose(result["frequenza_hz"], expected_hz, rel_tol=1e-12):
            raise AssertionError(f"Frequenza errata per offset {offset}")
        if not math.isclose(result["bpm"], expected_bpm, rel_tol=1e-12):
            raise AssertionError(f"BPM errato per offset {offset}")
    return True
