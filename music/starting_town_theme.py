#!/usr/bin/env python3
"""
Starting Town Theme - "Dawn of Adventure"
An 8-bit tranquil yet adventurous theme for the starting town.

Music Theory Approach:
- Key: G Major (bright, hopeful)
- Tempo: 75 BPM (slow, peaceful)
- Time Signature: 4/4
- Chord Progression: I - V - vi - IV (G - D - Em - C)
  This progression evokes hope and gentle adventure
- Melody uses pentatonic scale with passing tones for accessibility
- Arpeggiated accompaniment creates movement while maintaining tranquility
"""

import numpy as np
from scipy.io import wavfile
import os

# Audio settings
SAMPLE_RATE = 44100
BPM = 75
BEAT_DURATION = 60.0 / BPM  # seconds per beat

# Note frequencies (Hz) - Equal temperament tuning
NOTES = {
    # Octave 2
    'C2': 65.41, 'D2': 73.42, 'E2': 82.41, 'F2': 87.31, 'G2': 98.00,
    'A2': 110.00, 'B2': 123.47,
    # Octave 3
    'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00,
    'A3': 220.00, 'B3': 246.94,
    # Octave 4
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00,
    'A4': 440.00, 'B4': 493.88,
    # Octave 5
    'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99,
    'A5': 880.00, 'B5': 987.77,
    # Sharps/Flats
    'F#3': 185.00, 'F#4': 369.99, 'F#5': 739.99,
    'REST': 0
}


def square_wave(freq, duration, duty_cycle=0.5, volume=0.3):
    """Generate a square wave - classic 8-bit sound."""
    if freq == 0:
        return np.zeros(int(SAMPLE_RATE * duration))
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = np.where((t * freq) % 1 < duty_cycle, 1, -1) * volume
    return wave


def triangle_wave(freq, duration, volume=0.4):
    """Generate a triangle wave - softer bass sound."""
    if freq == 0:
        return np.zeros(int(SAMPLE_RATE * duration))
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = 2 * np.abs(2 * ((t * freq) % 1) - 1) - 1
    return wave * volume


def pulse_wave(freq, duration, duty_cycle=0.25, volume=0.25):
    """Generate a pulse wave - thinner 8-bit sound for arpeggios."""
    if freq == 0:
        return np.zeros(int(SAMPLE_RATE * duration))
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = np.where((t * freq) % 1 < duty_cycle, 1, -1) * volume
    return wave


def noise(duration, volume=0.1):
    """Generate white noise - for percussion."""
    samples = int(SAMPLE_RATE * duration)
    # Use lower sample rate noise for 8-bit feel
    noise_samples = np.random.uniform(-1, 1, samples // 8)
    noise_signal = np.repeat(noise_samples, 8)[:samples]
    return noise_signal * volume


def apply_envelope(wave, attack=0.01, decay=0.05, sustain=0.7, release=0.1):
    """Apply ADSR envelope for more natural sound."""
    length = len(wave)
    attack_samples = int(attack * SAMPLE_RATE)
    decay_samples = int(decay * SAMPLE_RATE)
    release_samples = int(release * SAMPLE_RATE)

    envelope = np.ones(length)

    # Attack
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Decay
    decay_end = attack_samples + decay_samples
    if decay_samples > 0 and decay_end < length:
        envelope[attack_samples:decay_end] = np.linspace(1, sustain, decay_samples)

    # Sustain (already at sustain level)
    if decay_end < length - release_samples:
        envelope[decay_end:length - release_samples] = sustain

    # Release
    if release_samples > 0:
        envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)

    return wave * envelope


def generate_melody():
    """
    Generate the main melody line.

    The melody uses a call-and-response structure common in adventure game music.
    Pentatonic-based (G, A, B, D, E) with passing tones for color.
    Condensed to ~30 seconds (8 bars at 75 BPM).
    """
    # Melody notes with durations (in beats)
    # Phrase 1: Opening statement - hopeful, rising (2 bars)
    phrase1 = [
        ('G4', 1), ('A4', 0.5), ('B4', 0.5), ('D5', 2),   # Bar 1
        ('E5', 1), ('D5', 1), ('B4', 1), ('REST', 1),     # Bar 2
    ]

    # Phrase 2: Response - gentle descent (2 bars)
    phrase2 = [
        ('B4', 1), ('A4', 0.5), ('G4', 0.5), ('A4', 2),   # Bar 3
        ('G4', 1), ('E4', 1), ('D4', 1), ('REST', 1),     # Bar 4
    ]

    # Phrase 3: Building adventure - rising with energy (2 bars)
    phrase3 = [
        ('E4', 1), ('G4', 1), ('A4', 1), ('B4', 1),       # Bar 5
        ('D5', 1.5), ('B4', 0.5), ('A4', 1), ('G4', 1),   # Bar 6
    ]

    # Phrase 4: Resolution - peaceful ending for seamless loop (2 bars)
    phrase4 = [
        ('A4', 1), ('B4', 0.5), ('D5', 0.5), ('E5', 1), ('D5', 1),  # Bar 7
        ('G4', 3), ('REST', 1),                           # Bar 8
    ]

    return phrase1 + phrase2 + phrase3 + phrase4


def generate_bass():
    """
    Generate the bass line following the chord progression.

    Chord progression (G - D - Em - C) for 8 bars.
    Bass plays root notes with occasional fifths for movement.
    """
    # Each chord gets 4 beats (1 bar)
    # Using octave 2-3 for bass depth

    bass_pattern = [
        # Bar 1: G major
        ('G2', 2), ('G2', 1), ('D3', 1),
        # Bar 2: D major
        ('D2', 2), ('D2', 1), ('A2', 1),
        # Bar 3: E minor
        ('E2', 2), ('E2', 1), ('B2', 1),
        # Bar 4: C major
        ('C3', 2), ('C3', 1), ('G2', 1),
        # Bar 5: G major (variation)
        ('G2', 2), ('D3', 1), ('G2', 1),
        # Bar 6: D major
        ('D2', 2), ('A2', 1), ('D2', 1),
        # Bar 7: C major (pre-resolution)
        ('C3', 2), ('G2', 1), ('C3', 1),
        # Bar 8: G major (resolution - sustained)
        ('G2', 4),
    ]

    return bass_pattern


def generate_arpeggio():
    """
    Generate arpeggiated chord tones for texture.

    Uses pulse waves at 25% duty cycle for thinner, sparkly sound.
    Arpeggios rise through chord tones creating gentle movement.
    8 bars total matching the melody and bass.
    """
    # Arpeggio patterns for each chord (eighth notes = 0.5 beats)
    # G major: G-B-D, D major: D-F#-A, E minor: E-G-B, C major: C-E-G

    arp_notes = []

    # 8 bars total, each bar has 8 eighth notes
    chord_patterns = [
        # G major arpeggio
        [('G4', 0.5), ('B4', 0.5), ('D5', 0.5), ('G5', 0.5),
         ('D5', 0.5), ('B4', 0.5), ('D5', 0.5), ('B4', 0.5)],
        # D major arpeggio
        [('D4', 0.5), ('F#4', 0.5), ('A4', 0.5), ('D5', 0.5),
         ('A4', 0.5), ('F#4', 0.5), ('A4', 0.5), ('F#4', 0.5)],
        # E minor arpeggio
        [('E4', 0.5), ('G4', 0.5), ('B4', 0.5), ('E5', 0.5),
         ('B4', 0.5), ('G4', 0.5), ('B4', 0.5), ('G4', 0.5)],
        # C major arpeggio
        [('C4', 0.5), ('E4', 0.5), ('G4', 0.5), ('C5', 0.5),
         ('G4', 0.5), ('E4', 0.5), ('G4', 0.5), ('E4', 0.5)],
    ]

    # 8-bar progression: G - D - Em - C - G - D - C - G
    progression = [0, 1, 2, 3, 0, 1, 3, 0]

    for chord_idx in progression:
        arp_notes.extend(chord_patterns[chord_idx])

    return arp_notes


def render_track(notes, wave_generator, **kwargs):
    """Render a track from note sequence to audio samples."""
    samples = []
    for note, duration in notes:
        freq = NOTES.get(note, 0)
        dur_seconds = duration * BEAT_DURATION
        wave = wave_generator(freq, dur_seconds, **kwargs)
        wave = apply_envelope(wave, attack=0.01, decay=0.03, sustain=0.8, release=0.08)
        samples.append(wave)
    return np.concatenate(samples)


def add_subtle_reverb(audio, delay=0.05, decay=0.3):
    """Add simple delay-based reverb for warmth."""
    delay_samples = int(delay * SAMPLE_RATE)
    reverb = np.zeros(len(audio) + delay_samples)
    reverb[:len(audio)] = audio
    reverb[delay_samples:delay_samples + len(audio)] += audio * decay
    return reverb[:len(audio)]


def generate_starting_town_theme():
    """Generate the complete starting town theme."""
    print("Generating 'Dawn of Adventure' - Starting Town Theme")
    print("=" * 50)
    print("Key: G Major | Tempo: 75 BPM | Duration: ~32 seconds")
    print("Chord Progression: G - D - Em - C (I - V - vi - IV)")
    print("=" * 50)

    # Generate each track
    print("\nRendering melody (square wave)...")
    melody_notes = generate_melody()
    melody = render_track(melody_notes, square_wave, duty_cycle=0.5, volume=0.25)

    print("Rendering bass (triangle wave)...")
    bass_notes = generate_bass()
    bass = render_track(bass_notes, triangle_wave, volume=0.35)

    print("Rendering arpeggios (pulse wave)...")
    arp_notes = generate_arpeggio()
    arpeggios = render_track(arp_notes, pulse_wave, duty_cycle=0.25, volume=0.15)

    # Match lengths
    max_length = max(len(melody), len(bass), len(arpeggios))

    def pad_to_length(arr, length):
        if len(arr) < length:
            return np.pad(arr, (0, length - len(arr)))
        return arr[:length]

    melody = pad_to_length(melody, max_length)
    bass = pad_to_length(bass, max_length)
    arpeggios = pad_to_length(arpeggios, max_length)

    # Mix tracks
    print("Mixing tracks...")
    mix = melody + bass + arpeggios

    # Add subtle reverb
    mix = add_subtle_reverb(mix, delay=0.03, decay=0.2)

    # Normalize to prevent clipping
    max_val = np.max(np.abs(mix))
    if max_val > 0:
        mix = mix / max_val * 0.8

    # Convert to 16-bit PCM
    audio_16bit = (mix * 32767).astype(np.int16)

    # Calculate duration
    duration = len(audio_16bit) / SAMPLE_RATE
    print(f"\nTotal duration: {duration:.1f} seconds")

    return audio_16bit


def main():
    """Generate and save the starting town theme."""
    # Generate the theme
    audio = generate_starting_town_theme()

    # Save to WAV file
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "starting_town_theme.wav")

    wavfile.write(output_path, SAMPLE_RATE, audio)
    print(f"\nSaved to: {output_path}")
    print("\nTheme Characteristics:")
    print("- Tranquil: Slow tempo, gentle arpeggios, major key")
    print("- Adventurous: Rising melodic phrases, hopeful chord progression")
    print("- 8-bit: Square/pulse/triangle waves, lo-fi warmth")
    print("- Loop-ready: Ends on tonic for seamless repetition")


if __name__ == "__main__":
    main()
