import os
import sys
import tempfile
import tkinter as tk
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import music_harmonizer
import pitch_timing


class PitchTimingTests(unittest.TestCase):
    def test_reference_points_match_equal_tempered_octaves(self):
        self.assertTrue(pitch_timing.validate_pitch_timing_reference_points())

        a3 = pitch_timing.calculate_pitch_timing(-12)
        a4 = pitch_timing.calculate_pitch_timing(0)
        a5 = pitch_timing.calculate_pitch_timing(midi_note=81)

        self.assertEqual((a3["nota_midi"], a3["frequenza_hz"], a3["bpm"]), (57, 220.0, 50.15))
        self.assertEqual((a4["nota_midi"], a4["frequenza_hz"], a4["bpm"]), (69, 440.0, 100.3))
        self.assertEqual((a5["nota_midi"], a5["frequenza_hz"], a5["bpm"]), (81, 880.0, 200.6))

    def test_subdivisions_and_cumulative_drift_use_note_quarter(self):
        result = pitch_timing.calculate_pitch_timing(
            12,
            beats_without_realign=8,
        )
        quarter_ms = 60000.0 / 200.6
        self.assertEqual(
            set(result["suddivisioni_ms"]),
            {"1/4", "1/8.", "1/8", "1/8T", "1/16", "1/32"},
        )

        self.assertAlmostEqual(result["suddivisioni_ms"]["1/4"], quarter_ms)
        self.assertAlmostEqual(result["suddivisioni_ms"]["1/8."], quarter_ms * 3.0 / 4.0)
        self.assertAlmostEqual(result["suddivisioni_ms"]["1/8"], quarter_ms / 2.0)
        self.assertAlmostEqual(result["suddivisioni_ms"]["1/8T"], quarter_ms / 3.0)
        self.assertAlmostEqual(result["suddivisioni_ms"]["1/16"], quarter_ms / 4.0)
        self.assertAlmostEqual(result["suddivisioni_ms"]["1/32"], quarter_ms / 8.0)
        self.assertAlmostEqual(
            result["deriva_totale_ms"],
            result["offset_singolo_ms"] * 8,
        )
        self.assertLess(result["offset_singolo_ms"], 0.0)
        self.assertEqual(pitch_timing.calculate_pitch_timing(0)["offset_singolo_ms"], 0.0)
        self.assertGreater(pitch_timing.calculate_pitch_timing(-12)["offset_singolo_ms"], 0.0)

    def test_invalid_pitch_and_reference_inputs_are_rejected(self):
        invalid_calls = (
            lambda: pitch_timing.calculate_pitch_timing(),
            lambda: pitch_timing.calculate_pitch_timing(0, midi_note=69),
            lambda: pitch_timing.calculate_pitch_timing(0.5),
            lambda: pitch_timing.calculate_pitch_timing(59),
            lambda: pitch_timing.calculate_pitch_timing(midi_note=128),
            lambda: pitch_timing.calculate_pitch_timing(0, ref_bpm=float("nan")),
            lambda: pitch_timing.calculate_pitch_timing(0, beats_without_realign=-1),
            lambda: pitch_timing.calculate_pitch_timing(0, ref_bpm=5e-324),
            lambda: pitch_timing.calculate_pitch_timing(1, beats_without_realign=10**1000),
        )
        for calculate in invalid_calls:
            with self.subTest(calculate=calculate), self.assertRaises(ValueError):
                calculate()


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

    def test_chord_labels_use_standard_international_symbols(self):
        app = self.make_app_without_tk()

        self.assertEqual(app.get_chord_label([69, 72, 76], root=69), "Am")
        self.assertEqual(app.get_chord_label([62, 65, 69, 72, 76], root=62), "Dm9")
        self.assertEqual(app.get_chord_label([60, 64, 67, 71, 74], root=60), "Cmaj9")
        self.assertEqual(app.get_chord_label([60, 65, 70], root=60), "C7sus4(no5)")
        self.assertEqual(app.get_chord_label([60, 64, 65, 70], root=60), "C7(no5, add11)")

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

    def test_sequencer_ui_applies_custom_scale_and_paginates_progression(self):
        root = tk.Tk()
        root.withdraw()
        app = music_harmonizer.MusicHarmonizerApp(root)
        try:
            packed_frames = app.frame_sequencer.pack_slaves()
            self.assertLess(
                packed_frames.index(app.sequencer_actions_frame),
                packed_frames.index(app.sequencer_grid_frame),
            )
            self.assertEqual(len(app.sequencer_chord_vars), 32)
            self.assertEqual(len(app.sequencer_chord_combos), 4)
            self.assertEqual(app.sequencer_note_duration_var.get(), "1/16")

            app.sequencer_custom_scale_var.set("1 2 3b 4 5 6b 7b")
            app.apply_sequencer_custom_scale()

            self.assertEqual(app.sequencer_scale_var.get(), "personale")
            self.assertEqual(app.sequencer_custom_scale_intervals, [0, 2, 3, 5, 7, 8, 10])
            self.assertEqual(len(app.get_sequencer_scale()), 8)

            app.change_sequencer_page(1)
            self.assertEqual(app.sequencer_page, 1)
            self.assertEqual(app.sequencer_page_label.cget("text"), "Battute 5–8 / 32")
            for _ in range(6):
                app.change_sequencer_page(1)
            self.assertEqual(app.sequencer_page, 7)
            self.assertEqual(app.sequencer_page_label.cget("text"), "Battute 29–32 / 32")
        finally:
            with patch("music_harmonizer.pygame.mixer.music.stop"), patch(
                "music_harmonizer.pygame.mixer.music.unload"
            ), patch("music_harmonizer.pygame.mixer.quit"):
                app.close()

    def test_sequencer_applies_harmonic_preset_once_and_preserves_later_bars(self):
        root = tk.Tk()
        root.withdraw()
        app = music_harmonizer.MusicHarmonizerApp(root)
        try:
            original_degrees = app.get_sequencer_chord_degrees()
            app.sequencer_preset_var.set("Jazz: ii–V–I")

            app.apply_sequencer_harmonic_preset()

            self.assertEqual(app.get_sequencer_chord_degrees()[:3], [1, 4, 0])
            self.assertEqual(
                app.get_sequencer_chord_degrees()[3:],
                original_degrees[3:],
            )
            self.assertEqual(app.sequencer_page, 0)
            self.assertIn("altre 29 battute non sono state modificate", app.sequencer_status.cget("text"))
        finally:
            with patch("music_harmonizer.pygame.mixer.music.stop"), patch(
                "music_harmonizer.pygame.mixer.music.unload"
            ), patch("music_harmonizer.pygame.mixer.quit"):
                app.close()

    def test_sequencer_applies_harmonic_preset_at_selected_bar(self):
        root = tk.Tk()
        root.withdraw()
        app = music_harmonizer.MusicHarmonizerApp(root)
        try:
            original_degrees = app.get_sequencer_chord_degrees()
            app.sequencer_preset_var.set("Jazz: ii–V–I")
            app.sequencer_preset_start_bar_var.set("10")

            app.apply_sequencer_harmonic_preset_here()

            updated_degrees = app.get_sequencer_chord_degrees()
            self.assertEqual(updated_degrees[9:12], [1, 4, 0])
            self.assertEqual(updated_degrees[:9], original_degrees[:9])
            self.assertEqual(updated_degrees[12:], original_degrees[12:])
            self.assertEqual(app.sequencer_page, 2)
            self.assertEqual(app.sequencer_page_label.cget("text"), "Battute 9–12 / 32")
            self.assertIn("battute 10–12", app.sequencer_status.cget("text"))
        finally:
            with patch("music_harmonizer.pygame.mixer.music.stop"), patch(
                "music_harmonizer.pygame.mixer.music.unload"
            ), patch("music_harmonizer.pygame.mixer.quit"):
                app.close()

    def test_sequencer_rejects_harmonic_preset_that_will_not_fit_at_selected_bar(self):
        root = tk.Tk()
        root.withdraw()
        app = music_harmonizer.MusicHarmonizerApp(root)
        try:
            original_degrees = app.get_sequencer_chord_degrees()
            app.sequencer_preset_var.set("Jazz: ii–V–I–vi")
            app.sequencer_preset_start_bar_var.set("30")

            app.apply_sequencer_harmonic_preset_here()

            self.assertEqual(app.get_sequencer_chord_degrees(), original_degrees)
            self.assertIn("richiede 4 battute", app.sequencer_status.cget("text"))
        finally:
            with patch("music_harmonizer.pygame.mixer.music.stop"), patch(
                "music_harmonizer.pygame.mixer.music.unload"
            ), patch("music_harmonizer.pygame.mixer.quit"):
                app.close()

    def test_sequencer_rejects_harmonic_preset_incompatible_with_scale(self):
        root = tk.Tk()
        root.withdraw()
        app = music_harmonizer.MusicHarmonizerApp(root)
        try:
            app.sequencer_scale_var.set("pentatonica_mag")
            original_degrees = app.get_sequencer_chord_degrees()
            app.sequencer_preset_var.set("Jazz: ii–V–I–vi")

            app.apply_sequencer_harmonic_preset()

            self.assertEqual(app.get_sequencer_chord_degrees(), original_degrees)
            self.assertIn("richiede almeno 6 gradi", app.sequencer_status.cget("text"))
        finally:
            with patch("music_harmonizer.pygame.mixer.music.stop"), patch(
                "music_harmonizer.pygame.mixer.music.unload"
            ), patch("music_harmonizer.pygame.mixer.quit"):
                app.close()

    def test_sequencer_meter_selector_updates_grid_and_keeps_notes_in_their_bars(self):
        root = tk.Tk()
        root.withdraw()
        app = music_harmonizer.MusicHarmonizerApp(root)
        try:
            app.sequencer_notes.update({(3, 60), (17, 62)})
            app.sequencer_note_lengths.update({(3, 60): 4, (17, 62): 2})
            app.sequencer_time_signature_var.set("3/4")
            app.update_sequencer_time_signature()

            self.assertEqual(app.sequencer_steps_per_bar, 12)
            self.assertEqual(app.sequencer_notes, {(3, 60), (13, 62)})
            self.assertEqual(app.sequencer_note_lengths, {(3, 60): 4, (13, 62): 2})

            app.sequencer_time_signature_var.set("8/16")
            app.update_sequencer_time_signature()
            self.assertEqual(app.sequencer_steps_per_bar, 8)
            self.assertEqual(app.sequencer_notes, {(3, 60), (9, 62)})
        finally:
            with patch("music_harmonizer.pygame.mixer.music.stop"), patch(
                "music_harmonizer.pygame.mixer.music.unload"
            ), patch("music_harmonizer.pygame.mixer.quit"):
                app.close()

    def test_sequencer_loop_plays_selected_bar_repeatedly(self):
        root = tk.Tk()
        root.withdraw()
        app = music_harmonizer.MusicHarmonizerApp(root)
        try:
            app.sequencer_loop_bar_var.set("5")
            with patch.object(app, "ascolta_midi", return_value=True) as play:
                app.loop_sequencer_bar()

            self.assertEqual(app.sequencer_page, 1)
            play.assert_called_once()
            self.assertEqual(play.call_args.kwargs["loops"], -1)
            self.assertEqual(app.sequencer_channel_metadata["Accordi"][0]["bar"], 5)
        finally:
            with patch("music_harmonizer.pygame.mixer.music.stop"), patch(
                "music_harmonizer.pygame.mixer.music.unload"
            ), patch("music_harmonizer.pygame.mixer.quit"):
                app.close()

    def test_sequencer_octave_control_limits_grid_to_two_octaves(self):
        app = self.make_app_without_tk()
        app.sequencer_octave_var = Mock()
        app.sequencer_octave_var.get.return_value = "5"
        app.sequencer_selected_notes = {(0, 60)}
        app.sequencer_selection_box = (0, 60, 0, 60)

        with patch.object(app, "redraw_sequencer_grid") as redraw:
            app.change_sequencer_octave()

        self.assertEqual(app.sequencer_octave, 5)
        self.assertEqual(app.sequencer_low_note, 72)
        self.assertEqual(app.sequencer_high_note, 95)
        self.assertEqual(app.sequencer_high_note - app.sequencer_low_note + 1, 24)
        self.assertFalse(app.sequencer_selected_notes)
        self.assertIsNone(app.sequencer_selection_box)
        redraw.assert_called_once()

    def test_sequencer_mouse_selection_copies_and_pastes_notes(self):
        app = self.make_app_without_tk()
        app.sequencer_canvas = Mock()
        app.sequencer_canvas.canvasx.side_effect = lambda value: value
        app.sequencer_canvas.canvasy.side_effect = lambda value: value
        app.sequencer_low_note = 48
        app.sequencer_high_note = 71
        app.sequencer_cell_width = 14
        app.sequencer_cell_height = 22
        app.sequencer_page = 0
        app.sequencer_bars = 32
        app.sequencer_bars_per_page = 4
        app.sequencer_steps_per_bar = 16
        app.sequencer_notes = {(0, 60), (1, 59), (3, 55)}
        app.sequencer_note_lengths = {(0, 60): 4, (1, 59): 0.5, (3, 55): 2}
        app.sequencer_note_duration_var = Mock()
        app.sequencer_note_duration_var.get.return_value = "1/16"
        app.sequencer_selected_notes = set()
        app.sequencer_selection_box = None
        app.sequencer_selection_start = None
        app.sequencer_selection_current = None
        app.sequencer_clipboard = ()
        app.sequencer_paste_armed = False
        app.sequencer_status = Mock()

        def mouse_event(step, pitch):
            return Mock(
                x=44 + step * app.sequencer_cell_width + 7,
                y=(
                    26
                    + (app.sequencer_high_note - pitch)
                    * app.sequencer_cell_height
                    + 11
                ),
            )

        with patch.object(app, "redraw_sequencer_grid"):
            app.begin_sequencer_mouse_action(mouse_event(0, 60))
            app.drag_sequencer_selection(mouse_event(1, 59))
            app.finish_sequencer_mouse_action(mouse_event(1, 59))
            app.copy_sequencer_notes()
            app.arm_sequencer_paste()
            app.paste_sequencer_notes((4, 62))

        self.assertEqual(app.sequencer_clipboard, ((0, 0, 4), (1, 1, 0.5)))
        self.assertEqual(app.sequencer_notes, {(0, 60), (1, 59), (3, 55), (4, 62), (5, 61)})
        self.assertEqual(app.sequencer_note_lengths[(4, 62)], 4)
        self.assertEqual(app.sequencer_note_lengths[(5, 61)], 0.5)
        self.assertFalse(app.sequencer_paste_armed)

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
        melody_metadata = app.sequencer_channel_metadata["Melodia"]
        expected_starts = [
            item["step"] * (app.TPB // 4) + item["shift_ticks"]
            for item in melody_metadata
        ]
        self.assertEqual(melody_start_ticks, sorted(expected_starts))
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "sequencer.mid")
            midi.save(path)
            saved_midi = music_harmonizer.MidiFile(path)
            self.assertEqual(len(saved_midi.tracks), 3)
            self.assertEqual(saved_midi.ticks_per_beat, 480)

    def test_phase_alignment_metadata_uses_a4_reference_and_integer_cycles(self):
        app = self.make_app_without_tk()

        a4 = app.get_phase_alignment_metadata(69, 100)
        c4 = app.get_phase_alignment_metadata(60, 100)

        self.assertEqual(a4["frequency_hz"], 440.0)
        self.assertEqual(a4["cycles_per_quarter"], 264)
        self.assertEqual(a4["gate_ms"], 2400.0)
        self.assertEqual(a4["shift_ms"], 0.0)
        self.assertEqual(c4["cycles_per_quarter"], 156)
        self.assertAlmostEqual(c4["gate_ms"] + c4["shift_ms"], 2400.0)
        self.assertEqual(c4["cycles"], c4["cycles_per_quarter"] * 4)

    def test_sequencer_applies_phase_gate_and_configurable_chord_voicing(self):
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
            set(),
            armonia="quarte",
            voices=5,
        )

        metadata = app.sequencer_channel_metadata["Accordi"][0]
        self.assertEqual(metadata["root_note"], 60)
        self.assertEqual(metadata["cycles_per_quarter"], 156)
        self.assertEqual(metadata["cycles"], 624)
        self.assertGreater(metadata["shift_ms"], 0)
        self.assertEqual(len(app.sequencer_channel_metadata["Accordi"]), 4)
        self.assertEqual(app.sequencer_channel_metadata["Melodia"], [])

        track_events = list(self._absolute_events(midi.tracks[1]))
        events = [
            message for _, message in track_events
            if message.type in ("note_on", "note_off")
        ]
        self.assertEqual(sum(message.type == "note_on" for message in events), 20)
        first_note_on_tick = next(
            tick
            for tick, message in track_events
            if message.type == "note_on"
        )
        self.assertEqual(first_note_on_tick, metadata["shift_ticks"])
        first_note_off_tick = next(
            tick
            for tick, message in track_events
            if message.type == "note_off"
        )
        self.assertEqual(first_note_off_tick, app.TPB * 4)
        chord_text = next(
            (tick, message.text)
            for tick, message in track_events
            if message.type == "text"
        )
        self.assertEqual(chord_text[0], first_note_on_tick)
        self.assertEqual(chord_text[1], metadata["text"])
        self.assertIn("I Grado - C", chord_text[1])
        self.assertTrue(chord_text[1].endswith("(Quarte)"))
        self.assertEqual(first_note_off_tick - first_note_on_tick, metadata["gate_ticks"])

    def test_chord_duration_and_preceding_pause_are_applied_to_midi_timing(self):
        app = self.make_app_without_tk()
        app.C = 60
        app.TPB = 480
        app.sequencer_bars = 4
        app.sequencer_steps_per_bar = 16
        app.scale_map = {"maggiore": [0, 2, 4, 5, 7, 9, 11, 12]}
        durations = ["1/2", "1/1", "1/1", "1/2"]
        pauses = ["1/8", "Nessuna", "Nessuna", "Nessuna"]

        midi = app.build_sequencer_midi(
            "C",
            "maggiore",
            100,
            [0, 4, 5, 3],
            set(),
            chord_durations=durations,
            chord_pauses=pauses,
        )

        metadata = app.sequencer_channel_metadata["Accordi"][0]
        events = list(self._absolute_events(midi.tracks[1]))
        note_on_tick = next(tick for tick, message in events if message.type == "note_on")
        note_off_tick = next(tick for tick, message in events if message.type == "note_off")
        self.assertEqual(metadata["duration_beats"], 2.0)
        self.assertEqual(metadata["pause_beats"], 0.5)
        self.assertEqual(metadata["duration_ticks"], 2 * app.TPB)
        self.assertEqual(metadata["pause_ticks"], app.TPB // 2)
        self.assertEqual(note_on_tick, metadata["pause_ticks"] + metadata["shift_ticks"])
        self.assertEqual(metadata["shift_ticks"], metadata["micro_shift_ticks"])
        self.assertEqual(metadata["start_offset_ticks"], note_on_tick)
        self.assertGreaterEqual(note_on_tick, metadata["pause_ticks"])
        self.assertEqual(note_off_tick, metadata["pause_ticks"] + metadata["duration_ticks"])
        self.assertEqual(note_off_tick - note_on_tick, metadata["gate_ticks"])
        self.assertEqual(
            sum(message.time for message in midi.tracks[1]),
            app.sequencer_bars * app.TPB * 4,
        )

    def test_sixteenth_chord_timing_is_applied_to_midi(self):
        app = self.make_app_without_tk()
        app.C = 60
        app.TPB = 480
        app.sequencer_bars = 4
        app.sequencer_steps_per_bar = 16
        app.scale_map = {"maggiore": [0, 2, 4, 5, 7, 9, 11, 12]}

        app.build_sequencer_midi(
            "C",
            "maggiore",
            100,
            [0, 4, 5, 3],
            set(),
            chord_durations=["3/16", "1/1", "1/1", "1/1"],
            chord_pauses=["1/16", "Nessuna", "Nessuna", "Nessuna"],
        )

        metadata = app.sequencer_channel_metadata["Accordi"][0]
        self.assertEqual(metadata["duration_beats"], 0.75)
        self.assertEqual(metadata["pause_beats"], 0.25)
        self.assertEqual(metadata["duration_ticks"], 360)
        self.assertEqual(metadata["pause_ticks"], 120)
        with self.assertRaisesRegex(ValueError, "incrementi di 1/16"):
            app.build_sequencer_midi(
                "C",
                "maggiore",
                100,
                [0, 4, 5, 3],
                set(),
                chord_durations=["1/32", "1/1", "1/1", "1/1"],
            )

    def test_chord_timing_rejects_overlong_combinations_and_missing_bars(self):
        app = self.make_app_without_tk()
        app.C = 60
        app.TPB = 480
        app.sequencer_bars = 4
        app.sequencer_steps_per_bar = 16
        app.scale_map = {"maggiore": [0, 2, 4, 5, 7, 9, 11, 12]}

        with self.assertRaisesRegex(ValueError, "Battuta 1"):
            app.build_sequencer_midi(
                "C",
                "maggiore",
                100,
                [0, 4, 5, 3],
                set(),
                chord_durations=["1/1", "1/1", "1/1", "1/1"],
                chord_pauses=["1/8", "Nessuna", "Nessuna", "Nessuna"],
            )
        with self.assertRaisesRegex(ValueError, "per ogni battuta"):
            app.build_sequencer_midi(
                "C",
                "maggiore",
                100,
                [0, 4, 5, 3],
                set(),
                chord_durations=["1/2"],
            )

    def test_sequencer_midi_exports_four_chords_with_individual_timing(self):
        app = self.make_app_without_tk()
        app.C = 60
        app.TPB = 480
        app.sequencer_bars = 4
        app.sequencer_steps_per_bar = 16
        app.scale_map = {"maggiore": [0, 2, 4, 5, 7, 9, 11, 12]}
        chord_slots = [
            [
                (0, "1/4", "Nessuna"),
                (2, "3/16", "1/16"),
                (4, "1/4", "Nessuna"),
                (3, "3/16", "1/16"),
            ],
            [(4, "1/1", "Nessuna"), None, None, None],
            [(5, "1/1", "Nessuna"), None, None, None],
            [(3, "1/1", "Nessuna"), None, None, None],
        ]

        midi = app.build_sequencer_midi(
            "C",
            "maggiore",
            100,
            [0, 4, 5, 3],
            set(),
            chord_slots=chord_slots,
        )

        metadata = app.sequencer_channel_metadata["Accordi"]
        first_bar = [item for item in metadata if item["bar"] == 1]
        self.assertEqual([item["slot"] for item in first_bar], [1, 2, 3, 4])
        self.assertEqual(len(metadata), 7)
        cursor = 0
        for item in first_bar:
            self.assertEqual(
                item["start_offset_ticks"],
                cursor + item["pause_ticks"] + item["shift_ticks"],
            )
            cursor += item["pause_ticks"] + item["duration_ticks"]
        self.assertEqual(cursor, app.TPB * 4)

        events = list(self._absolute_events(midi.tracks[1]))
        chord_text_ticks = [
            tick for tick, message in events if message.type == "text"
        ]
        self.assertEqual(
            chord_text_ticks[:4],
            [item["start_offset_ticks"] for item in first_bar],
        )
        self.assertEqual(
            sum(message.type == "note_on" for _, message in events),
            21,
        )

    def test_sequencer_midi_rejects_overlong_multi_chord_bar(self):
        app = self.make_app_without_tk()
        app.C = 60
        app.TPB = 480
        app.sequencer_bars = 4
        app.sequencer_steps_per_bar = 16
        app.scale_map = {"maggiore": [0, 2, 4, 5, 7, 9, 11, 12]}
        chord_slots = [
            [
                (0, "1/2", "Nessuna"),
                (2, "1/2", "Nessuna"),
                (4, "1/16", "Nessuna"),
                None,
            ],
            [(4, "1/1", "Nessuna"), None, None, None],
            [(5, "1/1", "Nessuna"), None, None, None],
            [(3, "1/1", "Nessuna"), None, None, None],
        ]

        with self.assertRaisesRegex(ValueError, "Battuta 1, accordo 3"):
            app.build_sequencer_midi(
                "C",
                "maggiore",
                100,
                [0, 4, 5, 3],
                set(),
                chord_slots=chord_slots,
            )

    def test_whole_bar_chord_duration_matches_non_four_four_meter(self):
        app = self.make_app_without_tk()
        app.C = 60
        app.TPB = 480
        app.sequencer_bars = 4
        app.sequencer_steps_per_bar = 12
        app.scale_map = {"maggiore": [0, 2, 4, 5, 7, 9, 11, 12]}
        chord_slots = [
            [(0, "1/1", "Nessuna"), None, None, None],
            [(4, "1/1", "Nessuna"), None, None, None],
            [(5, "1/1", "Nessuna"), None, None, None],
            [(3, "1/1", "Nessuna"), None, None, None],
        ]

        app.build_sequencer_midi(
            "C",
            "maggiore",
            100,
            [0, 4, 5, 3],
            set(),
            time_signature=(3, 4),
            chord_slots=chord_slots,
        )

        self.assertEqual(
            app.sequencer_channel_metadata["Accordi"][0]["duration_ticks"],
            app.TPB * 3,
        )

    def test_sequencer_loop_includes_all_chords_in_selected_bar(self):
        app = self.make_app_without_tk()
        app.C = 60
        app.TPB = 480
        app.sequencer_bars = 4
        app.sequencer_steps_per_bar = 16
        app.scale_map = {"maggiore": [0, 2, 4, 5, 7, 9, 11, 12]}
        chord_slots = [
            [(0, "1/1", "Nessuna"), None, None, None],
            [(1, "1/2", "Nessuna"), (4, "1/2", "Nessuna"), None, None],
            [(5, "1/1", "Nessuna"), None, None, None],
            [(3, "1/1", "Nessuna"), None, None, None],
        ]

        midi = app.build_sequencer_midi(
            "C",
            "maggiore",
            100,
            [0, 4, 5, 3],
            set(),
            loop_bar=2,
            chord_slots=chord_slots,
        )

        metadata = app.sequencer_channel_metadata["Accordi"]
        self.assertEqual([item["bar"] for item in metadata], [2, 2])
        self.assertEqual([item["slot"] for item in metadata], [1, 2])
        self.assertEqual(
            sum(message.time for message in midi.tracks[1]),
            app.TPB * 4,
        )

    def test_sequencer_exposes_per_bar_chord_duration_and_pause_controls(self):
        root = tk.Tk()
        root.withdraw()
        app = music_harmonizer.MusicHarmonizerApp(root)
        try:
            self.assertEqual(len(app.sequencer_chord_duration_vars), 32)
            self.assertEqual(len(app.sequencer_chord_pause_vars), 32)
            self.assertEqual(len(app.sequencer_chord_slot_vars), 4)
            self.assertTrue(
                all(len(slot_vars) == 32 for slot_vars in app.sequencer_chord_slot_vars)
            )
            self.assertEqual(len(app.sequencer_chord_slot_combos), 4)
            self.assertTrue(
                all(len(combos) == 4 for combos in app.sequencer_chord_slot_combos)
            )
            self.assertEqual(app.sequencer_chord_slot_vars[1][0].get(), "—")
            self.assertEqual(len(app.sequencer_chord_duration_combos), 4)
            self.assertEqual(len(app.sequencer_chord_pause_combos), 4)
            self.assertEqual(
                app.sequencer_chord_duration_combos[0].cget("values"),
                app.get_sequencer_chord_duration_options(),
            )
            self.assertTrue(
                {"1/1", "1/2", "1/4", "1/8", "3/16", "1/16"}.issubset(
                    set(app.sequencer_chord_duration_combos[0].cget("values"))
                )
            )

            app.sequencer_chord_duration_vars[0].set("1/2")
            app.sequencer_chord_pause_vars[0].set("1/8")
            self.assertTrue(app.validate_sequencer_chord_timing())
            app.sequencer_chord_duration_vars[0].set("1/1")
            self.assertFalse(app.validate_sequencer_chord_timing())
            self.assertIn("Battuta 1", app.sequencer_status.cget("text"))
        finally:
            with patch("music_harmonizer.pygame.mixer.music.stop"), patch(
                "music_harmonizer.pygame.mixer.music.unload"
            ), patch("music_harmonizer.pygame.mixer.quit"):
                app.close()

    def test_chord_timeline_drag_moves_and_trims_on_sixteenth_grid(self):
        root = tk.Tk()
        root.withdraw()
        app = music_harmonizer.MusicHarmonizerApp(root)
        try:
            app.sequencer_chord_duration_vars[0].set("1/2")
            app.sequencer_chord_pause_vars[0].set("1/8")
            root.update_idletasks()
            self.assertTrue(app.sequencer_canvas.find_withtag("chord_block"))

            left = app.sequencer_chord_timeline_left
            top = app.sequencer_chord_timeline_top
            step_width = app.sequencer_chord_timeline_step_width
            middle_y = top + app.sequencer_chord_timeline_row_height // 2
            center_x = left + (2 + 4) * step_width
            app.begin_sequencer_mouse_action(
                SimpleNamespace(x=center_x, y=middle_y)
            )
            app.drag_sequencer_selection(
                SimpleNamespace(x=center_x + 2 * step_width, y=middle_y)
            )
            app.finish_sequencer_mouse_action(
                SimpleNamespace(x=center_x + 2 * step_width, y=middle_y)
            )
            self.assertEqual(app.sequencer_chord_pause_vars[0].get(), "1/4")
            self.assertEqual(app.sequencer_chord_duration_vars[0].get(), "1/2")

            left_edge_x = left + 4 * step_width + 2
            app.begin_sequencer_mouse_action(
                SimpleNamespace(x=left_edge_x, y=middle_y)
            )
            app.drag_sequencer_selection(
                SimpleNamespace(x=left_edge_x - step_width, y=middle_y)
            )
            app.finish_sequencer_mouse_action(
                SimpleNamespace(x=left_edge_x - step_width, y=middle_y)
            )
            self.assertEqual(app.sequencer_chord_pause_vars[0].get(), "3/16")
            self.assertEqual(app.sequencer_chord_duration_vars[0].get(), "9/16")

            right_edge_x = left + (3 + 9) * step_width - 2
            app.begin_sequencer_mouse_action(
                SimpleNamespace(x=right_edge_x, y=middle_y)
            )
            app.drag_sequencer_selection(
                SimpleNamespace(x=right_edge_x + step_width, y=middle_y)
            )
            app.finish_sequencer_mouse_action(
                SimpleNamespace(x=right_edge_x + step_width, y=middle_y)
            )
            self.assertEqual(app.sequencer_chord_pause_vars[0].get(), "3/16")
            self.assertEqual(app.sequencer_chord_duration_vars[0].get(), "5/8")

            right_edge_x = left + (3 + 10) * step_width - 2
            app.begin_sequencer_mouse_action(
                SimpleNamespace(x=right_edge_x, y=middle_y)
            )
            app.drag_sequencer_selection(
                SimpleNamespace(x=right_edge_x + 20 * step_width, y=middle_y)
            )
            app.finish_sequencer_mouse_action(
                SimpleNamespace(x=right_edge_x + 20 * step_width, y=middle_y)
            )
            self.assertEqual(app.sequencer_chord_duration_vars[0].get(), "13/16")

            left_edge_x = left + 3 * step_width + 2
            app.begin_sequencer_mouse_action(
                SimpleNamespace(x=left_edge_x, y=middle_y)
            )
            app.drag_sequencer_selection(
                SimpleNamespace(x=left_edge_x + 20 * step_width, y=middle_y)
            )
            app.finish_sequencer_mouse_action(
                SimpleNamespace(x=left_edge_x + 20 * step_width, y=middle_y)
            )
            self.assertEqual(app.sequencer_chord_pause_vars[0].get(), "15/16")
            self.assertEqual(app.sequencer_chord_duration_vars[0].get(), "1/16")
        finally:
            with patch("music_harmonizer.pygame.mixer.music.stop"), patch(
                "music_harmonizer.pygame.mixer.music.unload"
            ), patch("music_harmonizer.pygame.mixer.quit"):
                app.close()

    def test_chord_timeline_drag_targets_a_secondary_chord(self):
        root = tk.Tk()
        root.withdraw()
        app = music_harmonizer.MusicHarmonizerApp(root)
        try:
            app.sequencer_chord_duration_vars[0].set("1/2")
            app.sequencer_chord_slot_vars[1][0].set("5 - G")
            app.sequencer_chord_duration_slot_vars[1][0].set("1/4")
            app.refresh_sequencer_chords()
            root.update_idletasks()

            left = app.sequencer_chord_timeline_left
            top = app.sequencer_chord_timeline_top
            step_width = app.sequencer_chord_timeline_step_width
            middle_y = top + app.sequencer_chord_timeline_row_height // 2
            center_x = left + (8 + 2) * step_width
            app.begin_sequencer_mouse_action(
                SimpleNamespace(x=center_x, y=middle_y)
            )
            app.drag_sequencer_selection(
                SimpleNamespace(x=center_x + step_width, y=middle_y)
            )
            app.finish_sequencer_mouse_action(
                SimpleNamespace(x=center_x + step_width, y=middle_y)
            )

            self.assertEqual(
                app.sequencer_chord_pause_slot_vars[1][0].get(),
                "1/16",
            )
            self.assertEqual(
                app.sequencer_chord_duration_slot_vars[1][0].get(),
                "1/4",
            )
            self.assertEqual(app.sequencer_chord_duration_vars[0].get(), "1/2")
        finally:
            with patch("music_harmonizer.pygame.mixer.music.stop"), patch(
                "music_harmonizer.pygame.mixer.music.unload"
            ), patch("music_harmonizer.pygame.mixer.quit"):
                app.close()

    def test_sequencer_note_values_apply_frequency_based_gate_and_microshift(self):
        app = self.make_app_without_tk()
        app.C = 60
        app.TPB = 480
        app.sequencer_bars = 4
        app.sequencer_steps_per_bar = 16
        app.scale_map = {"maggiore": [0, 2, 4, 5, 7, 9, 11, 12]}

        for note_value, duration_steps in (
            ("1/1", 16),
            ("1/2", 8),
            ("1/4", 4),
            ("1/8", 2),
            ("1/16", 1),
            ("1/32", 0.5),
        ):
            with self.subTest(note_value=note_value):
                midi = app.build_sequencer_midi(
                    "C",
                    "maggiore",
                    100,
                    [0, 4, 5, 3],
                    {(0, 72)},
                    note_value=note_value,
                )
                metadata = app.sequencer_channel_metadata["Melodia"][0]
                track_events = list(self._absolute_events(midi.tracks[2]))
                on_tick = next(tick for tick, message in track_events if message.type == "note_on")
                off_tick = next(tick for tick, message in track_events if message.type == "note_off")
                nominal_end = duration_steps * (app.TPB // 4)

                self.assertEqual(metadata["duration_steps"], duration_steps)
                self.assertEqual(off_tick, nominal_end)
                self.assertEqual(off_tick - on_tick, metadata["gate_ticks"])
                self.assertAlmostEqual(
                    metadata["gate_ms"] + metadata["shift_ms"],
                    duration_steps * 150.0,
                )
                self.assertEqual(
                    metadata["cycles"],
                    round(metadata["frequency_hz"] * metadata["gate_ms"] / 1000),
                )

    def test_sequencer_note_entry_uses_selected_duration_and_draws_note_length(self):
        root = tk.Tk()
        root.withdraw()
        app = music_harmonizer.MusicHarmonizerApp(root)
        try:
            app.sequencer_note_duration_var.set("1/8")
            event = Mock(
                x=44 + 2 * app.sequencer_cell_width + 3,
                y=(
                    26
                    + app.sequencer_chord_timeline_height
                    + (app.sequencer_high_note - 60)
                    * app.sequencer_cell_height
                    + 3
                ),
            )
            with patch.object(app, "redraw_sequencer_grid"):
                app.begin_sequencer_mouse_action(event)
                app.finish_sequencer_mouse_action(event)

            self.assertIn((2, 60), app.sequencer_notes)
            self.assertEqual(app.sequencer_note_lengths[(2, 60)], 2)

            with patch.object(app.sequencer_canvas, "create_rectangle", wraps=app.sequencer_canvas.create_rectangle) as draw:
                app.redraw_sequencer_grid()
            note_rectangles = [
                call for call in draw.call_args_list
                if "melody_note" in call.kwargs.get("tags", ())
            ]
            self.assertEqual(len(note_rectangles), 1)
            self.assertEqual(
                note_rectangles[0].args[2] - note_rectangles[0].args[0],
                2 * app.sequencer_cell_width,
            )
        finally:
            with patch("music_harmonizer.pygame.mixer.music.stop"), patch(
                "music_harmonizer.pygame.mixer.music.unload"
            ), patch("music_harmonizer.pygame.mixer.quit"):
                app.close()

    def test_sequencer_loop_contains_only_selected_bar_and_one_bar_duration(self):
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
            {(0, 72), (16, 74), (32, 76)},
            note_value="1/4",
            loop_bar=2,
        )

        chord_events = list(self._absolute_events(midi.tracks[1]))
        melody_events = list(self._absolute_events(midi.tracks[2]))
        chord_notes = [message for _, message in chord_events if message.type == "note_on"]
        melody_notes = [message for _, message in melody_events if message.type == "note_on"]
        self.assertEqual(len(chord_notes), 3)
        self.assertEqual([message.note for message in melody_notes], [74])
        self.assertEqual(
            app.sequencer_channel_metadata["Accordi"][0]["bar"],
            2,
        )
        self.assertEqual(
            app.sequencer_channel_metadata["Melodia"][0]["bar"],
            2,
        )
        self.assertEqual(
            next(tick for tick, message in melody_events if message.type == "note_off"),
            app.TPB,
        )
        for track in midi.tracks:
            absolute_tick = sum(message.time for message in track)
            self.assertEqual(absolute_tick, app.TPB * 4)

    def test_sequencer_exports_selected_time_signatures_with_correct_bar_lengths(self):
        app = self.make_app_without_tk()
        app.C = 60
        app.TPB = 480
        app.sequencer_bars = 4
        app.scale_map = {"maggiore": [0, 2, 4, 5, 7, 9, 11, 12]}

        for signature, steps_per_bar, beats_per_bar in (
            ((4, 4), 16, 4),
            ((3, 4), 12, 3),
            ((5, 4), 20, 5),
            ((8, 16), 8, 2),
        ):
            with self.subTest(signature=signature):
                app.sequencer_steps_per_bar = steps_per_bar
                midi = app.build_sequencer_midi(
                    "C",
                    "maggiore",
                    100,
                    [0, 4, 5, 3],
                    set(),
                    time_signature=signature,
                )
                signature_event = next(
                    message
                    for message in midi.tracks[0]
                    if message.type == "time_signature"
                )
                self.assertEqual(
                    (signature_event.numerator, signature_event.denominator),
                    signature,
                )
                timing = app.sequencer_channel_metadata["Accordi"][0]
                expected_bar_ticks = round(app.TPB * beats_per_bar)
                self.assertEqual(timing["gate_ticks"] + timing["shift_ticks"], expected_bar_ticks)
                self.assertEqual(
                    timing["gate_ms"] + timing["shift_ms"],
                    beats_per_bar * 600.0,
                )

    def test_sequencer_midi_text_events_round_trip_with_chord_names(self):
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
            [0, 3, 4, 0],
            set(),
        )

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "chord-text.mid")
            midi.save(path)
            imported = music_harmonizer.MidiFile(path)

        events = list(self._absolute_events(imported.tracks[1]))
        text_events = [(tick, message.text) for tick, message in events if message.type == "text"]
        note_on_ticks = [tick for tick, message in events if message.type == "note_on"]
        self.assertEqual(len(text_events), 4)
        self.assertEqual([tick for tick, _ in text_events], [
            next(
                note_tick
                for note_tick, message in events
                if message.type == "note_on" and note_tick >= previous_tick
            )
            for previous_tick, _ in text_events
        ])
        self.assertIn("I Grado - C", text_events[0][1])
        self.assertIn("IV Grado - F", text_events[1][1])
        self.assertEqual(len(note_on_ticks), 12)

    def test_sequencer_supports_personal_scales_and_thirty_two_bars(self):
        app = self.make_app_without_tk()
        app.C = 60
        app.TPB = 480
        app.sequencer_bars = 32
        app.sequencer_steps_per_bar = 16
        app.scale_map = {"maggiore": [0, 2, 4, 5, 7, 9, 11, 12]}
        app.sequencer_custom_scale_intervals = [0, 2, 3, 5, 7, 8, 10]

        midi = app.build_sequencer_midi(
            "C",
            "personale",
            100,
            [0] * app.sequencer_bars,
            {(511, 72)},
        )

        self.assertEqual(len(app.sequencer_channel_metadata["Accordi"]), 32)
        self.assertEqual(app.sequencer_channel_metadata["Accordi"][0]["root_note"], 60)
        chord_events = [
            message for message in midi.tracks[1]
            if message.type in ("note_on", "note_off")
        ]
        self.assertEqual(sum(message.type == "note_on" for message in chord_events), 32 * 3)
        melody_starts = []
        absolute_tick = 0
        for message in midi.tracks[2]:
            absolute_tick += message.time
            if message.type == "note_on":
                melody_starts.append(absolute_tick)
        melody_metadata = app.sequencer_channel_metadata["Melodia"]
        self.assertEqual(
            melody_starts,
            [
                511 * (app.TPB // 4) + melody_metadata[0]["shift_ticks"]
            ],
        )

    def test_sequencer_scale_intervals_add_octave_when_personal_formula_omits_it(self):
        app = self.make_app_without_tk()
        app.scale_map = {}
        app.sequencer_custom_scale_intervals = [0, 3, 5, 7, 10]

        self.assertEqual(
            app.get_sequencer_scale_intervals("personale"),
            [0, 3, 5, 7, 10, 12],
        )

    @staticmethod
    def _absolute_events(events):
        absolute_tick = 0
        for message in events:
            absolute_tick += message.time
            yield absolute_tick, message

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
