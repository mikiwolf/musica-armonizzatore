import os
import sys
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import music_harmonizer


class MusicHarmonizerAppTests(unittest.TestCase):
    def make_app_without_tk(self):
        app = music_harmonizer.MusicHarmonizerApp.__new__(music_harmonizer.MusicHarmonizerApp)
        app.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return app

    def test_init_continues_when_pygame_audio_fails(self):
        root = tk.Tk()
        root.withdraw()
        app = None
        try:
            with patch("music_harmonizer.pygame.mixer.init", side_effect=Exception("audio unavailable")):
                app = music_harmonizer.MusicHarmonizerApp(root)
            self.assertFalse(app.audio_available)
            self.assertIn("audio unavailable", app.audio_error)
        finally:
            if app is None:
                root.destroy()
            else:
                app.close()

    def test_chord_inversions_include_slash_notation_and_voicings(self):
        app = self.make_app_without_tk()

        inversions = app.get_chord_inversions([60, 64, 67], 60)

        self.assertEqual(len(inversions), 3)
        self.assertIn("Fondamentale: C (C4, E4, G4)", inversions[0])
        self.assertIn("I rivolto: C/E (E4, G4, C5)", inversions[1])
        self.assertIn("II rivolto: C/G (G4, C5, E5)", inversions[2])

    def test_harmonic_implication_identifies_major_dominant(self):
        app = self.make_app_without_tk()

        implication = app.get_harmonic_implication(
            [0, 2, 4, 5, 7, 9, 11, 12],
            4,
            "G",
        )

        self.assertEqual(implication, "V - dominante: crea tensione e tende a risolvere su I.")

    def test_diatonic_triads_match_major_and_minor_scales(self):
        app = self.make_app_without_tk()
        cases = (
            (
                [60, 62, 64, 65, 67, 69, 71, 72],
                [("I", "C"), ("ii", "Dm"), ("iii", "Em"), ("IV", "F"),
                 ("V", "G"), ("vi", "Am"), ("vii°", "Bdim")],
            ),
            (
                [69, 71, 72, 74, 76, 77, 79, 81],
                [("i", "Am"), ("ii°", "Bdim"), ("III", "C"), ("iv", "Dm"),
                 ("v", "Em"), ("VI", "F"), ("VII", "G")],
            ),
            (
                [60, 62, 63, 65, 67, 68, 70, 72],
                [("i", "Cm"), ("ii°", "Ddim"), ("III", "Eb"), ("iv", "Fm"),
                 ("v", "Gm"), ("VI", "Ab"), ("VII", "Bb")],
            ),
        )

        for scale, expected in cases:
            with self.subTest(scale=scale):
                rows = app.get_diatonic_harmony(scale)
                self.assertEqual(
                    [(row["numeral"], row["chord"]) for row in rows],
                    expected,
                )

    def test_diatonic_triads_detect_harmonic_minor_augmented_and_dorian(self):
        app = self.make_app_without_tk()
        harmonic_minor = app.get_diatonic_harmony([69, 71, 72, 74, 76, 77, 80, 81])
        dorian = app.get_diatonic_harmony([62, 64, 65, 67, 69, 71, 72, 74])

        self.assertEqual(
            [(row["numeral"], row["chord"]) for row in harmonic_minor],
            [("i", "Am"), ("ii°", "Bdim"), ("III+", "Caug"), ("iv", "Dm"),
             ("V", "E"), ("VI", "F"), ("vii°", "G#dim")],
        )
        self.assertEqual(
            [(row["numeral"], row["chord"]) for row in dorian],
            [("i", "Dm"), ("ii", "Em"), ("III", "F"), ("IV", "G"),
             ("v", "Am"), ("vi°", "Bdim"), ("VII", "C")],
        )

    def test_diatonic_harmony_excludes_octave_and_marks_non_heptatonic_scales(self):
        app = self.make_app_without_tk()
        pentatonic = app.get_diatonic_harmony([60, 63, 65, 67, 70, 72])
        hexatonic = app.get_diatonic_harmony([60, 62, 64, 66, 68, 70, 72])

        self.assertEqual(len(app.get_diatonic_harmony([60, 62, 64, 65, 67, 69, 71, 72])), 7)
        self.assertEqual(len(pentatonic), 5)
        self.assertEqual(len(hexatonic), 6)
        for rows in (pentatonic, hexatonic):
            self.assertTrue(all(row["role"] is None for row in rows))
            self.assertTrue(all(row["numeral"].isdigit() for row in rows))

    def test_harmonic_implication_rejects_degree_outside_scale(self):
        app = self.make_app_without_tk()

        with self.assertRaises(ValueError):
            app.get_harmonic_implication([0, 2, 4, 5, 7, 9, 11, 12], 7, "C")

    def test_analysis_report_lists_functions_without_duplicate_tonic(self):
        app = self.make_app_without_tk()
        app.C = 60
        app.text_note = Mock()
        app.text_note.get.return_value = "1 2 3 4 5 6 7 8"
        app.text_analisi = Mock()
        app.var_tono_pers = Mock()
        app.var_tono_pers.get.return_value = "C"
        app.var_nome_scala_pers = Mock()
        app.var_nome_scala_pers.get.return_value = "Maggiore"
        app.var_armonia_pers = Mock()
        app.var_armonia_pers.get.return_value = "terze"
        app.var_voci_pers = Mock()
        app.var_voci_pers.get.return_value = 3

        app.analizza_note()

        report = "".join(call.args[1] for call in app.text_analisi.insert.call_args_list)
        self.assertIn("FUNZIONI DIATONICHE", report)
        self.assertIn("tonica", report)
        self.assertIn("sottodominante", report)
        self.assertEqual(report.count("vii°"), 2)
        self.assertNotIn("Grado 8", report)

    def test_analysis_report_preserves_diatonic_flat_spellings(self):
        app = self.make_app_without_tk()
        app.C = 60
        app.text_note = Mock()
        app.text_note.get.return_value = "1 2 3b 4 5 6b 7b 8"
        app.text_analisi = Mock()
        app.var_tono_pers = Mock()
        app.var_tono_pers.get.return_value = "C"
        app.var_nome_scala_pers = Mock()
        app.var_nome_scala_pers.get.return_value = "Minore naturale"
        app.var_armonia_pers = Mock()
        app.var_armonia_pers.get.return_value = "terze"
        app.var_voci_pers = Mock()
        app.var_voci_pers.get.return_value = 3

        app.analizza_note()

        report = "".join(call.args[1] for call in app.text_analisi.insert.call_args_list)
        self.assertIn("III   Eb", report)
        self.assertIn("Eb4, G4, Bb4", report)

    def test_chord_inversions_support_seven_distinct_tones(self):
        app = self.make_app_without_tk()

        inversions = app.get_chord_inversions([60, 62, 64, 65, 67, 69, 71, 72], 60)

        self.assertEqual(len(inversions), 7)
        self.assertTrue(inversions[-1].startswith("VI rivolto:"))

    def test_unknown_scale_reports_chord_quality_implication(self):
        app = self.make_app_without_tk()

        implication = app.get_harmonic_implication([0, 1, 4, 7, 8], 0, "Cdim")
        half_diminished = app.get_chord_quality_implication("Cm7b5")

        self.assertIn("instabile e tesa", implication)
        self.assertIn("instabile e tesa", half_diminished)

    def test_scale_formula_round_trips_every_predefined_scale(self):
        root = tk.Tk()
        root.withdraw()
        app = music_harmonizer.MusicHarmonizerApp(root)
        try:
            for name, intervals in app.scale_map.items():
                formula = app.intervals_to_formula(intervals)
                with patch("music_harmonizer.messagebox.showerror") as showerror:
                    self.assertEqual(app.parse_note_input(formula), intervals, name)
                    showerror.assert_not_called()
        finally:
            with patch("music_harmonizer.pygame.mixer.music.stop"), patch(
                "music_harmonizer.pygame.mixer.music.unload"
            ), patch("music_harmonizer.pygame.mixer.quit"):
                app.close()

    def test_note_parser_rejects_malformed_or_out_of_order_input(self):
        app = self.make_app_without_tk()

        with patch("music_harmonizer.messagebox.showerror") as showerror:
            self.assertIsNone(app.parse_note_input("1 2x 3"))
            self.assertIsNone(app.parse_note_input("1 8 7"))
            self.assertIsNone(app.parse_note_input("1 2 2"))
            showerror.assert_called()

        self.assertEqual(app.parse_note_input("1 2 3"), [0, 2, 4])
        self.assertEqual(app.parse_note_input("1 2 3 4 5 6 7 8"), [0, 2, 4, 5, 7, 9, 11, 12])

    def test_chord_builder_rejects_invalid_voice_count(self):
        app = self.make_app_without_tk()

        for voices in (0, 9):
            with self.subTest(voices=voices):
                with self.assertRaises(ValueError):
                    app.build_chord_notes(60, "terze", voices, [60, 62, 64, 65, 67, 69, 71, 72])

    def test_midi_generation_rejects_invalid_options(self):
        app = self.make_app_without_tk()
        app.TPB = 480
        app._temp_directory = tempfile.TemporaryDirectory(prefix="music-harmonizer-test-")
        try:
            with patch("music_harmonizer.messagebox.showerror") as showerror:
                self.assertIsNone(app.genera_midi("C", [60], "test", 0, "terze"))
                self.assertIsNone(app.genera_midi("C", [60], "test", 90, "terze", voices=0))
                self.assertEqual(showerror.call_count, 2)
        finally:
            app._temp_directory.cleanup()

    def test_custom_playback_status_does_not_claim_failed_playback(self):
        app = self.make_app_without_tk()
        app.C = 60
        app.root = Mock()
        app.text_note = Mock()
        app.text_note.get.return_value = "1 2 3 4 5 6 7 8"
        app.label_status_pers = Mock()
        app.var_bpm_pers = Mock()
        app.var_bpm_pers.get.return_value = "90"
        app.var_tono_pers = Mock()
        app.var_tono_pers.get.return_value = "C"
        app.var_nome_scala_pers = Mock()
        app.var_nome_scala_pers.get.return_value = "Test"
        app.var_armonia_pers = Mock()
        app.var_armonia_pers.get.return_value = "terze"
        app.var_voci_pers = Mock()
        app.var_voci_pers.get.return_value = 2
        app.genera_midi = Mock(return_value="test.mid")
        app.ascolta_midi = Mock(return_value=False)

        app.genera_e_ascolta_note()

        status = app.label_status_pers.config.call_args.kwargs["text"]
        self.assertIn("riproduzione non avviata", status)
        self.assertNotIn("Riproducendo", status)

    def test_unavailable_audio_reports_playback_failure(self):
        app = self.make_app_without_tk()
        app.audio_available = False
        app.audio_error = "audio unavailable"
        with tempfile.NamedTemporaryFile(suffix=".mid") as midi_file:
            with patch("music_harmonizer.messagebox.showinfo"):
                self.assertFalse(app.ascolta_midi(midi_file.name))

    def test_predefined_scale_loader_reports_success(self):
        app = self.make_app_without_tk()
        app.text_note = Mock()
        app.var_tono_pers = Mock()
        app.var_nome_scala_pers = Mock()
        app.var_bpm_pers = Mock()
        app.var_armonia_pers = Mock()
        app.var_voci_pers = Mock()

        self.assertTrue(app.carica_su_personalizzata([0, 2, 4, 5, 7, 9, 11, 12], "C", "maggiore", 90, "terze", 2))
        app.text_note.insert.assert_called_once_with(tk.END, "1 2 3 4 5 6 7 8")

    def test_sequencer_exports_chords_and_melody_on_separate_tracks(self):
        app = self.make_app_without_tk()
        app.C = 60
        app.TPB = 480
        app.sequencer_bars = 4
        app.sequencer_steps_per_bar = 16
        app.scale_map = {"maggiore": [0, 2, 4, 5, 7, 9, 11, 12]}

        midi = app.build_sequencer_midi(
            "C",
            "maggiore",
            100,
            [0, 4, 5, 3],
            {(0, 72), (17, 74)},
        )

        self.assertEqual(len(midi.tracks), 3)
        chord_events = [message for message in midi.tracks[1] if message.type in ("note_on", "note_off")]
        melody_events = [message for message in midi.tracks[2] if message.type in ("note_on", "note_off")]
        self.assertEqual(sum(message.type == "note_on" for message in chord_events), 12)
        self.assertEqual(sum(message.type == "note_off" for message in chord_events), 12)
        self.assertEqual(sum(message.type == "note_on" for message in melody_events), 2)
        self.assertEqual(sum(message.type == "note_off" for message in melody_events), 2)

        melody_start_ticks = []
        absolute_tick = 0
        for message in midi.tracks[2]:
            absolute_tick += message.time
            if message.type == "note_on":
                melody_start_ticks.append(absolute_tick)
        self.assertEqual(melody_start_ticks, [0, 17 * 120])
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "sequencer.mid")
            midi.save(path)
            saved_midi = music_harmonizer.MidiFile(path)
            self.assertEqual(len(saved_midi.tracks), 3)
            self.assertEqual(saved_midi.ticks_per_beat, 480)

    def test_sequencer_rejects_bad_progression_and_notes(self):
        app = self.make_app_without_tk()
        app.C = 60
        app.TPB = 480
        app.sequencer_bars = 4
        app.sequencer_steps_per_bar = 16
        app.scale_map = {"maggiore": [0, 2, 4, 5, 7, 9, 11, 12]}

        with self.assertRaises(ValueError):
            app.build_sequencer_midi("C", "maggiore", 90, [0, 1], set())
        with self.assertRaises(ValueError):
            app.build_sequencer_midi("C", "maggiore", 90, [0, 1, 2, 99], set())
        with self.assertRaises(ValueError):
            app.build_sequencer_midi("C", "maggiore", 90, [0, 1, 2, 3], {(64, 60)})

    def test_generated_midi_is_removed_when_app_closes(self):
        app = self.make_app_without_tk()
        app.TPB = 480
        app.audio_available = True
        app._closed = False
        app._temp_directory = tempfile.TemporaryDirectory(prefix="music-harmonizer-test-")
        app.root = Mock()
        temp_directory = app._temp_directory.name

        filename = app.genera_midi("C", [60], "..\\Test", 90, "terze")

        self.assertTrue(os.path.isfile(filename))
        self.assertEqual(os.path.dirname(filename), temp_directory)
        self.assertNotIn("..", os.path.basename(filename))

        with patch("music_harmonizer.pygame.mixer.music.stop") as stop, patch(
            "music_harmonizer.pygame.mixer.music.unload"
        ) as unload, patch("music_harmonizer.pygame.mixer.quit") as quit_mixer:
            app.close()
            app.close()

        self.assertFalse(os.path.exists(temp_directory))
        app.root.destroy.assert_called_once()
        stop.assert_called_once()
        unload.assert_called_once()
        quit_mixer.assert_called_once()


if __name__ == "__main__":
    unittest.main()
