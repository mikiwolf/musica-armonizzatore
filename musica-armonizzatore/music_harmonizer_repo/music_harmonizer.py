# Copyright (C) 2026 Mikiwolf
# SPDX-License-Identifier: GPL-3.0-or-later

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog
import pygame
import re
import shutil
import os
import tempfile
import math
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo

class MusicHarmonizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Harmonizer - Armonizzatore Musicale")
        self.root.geometry("1100x700")
        self.root.configure(bg="#f0f0f0")
        self._temp_directory = tempfile.TemporaryDirectory(prefix="music-harmonizer-")
        self._closed = False
        
        self.BPM = 90
        self.TPB = 480
        self.C = 60
        
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.note_italian = {
            '1': 'Do', '2': 'Re', '3': 'Mi', '4': 'Fa', 
            '5': 'Sol', '6': 'La', '7': 'Si'
        }
        self.scale_map = {
            'maggiore':[0,2,4,5,7,9,11,12],
            'minore_naturale':[0,2,3,5,7,8,10,12],
            'minore_armonica':[0,2,3,5,7,8,11,12],
            'minore_melodica':[0,2,3,5,7,9,11,12],
            'dorica':[0,2,3,5,7,9,10,12],
            'frigia':[0,1,3,5,7,8,10,12],
            'lidia':[0,2,4,6,7,9,11,12],
            'misolidia':[0,2,4,5,7,9,10,12],
            'locria':[0,1,3,5,6,8,10,12],
            'pentatonica_mag':[0,2,4,7,9,12],
            'pentatonica_min':[0,3,5,7,10,12],
            'blues':[0,3,5,6,7,10,12],
            'bebop_dominante':[0,2,4,5,7,9,10,11,12],
            'bebop_minore':[0,2,3,4,5,7,9,11,12],
            'diminuita':[0,2,3,5,6,8,9,11,12],
            'aumentata':[0,3,4,8,9,12],
            'araba':[0,2,3,5,7,8,11,12],
            'araba_maggiore':[0,2,4,5,7,8,11,12],
            'araba_minore':[0,2,3,5,7,8,10,12],
            'orientale':[0,1,4,5,7,8,11,12],
            'orientale_maggiore':[0,2,4,6,7,8,10,12],
            'orientale_minore':[0,2,3,6,7,8,10,12],
            'persiana':[0,1,4,5,7,8,11,12],
            'persiana_maggiore':[0,1,4,5,7,8,11,12],
            'persiana_minore':[0,1,3,5,6,8,10,12],
            'russa':[0,2,3,6,7,9,10,12],
            'russa_maggiore':[0,2,4,6,7,9,10,12],
            'russa_minore':[0,2,3,5,7,8,10,12],
            'rumena':[0,2,3,6,7,9,10,12],
            'rumena_maggiore':[0,2,3,6,7,9,10,12],
            'rumena_minore':[0,2,3,5,7,8,10,12],
            'ungherese':[0,2,3,6,7,8,11,12],
            'ungherese_maggiore':[0,2,4,6,7,8,11,12],
            'ungherese_minore':[0,2,3,6,7,8,11,12],
            'egizia':[0,2,4,5,8,10,12],
            'egizia_maggiore':[0,2,4,7,9,11,12],
            'egizia_minore':[0,2,3,7,9,10,12],
            'enigmatica':[0,1,4,6,8,10,11,12],
            'enigmatica_maggiore':[0,1,4,6,8,10,11,12],
            'enigmatica_minore':[0,2,3,6,8,9,10,12],
            'double_harmonic':[0,1,4,5,7,8,11,12],
            'double_harmonic_maggiore':[0,1,4,5,7,8,11,12],
            'double_harmonic_minore':[0,2,3,5,7,8,11,12],
            'napoletana':[0,1,3,5,7,8,10,12],
            'napoletana_maggiore':[0,1,3,5,7,8,10,12],
            'napoletana_minore':[0,1,3,5,7,8,10,12],
        }
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.frame_predefinite = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_predefinite, text="📚 Scale Predefinite")
        self.setup_tab_predefinite()
        
        self.frame_personalizzate = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_personalizzate, text="✏️ Note Musicali")
        self.setup_tab_note_musicali()

        self.frame_sequencer = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_sequencer, text="🎼 Sequencer")
        self.setup_tab_sequencer()
        
        self.audio_available = True
        self.audio_error = ""
        try:
            pygame.mixer.init()
        except Exception as exc:
            self.audio_available = False
            self.audio_error = str(exc)
            self.label_status = ttk.Label(self.frame_predefinite, text="⚠️ Audio non disponibile", foreground="orange", font=("Arial", 8))
            self.label_status.pack(fill=tk.X, pady=3)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def close(self):
        if self._closed:
            return

        self._closed = True
        try:
            try:
                if self.audio_available:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
            finally:
                if self.audio_available:
                    pygame.mixer.quit()
        finally:
            try:
                self._temp_directory.cleanup()
            finally:
                self.root.destroy()
    
    def setup_tab_predefinite(self):
        main_frame = ttk.Frame(self.frame_predefinite)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== RIGA 1: TONO =====
        frame_tono = ttk.LabelFrame(main_frame, text="1. Tono", padding="5")
        frame_tono.pack(fill=tk.X, pady=3)
        
        ttk.Label(frame_tono, text="Base:").pack(side=tk.LEFT, padx=2)
        self.var_tono = tk.StringVar(value="C")
        combo_tono = ttk.Combobox(frame_tono, textvariable=self.var_tono, 
                                   values=self.note_names, state="readonly", width=4)
        combo_tono.pack(side=tk.LEFT, padx=2)
        
        # ===== RIGA 2: SCALA (2 colonne) =====
        frame_scala = ttk.LabelFrame(main_frame, text="2. Scala", padding="5")
        frame_scala.pack(fill=tk.BOTH, expand=True, pady=3)
        
        self.var_scala = tk.StringVar(value="maggiore")
        
        scales = [
            ("Maggiore", "maggiore"),
            ("Minore Nat.", "minore_naturale"),
            ("Minore Arm.", "minore_armonica"),
            ("Minore Mel.", "minore_melodica"),
            ("Dorica", "dorica"),
            ("Frigia", "frigia"),
            ("Lidia", "lidia"),
            ("Misolidia", "misolidia"),
            ("Locria", "locria"),
            ("Pent. Mag.", "pentatonica_mag"),
            ("Pent. Min.", "pentatonica_min"),
            ("Blues", "blues"),
            ("Bebop Dom.", "bebop_dominante"),
            ("Bebop Min.", "bebop_minore"),
            ("Diminuita", "diminuita"),
            ("Aumentata", "aumentata"),
            ("Araba Mag.", "araba_maggiore"),
            ("Araba Min.", "araba_minore"),
            ("Orientale Mag.", "orientale_maggiore"),
            ("Orientale Min.", "orientale_minore"),
            ("Persiana Mag.", "persiana_maggiore"),
            ("Persiana Min.", "persiana_minore"),
            ("Russa Mag.", "russa_maggiore"),
            ("Russa Min.", "russa_minore"),
            ("Rumena Mag.", "rumena_maggiore"),
            ("Rumena Min.", "rumena_minore"),
            ("Ungherese Mag.", "ungherese_maggiore"),
            ("Ungherese Min.", "ungherese_minore"),
            ("Egizia Mag.", "egizia_maggiore"),
            ("Egizia Min.", "egizia_minore"),
            ("Enigmatica Mag.", "enigmatica_maggiore"),
            ("Enigmatica Min.", "enigmatica_minore"),
            ("Double Harmonic Mag.", "double_harmonic_maggiore"),
            ("Double Harmonic Min.", "double_harmonic_minore"),
            ("Napoletana Mag.", "napoletana_maggiore"),
            ("Napoletana Min.", "napoletana_minore"),
        ]
        
        button_frame = ttk.Frame(frame_scala)
        button_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = 4
        for index, (label, value) in enumerate(scales):
            row = index // columns
            col = index % columns
            ttk.Radiobutton(button_frame, text=label, variable=self.var_scala,
                           value=value).grid(row=row, column=col, sticky="w", padx=5, pady=2)
        for c in range(columns):
            button_frame.columnconfigure(c, weight=1)
        
        # ===== RIGA 3: ARMONIZZAZIONE =====
        frame_armonizzazione = ttk.LabelFrame(main_frame, text="3. Armonizzazione", padding="5")
        frame_armonizzazione.pack(fill=tk.X, pady=3)
        
        self.var_armonia = tk.StringVar(value="terze")
        
        armonizzazioni = [
            ("Seconde", "seconde"),
            ("Terze", "terze"),
            ("Quarte", "quarte"),
            ("Quinte", "quinte"),
            ("Seste", "seste"),
            ("Settime", "settime"),
            ("Ottave", "ottave"),
        ]
        
        for label, value in armonizzazioni:
            ttk.Radiobutton(frame_armonizzazione, text=label, variable=self.var_armonia, 
                           value=value).pack(side=tk.LEFT, padx=5)
        
        # ===== RIGA 4: BPM =====
        frame_parametri = ttk.LabelFrame(main_frame, text="4. BPM", padding="5")
        frame_parametri.pack(fill=tk.X, pady=3)
        
        self.var_bpm = tk.StringVar(value="90")
        ttk.Spinbox(frame_parametri, from_=40, to=200, textvariable=self.var_bpm, 
               width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(frame_parametri, text="Voci:").pack(side=tk.LEFT, padx=6)
        self.var_voci = tk.IntVar(value=2)
        ttk.Spinbox(frame_parametri, from_=1, to=8, textvariable=self.var_voci, width=3).pack(side=tk.LEFT, padx=2)
        
        # ===== RIGA 5: BOTTONI =====
        frame_bottoni = ttk.Frame(main_frame)
        frame_bottoni.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame_bottoni, text="▶ Ascolta", 
                  command=self.genera_e_ascolta_predefinita, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_bottoni, text="💾 Salva", 
                  command=self.salva_predefinita_cartella, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_bottoni, text="⏹ Ferma", 
                  command=self.ferma_riproduzione, width=15).pack(side=tk.LEFT, padx=2)
        
        # ===== STATUS =====
        self.label_status = ttk.Label(main_frame, text="Pronto...", foreground="blue", font=("Arial", 8))
        self.label_status.pack(fill=tk.X, pady=3)
    
    def setup_tab_note_musicali(self):
        main_frame = ttk.Frame(self.frame_personalizzate)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=3)
        
        bottom_frame = ttk.Frame(main_frame)
        
        # ===== INFO =====
        info_frame = ttk.LabelFrame(top_frame, text="Istruzioni", padding="3")
        info_frame.pack(fill=tk.X, pady=3)
        instructions = (
            "Scrivi la scala usando gradi diatonici: 1 2 3 4 5 6 7 8. "
            "Usa # per il diesis e b per il bemolle, ad esempio 3b o 4#. "
            "La nota 8 indica l'ottava successiva di 1.\n"
            "Esempi: 1 2 3b 4 5 6b 7b 8 (minore naturale), "
            "1 2 3 4# 5 6 7 8 (lidia), 1 2 3b 5 6 7b 8 (pent. minore).\n"
            "Premi Analizza per vedere accordi, rivolti e funzione armonica; Ascolta per suonare la scala."
        )
        ttk.Label(info_frame, text=instructions, font=("Arial", 8), justify=tk.LEFT, wraplength=1000).pack(anchor=tk.W)
        
        # ===== INPUT NOTE =====
        frame_input = ttk.LabelFrame(top_frame, text="Scala", padding="3")
        frame_input.pack(fill=tk.X, pady=3)
        
        ttk.Label(frame_input, text="Tono:").pack(side=tk.LEFT, padx=2)
        self.var_tono_pers = tk.StringVar(value="C")
        ttk.Combobox(frame_input, textvariable=self.var_tono_pers, 
                    values=self.note_names, state="readonly", width=4).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(frame_input, text="Nome:").pack(side=tk.LEFT, padx=2)
        self.var_nome_scala_pers = tk.StringVar(value="MiaScala")
        ttk.Entry(frame_input, textvariable=self.var_nome_scala_pers, width=12).pack(side=tk.LEFT, padx=2)
        
        # ===== NOTE =====
        frame_note = ttk.LabelFrame(top_frame, text="Note", padding="3")
        frame_note.pack(fill=tk.X, pady=3)
        
        self.text_note = tk.Text(frame_note, height=2, width=100)
        self.text_note.pack(pady=2, fill=tk.X)
        self.text_note.insert(tk.END, "1 2 3 4 5 6 7 8")
        
        # ===== PRESETS =====
        frame_rapidi = ttk.LabelFrame(top_frame, text="Presets", padding="3")
        frame_rapidi.pack(fill=tk.X, pady=3)
        
        self.presets_note = {
            "Magg.": "1 2 3 4 5 6 7 8",
            "Min.Nat.": "1 2 3b 4 5 6b 7b 8",
            "Min.Arm.": "1 2 3b 4 5 6b 7 8",
            "Bebop": "1 3b 4 5 6 6# 7 8",
            "Dimin.": "1 3b 5b 6 8",
        }
        
        presets_frame = ttk.Frame(frame_rapidi)
        presets_frame.pack(fill=tk.X)
        for index, (nome, note) in enumerate(self.presets_note.items()):
            ttk.Button(presets_frame, text=nome, width=10,
                      command=lambda v=note, n=nome: self.seleziona_preset_note(v, n)).grid(row=0, column=index, padx=4, pady=2)
        for c in range(len(self.presets_note)):
            presets_frame.columnconfigure(c, weight=1)
        
        # ===== ANALISI =====
        frame_analisi = ttk.LabelFrame(bottom_frame, text="Analisi", padding="3")
        frame_analisi.pack(fill=tk.BOTH, expand=True, pady=3)
        
        self.text_analisi = tk.Text(
            frame_analisi,
            height=12,
            width=100,
            bg="white",
            state=tk.DISABLED,
            font=("Segoe UI", 9),
            wrap=tk.WORD,
        )
        self.text_analisi.tag_configure("title", font=("Segoe UI", 11, "bold"), foreground="#17365d")
        self.text_analisi.tag_configure("section", font=("Segoe UI", 9, "bold"), foreground="#1f4e79")
        self.text_analisi.tag_configure("degree", font=("Segoe UI", 9, "bold"))
        self.text_analisi.tag_configure("tendency", foreground="#555555")
        scrollbar_analisi = ttk.Scrollbar(frame_analisi, orient=tk.VERTICAL, command=self.text_analisi.yview)
        self.text_analisi.configure(yscrollcommand=scrollbar_analisi.set)
        scrollbar_analisi.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_analisi.pack(padx=4, pady=4, fill=tk.BOTH, expand=True)
        
        # ===== CONFIG =====
        frame_config = ttk.LabelFrame(main_frame, text="Armonizzazione per ascolto e MIDI", padding="5")
        frame_config.pack(fill=tk.X, pady=3)
        
        ttk.Label(frame_config, text="Intervallo:").pack(side=tk.LEFT, padx=2)
        self.var_armonia_pers = tk.StringVar(value="terze")
        ttk.Combobox(frame_config, textvariable=self.var_armonia_pers,
                    values=["seconde", "terze", "quarte", "quinte", "seste", "settime", "ottave"],
                    state="readonly", width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(frame_config, text="BPM:").pack(side=tk.LEFT, padx=2)
        self.var_bpm_pers = tk.StringVar(value="90")
        ttk.Spinbox(frame_config, from_=40, to=200, textvariable=self.var_bpm_pers, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(frame_config, text="Voci:").pack(side=tk.LEFT, padx=6)
        self.var_voci_pers = tk.IntVar(value=2)
        ttk.Spinbox(frame_config, from_=1, to=8, textvariable=self.var_voci_pers, width=3).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(frame_config, text="Analizza", command=self.analizza_note, width=10).pack(side=tk.LEFT, padx=2)
        
        # ===== BOTTONI =====
        frame_bottoni_pers = ttk.Frame(main_frame)
        frame_bottoni_pers.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame_bottoni_pers, text="▶ Ascolta", 
                  command=self.genera_e_ascolta_note, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_bottoni_pers, text="💾 Salva", 
                  command=self.salva_note_cartella, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_bottoni_pers, text="⏹ Ferma", 
                  command=self.ferma_riproduzione, width=15).pack(side=tk.LEFT, padx=2)
        
        self.label_status_pers = ttk.Label(main_frame, text="Pronto...", foreground="blue", font=("Arial", 8))
        self.label_status_pers.pack(fill=tk.X, pady=3)
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=3)

    def setup_tab_sequencer(self):
        self.sequencer_notes = set()
        self.sequencer_note_lengths = {}
        self.sequencer_note_duration_steps = {
            "1/1": 16,
            "1/2": 8,
            "1/4": 4,
            "1/8": 2,
            "1/16": 1,
            "1/32": 0.5,
        }
        self.sequencer_steps_per_bar = 16
        self.sequencer_bars = 32
        self.sequencer_bars_per_page = 4
        self.sequencer_page = 0
        self.sequencer_octave = 3
        self.sequencer_low_note = (self.sequencer_octave + 1) * 12
        self.sequencer_high_note = self.sequencer_low_note + 23
        self.sequencer_cell_width = 14
        self.sequencer_cell_height = 22
        self.sequencer_chord_vars = []
        self.sequencer_chord_combos = []
        self.sequencer_custom_scale_intervals = [0, 2, 4, 5, 7, 9, 11, 12]
        self.sequencer_selected_notes = set()
        self.sequencer_selection_box = None
        self.sequencer_selection_start = None
        self.sequencer_selection_current = None
        self.sequencer_clipboard = ()
        self.sequencer_paste_armed = False

        controls = ttk.LabelFrame(self.frame_sequencer, text="Impostazioni", padding=5)
        controls.pack(fill=tk.X, padx=6, pady=5)

        ttk.Label(controls, text="Tonalità:").pack(side=tk.LEFT, padx=(0, 3))
        self.sequencer_key_var = tk.StringVar(value="C")
        ttk.Combobox(
            controls,
            textvariable=self.sequencer_key_var,
            values=self.note_names,
            state="readonly",
            width=5,
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(controls, text="Scala:").pack(side=tk.LEFT, padx=(0, 3))
        self.sequencer_scale_var = tk.StringVar(value="maggiore")
        ttk.Combobox(
            controls,
            textvariable=self.sequencer_scale_var,
            values=[*self.scale_map, "personale"],
            state="readonly",
            width=20,
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(controls, text="BPM:").pack(side=tk.LEFT, padx=(0, 3))
        self.sequencer_bpm_var = tk.StringVar(value="100")
        ttk.Spinbox(
            controls,
            from_=40,
            to=200,
            textvariable=self.sequencer_bpm_var,
            width=5,
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(controls, text="Metro:").pack(side=tk.LEFT, padx=(0, 3))
        self.sequencer_time_signature_var = tk.StringVar(value="4/4")
        time_signature_combo = ttk.Combobox(
            controls,
            textvariable=self.sequencer_time_signature_var,
            values=("4/4", "3/4", "5/4", "2/4", "6/8", "7/8", "9/8", "12/8", "8/16"),
            state="readonly",
            width=6,
        )
        time_signature_combo.pack(side=tk.LEFT, padx=(0, 10))
        time_signature_combo.bind(
            "<<ComboboxSelected>>", self.update_sequencer_time_signature
        )

        ttk.Label(controls, text="Durata note:").pack(side=tk.LEFT, padx=(0, 3))
        self.sequencer_note_duration_var = tk.StringVar(value="1/16")
        ttk.Combobox(
            controls,
            textvariable=self.sequencer_note_duration_var,
            values=tuple(self.sequencer_note_duration_steps),
            state="readonly",
            width=5,
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(controls, text="Armonia:").pack(side=tk.LEFT, padx=(0, 3))
        self.sequencer_harmony_var = tk.StringVar(value="terze")
        ttk.Combobox(
            controls,
            textvariable=self.sequencer_harmony_var,
            values=("terze", "quarte", "quinte"),
            state="readonly",
            width=8,
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(controls, text="Voci:").pack(side=tk.LEFT, padx=(0, 3))
        self.sequencer_voices_var = tk.IntVar(value=3)
        ttk.Spinbox(
            controls,
            from_=3,
            to=5,
            textvariable=self.sequencer_voices_var,
            width=3,
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(controls, text="Ottava:").pack(side=tk.LEFT, padx=(0, 3))
        self.sequencer_octave_var = tk.StringVar(value=str(self.sequencer_octave))
        octave_combo = ttk.Combobox(
            controls,
            textvariable=self.sequencer_octave_var,
            values=tuple(str(octave) for octave in range(2, 8)),
            state="readonly",
            width=3,
        )
        octave_combo.pack(side=tk.LEFT, padx=(0, 10))
        octave_combo.bind("<<ComboboxSelected>>", self.change_sequencer_octave)

        ttk.Label(controls, text="Griglia: 1/16 · clic note · trascina selezione · Ctrl+C/Ctrl+V").pack(
            side=tk.LEFT, padx=5
        )

        custom_scale = ttk.LabelFrame(
            self.frame_sequencer,
            text="Scala personale (gradi e alterazioni, per esempio: 1 2 3b 4 5 6b 7b 8)",
            padding=5,
        )
        custom_scale.pack(fill=tk.X, padx=6, pady=3)
        self.sequencer_custom_scale_var = tk.StringVar(value="1 2 3 4 5 6 7 8")
        ttk.Entry(
            custom_scale,
            textvariable=self.sequencer_custom_scale_var,
            width=50,
        ).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(
            custom_scale,
            text="Applica scala personale",
            command=self.apply_sequencer_custom_scale,
        ).pack(side=tk.LEFT)

        progression = ttk.LabelFrame(self.frame_sequencer, text="Progressione (un accordo per battuta)", padding=5)
        progression.pack(fill=tk.X, padx=6, pady=4)
        navigation = ttk.Frame(progression)
        navigation.pack(fill=tk.X)
        ttk.Button(navigation, text="◀ Pagina", command=lambda: self.change_sequencer_page(-1)).pack(
            side=tk.LEFT, padx=2
        )
        self.sequencer_page_label = ttk.Label(navigation, text="")
        self.sequencer_page_label.pack(side=tk.LEFT, padx=8)
        ttk.Button(navigation, text="Pagina ▶", command=lambda: self.change_sequencer_page(1)).pack(
            side=tk.LEFT, padx=2
        )
        self.sequencer_progression_page = ttk.Frame(progression)
        self.sequencer_progression_page.pack(fill=tk.X, pady=(4, 0))
        self.sequencer_chord_vars = [
            tk.StringVar(value=str([1, 5, 6, 4][bar % 4]))
            for bar in range(self.sequencer_bars)
        ]

        self.sequencer_scale_var.trace_add("write", self.refresh_sequencer_chords)
        self.sequencer_key_var.trace_add("write", self.refresh_sequencer_chords)
        self.render_sequencer_progression_page()
        self.refresh_sequencer_chords()

        grid_frame = ttk.Frame(self.frame_sequencer)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        self.sequencer_canvas = tk.Canvas(grid_frame, background="white", highlightthickness=1)
        horizontal = ttk.Scrollbar(grid_frame, orient=tk.HORIZONTAL, command=self.sequencer_canvas.xview)
        vertical = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.sequencer_canvas.yview)
        self.sequencer_canvas.configure(
            xscrollcommand=horizontal.set,
            yscrollcommand=vertical.set,
        )
        self.sequencer_canvas.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        grid_frame.rowconfigure(0, weight=1)
        grid_frame.columnconfigure(0, weight=1)
        self.sequencer_canvas.bind("<Button-1>", self.begin_sequencer_mouse_action)
        self.sequencer_canvas.bind("<B1-Motion>", self.drag_sequencer_selection)
        self.sequencer_canvas.bind("<ButtonRelease-1>", self.finish_sequencer_mouse_action)
        self.sequencer_canvas.bind("<Control-c>", self.copy_sequencer_notes)
        self.sequencer_canvas.bind("<Control-C>", self.copy_sequencer_notes)
        self.sequencer_canvas.bind("<Control-v>", self.arm_sequencer_paste)
        self.sequencer_canvas.bind("<Control-V>", self.arm_sequencer_paste)

        actions = ttk.Frame(self.frame_sequencer)
        actions.pack(fill=tk.X, padx=6, pady=4)
        ttk.Button(actions, text="Copia", command=self.copy_sequencer_notes).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions, text="Incolla", command=self.arm_sequencer_paste).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions, text="▶ Ascolta", command=self.play_sequencer).pack(side=tk.LEFT, padx=2)
        ttk.Label(actions, text="Loop battuta:").pack(side=tk.LEFT, padx=(8, 2))
        self.sequencer_loop_bar_var = tk.StringVar(value="1")
        ttk.Spinbox(
            actions,
            from_=1,
            to=self.sequencer_bars,
            textvariable=self.sequencer_loop_bar_var,
            width=3,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions, text="⟳ Loop", command=self.loop_sequencer_bar).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions, text="⏹ Ferma", command=self.ferma_riproduzione).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions, text="💾 Esporta MIDI", command=self.save_sequencer).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions, text="Svuota melodia", command=self.clear_sequencer).pack(side=tk.LEFT, padx=2)
        ttk.Label(actions, text="Blu: scala · Verde chiaro: accordi").pack(side=tk.LEFT, padx=8)
        self.sequencer_status = ttk.Label(actions, text="Pronto", foreground="blue")
        self.sequencer_status.pack(side=tk.LEFT, padx=8)
        self.redraw_sequencer_grid()

    def change_sequencer_octave(self, *_):
        try:
            octave = int(self.sequencer_octave_var.get())
        except ValueError:
            return
        if not 2 <= octave <= 7:
            return
        self.sequencer_octave = octave
        self.sequencer_low_note = (octave + 1) * 12
        self.sequencer_high_note = self.sequencer_low_note + 23
        self.sequencer_selected_notes.clear()
        self.sequencer_selection_box = None
        self.redraw_sequencer_grid()

    @staticmethod
    def parse_sequencer_time_signature(value):
        match = re.fullmatch(r"\s*(\d+)\s*/\s*(\d+)\s*", value)
        if match is None:
            raise ValueError("Metro non valido; usa una forma come 4/4 o 6/8")
        numerator, denominator = map(int, match.groups())
        if not 1 <= numerator <= 16 or denominator not in (2, 4, 8, 16):
            raise ValueError("Usa un numeratore da 1 a 16 e denominatore 2, 4, 8 o 16")
        steps_per_bar = numerator * 16 / denominator
        if not steps_per_bar.is_integer():
            raise ValueError("Il metro selezionato non è rappresentabile sulla griglia")
        return numerator, denominator, int(steps_per_bar)

    def update_sequencer_time_signature(self, *_):
        try:
            _, _, steps_per_bar = self.parse_sequencer_time_signature(
                self.sequencer_time_signature_var.get()
            )
        except ValueError as exc:
            self.sequencer_status.config(text=str(exc), foreground="red")
            return

        old_steps_per_bar = self.sequencer_steps_per_bar
        if steps_per_bar != old_steps_per_bar:
            remapped_notes = set()
            remapped_lengths = {}
            for step, pitch in self.sequencer_notes:
                bar, step_in_bar = divmod(step, old_steps_per_bar)
                new_step = bar * steps_per_bar + min(step_in_bar, steps_per_bar - 1)
                remapped_notes.add((new_step, pitch))
                if (step, pitch) in self.sequencer_note_lengths:
                    remapped_lengths[(new_step, pitch)] = self.sequencer_note_lengths[
                        (step, pitch)
                    ]
            self.sequencer_notes = remapped_notes
            self.sequencer_note_lengths = remapped_lengths
            self.sequencer_steps_per_bar = steps_per_bar
            self.sequencer_selected_notes.clear()
            self.sequencer_selection_box = None
        self.redraw_sequencer_grid()

    def get_sequencer_time_signature(self):
        value = getattr(self, "sequencer_time_signature_var", None)
        if value is None:
            return 4, 4
        numerator, denominator, _ = self.parse_sequencer_time_signature(value.get())
        return numerator, denominator

    def get_sequencer_scale(self):
        key = self.sequencer_key_var.get()
        scale_name = self.sequencer_scale_var.get()
        if key not in self.note_names:
            raise ValueError("Seleziona una tonalità e una scala valide")
        if scale_name == "personale":
            intervals = self.get_sequencer_scale_intervals(scale_name)
        elif scale_name in self.scale_map:
            intervals = self.get_sequencer_scale_intervals(scale_name)
        else:
            raise ValueError("Seleziona una tonalità e una scala valide")
        base = self.C + self.note_names.index(key)
        return [base + interval for interval in intervals]

    def get_sequencer_scale_intervals(self, scale_name):
        if scale_name == "personale":
            intervals = list(self.sequencer_custom_scale_intervals)
        elif scale_name in self.scale_map:
            intervals = list(self.scale_map[scale_name])
        else:
            raise ValueError("Scala non valida")
        if intervals[-1] != 12:
            intervals.append(12)
        return intervals

    def apply_sequencer_custom_scale(self):
        intervals = self.parse_note_input(self.sequencer_custom_scale_var.get())
        if intervals is None:
            self.sequencer_status.config(text="Scala personale non valida", foreground="red")
            return
        self.sequencer_custom_scale_intervals = intervals
        self.sequencer_scale_var.set("personale")
        self.refresh_sequencer_chords()
        self.sequencer_status.config(text="Scala personale applicata", foreground="green")

    def render_sequencer_progression_page(self):
        for child in self.sequencer_progression_page.winfo_children():
            child.destroy()

        first_bar = self.sequencer_page * self.sequencer_bars_per_page
        last_bar = min(first_bar + self.sequencer_bars_per_page, self.sequencer_bars)
        self.sequencer_page_label.config(
            text=f"Battute {first_bar + 1}–{last_bar} / {self.sequencer_bars}"
        )
        self.sequencer_chord_combos = []
        for bar in range(first_bar, last_bar):
            ttk.Label(self.sequencer_progression_page, text=f"Battuta {bar + 1}:").pack(
                side=tk.LEFT, padx=(4, 2)
            )
            combo = ttk.Combobox(
                self.sequencer_progression_page,
                textvariable=self.sequencer_chord_vars[bar],
                state="readonly",
                width=16,
            )
            combo.pack(side=tk.LEFT, padx=(0, 8))
            combo.bind("<<ComboboxSelected>>", self.redraw_sequencer_grid)
            self.sequencer_chord_combos.append(combo)

    def change_sequencer_page(self, page_delta):
        last_page = (self.sequencer_bars - 1) // self.sequencer_bars_per_page
        self.sequencer_page = min(max(self.sequencer_page + page_delta, 0), last_page)
        self.sequencer_selected_notes.clear()
        self.sequencer_selection_box = None
        self.render_sequencer_progression_page()
        self.refresh_sequencer_chords()

    def get_sequencer_chord_degrees(self):
        scale_size = len(self.get_sequencer_scale()) - 1
        degrees = []
        for index, chord_var in enumerate(self.sequencer_chord_vars):
            match = re.match(r"\s*(\d+)", chord_var.get())
            degree = int(match.group(1)) - 1 if match else [0, 4, 5, 3][index]
            degrees.append(min(max(degree, 0), scale_size - 1))
        return degrees

    def refresh_sequencer_chords(self, *_):
        if not hasattr(self, "sequencer_chord_combos"):
            return
        try:
            scale = self.get_sequencer_scale()
            scale_size = len(scale) - 1
            for chord_var in self.sequencer_chord_vars:
                match = re.match(r"\s*(\d+)", chord_var.get())
                degree = int(match.group(1)) - 1 if match else 0
                degree = min(max(degree, 0), scale_size - 1)
                root = scale[degree]
                notes = self.build_chord_notes(root, "terze", 3, scale)
                label = self.get_chord_label(notes, root=root)
                options = []
                for option_degree, option_root in enumerate(scale[:-1]):
                    chord = self.build_chord_notes(option_root, "terze", 3, scale)
                    options.append(
                        f"{option_degree + 1} - {self.get_chord_label(chord, root=option_root)}"
                    )
                chord_var.set(f"{degree + 1} - {label}")
            first_bar = self.sequencer_page * self.sequencer_bars_per_page
            for combo, chord_var in zip(
                self.sequencer_chord_combos,
                self.sequencer_chord_vars[first_bar:first_bar + self.sequencer_bars_per_page],
            ):
                options = [
                    f"{degree + 1} - {self.get_chord_label(self.build_chord_notes(root, 'terze', 3, scale), root=root)}"
                    for degree, root in enumerate(scale[:-1])
                ]
                combo.configure(values=options)
            self.redraw_sequencer_grid()
        except (ValueError, tk.TclError) as exc:
            self.sequencer_status.config(text=f"Impossibile aggiornare gli accordi: {exc}", foreground="red")

    def redraw_sequencer_grid(self, *_):
        if not hasattr(self, "sequencer_canvas"):
            return
        canvas = self.sequencer_canvas
        canvas.delete("all")
        left = 44
        top = 26
        cell_width = self.sequencer_cell_width
        cell_height = self.sequencer_cell_height
        first_bar = self.sequencer_page * self.sequencer_bars_per_page
        visible_bars = min(self.sequencer_bars_per_page, self.sequencer_bars - first_bar)
        visible_steps = visible_bars * self.sequencer_steps_per_bar
        try:
            _, denominator = self.get_sequencer_time_signature()
            steps_per_beat = 16 // denominator
        except ValueError:
            steps_per_beat = 4
        width = left + visible_steps * cell_width
        height = top + (self.sequencer_high_note - self.sequencer_low_note + 1) * cell_height

        try:
            scale = self.get_sequencer_scale()
            chord_degrees = self.get_sequencer_chord_degrees()
            scale_pcs = {note % 12 for note in scale}
            chord_pcs_by_bar = []
            for degree in chord_degrees[first_bar:first_bar + visible_bars]:
                chord = self.build_chord_notes(scale[degree], "terze", 3, scale)
                chord_pcs_by_bar.append({note % 12 for note in chord})
        except (ValueError, tk.TclError):
            scale_pcs = set()
            chord_pcs_by_bar = [set() for _ in range(visible_bars)]

        for visible_bar in range(visible_bars):
            bar_x = left + visible_bar * self.sequencer_steps_per_bar * cell_width
            canvas.create_text(
                bar_x + self.sequencer_steps_per_bar * cell_width / 2,
                12,
                text=f"Battuta {first_bar + visible_bar + 1}",
                fill="#333333",
            )

        for pitch in range(self.sequencer_high_note, self.sequencer_low_note - 1, -1):
            row = self.sequencer_high_note - pitch
            y = top + row * cell_height
            canvas.create_text(left - 6, y + cell_height / 2, text=self.get_note_name(pitch), anchor=tk.E, fill="#333333")
            for visible_step in range(visible_steps):
                bar = visible_step // self.sequencer_steps_per_bar
                absolute_step = first_bar * self.sequencer_steps_per_bar + visible_step
                x = left + visible_step * cell_width
                chord_tone = pitch % 12 in chord_pcs_by_bar[bar]
                pitch_class = pitch % 12
                if chord_tone:
                    fill = "#c8e6c9"
                elif pitch_class in scale_pcs:
                    fill = "#244f78"
                else:
                    fill = "#f0f0f0" if pitch_class in (1, 3, 6, 8, 10) else "#ffffff"
                if (absolute_step, pitch) in self.sequencer_notes:
                    fill = "#287a55"
                outline = "#9aa0a6" if visible_step % steps_per_beat else "#626a73"
                if (absolute_step, pitch) in self.sequencer_selected_notes:
                    outline = "#e65100"
                canvas.create_rectangle(
                    x,
                    y,
                    x + cell_width,
                    y + cell_height,
                    fill=fill,
                    outline=outline,
                    width=2 if visible_step % self.sequencer_steps_per_bar == 0 else 1,
                )

        page_start = first_bar * self.sequencer_steps_per_bar
        page_end = page_start + visible_steps
        for step, pitch in self.sequencer_notes:
            if not self.sequencer_low_note <= pitch <= self.sequencer_high_note:
                continue
            length_steps = self.sequencer_note_lengths.get(
                (step, pitch),
                self.get_sequencer_note_duration_steps("1/16"),
            )
            note_start = step
            note_end = step + length_steps
            if note_end <= page_start or note_start >= page_end:
                continue
            visible_start = max(note_start, page_start)
            visible_end = min(note_end, page_end)
            x1 = left + (visible_start - page_start) * cell_width
            x2 = left + (visible_end - page_start) * cell_width
            y1 = top + (self.sequencer_high_note - pitch) * cell_height
            color = "#287a55" if (step, pitch) in self.sequencer_selected_notes else "#35966a"
            canvas.create_rectangle(
                x1,
                y1 + 3,
                max(x1 + 2, x2),
                y1 + cell_height - 3,
                fill=color,
                outline="#17482e",
                tags=("melody_note", f"note_{step}_{pitch}"),
            )

        if self.sequencer_selection_box is not None:
            first_step, highest_pitch, last_step, lowest_pitch = self.sequencer_selection_box
            page_start = first_bar * self.sequencer_steps_per_bar
            x1 = left + (first_step - page_start) * cell_width
            x2 = left + (last_step - page_start + 1) * cell_width
            y1 = top + (self.sequencer_high_note - highest_pitch) * cell_height
            y2 = top + (self.sequencer_high_note - lowest_pitch + 1) * cell_height
            canvas.create_rectangle(
                x1, y1, x2, y2, outline="#e65100", width=2, dash=(4, 2), tags="selection"
            )
        canvas.configure(scrollregion=(0, 0, width + 2, height + 2))

    def get_sequencer_cell_from_event(self, event):
        x = self.sequencer_canvas.canvasx(event.x) - 44
        y = self.sequencer_canvas.canvasy(event.y) - 26
        if x < 0 or y < 0:
            return None
        visible_step = int(x // self.sequencer_cell_width)
        row = int(y // self.sequencer_cell_height)
        visible_steps = self.sequencer_bars_per_page * self.sequencer_steps_per_bar
        pitch = self.sequencer_high_note - row
        if visible_step >= visible_steps or not self.sequencer_low_note <= pitch <= self.sequencer_high_note:
            return None
        step = (
            self.sequencer_page * self.sequencer_bars_per_page * self.sequencer_steps_per_bar
            + visible_step
        )
        if step >= self.sequencer_bars * self.sequencer_steps_per_bar:
            return None
        return step, pitch

    def begin_sequencer_mouse_action(self, event):
        self.sequencer_canvas.focus_set()
        cell = self.get_sequencer_cell_from_event(event)
        if cell is None:
            self.sequencer_selection_start = None
            return
        if self.sequencer_paste_armed:
            self.paste_sequencer_notes(cell)
            return "break"
        self.sequencer_selection_start = cell
        self.sequencer_selection_current = cell
        self.sequencer_selection_box = None
        return "break"

    def drag_sequencer_selection(self, event):
        if self.sequencer_selection_start is None:
            return
        cell = self.get_sequencer_cell_from_event(event)
        if cell is None:
            return
        self.sequencer_selection_current = cell
        start_step, start_pitch = self.sequencer_selection_start
        current_step, current_pitch = cell
        if (start_step, start_pitch) == (current_step, current_pitch):
            return
        first_step = min(start_step, current_step)
        last_step = max(start_step, current_step)
        highest_pitch = max(start_pitch, current_pitch)
        lowest_pitch = min(start_pitch, current_pitch)
        self.sequencer_selection_box = (first_step, highest_pitch, last_step, lowest_pitch)
        self.sequencer_selected_notes = {
            note for note in self.sequencer_notes
            if first_step <= note[0] <= last_step and lowest_pitch <= note[1] <= highest_pitch
        }
        self.redraw_sequencer_grid()

    def finish_sequencer_mouse_action(self, event):
        if self.sequencer_selection_start is None:
            return
        start = self.sequencer_selection_start
        end = self.get_sequencer_cell_from_event(event)
        self.sequencer_selection_start = None
        self.sequencer_selection_current = None
        if end is None:
            return
        if start == end:
            step, pitch = start
            note = (step, pitch)
            if note in self.sequencer_notes:
                self.sequencer_notes.remove(note)
                self.sequencer_note_lengths.pop(note, None)
                self.sequencer_selected_notes.discard(note)
            else:
                self.sequencer_notes.add(note)
                self.sequencer_note_lengths[note] = self.get_sequencer_note_duration_steps(
                    self.sequencer_note_duration_var.get()
                )
            self.sequencer_selection_box = None
        self.redraw_sequencer_grid()

    def copy_sequencer_notes(self, *_):
        if not self.sequencer_selected_notes:
            self.sequencer_status.config(text="Seleziona note da copiare", foreground="orange")
            return "break"
        first_step = min(step for step, _ in self.sequencer_selected_notes)
        highest_pitch = max(pitch for _, pitch in self.sequencer_selected_notes)
        default_length = self.get_sequencer_note_duration_steps("1/16")
        self.sequencer_clipboard = tuple(
            (
                step - first_step,
                highest_pitch - pitch,
                self.sequencer_note_lengths.get((step, pitch), default_length),
            )
            for step, pitch in sorted(self.sequencer_selected_notes)
        )
        self.sequencer_status.config(
            text=f"{len(self.sequencer_clipboard)} note copiate", foreground="blue"
        )
        return "break"

    def arm_sequencer_paste(self, *_):
        if not self.sequencer_clipboard:
            self.sequencer_status.config(text="Nessuna nota copiata", foreground="orange")
            return "break"
        self.sequencer_paste_armed = True
        self.sequencer_status.config(text="Clicca la cella iniziale per incollare", foreground="blue")
        return "break"

    def paste_sequencer_notes(self, anchor):
        anchor_step, anchor_pitch = anchor
        pasted = set()
        pasted_lengths = {}
        total_steps = self.sequencer_bars * self.sequencer_steps_per_bar
        for step_offset, pitch_offset, length_steps in self.sequencer_clipboard:
            step = anchor_step + step_offset
            pitch = anchor_pitch - pitch_offset
            if (
                step < total_steps
                and self.sequencer_low_note <= pitch <= self.sequencer_high_note
            ):
                pasted.add((step, pitch))
                pasted_lengths[(step, pitch)] = length_steps
        self.sequencer_notes.update(pasted)
        self.sequencer_note_lengths.update(pasted_lengths)
        self.sequencer_selected_notes = pasted
        self.sequencer_paste_armed = False
        self.sequencer_selection_box = None
        self.sequencer_status.config(text=f"{len(pasted)} note incollate", foreground="green")
        self.redraw_sequencer_grid()

    def toggle_sequencer_note(self, event):
        cell = self.get_sequencer_cell_from_event(event)
        if cell is None:
            return
        step, pitch = cell
        note = (step, pitch)
        if note in self.sequencer_notes:
            self.sequencer_notes.remove(note)
            self.sequencer_note_lengths.pop(note, None)
        else:
            self.sequencer_notes.add(note)
            self.sequencer_note_lengths[note] = self.get_sequencer_note_duration_steps(
                self.sequencer_note_duration_var.get()
            )
        self.redraw_sequencer_grid()

    def clear_sequencer(self):
        self.sequencer_notes.clear()
        self.sequencer_note_lengths.clear()
        self.redraw_sequencer_grid()
        self.sequencer_status.config(text="Melodia svuotata", foreground="blue")

    def get_phase_alignment_metadata(self, root_note, bpm, beats_per_chord=4):
        """Calcola frequenza, Gate e Micro-shift per una battuta in 4/4."""
        if not 40 <= bpm <= 200:
            raise ValueError("Il BPM deve essere compreso tra 40 e 200")
        if not isinstance(root_note, int) or not 0 <= root_note <= 127:
            raise ValueError("La fondamentale deve essere una nota MIDI valida")
        if not isinstance(beats_per_chord, (int, float)) or beats_per_chord <= 0:
            raise ValueError("La durata dell'accordo deve essere positiva")

        frequency_hz = 440.0 * 2 ** ((root_note - 69) / 12)
        quarter_ms = 60000.0 / bpm
        cycles_per_quarter = math.floor(frequency_hz * quarter_ms / 1000.0)
        quarter_gate_ms = cycles_per_quarter / frequency_hz * 1000.0
        quarter_shift_ms = quarter_ms - quarter_gate_ms
        chord_ms = quarter_ms * beats_per_chord
        cycles = math.floor(cycles_per_quarter * beats_per_chord)
        gate_ms = cycles / frequency_hz * 1000.0

        return {
            "frequency_hz": frequency_hz,
            "cycles_per_quarter": cycles_per_quarter,
            "cycles": cycles,
            "quarter_ms": quarter_ms,
            "quarter_gate_ms": quarter_gate_ms,
            "quarter_shift_ms": quarter_shift_ms,
            "gate_ms": gate_ms,
            "shift_ms": chord_ms - gate_ms,
        }

    def get_note_phase_alignment_metadata(self, midi_note, bpm, duration_beats):
        if not 40 <= bpm <= 200:
            raise ValueError("Il BPM deve essere compreso tra 40 e 200")
        if not isinstance(midi_note, int) or not 0 <= midi_note <= 127:
            raise ValueError("La nota deve essere un valore MIDI valido")
        if not isinstance(duration_beats, (int, float)) or duration_beats <= 0:
            raise ValueError("La durata della nota deve essere positiva")

        frequency_hz = 440.0 * 2 ** ((midi_note - 69) / 12)
        quarter_ms = 60000.0 / bpm
        duration_ms = quarter_ms * duration_beats
        cycles = math.floor(frequency_hz * duration_ms / 1000.0)
        gate_ms = cycles / frequency_hz * 1000.0
        return {
            "frequency_hz": frequency_hz,
            "cycles": cycles,
            "duration_ms": duration_ms,
            "gate_ms": gate_ms,
            "shift_ms": duration_ms - gate_ms,
            "quarter_ms": quarter_ms,
        }

    def get_sequencer_note_duration_steps(self, note_value):
        duration_steps = getattr(
            self,
            "sequencer_note_duration_steps",
            {"1/1": 16, "1/2": 8, "1/4": 4, "1/8": 2, "1/16": 1, "1/32": 0.5},
        )
        try:
            return duration_steps[note_value]
        except KeyError as exc:
            raise ValueError("Seleziona una durata da 1/1 a 1/32") from exc

    def build_sequencer_midi(
        self,
        key,
        scale_name,
        bpm,
        chord_degrees,
        melody_notes,
        armonia="terze",
        voices=3,
        note_value="1/16",
        loop_bar=None,
        melody_note_lengths=None,
        time_signature=(4, 4),
    ):
        if not 40 <= bpm <= 200:
            raise ValueError("Il BPM deve essere compreso tra 40 e 200")
        if key not in self.note_names or (
            scale_name != "personale" and scale_name not in self.scale_map
        ):
            raise ValueError("Tonalità o scala non valida")
        if armonia not in ("terze", "quarte", "quinte"):
            raise ValueError("L'armonia deve essere per terze, quarte o quinte")
        if not isinstance(voices, int) or not 3 <= voices <= 5:
            raise ValueError("Il numero di voci deve essere compreso tra 3 e 5")
        try:
            numerator, denominator, steps_per_bar = self.parse_sequencer_time_signature(
                f"{time_signature[0]}/{time_signature[1]}"
            )
        except (TypeError, IndexError, ValueError) as exc:
            raise ValueError("Metro non valido") from exc
        if steps_per_bar != self.sequencer_steps_per_bar:
            raise ValueError("Aggiorna la griglia prima di generare il MIDI con questo metro")
        note_duration_steps = self.get_sequencer_note_duration_steps(note_value)
        melody_note_lengths = melody_note_lengths or {}
        if loop_bar is not None and (
            not isinstance(loop_bar, int) or not 1 <= loop_bar <= self.sequencer_bars
        ):
            raise ValueError("La battuta del loop deve essere compresa nella sequenza")
        melody_notes = tuple(melody_notes)
        scale = [
            self.C + self.note_names.index(key) + interval
            for interval in self.get_sequencer_scale_intervals(scale_name)
        ]
        scale_size = len(scale) - 1
        if len(chord_degrees) != self.sequencer_bars:
            raise ValueError(f"Seleziona un accordo per ciascuna delle {self.sequencer_bars} battute")
        if any(not isinstance(degree, int) or not 0 <= degree < scale_size for degree in chord_degrees):
            raise ValueError("Progressione: grado di accordo non valido")

        total_steps = self.sequencer_bars * self.sequencer_steps_per_bar
        for step, pitch in melody_notes:
            if not isinstance(step, int) or not 0 <= step < total_steps:
                raise ValueError("La melodia contiene un passo fuori dalla sequenza")
            if not isinstance(pitch, int) or not 0 <= pitch <= 127:
                raise ValueError("Le note MIDI devono essere comprese tra 0 e 127")

        midi = MidiFile(type=1, ticks_per_beat=self.TPB)
        tempo_track = MidiTrack()
        tempo_track.append(MetaMessage("set_tempo", tempo=bpm2tempo(bpm), time=0))
        tempo_track.append(
            MetaMessage("time_signature", numerator=numerator, denominator=denominator, time=0)
        )
        beats_per_bar = numerator * 4 / denominator
        ticks_per_bar = round(self.TPB * beats_per_bar)
        loop_offset = (loop_bar - 1) * ticks_per_bar if loop_bar is not None else 0
        if loop_bar is not None:
            tempo_track.append(MetaMessage("end_of_track", time=ticks_per_bar))
        midi.tracks.append(tempo_track)

        ticks_per_step = self.TPB // 4
        total_ticks = self.sequencer_bars * ticks_per_bar
        chord_metadata = []
        melody_metadata = []
        for track_name in ("Accordi", "Melodia"):
            track = MidiTrack()
            midi.tracks.append(track)
            track.append(MetaMessage("track_name", name=track_name, time=0))
            track.append(Message("program_change", program=0, time=0))
            events = []

            if track_name == "Accordi":
                for bar, degree in enumerate(chord_degrees):
                    if loop_bar is not None and bar + 1 != loop_bar:
                        continue
                    root_note = scale[degree]
                    chord_notes = self.build_chord_notes(root_note, armonia, voices, scale)
                    timing = self.get_phase_alignment_metadata(
                        root_note, bpm, beats_per_chord=beats_per_bar
                    )
                    gate_ticks = round(timing["gate_ms"] / timing["quarter_ms"] * self.TPB)
                    shift_ticks = ticks_per_bar - gate_ticks
                    bar_start = bar * ticks_per_bar
                    start = bar_start + shift_ticks - loop_offset
                    end = bar_start + ticks_per_bar - loop_offset
                    chord_name = self.get_chord_label(chord_notes, root=root_note)
                    degree_names = ("I", "II", "III", "IV", "V", "VI", "VII")
                    degree_name = (
                        degree_names[degree]
                        if degree < len(degree_names)
                        else f"Grado {degree + 1}"
                    )
                    chord_text = f"{degree_name} Grado - {chord_name}"
                    if armonia != "terze":
                        harmony_names = {"quarte": "Quarte", "quinte": "Quinte"}
                        chord_text += f" ({harmony_names[armonia]})"
                    chord_metadata.append({
                        "bar": bar + 1,
                        "degree": degree + 1,
                        "time_signature": f"{numerator}/{denominator}",
                        "name": chord_name,
                        "text": chord_text,
                        "root_note": root_note,
                        "frequency_hz": timing["frequency_hz"],
                        "cycles_per_quarter": timing["cycles_per_quarter"],
                        "cycles": timing["cycles"],
                        "gate_ms": timing["gate_ms"],
                        "shift_ms": timing["shift_ms"],
                        "gate_ticks": gate_ticks,
                        "shift_ticks": shift_ticks,
                    })
                    events.append((start, 1, MetaMessage("text", text=chord_text)))
                    for pitch in chord_notes:
                        events.append((start, 1, Message("note_on", note=pitch, velocity=58)))
                        events.append((end, 0, Message("note_off", note=pitch, velocity=0)))
            else:
                for step, pitch in melody_notes:
                    bar = step // self.sequencer_steps_per_bar
                    if loop_bar is not None and bar + 1 != loop_bar:
                        continue
                    nominal_start = step * ticks_per_step
                    duration_steps = melody_note_lengths.get(
                        (step, pitch), note_duration_steps
                    )
                    nominal_end = min(
                        nominal_start + round(duration_steps * ticks_per_step),
                        total_ticks,
                    )
                    if loop_bar is not None:
                        nominal_end = min(nominal_end, loop_offset + ticks_per_bar)
                    actual_duration_beats = (nominal_end - nominal_start) / self.TPB
                    timing = self.get_note_phase_alignment_metadata(
                        pitch, bpm, actual_duration_beats
                    )
                    duration_ticks = nominal_end - nominal_start
                    gate_ticks = round(timing["gate_ms"] / timing["quarter_ms"] * self.TPB)
                    gate_ticks = min(duration_ticks, max(1, gate_ticks))
                    shift_ticks = duration_ticks - gate_ticks
                    start = nominal_start + shift_ticks - loop_offset
                    end = nominal_end - loop_offset
                    events.append((start, 1, Message("note_on", note=pitch, velocity=96)))
                    events.append((end, 0, Message("note_off", note=pitch, velocity=0)))
                    melody_metadata.append({
                        "bar": bar + 1,
                        "step": step,
                        "note": pitch,
                        "frequency_hz": timing["frequency_hz"],
                        "cycles": timing["cycles"],
                        "duration_steps": (nominal_end - nominal_start) / ticks_per_step,
                        "gate_ms": timing["gate_ms"],
                        "shift_ms": timing["shift_ms"],
                        "gate_ticks": gate_ticks,
                        "shift_ticks": shift_ticks,
                    })

            previous_tick = 0
            for tick, _, message in sorted(
                events,
                key=lambda event: (event[0], event[1], getattr(event[2], "note", -1)),
            ):
                message.time = tick - previous_tick
                track.append(message)
                previous_tick = tick
            if loop_bar is not None:
                track.append(MetaMessage("end_of_track", time=ticks_per_bar - previous_tick))

        self.sequencer_channel_metadata = {
            "Accordi": chord_metadata,
            "Melodia": melody_metadata,
        }
        return midi

    def play_sequencer(self):
        try:
            midi = self.build_sequencer_midi(
                self.sequencer_key_var.get(),
                self.sequencer_scale_var.get(),
                int(self.sequencer_bpm_var.get()),
                self.get_sequencer_chord_degrees(),
                self.sequencer_notes,
                self.sequencer_harmony_var.get(),
                int(self.sequencer_voices_var.get()),
                self.sequencer_note_duration_var.get(),
                melody_note_lengths=self.sequencer_note_lengths,
                time_signature=self.parse_sequencer_time_signature(
                    self.sequencer_time_signature_var.get()
                )[:2],
            )
            filename = os.path.join(self._temp_directory.name, "sequencer.mid")
            midi.save(filename)
            if self.ascolta_midi(filename):
                self.sequencer_status.config(text="Sequenza in riproduzione", foreground="green")
            else:
                self.sequencer_status.config(text="MIDI pronto; riproduzione non disponibile", foreground="orange")
        except (ValueError, OSError) as exc:
            messagebox.showerror("Errore Sequencer", str(exc))
            self.sequencer_status.config(text="Errore nella sequenza", foreground="red")

    def loop_sequencer_bar(self):
        try:
            bar = int(self.sequencer_loop_bar_var.get())
            if not 1 <= bar <= self.sequencer_bars:
                raise ValueError(f"La battuta deve essere compresa tra 1 e {self.sequencer_bars}")
            self.sequencer_page = (bar - 1) // self.sequencer_bars_per_page
            self.sequencer_selected_notes.clear()
            self.sequencer_selection_box = None
            self.render_sequencer_progression_page()
            self.refresh_sequencer_chords()
            midi = self.build_sequencer_midi(
                self.sequencer_key_var.get(),
                self.sequencer_scale_var.get(),
                int(self.sequencer_bpm_var.get()),
                self.get_sequencer_chord_degrees(),
                self.sequencer_notes,
                self.sequencer_harmony_var.get(),
                int(self.sequencer_voices_var.get()),
                self.sequencer_note_duration_var.get(),
                loop_bar=bar,
                melody_note_lengths=self.sequencer_note_lengths,
                time_signature=self.parse_sequencer_time_signature(
                    self.sequencer_time_signature_var.get()
                )[:2],
            )
            filename = os.path.join(self._temp_directory.name, "sequencer-loop.mid")
            midi.save(filename)
            if self.ascolta_midi(filename, loops=-1):
                self.sequencer_status.config(
                    text=f"Loop continuo sulla battuta {bar}", foreground="green"
                )
            else:
                self.sequencer_status.config(
                    text="Loop non avviato: riproduzione audio non disponibile",
                    foreground="orange",
                )
        except (ValueError, OSError) as exc:
            messagebox.showerror("Errore Loop", str(exc))
            self.sequencer_status.config(text="Impossibile avviare il loop", foreground="red")

    def save_sequencer(self):
        try:
            midi = self.build_sequencer_midi(
                self.sequencer_key_var.get(),
                self.sequencer_scale_var.get(),
                int(self.sequencer_bpm_var.get()),
                self.get_sequencer_chord_degrees(),
                self.sequencer_notes,
                self.sequencer_harmony_var.get(),
                int(self.sequencer_voices_var.get()),
                self.sequencer_note_duration_var.get(),
                melody_note_lengths=self.sequencer_note_lengths,
                time_signature=self.parse_sequencer_time_signature(
                    self.sequencer_time_signature_var.get()
                )[:2],
            )
            save_path = filedialog.asksaveasfilename(
                defaultextension=".mid",
                filetypes=[("MIDI", "*.mid"), ("Tutti i file", "*.*")],
                initialfile="composizione.mid",
            )
            if not save_path:
                return
            midi.save(save_path)
            self.sequencer_status.config(text=f"Salvato: {os.path.basename(save_path)}", foreground="green")
            messagebox.showinfo("Esportazione MIDI", f"File salvato:\n{save_path}")
        except (ValueError, OSError) as exc:
            messagebox.showerror("Errore Sequencer", str(exc))
            self.sequencer_status.config(text="Errore nell'esportazione", foreground="red")

    # ===== METODI =====
    def parse_note_input(self, text_input):
        try:
            note_input = text_input.strip().split()
            if not note_input:
                raise ValueError("Inserisci almeno una nota")
            degree_intervals = [0, 2, 4, 5, 7, 9, 11]
            intervalli = []
            for nota in note_input:
                match = re.fullmatch(r"([1-8])([#b]*)", nota)
                if match is None:
                    raise ValueError(f"Nota {nota}: usa un grado da 1 a 8 e alterazioni # o b")

                degree = int(match.group(1))
                semitono = 12 if degree == 8 else degree_intervals[degree - 1]
                for accidental in match.group(2):
                    semitono += 1 if accidental == "#" else -1
                if not 0 <= semitono <= 12:
                    raise ValueError(f"Nota {nota}: fuori dall'ottava della scala")
                intervalli.append(semitono)

            if intervalli[0] != 0:
                raise ValueError("La scala deve iniziare dalla tonica (1)")
            if any(current <= previous for previous, current in zip(intervalli, intervalli[1:])):
                raise ValueError("Le note devono essere in ordine crescente e senza duplicati")
            return intervalli
        except ValueError as e:
            messagebox.showerror("Errore Input", f"Errore nel parsing: {str(e)}")
            return None
    
    def get_scale_da_note(self, tono, intervalli):
        """Crea la scala dal tono base e dagli intervalli"""
        try:
            tono_idx = self.note_names.index(tono)
            base = self.C + tono_idx  # C4 (60) + offset tono
            scala = [base + i for i in intervalli]
            return scala
        except Exception as e:
            messagebox.showerror("Errore Scala", f"Errore nella generazione scala: {str(e)}")
            return None

    def get_note_name(self, midi_note, pitch_names=None):
        pitch_class = midi_note % 12
        note_name = (
            pitch_names.get(pitch_class, self.note_names[pitch_class])
            if pitch_names
            else self.note_names[pitch_class]
        )
        octave = midi_note // 12 - 1
        return f"{note_name}{octave}"

    def get_pitch_name(self, pitch_class):
        names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return names[pitch_class % 12]

    def get_diatonic_pitch_name(self, pitch_class, tonic_pitch_class, degree_index):
        letters = ("C", "D", "E", "F", "G", "A", "B")
        natural_pitch_classes = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
        tonic_letter = self.get_pitch_name(tonic_pitch_class)[0]
        letter = letters[(letters.index(tonic_letter) + degree_index) % len(letters)]
        alteration = (pitch_class - natural_pitch_classes[letter] + 6) % 12 - 6
        accidental = "#" * alteration if alteration > 0 else "b" * -alteration
        return f"{letter}{accidental}"

    def semitone_to_degree(self, semitone):
        mapping = {
            0: '1',
            1: '1#',
            2: '2',
            3: '3b',
            4: '3',
            5: '4',
            6: '5b',
            7: '5',
            8: '5#',
            9: '6',
            10: '7b',
            11: '7',
            12: '8',
        }
        return mapping.get(semitone, str(semitone))

    def intervals_to_formula(self, intervals):
        return ' '.join(self.semitone_to_degree(i) for i in intervals)

    def get_chord_formula(self, chord_notes):
        pitch_classes = sorted({n % 12 for n in chord_notes})
        if not pitch_classes:
            return ""
        root = min(chord_notes) % 12
        intervals = tuple(sorted({(pc - root) % 12 for pc in pitch_classes}))
        return self.intervals_to_formula(intervals)

    def get_chord_label(self, chord_notes, root=None, root_name=None):
        if not chord_notes:
            return ""

        pitch_classes = sorted({n % 12 for n in chord_notes})
        if not pitch_classes:
            return ""

        chord_templates = {
            (0, 4, 7): "{}",
            (0, 3, 7): "{}m",
            (0, 3, 6): "{}dim",
            (0, 4, 8): "{}aug",
            (0, 2, 7): "{}sus2",
            (0, 5, 7): "{}sus4",
            (0, 5, 10): "{}7sus4(no5)",
            (0, 5, 7, 10): "{}7sus4",
            (0, 4, 7, 10): "{}7",
            (0, 3, 7, 10): "{}m7",
            (0, 4, 7, 11): "{}maj7",
            (0, 3, 7, 11): "{}m(maj7)",
            (0, 4, 7, 9): "{}6",
            (0, 3, 7, 9): "{}m6",
            (0, 2, 4, 7): "{}add9",
            (0, 2, 3, 7): "{}m(add9)",
            (0, 2, 4, 7, 10): "{}9",
            (0, 2, 4, 7, 11): "{}maj9",
            (0, 2, 3, 7, 10): "{}m9",
            (0, 2, 3, 7, 11): "{}m(maj9)",
            (0, 2, 4, 5, 7, 10): "{}11",
            (0, 2, 3, 5, 7, 10): "{}m11",
            (0, 2, 4, 7, 9, 10): "{}13",
            (0, 2, 4, 7, 9, 11): "{}maj13",
            (0, 2, 3, 7, 9, 10): "{}m13",
            (0, 1, 4, 7, 10): "{}7b9",
            (0, 3, 4, 7, 10): "{}7#9",
            (0, 4, 7, 8, 10): "{}7#5",
            (0, 4, 6, 7, 10): "{}7b5",
            (0, 4, 6, 10): "{}7b5",
            (0, 3, 6, 10): "{}m7b5",
            (0, 3, 6, 9): "{}dim7",
        }

        if root is not None:
            root_pc = root % 12
            intervals = tuple(sorted((pc - root_pc) % 12 for pc in pitch_classes))
            display_root = root_name or self.get_pitch_name(root_pc)
            template = chord_templates.get(intervals)
            if template:
                return template.format(display_root)
            return self.get_standard_chord_fallback(display_root, intervals)

        def candidate_label(root):
            intervals = tuple(sorted((pc - root) % 12 for pc in pitch_classes))
            if not intervals or intervals[0] != 0:
                return None
            return chord_templates.get(intervals)

        for root in pitch_classes:
            template = candidate_label(root)
            if template:
                return template.format(self.get_pitch_name(root))

        root = min(chord_notes) % 12
        root_name = self.get_pitch_name(root)
        intervals = tuple(sorted({(pc - root) % 12 for pc in pitch_classes}))
        return self.get_standard_chord_fallback(root_name, intervals)

    @staticmethod
    def get_standard_chord_fallback(root_name, intervals):
        interval_names = {
            1: "b9",
            2: "9",
            5: "11",
            6: "#11",
            8: "b13",
            9: "13",
        }
        has_minor_third = 3 in intervals
        has_major_third = 4 in intervals
        has_fifth = 7 in intervals
        has_flat_seventh = 10 in intervals
        has_major_seventh = 11 in intervals

        if has_minor_third and 6 in intervals and not has_fifth:
            quality = "dim"
        elif has_minor_third and has_fifth and has_flat_seventh:
            quality = "m7"
        elif has_minor_third and has_fifth and has_major_seventh:
            quality = "m(maj7)"
        elif has_minor_third and has_fifth:
            quality = "m"
        elif has_major_third and has_fifth and has_flat_seventh:
            quality = "7"
        elif has_major_third and has_fifth and has_major_seventh:
            quality = "maj7"
        elif has_major_third and has_fifth:
            quality = ""
        elif not has_minor_third and not has_major_third and 5 in intervals:
            quality = "7sus4" if has_flat_seventh else "maj7sus4" if has_major_seventh else "sus4"
        elif not has_minor_third and not has_major_third and 2 in intervals:
            quality = "7sus2" if has_flat_seventh else "maj7sus2" if has_major_seventh else "sus2"
        elif has_major_third and has_flat_seventh:
            quality = "7(no5)" if not has_fifth else "7"
        elif has_major_third and has_major_seventh:
            quality = "maj7(no5)" if not has_fifth else "maj7"
        elif has_minor_third and has_flat_seventh:
            quality = "m7(no5)" if not has_fifth else "m7"
        elif has_minor_third and has_major_seventh:
            quality = "m(maj7)(no5)" if not has_fifth else "m(maj7)"
        else:
            quality = "no3" if not has_fifth else "5(no3)"

        represented = {0, 3, 4, 7, 10, 11}
        if quality.endswith("sus4"):
            represented.add(5)
        if quality.endswith("sus2"):
            represented.add(2)
        modifiers = []
        if quality.endswith("(no5)"):
            quality = quality[:-5]
            modifiers.append("no5")
        modifiers.extend(
            f"add{interval_names[interval]}"
            for interval in intervals
            if interval not in represented and interval in interval_names
        )
        suffix = quality
        if modifiers:
            suffix += f"({', '.join(modifiers)})"
        return f"{root_name}{suffix}"

    def get_chord_inversions(self, chord_notes, root, root_name=None, pitch_names=None):
        root_pc = root % 12
        notes_by_pitch = {}
        for note in sorted(chord_notes):
            notes_by_pitch.setdefault(note % 12, note)
        if root_pc not in notes_by_pitch:
            return []

        root_note = notes_by_pitch[root_pc]
        intervals = sorted((pc - root_pc) % 12 for pc in notes_by_pitch if pc != root_pc)
        root_position = [root_note] + [root_note + interval for interval in intervals]
        chord_label = self.get_chord_label(chord_notes, root, root_name).partition(" (")[0]
        inversions = []

        for index in range(len(root_position)):
            notes = root_position[index:] + [note + 12 for note in root_position[:index]]
            bass_name = (
                pitch_names.get(notes[0] % 12, self.get_pitch_name(notes[0] % 12))
                if pitch_names
                else self.get_pitch_name(notes[0] % 12)
            )
            position = "Fondamentale" if index == 0 else f"{['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'][index - 1]} rivolto"
            symbol = chord_label if index == 0 else f"{chord_label}/{bass_name}"
            note_names = ", ".join(self.get_note_name(note, pitch_names) for note in notes)
            inversions.append(f"{position}: {symbol} ({note_names})")

        return inversions

    def get_chord_quality_implication(self, chord_label):
        if " (" in chord_label:
            return "Accordo parziale o non standard: la direzione dipende dal contesto."

        root_name = next(
            (name for name in sorted(self.note_names, key=len, reverse=True) if chord_label.startswith(name)),
            "",
        )
        quality = chord_label[len(root_name):]

        if "dim" in quality or quality in ("m7b5", "7b5"):
            return "Sonorità instabile e tesa; in genere richiede una risoluzione."
        if quality.startswith("aug"):
            return "Sonorità instabile e sospesa; tende a muoversi verso un accordo più stabile."
        if quality.startswith("sus"):
            return "Sonorità sospesa; la terza omessa tende spesso a essere esplicitata."
        if quality == "7":
            return "Colore dominante e tensione; spesso tende a risolvere sulla tonica."
        if quality.startswith("m") and not quality.startswith("maj"):
            return "Colore minore; la funzione dipende dal grado e dal contesto."
        if quality.startswith("maj7") or quality.startswith("maj9"):
            return "Colore maggiore e stabile, con una tensione morbida della settima."
        if quality in ("", "add9"):
            return "Sonorità maggiore generalmente stabile; la funzione dipende dal grado."
        return "Funzione e direzione dipendono dal contesto armonico."

    def get_harmonic_implication(self, scale_intervals, degree_index, chord_label):
        scale_pcs = [int(interval) % 12 for interval in scale_intervals]
        if len(scale_pcs) > 1 and scale_pcs[-1] == scale_pcs[0]:
            scale_pcs.pop()
        if not 0 <= degree_index < len(scale_pcs):
            raise ValueError("Il grado deve appartenere alla scala analizzata")

        profile = self.get_diatonic_chord_profile(scale_intervals, degree_index)
        if profile is not None:
            return f"{profile['numeral']} - {profile['role']}: {profile['tendency']}."
        return self.get_chord_quality_implication(chord_label)

    @staticmethod
    def get_triad_quality(chord_intervals):
        return {
            (0, 3, 6): ("diminuita", "dim", "°", "minor"),
            (0, 3, 7): ("minore", "m", "", "minor"),
            (0, 4, 7): ("maggiore", "", "", "major"),
            (0, 4, 8): ("aumentata", "aug", "+", "major"),
        }.get(chord_intervals)

    def get_diatonic_chord_profile(self, scale_intervals, degree_index):
        scale = [int(interval) for interval in scale_intervals]
        if len(scale) > 1 and scale[-1] % 12 == scale[0] % 12:
            scale.pop()
        scale_pcs = [interval % 12 for interval in scale]
        if len(scale_pcs) != 7 or len(set(scale_pcs)) != 7:
            return None
        if not 0 <= degree_index < len(scale):
            raise ValueError("Il grado deve appartenere alla scala analizzata")

        root = scale[degree_index]
        chord_intervals = tuple(
            sorted({
                (scale[(degree_index + offset) % 7]
                 + 12 * ((degree_index + offset) // 7)
                 - root) % 12
                for offset in (0, 2, 4)
            })
        )
        quality = self.get_triad_quality(chord_intervals)
        if quality is None:
            quality_name, suffix, numeral_suffix, numeral_case = (
                "non standarde",
                "",
                "?",
                "major",
            )
        else:
            quality_name, suffix, numeral_suffix, numeral_case = quality

        roman = ("I", "II", "III", "IV", "V", "VI", "VII")[degree_index]
        if numeral_case == "minor":
            roman = roman.lower()
        numeral = f"{roman}{numeral_suffix}"

        scale_key = tuple(sorted(scale_pcs))
        functions_by_scale = {
            (0, 2, 4, 5, 7, 9, 11): [
                ("I", "tonica", "stabilità e riposo"),
                ("ii", "predominante", "prepara la dominante V"),
                ("iii", "medianta", "colore di tonica, spesso conduce a IV o vi"),
                ("IV", "sottodominante", "apre il percorso e tende verso V"),
                ("V", "dominante", "crea tensione e tende a risolvere su I"),
                ("vi", "relativa minore", "area di riposo o sostituzione della tonica"),
                ("vii°", "sensibile", "forte tensione, tende a risolvere su I"),
            ],
            (0, 2, 3, 5, 7, 8, 10): [
                ("i", "tonica", "stabilità e riposo"),
                ("ii°", "predominante", "prepara la dominante o il ritorno a i"),
                ("III", "medianta", "relativa maggiore, apre verso altri gradi"),
                ("iv", "sottodominante", "crea movimento verso V o i"),
                ("v", "dominante minore", "tende a i, con meno spinta della dominante maggiore"),
                ("VI", "sopradominante", "colore di passaggio o di sottodominante"),
                ("VII", "sottotonica", "spesso conduce a III; la risoluzione su i e meno forte"),
            ],
            (0, 2, 3, 5, 7, 8, 11): [
                ("i", "tonica", "stabilità e riposo"),
                ("ii°", "predominante", "prepara la dominante V"),
                ("III", "medianta", "colore caratteristico; direzione legata al contesto"),
                ("iv", "sottodominante", "crea movimento verso V o i"),
                ("V", "dominante", "tensione forte, tende a risolvere su i"),
                ("VI", "sopradominante", "colore di passaggio o di sottodominante"),
                ("vii°", "sensibile", "tensione forte, tende a risolvere su i"),
            ],
        }
        functions = functions_by_scale.get(scale_key)
        if functions is not None:
            _, role, tendency = functions[degree_index]
        else:
            role, tendency = self.get_modal_degree_function(
                degree_index,
                chord_intervals,
                scale_pcs,
            )
            if degree_index == 0 and chord_intervals in ((0, 3, 6), (0, 4, 8)):
                tendency = "centro modale, ma la triade ha una sonorità instabile"

        return {
            "numeral": numeral,
            "quality": quality_name,
            "role": role,
            "tendency": tendency,
        }

    @staticmethod
    def get_modal_degree_function(degree_index, chord_intervals, scale_pcs):
        roles = {
            0: ("tonica", "centro di stabilità e riferimento della scala"),
            1: ("sopratonica", "grado di passaggio o di preparazione"),
            2: ("mediante", "colore intermedio tra tonica e sottodominante"),
            3: ("sottodominante", "apre il movimento verso il quinto grado"),
            5: ("sopradominante", "grado di colore, spesso vicino all'area di tonica"),
        }
        if degree_index == 4:
            if chord_intervals == (0, 4, 7) and scale_pcs[6] == 11:
                return "dominante", "la sensibile rafforza la risoluzione verso la tonica"
            return "dominante modale", "la spinta verso la tonica dipende dalla qualità dell'accordo"
        if degree_index == 6:
            if scale_pcs[6] == 11:
                return "sensibile", "la sensibile tende a salire di semitono verso la tonica"
            return "sottotonica", "la risoluzione verso la tonica è meno diretta"
        return roles[degree_index]

    def get_diatonic_harmony(self, scale_notes):
        degrees = list(scale_notes)
        if len(degrees) > 1 and (degrees[-1] - degrees[0]) % 12 == 0:
            degrees.pop()
        if not degrees:
            return []

        scale_intervals = [note - degrees[0] for note in degrees]
        is_heptatonic = len(degrees) == 7 and len({note % 12 for note in degrees}) == 7
        rows = []
        for degree_index, root in enumerate(degrees):
            chord_notes = [
                degrees[(degree_index + offset) % len(degrees)]
                + 12 * ((degree_index + offset) // len(degrees))
                for offset in (0, 2, 4)
            ]
            chord_intervals = tuple(
                sorted({(note - chord_notes[0]) % 12 for note in chord_notes})
            )
            quality = self.get_triad_quality(chord_intervals)
            root_name = (
                self.get_diatonic_pitch_name(root % 12, degrees[0] % 12, degree_index)
                if is_heptatonic
                else self.get_pitch_name(root % 12)
            )
            if quality is None:
                formula = self.intervals_to_formula(chord_intervals)
                chord_name = f"{root_name} ({formula})"
                quality_name = "non standarde"
                if degree_index < 7:
                    roman = ("I", "II", "III", "IV", "V", "VI", "VII")[degree_index]
                    numeral = f"{roman}?" if len(degrees) == 7 else str(degree_index + 1)
                else:
                    numeral = str(degree_index + 1)
            else:
                quality_name, suffix, numeral_suffix, numeral_case = quality
                chord_name = f"{root_name}{suffix}"
                roman = ("I", "II", "III", "IV", "V", "VI", "VII")[degree_index]
                if numeral_case == "minor":
                    roman = roman.lower()
                numeral = (
                    f"{roman}{numeral_suffix}"
                    if len(degrees) == 7
                    else str(degree_index + 1)
                )

            profile = (
                self.get_diatonic_chord_profile(scale_intervals, degree_index)
                if len(degrees) == 7
                else None
            )
            rows.append({
                "degree": degree_index + 1,
                "numeral": profile["numeral"] if profile else numeral,
                "chord": chord_name,
                "root": root_name,
                "quality": quality_name,
                "role": profile["role"] if profile else None,
                "tendency": profile["tendency"] if profile else None,
                "notes": chord_notes,
            })
        return rows

    def build_chord_notes(self, root, armonia, voices, scale=None):
        if not 1 <= voices <= 8:
            raise ValueError("Il numero di voci deve essere compreso tra 1 e 8")

        # Armonizzazione in termini di gradi di scala, non di semitoni fissi.
        step_map = {
            'seconde': 1,
            'terze': 2,
            'quarte': 3,
            'quinte': 4,
            'seste': 5,
            'settime': 6,
            'ottave': 7,
        }
        scale_step = step_map.get(armonia, 7)
        if scale is None or not scale:
            semitone_map = {
                'seconde': 2,
                'terze': 4,
                'quarte': 5,
                'quinte': 7,
                'seste': 9,
                'settime': 11,
                'ottave': 12,
            }
            step = semitone_map.get(armonia, 12)
            chord_notes = []
            for k in range(voices):
                note = root + k * step
                while note > 127:
                    note -= 12
                while note < 0:
                    note += 12
                chord_notes.append(note)
            return chord_notes

        base_scale = scale
        if len(scale) > 1 and scale[-1] - scale[0] == 12:
            base_scale = scale[:-1]

        chord_notes = []
        root_pc = root % 12
        root_octave = root // 12
        base_pcs = [n % 12 for n in base_scale]

        try:
            root_index = base_pcs.index(root_pc)
        except ValueError:
            # Se la root non è nella scala, usa il semitono fisso come fallback.
            return self.build_chord_notes(root, armonia, voices, scale=None)

        len_base = len(base_scale)
        for k in range(voices):
            degree_index = root_index + k * scale_step
            octave_shift = degree_index // len_base
            scale_pc = base_pcs[degree_index % len_base]
            note = scale_pc + (root_octave + octave_shift) * 12
            while note > 127:
                note -= 12
            while note < 0:
                note += 12
            chord_notes.append(note)
        return chord_notes

    def genera_e_ascolta_note(self):
        try:
            self.label_status_pers.config(text="⏳ Parsing note...", foreground="orange")
            self.root.update()
            
            text_input = self.text_note.get("1.0", tk.END).strip()
            
            if not text_input:
                messagebox.showerror("Errore", "Inserisci le note!")
                self.label_status_pers.config(text="❌ Nessuna nota", foreground="red")
                return
            
            # Parse le note
            intervalli = self.parse_note_input(text_input)
            
            if intervalli is None:
                self.label_status_pers.config(text="❌ Errore parsing", foreground="red")
                return
            
            # Prendi i valori di configurazione
            bpm = int(self.var_bpm_pers.get())
            tono = self.var_tono_pers.get()
            nome = self.var_nome_scala_pers.get()
            armonia = self.var_armonia_pers.get()
            
            # Genera la scala
            scala = self.get_scale_da_note(tono, intervalli)
            
            if scala is None:
                self.label_status_pers.config(text="❌ Errore scala", foreground="red")
                return
            
            # Genera il MIDI
            voices = int(self.var_voci_pers.get()) if hasattr(self, 'var_voci_pers') else 1
            filename = self.genera_midi(tono, scala, nome, bpm, armonia, voices=voices)
            if not filename:
                self.label_status_pers.config(text="❌ Errore generazione MIDI", foreground="red")
                return

            if self.ascolta_midi(filename):
                self.label_status_pers.config(text=f"🎵 Riproducendo: {nome}", foreground="green")
            else:
                self.label_status_pers.config(text="⚠️ MIDI creato, riproduzione non avviata", foreground="orange")
            
        except ValueError as e:
            messagebox.showerror("Errore BPM", f"BPM non valido: {str(e)}")
            self.label_status_pers.config(text="❌ BPM invalido", foreground="red")
        except Exception as e:
            messagebox.showerror("Errore Generale", f"Errore: {str(e)}")
            self.label_status_pers.config(text="❌ Errore", foreground="red")
    
    def salva_note_cartella(self):
        try:
            self.label_status_pers.config(text="⏳ Generando...", foreground="orange")
            self.root.update()
            
            text_input = self.text_note.get("1.0", tk.END).strip()
            
            if not text_input:
                messagebox.showerror("Errore", "Inserisci le note!")
                return
            
            # Parse le note
            intervalli = self.parse_note_input(text_input)
            
            if intervalli is None:
                return
            
            # Prendi i valori
            bpm = int(self.var_bpm_pers.get())
            tono = self.var_tono_pers.get()
            nome = self.var_nome_scala_pers.get()
            armonia = self.var_armonia_pers.get()
            
            # Genera scala
            scala = self.get_scale_da_note(tono, intervalli)
            
            if scala is None:
                return
            
            # Genera MIDI
            voices = int(self.var_voci_pers.get()) if hasattr(self, 'var_voci_pers') else 1
            filename = self.genera_midi(tono, scala, nome, bpm, armonia, voices=voices)
            if not filename:
                self.label_status_pers.config(text="❌ Errore generazione MIDI", foreground="red")
                return
            
            # Dialog salvataggio
            save_path = filedialog.asksaveasfilename(
                defaultextension=".mid",
                filetypes=[("MIDI", "*.mid"), ("All", "*.*")],
                initialfile=os.path.basename(filename)
            )
            
            if save_path:
                shutil.copy(filename, save_path)
                messagebox.showinfo("✓ Successo", f"File salvato!\n{os.path.basename(save_path)}")
                self.label_status_pers.config(text=f"✅ Salvato: {os.path.basename(save_path)}", foreground="green")
        except ValueError as e:
            messagebox.showerror("Errore BPM", f"BPM non valido: {str(e)}")
            self.label_status_pers.config(text="❌ BPM invalido", foreground="red")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore: {str(e)}")
            self.label_status_pers.config(text="❌ Errore", foreground="red")
    
    def ferma_riproduzione(self):
        if self.audio_available:
            try:
                pygame.mixer.music.stop()
            finally:
                pygame.mixer.music.unload()
        else:
            self.label_status_pers.config(text="⚠️ Audio non disponibile", foreground="orange")

    def genera_midi(self, tono, scala, nome, bpm, armonia, voices=1):
        try:
            if not 40 <= bpm <= 200:
                raise ValueError("Il BPM deve essere compreso tra 40 e 200")
            if not 1 <= voices <= 8:
                raise ValueError("Il numero di voci deve essere compreso tra 1 e 8")

            mid = MidiFile()
            mid.ticks_per_beat = self.TPB
            track = MidiTrack()
            mid.tracks.append(track)

            # Imposta tempo
            tempo = bpm2tempo(bpm)
            track.append(MetaMessage('set_tempo', tempo=tempo, time=0))
            track.append(Message('program_change', program=0, time=0))

            # Durata in ticks (nota di quarto)
            note_duration = int(self.TPB)

            for n in scala:
                chord_notes = self.build_chord_notes(n, armonia, voices, scala)
                # Normalizza le note nell'intervallo MIDI 0-127
                norm_notes = []
                for note in chord_notes:
                    nn = note
                    while nn > 127:
                        nn -= 12
                    while nn < 0:
                        nn += 12
                    norm_notes.append(nn)

                # nota on simultanee
                for idx, nn in enumerate(norm_notes):
                    track.append(Message('note_on', note=nn, velocity=90, time=0))

                # nota off: primo off con durata, gli altri a tempo 0
                for idx, nn in enumerate(norm_notes):
                    if idx == 0:
                        track.append(Message('note_off', note=nn, velocity=0, time=note_duration))
                    else:
                        track.append(Message('note_off', note=nn, velocity=0, time=0))

            safe_name = "".join(
                character if character.isalnum() or character in ("-", "_") else "_"
                for character in str(nome)
            ).strip("_") or "scala"
            filename = os.path.join(self._temp_directory.name, f"{safe_name}_{tono}_{bpm}.mid")
            mid.save(filename)
            return filename
        except Exception as e:
            messagebox.showerror("Errore MIDI", f"Impossibile generare MIDI: {e}")
            return None

    def ascolta_midi(self, filename, loops=0):
        try:
            if not filename or not os.path.exists(filename):
                messagebox.showerror("Errore Riproduzione", "File MIDI non trovato")
                return False

            if not self.audio_available:
                messagebox.showinfo("Riproduzione", f"Audio non disponibile: {self.audio_error}")
                return False

            try:
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play(loops=loops)
                return True
            except Exception:
                if loops != 0:
                    messagebox.showinfo(
                        "Riproduzione",
                        "Il loop continuo richiede il mixer audio interno.",
                    )
                    return False
                # Fallback: apri il file con l'app predefinita del sistema
                try:
                    os.startfile(filename)
                    return True
                except Exception as e:
                    messagebox.showinfo("Riproduzione", f"Impossibile riprodurre il file: {e}")
                    return False
        except Exception as e:
            messagebox.showerror("Errore Riproduzione", str(e))
            return False

    def genera_e_ascolta_predefinita(self):
        try:
            bpm = int(self.var_bpm.get())
            tono = self.var_tono.get()
            scala_name = self.var_scala.get()
            armonia = self.var_armonia.get()

            intervalli = self.scale_map.get(scala_name, self.scale_map['maggiore'])
            scala = self.get_scale_da_note(tono, intervalli)
            if scala is None:
                return

            voices = int(self.var_voci.get()) if hasattr(self, 'var_voci') else 1
            if not self.carica_su_personalizzata(intervalli, tono, scala_name, bpm, armonia, voices):
                return
            filename = self.genera_midi(tono, scala, scala_name, bpm, armonia, voices=voices)
            if filename:
                if self.ascolta_midi(filename):
                    self.label_status.config(text=f"🎵 Riproducendo: {scala_name}", foreground="green")
                else:
                    self.label_status.config(text="⚠️ MIDI creato, riproduzione non avviata", foreground="orange")
            else:
                self.label_status.config(text="❌ Errore generazione MIDI", foreground="red")
        except Exception as e:
            messagebox.showerror("Errore", str(e))
            self.label_status.config(text="❌ Errore", foreground="red")

    def salva_predefinita_cartella(self):
        try:
            bpm = int(self.var_bpm.get())
            tono = self.var_tono.get()
            scala_name = self.var_scala.get()
            armonia = self.var_armonia.get()

            intervalli = self.scale_map.get(scala_name, self.scale_map['maggiore'])
            scala = self.get_scale_da_note(tono, intervalli)
            if scala is None:
                return

            voices = int(self.var_voci.get()) if hasattr(self, 'var_voci') else 1
            if not self.carica_su_personalizzata(intervalli, tono, scala_name, bpm, armonia, voices):
                return
            filename = self.genera_midi(tono, scala, scala_name, bpm, armonia, voices=voices)
            if not filename:
                return

            save_path = filedialog.asksaveasfilename(
                defaultextension=".mid",
                filetypes=[("MIDI", "*.mid"), ("All", "*.*")],
                initialfile=os.path.basename(filename)
            )
            if save_path:
                shutil.copy(filename, save_path)
                messagebox.showinfo("✓ Successo", f"File salvato!\n{os.path.basename(save_path)}")
                self.label_status.config(text=f"✅ Salvato: {os.path.basename(save_path)}", foreground="green")
        except Exception as e:
            messagebox.showerror("Errore", str(e))
            self.label_status.config(text="❌ Errore", foreground="red")

    def seleziona_preset_note(self, valore, nome):
        try:
            self.text_note.delete("1.0", tk.END)
            self.text_note.insert(tk.END, valore)
            self.label_status_pers.config(text=f"Preset: {nome}", foreground="green")
        except Exception as e:
            messagebox.showerror("Errore Preset", str(e))

    def carica_su_personalizzata(self, intervalli, tono, nome, bpm, armonia, voices=1):
        """Copia la scala selezionata nella tab 'Note Musicali' e avvia l'analisi."""
        try:
            degree_text = self.intervals_to_formula(intervalli)

            if hasattr(self, 'var_tono_pers'):
                self.var_tono_pers.set(tono)
            if hasattr(self, 'var_nome_scala_pers'):
                self.var_nome_scala_pers.set(nome)

            self.text_note.delete("1.0", tk.END)
            self.text_note.insert(tk.END, degree_text)

            if hasattr(self, 'var_bpm_pers'):
                self.var_bpm_pers.set(str(bpm))
            if hasattr(self, 'var_armonia_pers'):
                self.var_armonia_pers.set(armonia)
            if hasattr(self, 'var_voci_pers'):
                self.var_voci_pers.set(int(voices))

            if hasattr(self, 'notebook') and hasattr(self, 'frame_personalizzate'):
                self.notebook.select(self.frame_personalizzate)
            if hasattr(self, 'root'):
                self.root.update_idletasks()
            if hasattr(self, 'text_note') and hasattr(self, 'text_analisi'):
                self.analizza_note()
            return True
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare scala: {e}")
            return False

    def analizza_note(self):
        try:
            text_input = self.text_note.get("1.0", tk.END).strip()
            intervalli = self.parse_note_input(text_input)
            if intervalli is None:
                return
            tono = self.var_tono_pers.get()
            scala = self.get_scale_da_note(tono, intervalli)
            if scala is None:
                return

            armonia = self.var_armonia_pers.get() if hasattr(self, 'var_armonia_pers') else 'terze'
            voices = int(self.var_voci_pers.get()) if hasattr(self, 'var_voci_pers') else 1

            harmony = self.get_diatonic_harmony(scala)
            is_diatonic = len(harmony) == 7 and all(row["role"] is not None for row in harmony)
            scale_name = (
                self.var_nome_scala_pers.get().strip()
                if hasattr(self, 'var_nome_scala_pers')
                else ""
            ) or "Scala personalizzata"
            note_names = " · ".join(
                row["root"] for row in harmony
            )
            report = [
                (f"ANALISI ARMONICA — {scale_name}\n", "title"),
                (f"Tonalità: {tono}   ·   Gradi: {note_names}\n\n", ""),
            ]

            if is_diatonic:
                report.append(("FUNZIONI DIATONICHE · accordi costruiti per terze\n", "section"))
            else:
                report.extend([
                    (f"ARMONIZZAZIONE IN TERZE · {len(harmony)} gradi\n", "section"),
                    ("Scala non eptatonica: le funzioni tonali standard non vengono assegnate.\n", "tendency"),
                ])

            for row in harmony:
                if is_diatonic:
                    report.append((
                        f"{row['numeral']:<5} {row['chord']:<8} {row['quality']} · {row['role']}\n",
                        "degree",
                    ))
                    report.append((f"      {row['tendency']}\n", "tendency"))
                else:
                    report.append((
                        f"Grado {row['degree']} · {row['chord']} · {row['quality']}\n",
                        "degree",
                    ))

            if voices > 1:
                report.append((f"\nVOICING SELEZIONATO · {armonia}, {voices} voci\n", "section"))
                scale_degrees = [row["notes"][0] for row in harmony]
                pitch_names = {
                    row["notes"][0] % 12: row["root"]
                    for row in harmony
                }
                for row in harmony:
                    root = row["notes"][0]
                    chord_notes = self.build_chord_notes(root, armonia, voices, scale_degrees)
                    chord_note_names = [
                        self.get_note_name(note, pitch_names) for note in chord_notes
                    ]
                    chord_label = self.get_chord_label(chord_notes, root, row["root"])
                    degree_label = row["numeral"] if is_diatonic else f"Grado {row['degree']}"
                    report.append((f"{degree_label} · {chord_label}\n", "degree"))
                    report.append((f"      Note: {', '.join(chord_note_names)}\n", ""))
                    inversions = self.get_chord_inversions(
                        chord_notes,
                        root,
                        row["root"],
                        pitch_names,
                    )
                    if inversions:
                        report.append((f"      Rivolti: {'; '.join(inversions)}\n", "tendency"))

            self.text_analisi.config(state=tk.NORMAL)
            self.text_analisi.delete("1.0", tk.END)
            for content, tag in report:
                self.text_analisi.insert(tk.END, content, tag)
            self.text_analisi.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Errore Analisi", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = MusicHarmonizerApp(root)
    root.deiconify()
    root.update()
    root.lift()
    try:
        root.attributes("-topmost", True)
        root.after(100, lambda: root.attributes("-topmost", False))
    except Exception:
        pass
    root.focus_force()
    root.mainloop()
