#!/usr/bin/env python3
"""
Starting Town Theme - "Peaceful Horizons"
An 8-bit tranquil yet adventurous theme for the starting town.

Music Theory Approach:
- Key: C Major (pure, innocent, hopeful)
- Tempo: 64 BPM (slow, peaceful, contemplative)
- Time Signature: 4/4
- Duration: ~45 seconds (12 bars)
- Chord Progression:
  * Main: I - V - vi - IV (C - G - Am - F) - the "axis progression"
  * Bridge: IV - I - ii - V (F - C - Dm - G) - subdominant motion
  This creates a sense of wonder and gentle adventure

Compositional Techniques:
- Melody uses Ionian mode with pentatonic emphasis for accessibility
- Countermelody provides harmonic depth and movement
- Arpeggiated accompaniment in 16th notes for shimmer
- Triangle wave bass for warmth and grounding
- Call-and-response phrasing for musical interest
- Stepwise motion with occasional leaps for tranquility
- Ends on V chord resolving to I for seamless loop
"""

import numpy as np
from scipy.io import wavfile
import os

# Audio settings
SAMPLE_RATE = 44100
BPM = 64  # Slow tempo for tranquility (~45 seconds for 12 bars)
BEAT_DURATION = 60.0 / BPM  # seconds per beat

# Note frequencies (Hz) - Equal temperament tuning A4=440Hz
NOTES = {
    # Octave 2 (bass range)
    'C2': 65.41, 'D2': 73.42, 'E2': 82.41, 'F2': 87.31, 'G2': 98.00,
    'A2': 110.00, 'B2': 123.47,
    # Octave 3 (low range)
    'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00,
    'A3': 220.00, 'B3': 246.94,
    # Octave 4 (mid range)
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00,
    'A4': 440.00, 'B4': 493.88,
    # Octave 5 (high range)
    'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99,
    'A5': 880.00, 'B5': 987.77,
    # Octave 6 (sparkle range)
    'C6': 1046.50, 'D6': 1174.66, 'E6': 1318.51,
    'REST': 0
}


def square_wave(freq, duration, duty_cycle=0.5, volume=0.3):
    """
    Generate a square wave - the classic 8-bit lead sound.

    Square waves have a bright, clear tone that cuts through the mix.
    Used for melody lines in NES-era music.
    """
    if freq == 0:
        return np.zeros(int(SAMPLE_RATE * duration))
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = np.where((t * freq) % 1 < duty_cycle, 1, -1) * volume
    return wave


def triangle_wave(freq, duration, volume=0.4):
    """
    Generate a triangle wave - warm, mellow bass sound.

    Triangle waves have fewer harmonics, creating a softer tone.
    Used for bass lines in NES music (channel 3).
    """
    if freq == 0:
        return np.zeros(int(SAMPLE_RATE * duration))
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = 2 * np.abs(2 * ((t * freq) % 1) - 1) - 1
    return wave * volume


def pulse_wave(freq, duration, duty_cycle=0.25, volume=0.25):
    """
    Generate a pulse wave - thinner, more delicate sound.

    25% duty cycle creates a hollow, flute-like quality.
    Perfect for arpeggios and countermelodies.
    """
    if freq == 0:
        return np.zeros(int(SAMPLE_RATE * duration))
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = np.where((t * freq) % 1 < duty_cycle, 1, -1) * volume
    return wave


def apply_envelope(wave, attack=0.02, decay=0.05, sustain=0.7, release=0.15):
    """
    Apply ADSR envelope for musical expression.

    Longer attack and release create a gentler, more tranquil feel.
    This softens the harsh edges of the 8-bit waveforms.
    """
    length = len(wave)
    attack_samples = int(attack * SAMPLE_RATE)
    decay_samples = int(decay * SAMPLE_RATE)
    release_samples = int(release * SAMPLE_RATE)

    envelope = np.ones(length)

    # Attack - gentle fade in
    if attack_samples > 0 and attack_samples < length:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Decay to sustain level
    decay_end = min(attack_samples + decay_samples, length)
    if decay_samples > 0 and attack_samples < length:
        actual_decay = decay_end - attack_samples
        if actual_decay > 0:
            envelope[attack_samples:decay_end] = np.linspace(1, sustain, actual_decay)

    # Sustain
    sustain_end = max(0, length - release_samples)
    if decay_end < sustain_end:
        envelope[decay_end:sustain_end] = sustain

    # Release - gentle fade out
    if release_samples > 0 and release_samples < length:
        envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)

    return wave * envelope


def generate_melody():
    """
    Generate the main melody line - the voice of adventure.

    The melody tells a story:
    - Bars 1-4: Introduction - gentle awakening, discovering the world
    - Bars 5-8: Development - growing sense of wonder and possibility
    - Bars 9-12: Resolution - peaceful acceptance, ready for journey

    Uses primarily stepwise motion with strategic leaps for interest.
    Pentatonic emphasis (C, D, E, G, A) with passing tones.
    """
    # Bar 1-2: Opening theme over C-G (I-V)
    # Gentle ascending pattern, suggesting dawn breaking
    phrase1 = [
        ('E4', 1), ('G4', 0.5), ('A4', 0.5), ('G4', 1), ('E4', 1),  # Bar 1: C major feel
        ('D4', 1), ('E4', 0.5), ('G4', 0.5), ('A4', 1), ('REST', 1),  # Bar 2: Moving to G
    ]

    # Bar 3-4: Response over Am-F (vi-IV)
    # Slightly melancholic but hopeful, stepping down
    phrase2 = [
        ('A4', 1), ('G4', 0.5), ('E4', 0.5), ('G4', 1.5), ('E4', 0.5),  # Bar 3: Am color
        ('F4', 1), ('E4', 0.5), ('D4', 0.5), ('C4', 2),  # Bar 4: Resolve to F
    ]

    # Bar 5-6: Development over C-G (I-V)
    # Higher register, more energy, adventure beckons
    phrase3 = [
        ('G4', 0.5), ('A4', 0.5), ('C5', 1), ('D5', 1), ('C5', 1),  # Bar 5: Rising
        ('B4', 0.5), ('A4', 0.5), ('G4', 1), ('A4', 1), ('REST', 1),  # Bar 6: Gentle fall
    ]

    # Bar 7-8: Climax over Am-F (vi-IV)
    # Peak of the melody, most expressive moment
    phrase4 = [
        ('C5', 1.5), ('B4', 0.5), ('A4', 1), ('G4', 1),  # Bar 7: Climax
        ('A4', 1), ('G4', 0.5), ('E4', 0.5), ('F4', 1), ('E4', 1),  # Bar 8: Descending
    ]

    # Bar 9-10: Recapitulation over F-C (IV-I)
    # Return to opening material, varied
    phrase5 = [
        ('E4', 0.5), ('F4', 0.5), ('G4', 1), ('A4', 1), ('G4', 1),  # Bar 9
        ('E4', 1), ('D4', 0.5), ('E4', 0.5), ('G4', 1), ('REST', 1),  # Bar 10
    ]

    # Bar 11-12: Final resolution over Dm-G (ii-V)
    # Prepares for loop, ends on G leading back to C
    phrase6 = [
        ('D4', 1), ('F4', 0.5), ('E4', 0.5), ('D4', 1), ('E4', 1),  # Bar 11: Dm feel
        ('G4', 2), ('A4', 0.5), ('G4', 0.5), ('REST', 1),  # Bar 12: V chord, leads to I
    ]

    return phrase1 + phrase2 + phrase3 + phrase4 + phrase5 + phrase6


def generate_countermelody():
    """
    Generate a countermelody for harmonic richness.

    The countermelody moves in contrary motion to the main melody,
    filling in harmonically and creating a fuller texture.
    Uses longer note values for a more tranquil feel.
    """
    # Simpler, sustained notes that complement the melody
    counter = [
        # Bars 1-4
        ('C4', 2), ('G3', 2),  # Bar 1
        ('G3', 2), ('B3', 2),  # Bar 2
        ('E4', 2), ('C4', 2),  # Bar 3
        ('A3', 2), ('C4', 2),  # Bar 4
        # Bars 5-8
        ('E4', 2), ('D4', 2),  # Bar 5
        ('D4', 2), ('E4', 2),  # Bar 6
        ('E4', 2), ('C4', 2),  # Bar 7
        ('C4', 2), ('A3', 2),  # Bar 8
        # Bars 9-12
        ('A3', 2), ('C4', 2),  # Bar 9
        ('G3', 2), ('B3', 2),  # Bar 10
        ('A3', 2), ('F3', 2),  # Bar 11
        ('G3', 2), ('D4', 2),  # Bar 12
    ]
    return counter


def generate_bass():
    """
    Generate the bass line following the chord progression.

    12-bar progression:
    | C  | G  | Am | F  | C  | G  | Am | F  | F  | C  | Dm | G  |
    | I  | V  | vi | IV | I  | V  | vi | IV | IV | I  | ii | V  |

    Bass provides the harmonic foundation with root-fifth motion.
    Triangle wave for warm, rounded tone.
    """
    bass_pattern = [
        # Bar 1: C major
        ('C2', 2), ('G2', 1), ('C2', 1),
        # Bar 2: G major
        ('G2', 2), ('D3', 1), ('G2', 1),
        # Bar 3: A minor
        ('A2', 2), ('E2', 1), ('A2', 1),
        # Bar 4: F major
        ('F2', 2), ('C3', 1), ('F2', 1),
        # Bar 5: C major
        ('C2', 2), ('E2', 1), ('G2', 1),
        # Bar 6: G major
        ('G2', 2), ('B2', 1), ('G2', 1),
        # Bar 7: A minor
        ('A2', 2), ('E2', 1), ('A2', 1),
        # Bar 8: F major
        ('F2', 2), ('A2', 1), ('F2', 1),
        # Bar 9: F major (subdominant emphasis)
        ('F2', 2), ('C3', 1), ('A2', 1),
        # Bar 10: C major
        ('C2', 2), ('G2', 1), ('E2', 1),
        # Bar 11: D minor (ii chord)
        ('D2', 2), ('A2', 1), ('D2', 1),
        # Bar 12: G major (V chord - creates tension for loop)
        ('G2', 3), ('REST', 1),
    ]
    return bass_pattern


def generate_arpeggio():
    """
    Generate shimmering arpeggiated accompaniment.

    Arpeggios create gentle movement and fill the texture.
    Using broken chord patterns in 8th notes for a flowing feel.
    Quieter than melody to stay in background.
    """
    # Arpeggio patterns for each chord (8th notes)
    patterns = {
        'C':  [('C4', 0.5), ('E4', 0.5), ('G4', 0.5), ('C5', 0.5),
               ('G4', 0.5), ('E4', 0.5), ('G4', 0.5), ('E4', 0.5)],
        'G':  [('G3', 0.5), ('B3', 0.5), ('D4', 0.5), ('G4', 0.5),
               ('D4', 0.5), ('B3', 0.5), ('D4', 0.5), ('B3', 0.5)],
        'Am': [('A3', 0.5), ('C4', 0.5), ('E4', 0.5), ('A4', 0.5),
               ('E4', 0.5), ('C4', 0.5), ('E4', 0.5), ('C4', 0.5)],
        'F':  [('F3', 0.5), ('A3', 0.5), ('C4', 0.5), ('F4', 0.5),
               ('C4', 0.5), ('A3', 0.5), ('C4', 0.5), ('A3', 0.5)],
        'Dm': [('D3', 0.5), ('F3', 0.5), ('A3', 0.5), ('D4', 0.5),
               ('A3', 0.5), ('F3', 0.5), ('A3', 0.5), ('F3', 0.5)],
    }

    # 12-bar progression
    progression = ['C', 'G', 'Am', 'F', 'C', 'G', 'Am', 'F', 'F', 'C', 'Dm', 'G']

    arp_notes = []
    for chord in progression:
        arp_notes.extend(patterns[chord])

    return arp_notes


def generate_pad():
    """
    Generate sustained pad notes for atmosphere.

    Long, held notes create a sense of space and tranquility.
    Uses very quiet volume to sit behind other elements.
    """
    # Whole-note chords (4 beats each)
    pad_notes = [
        ('E4', 4),   # Bar 1: C chord - 3rd
        ('D4', 4),   # Bar 2: G chord - 5th
        ('C4', 4),   # Bar 3: Am chord - 3rd
        ('A3', 4),   # Bar 4: F chord - 3rd
        ('G4', 4),   # Bar 5: C chord - 5th
        ('B3', 4),   # Bar 6: G chord - 3rd
        ('E4', 4),   # Bar 7: Am chord - 5th
        ('C4', 4),   # Bar 8: F chord - 5th
        ('F4', 4),   # Bar 9: F chord - root
        ('E4', 4),   # Bar 10: C chord - 3rd
        ('F3', 4),   # Bar 11: Dm chord - 3rd
        ('D4', 4),   # Bar 12: G chord - 5th
    ]
    return pad_notes


def render_track(notes, wave_generator, **kwargs):
    """Render a track from note sequence to audio samples."""
    samples = []
    for note, duration in notes:
        freq = NOTES.get(note, 0)
        dur_seconds = duration * BEAT_DURATION
        wave = wave_generator(freq, dur_seconds, **kwargs)
        wave = apply_envelope(wave)
        samples.append(wave)
    return np.concatenate(samples) if samples else np.array([])


def render_track_soft(notes, wave_generator, **kwargs):
    """Render a track with softer envelope for pads."""
    samples = []
    for note, duration in notes:
        freq = NOTES.get(note, 0)
        dur_seconds = duration * BEAT_DURATION
        wave = wave_generator(freq, dur_seconds, **kwargs)
        wave = apply_envelope(wave, attack=0.1, decay=0.1, sustain=0.6, release=0.2)
        samples.append(wave)
    return np.concatenate(samples) if samples else np.array([])


def add_reverb(audio, delay=0.08, decay=0.25):
    """
    Add simple delay-based reverb for space and warmth.

    Creates a sense of environment, making the music feel
    like it exists in a cozy space.
    """
    delay_samples = int(delay * SAMPLE_RATE)
    reverb = np.zeros(len(audio) + delay_samples * 3)
    reverb[:len(audio)] = audio
    reverb[delay_samples:delay_samples + len(audio)] += audio * decay
    reverb[delay_samples*2:delay_samples*2 + len(audio)] += audio * (decay * 0.5)
    reverb[delay_samples*3:delay_samples*3 + len(audio)] += audio * (decay * 0.25)
    return reverb[:len(audio)]


def generate_starting_town_theme():
    """Generate the complete starting town theme - 'Peaceful Horizons'."""
    print("=" * 60)
    print("Generating 'Peaceful Horizons' - Starting Town Theme")
    print("=" * 60)
    print(f"Key: C Major | Tempo: {BPM} BPM | Target: ~45 seconds")
    print("Progression: C-G-Am-F | C-G-Am-F | F-C-Dm-G")
    print("Style: Tranquil 8-bit adventure")
    print("=" * 60)

    # Generate each musical layer
    print("\n[1/5] Rendering melody (square wave)...")
    melody_notes = generate_melody()
    melody = render_track(melody_notes, square_wave, duty_cycle=0.5, volume=0.22)

    print("[2/5] Rendering countermelody (pulse wave)...")
    counter_notes = generate_countermelody()
    counter = render_track_soft(counter_notes, pulse_wave, duty_cycle=0.25, volume=0.12)

    print("[3/5] Rendering bass (triangle wave)...")
    bass_notes = generate_bass()
    bass = render_track(bass_notes, triangle_wave, volume=0.30)

    print("[4/5] Rendering arpeggios (pulse wave)...")
    arp_notes = generate_arpeggio()
    arpeggios = render_track(arp_notes, pulse_wave, duty_cycle=0.125, volume=0.10)

    print("[5/5] Rendering pad (triangle wave)...")
    pad_notes = generate_pad()
    pad = render_track_soft(pad_notes, triangle_wave, volume=0.08)

    # Match all track lengths
    max_length = max(len(melody), len(bass), len(arpeggios), len(counter), len(pad))

    def pad_to_length(arr, length):
        if len(arr) < length:
            return np.pad(arr, (0, length - len(arr)))
        return arr[:length]

    melody = pad_to_length(melody, max_length)
    counter = pad_to_length(counter, max_length)
    bass = pad_to_length(bass, max_length)
    arpeggios = pad_to_length(arpeggios, max_length)
    pad = pad_to_length(pad, max_length)

    # Mix all tracks together
    print("\nMixing tracks...")
    mix = melody + counter + bass + arpeggios + pad

    # Add subtle reverb for atmosphere
    print("Adding reverb...")
    mix = add_reverb(mix, delay=0.06, decay=0.2)

    # Normalize to prevent clipping, leave headroom
    max_val = np.max(np.abs(mix))
    if max_val > 0:
        mix = mix / max_val * 0.75

    # Convert to 16-bit PCM audio
    audio_16bit = (mix * 32767).astype(np.int16)

    # Report duration
    duration = len(audio_16bit) / SAMPLE_RATE
    print(f"\n{'=' * 60}")
    print(f"Final duration: {duration:.1f} seconds")
    print(f"{'=' * 60}")

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
    print("  • Tranquil: Slow 64 BPM, gentle dynamics, major key")
    print("  • Adventurous: Rising phrases, hopeful I-V-vi-IV progression")
    print("  • 8-bit: Square/pulse/triangle waves, lo-fi warmth")
    print("  • Layered: Melody, countermelody, bass, arpeggios, pad")
    print("  • Loop-ready: Ends on V chord resolving to I")


if __name__ == "__main__":
    main()
