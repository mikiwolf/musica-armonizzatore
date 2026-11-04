import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog
import pygame
import re
import shutil
import os
import tempfile
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
        self.sequencer_steps_per_bar = 16
        self.sequencer_bars = 4
        self.sequencer_low_note = 48
        self.sequencer_high_note = 83
        self.sequencer_cell_width = 28
        self.sequencer_cell_height = 22
        self.sequencer_chord_vars = []
        self.sequencer_chord_combos = []

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
            values=list(self.scale_map),
            state="readonly",
            width=20,
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(controls, text="BPM:").pack(side=tk.LEFT, padx=(0, 3))
        self.sequencer_bpm_var = tk.StringVar(value="90")
        ttk.Spinbox(
            controls,
            from_=40,
            to=200,
            textvariable=self.sequencer_bpm_var,
            width=5,
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(controls, text="Ogni colonna è un sedicesimo; clicca le celle per inserire/togliere note.").pack(
            side=tk.LEFT, padx=5
        )

        progression = ttk.LabelFrame(self.frame_sequencer, text="Progressione (un accordo per battuta)", padding=5)
        progression.pack(fill=tk.X, padx=6, pady=4)
        for bar in range(self.sequencer_bars):
            ttk.Label(progression, text=f"Battuta {bar + 1}:").pack(side=tk.LEFT, padx=(4, 2))
            chord_var = tk.StringVar(value=str([1, 5, 6, 4][bar]))
            chord_combo = ttk.Combobox(progression, textvariable=chord_var, state="readonly", width=16)
            chord_combo.pack(side=tk.LEFT, padx=(0, 8))
            chord_combo.bind("<<ComboboxSelected>>", self.redraw_sequencer_grid)
            self.sequencer_chord_vars.append(chord_var)
            self.sequencer_chord_combos.append(chord_combo)

        self.sequencer_scale_var.trace_add("write", self.refresh_sequencer_chords)
        self.sequencer_key_var.trace_add("write", self.refresh_sequencer_chords)
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
        self.sequencer_canvas.bind("<Button-1>", self.toggle_sequencer_note)

        actions = ttk.Frame(self.frame_sequencer)
        actions.pack(fill=tk.X, padx=6, pady=4)
        ttk.Button(actions, text="▶ Ascolta", command=self.play_sequencer).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions, text="⏹ Ferma", command=self.ferma_riproduzione).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions, text="💾 Esporta MIDI", command=self.save_sequencer).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions, text="Svuota melodia", command=self.clear_sequencer).pack(side=tk.LEFT, padx=2)
        self.sequencer_status = ttk.Label(actions, text="Pronto", foreground="blue")
        self.sequencer_status.pack(side=tk.LEFT, padx=8)
        self.redraw_sequencer_grid()

    def get_sequencer_scale(self):
        key = self.sequencer_key_var.get()
        scale_name = self.sequencer_scale_var.get()
        if key not in self.note_names or scale_name not in self.scale_map:
            raise ValueError("Seleziona una tonalità e una scala valide")
        base = self.C + self.note_names.index(key)
        return [base + interval for interval in self.scale_map[scale_name]]

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
            degrees = self.get_sequencer_chord_degrees()
            for combo, chord_var, degree in zip(
                self.sequencer_chord_combos,
                self.sequencer_chord_vars,
                degrees,
            ):
                root = scale[degree]
                notes = self.build_chord_notes(root, "terze", 3, scale)
                label = self.get_chord_label(notes)
                options = []
                for option_degree, option_root in enumerate(scale[:-1]):
                    chord = self.build_chord_notes(option_root, "terze", 3, scale)
                    options.append(f"{option_degree + 1} - {self.get_chord_label(chord)}")
                combo.configure(values=options)
                chord_var.set(f"{degree + 1} - {label}")
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
        total_steps = self.sequencer_bars * self.sequencer_steps_per_bar
        width = left + total_steps * cell_width
        height = top + (self.sequencer_high_note - self.sequencer_low_note + 1) * cell_height

        try:
            scale = self.get_sequencer_scale()
            chord_degrees = self.get_sequencer_chord_degrees()
            chord_pcs_by_bar = []
            for degree in chord_degrees:
                chord = self.build_chord_notes(scale[degree], "terze", 3, scale)
                chord_pcs_by_bar.append({note % 12 for note in chord})
        except (ValueError, tk.TclError):
            chord_pcs_by_bar = [set() for _ in range(self.sequencer_bars)]

        for bar in range(self.sequencer_bars):
            bar_x = left + bar * self.sequencer_steps_per_bar * cell_width
            canvas.create_text(
                bar_x + self.sequencer_steps_per_bar * cell_width / 2,
                12,
                text=f"Battuta {bar + 1}",
                fill="#333333",
            )

        for pitch in range(self.sequencer_high_note, self.sequencer_low_note - 1, -1):
            row = self.sequencer_high_note - pitch
            y = top + row * cell_height
            canvas.create_text(left - 6, y + cell_height / 2, text=self.get_note_name(pitch), anchor=tk.E, fill="#333333")
            for step in range(total_steps):
                bar = step // self.sequencer_steps_per_bar
                x = left + step * cell_width
                chord_tone = pitch % 12 in chord_pcs_by_bar[bar]
                pitch_class = pitch % 12
                fill = "#dcefe5" if chord_tone else ("#f0f0f0" if pitch_class in (1, 3, 6, 8, 10) else "#ffffff")
                if (step, pitch) in self.sequencer_notes:
                    fill = "#287a55"
                outline = "#9aa0a6" if step % 4 else "#626a73"
                canvas.create_rectangle(
                    x,
                    y,
                    x + cell_width,
                    y + cell_height,
                    fill=fill,
                    outline=outline,
                    width=2 if step % self.sequencer_steps_per_bar == 0 else 1,
                )

        canvas.configure(scrollregion=(0, 0, width + 2, height + 2))

    def toggle_sequencer_note(self, event):
        x = self.sequencer_canvas.canvasx(event.x) - 44
        y = self.sequencer_canvas.canvasy(event.y) - 26
        if x < 0 or y < 0:
            return
        step = int(x // self.sequencer_cell_width)
        row = int(y // self.sequencer_cell_height)
        total_steps = self.sequencer_bars * self.sequencer_steps_per_bar
        pitch = self.sequencer_high_note - row
        if step >= total_steps or pitch < self.sequencer_low_note:
            return
        note = (step, pitch)
        if note in self.sequencer_notes:
            self.sequencer_notes.remove(note)
        else:
            self.sequencer_notes.add(note)
        self.redraw_sequencer_grid()

    def clear_sequencer(self):
        self.sequencer_notes.clear()
        self.redraw_sequencer_grid()
        self.sequencer_status.config(text="Melodia svuotata", foreground="blue")

    def build_sequencer_midi(self, key, scale_name, bpm, chord_degrees, melody_notes):
        if not 40 <= bpm <= 200:
            raise ValueError("Il BPM deve essere compreso tra 40 e 200")
        if key not in self.note_names or scale_name not in self.scale_map:
            raise ValueError("Tonalità o scala non valida")
        melody_notes = tuple(melody_notes)
        scale = [
            self.C + self.note_names.index(key) + interval
            for interval in self.scale_map[scale_name]
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
        tempo_track.append(MetaMessage("time_signature", numerator=4, denominator=4, time=0))
        midi.tracks.append(tempo_track)

        ticks_per_step = self.TPB // 4
        ticks_per_bar = self.TPB * 4
        for track_name in ("Accordi", "Melodia"):
            track = MidiTrack()
            midi.tracks.append(track)
            track.append(MetaMessage("track_name", name=track_name, time=0))
            track.append(Message("program_change", program=0, time=0))
            events = []

            if track_name == "Accordi":
                for bar, degree in enumerate(chord_degrees):
                    chord_notes = self.build_chord_notes(scale[degree], "terze", 3, scale)
                    start = bar * ticks_per_bar
                    end = start + ticks_per_bar
                    for pitch in chord_notes:
                        events.append((start, 1, Message("note_on", note=pitch, velocity=58)))
                        events.append((end, 0, Message("note_off", note=pitch, velocity=0)))
            else:
                for step, pitch in melody_notes:
                    start = step * ticks_per_step
                    end = start + ticks_per_step - 4
                    events.append((start, 1, Message("note_on", note=pitch, velocity=96)))
                    events.append((end, 0, Message("note_off", note=pitch, velocity=0)))

            previous_tick = 0
            for tick, _, message in sorted(events, key=lambda event: (event[0], event[1], event[2].note)):
                message.time = tick - previous_tick
                track.append(message)
                previous_tick = tick

        return midi

    def play_sequencer(self):
        try:
            midi = self.build_sequencer_midi(
                self.sequencer_key_var.get(),
                self.sequencer_scale_var.get(),
                int(self.sequencer_bpm_var.get()),
                self.get_sequencer_chord_degrees(),
                self.sequencer_notes,
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

    def save_sequencer(self):
        try:
            midi = self.build_sequencer_midi(
                self.sequencer_key_var.get(),
                self.sequencer_scale_var.get(),
                int(self.sequencer_bpm_var.get()),
                self.get_sequencer_chord_degrees(),
                self.sequencer_notes,
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
            (0, 4, 7, 10): "{}7",
            (0, 3, 7, 10): "{}m7",
            (0, 4, 7, 11): "{}maj7",
            (0, 3, 7, 11): "{}m(maj7)",
            (0, 2, 4, 7): "{}add9",
            (0, 2, 3, 7): "{}m(add9)",
            (0, 2, 4, 7, 11): "{}maj9",
            (0, 2, 3, 7, 10): "{}m9",
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
            return f"{display_root} ({self.intervals_to_formula(intervals)})"

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
        formula = self.get_chord_formula(chord_notes)
        return f"{root_name} ({formula})"

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

    def ascolta_midi(self, filename):
        try:
            if not filename or not os.path.exists(filename):
                messagebox.showerror("Errore Riproduzione", "File MIDI non trovato")
                return False

            if not self.audio_available:
                messagebox.showinfo("Riproduzione", f"Audio non disponibile: {self.audio_error}")
                return False

            try:
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
                return True
            except Exception:
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
