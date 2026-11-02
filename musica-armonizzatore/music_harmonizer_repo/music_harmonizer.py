import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog
import threading
import pygame
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
        
        self.BPM = 90
        self.TPB = 480
        self.C = 60
        
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.note_italian = {
            '1': 'Do', '2': 'Re', '3': 'Mi', '4': 'Fa', 
            '5': 'Sol', '6': 'La', '7': 'Si'
        }
        self.scale_degree_patterns = {
            'maggiore': '1 2 3 4 5 6 7 8',
            'minore_naturale': '1 2 3b 4 5 6b 7b 8',
            'minore_armonica': '1 2 3b 4 5 6b 7 8',
            'minore_melodica': '1 2 3b 4 5 6 7 8',
            'dorica': '1 2 3b 4 5 6 7b 8',
            'frigia': '1 2b 3b 4 5 6b 7b 8',
            'lidia': '1 2 3 4# 5 6 7 8',
            'misolidia': '1 2 3 4 5 6 7b 8',
            'locria': '1 2b 3b 4 5b 6b 7b 8',
            'pentatonica_mag': '1 2 3 5 6 8',
            'pentatonica_min': '1 3b 4 5 7b 8',
            'blues': '1 3b 4 5 6 7b 8',
            'bebop_dominante': '1 2 3 4 5 6 6# 7 8',
            'bebop_minore': '1 2 3b 4 5 6 7 8',
            'diminuita': '1 3b 4 5 6 7 8 8#',
            'aumentata': '1 3 4 6 8',
            'araba': '1 2 3b 4 5 6b 7 8',
            'araba_maggiore': '1 2 3 4 5 6b 7 8',
            'araba_minore': '1 2 3b 4 5 6b 7b 8',
            'orientale': '1 2b 3 4# 5 6b 7 8',
            'orientale_maggiore': '1 2 3 4# 5 6b 7 8',
            'orientale_minore': '1 2 3b 4# 5 6b 7b 8',
            'persiana': '1 1# 3 4 5b 6b 7 8',
            'persiana_maggiore': '1 1# 3 4 5b 6b 7 8',
            'persiana_minore': '1 2b 3 4 5b 6b 7b 8',
            'russa': '1 2 3b 4# 5 6 7b 8',
            'russa_maggiore': '1 2 3 4# 5 6 7b 8',
            'russa_minore': '1 2 3b 4 5 6b 7b 8',
            'rumena': '1 2 3b 4# 5 6 7b 8',
            'rumena_maggiore': '1 2 3b 4# 5 6 7b 8',
            'rumena_minore': '1 2 3b 4 5 6b 7 8',
            'ungherese': '1 2 3b 4# 5b 6 7 8',
            'ungherese_maggiore': '1 2 3 4# 5b 6 7 8',
            'ungherese_minore': '1 2 3b 4# 5b 6 7 8',
            'egizia': '1 2 3 5 6 7b 8',
            'egizia_maggiore': '1 2 3 5 6 7 8',
            'egizia_minore': '1 2 3b 5 6 7b 8',
            'enigmatica': '1 1# 3 4# 5# 6# 7 8',
            'enigmatica_maggiore': '1 1# 3 4# 5# 6# 7 8',
            'enigmatica_minore': '1 2 3b 4# 5# 6 7b 8',
            'double_harmonic': '1 1# 3 4 5 5# 7 8',
            'double_harmonic_maggiore': '1 1# 3 4 5 5# 7 8',
            'double_harmonic_minore': '1 2 3b 4 5 6b 7 8',
            'napoletana': '1 2b 3b 4 5 6 7 8',
            'napoletana_maggiore': '1 2b 3b 4 5 6 7 8',
            'napoletana_minore': '1 2b 3b 4 5 6b 7b 8',
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
        
        self.audio_available = True
        self.audio_error = ""
        try:
            pygame.mixer.init()
        except Exception as exc:
            self.audio_available = False
            self.audio_error = str(exc)
            self.label_status = ttk.Label(self.frame_predefinite, text="⚠️ Audio non disponibile", foreground="orange", font=("Arial", 8))
            self.label_status.pack(fill=tk.X, pady=3)
    
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
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=3)
        
        # ===== INFO =====
        info_frame = ttk.LabelFrame(top_frame, text="Istruzioni", padding="3")
        info_frame.pack(fill=tk.X, pady=3)
        instructions = (
            "Scrivi la scala usando gradi diatonici: 1 2 3 4 5 6 7 8. "
            "Usa # per il diesis e b per il bemolle, ad esempio 3b o 4#. "
            "La nota 8 indica l'ottava successiva di 1.\n"
            "Esempi: 1 2 3b 4 5 6b 7b 8 (minore naturale), "
            "1 2 3 4# 5 6 7 8 (lidia), 1 2 3b 5 6 7b 8 (pent. minore).\n"
            "Premi Analizza per vedere gli accordi generati e Ascolta per suonare la scala."
        )
        ttk.Label(info_frame, text=instructions, font=("Arial", 8), justify=tk.LEFT, wraplength=780).pack(anchor=tk.W)
        
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
        
        self.text_analisi = tk.Text(frame_analisi, height=4, width=100, bg="white", state=tk.DISABLED, font=("Courier", 8))
        self.text_analisi.pack(pady=2, fill=tk.BOTH, expand=True)
        
        # ===== CONFIG =====
        frame_config = ttk.LabelFrame(main_frame, text="Config", padding="3")
        frame_config.pack(fill=tk.X, pady=3)
        
        ttk.Label(frame_config, text="Armonia:").pack(side=tk.LEFT, padx=2)
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
    
    # ===== METODI =====
    def parse_note_input(self, text_input):
        try:
            note_input = text_input.strip().split()
            if not note_input:
                raise ValueError("Inserisci almeno una nota")
            
            intervalli = []
            intervalli_base = [0, 2, 4, 5, 7, 9, 11]
            
            for i, nota in enumerate(note_input):
                # Estrai il numero (1-7)
                base = int(nota[0])
                if base < 1 or base > 8:
                    raise ValueError(f"Nota {nota}: usa 1-8 (8=ottava)")

                # Intervallo base della nota (8 significa l'ottava del Do)
                if base == 8:
                    semitono = intervalli_base[0]
                else:
                    semitono = intervalli_base[base - 1]
                
                # Applica alterazioni (# e b)
                if len(nota) > 1:
                    alterazione = nota[1:]
                    for char in alterazione:
                        if char == '#':
                            semitono += 1
                        elif char == 'b':
                            semitono -= 1
                
                # Se è l'ultima nota, mettila un'ottava più alta
                if i == len(note_input) - 1:
                    semitono += 12
                
                intervalli.append(semitono)
            
            return intervalli
        except ValueError as e:
            messagebox.showerror("Errore Input", f"Errore nel parsing: {str(e)}")
            return None
        except Exception as e:
            messagebox.showerror("Errore", f"Errore imprevisto: {str(e)}")
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

    def get_note_name(self, midi_note):
        note_name = self.note_names[midi_note % 12]
        octave = midi_note // 12 - 1
        return f"{note_name}{octave}"

    def get_pitch_name(self, pitch_class):
        names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return names[pitch_class % 12]

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

    def get_chord_label(self, chord_notes):
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

    def build_chord_notes(self, root, armonia, voices, scale=None):
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
            
            # Riproduci in thread separato
            thread = threading.Thread(target=self.ascolta_midi, args=(filename,), daemon=True)
            thread.start()
            
            self.label_status_pers.config(text=f"🎵 Riproducendo: {nome}", foreground="green")
            
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
            
            # Dialog salvataggio
            save_path = filedialog.asksaveasfilename(
                defaultextension=".mid",
                filetypes=[("MIDI", "*.mid"), ("All", "*.*")],
                initialfile=filename
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
            pygame.mixer.music.stop()
        else:
            self.label_status_pers.config(text="⚠️ Audio non disponibile", foreground="orange")

    def genera_midi(self, tono, scala, nome, bpm, armonia, voices=1):
        try:
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

            filename = os.path.join(tempfile.gettempdir(), f"{nome}_{tono}_{bpm}.mid")
            mid.save(filename)
            return filename
        except Exception as e:
            messagebox.showerror("Errore MIDI", f"Impossibile generare MIDI: {e}")
            return None

    def ascolta_midi(self, filename):
        try:
            if not filename or not os.path.exists(filename):
                messagebox.showerror("Errore Riproduzione", "File MIDI non trovato")
                return

            if not self.audio_available:
                messagebox.showinfo("Riproduzione", f"Audio non disponibile: {self.audio_error}")
                return

            try:
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
            except Exception:
                # Fallback: apri il file con l'app predefinita del sistema
                try:
                    os.startfile(filename)
                except Exception as e:
                    messagebox.showinfo("Riproduzione", f"Impossibile riprodurre il file: {e}")
        except Exception as e:
            messagebox.showerror("Errore Riproduzione", str(e))

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
            try:
                self.carica_su_personalizzata(intervalli, tono, scala_name, bpm, armonia, voices)
            except Exception:
                pass
            filename = self.genera_midi(tono, scala, scala_name, bpm, armonia, voices=voices)
            if filename:
                thread = threading.Thread(target=self.ascolta_midi, args=(filename,), daemon=True)
                thread.start()
                self.label_status.config(text=f"🎵 Riproducendo: {scala_name}", foreground="green")
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
            try:
                self.carica_su_personalizzata(intervalli, tono, scala_name, bpm, armonia, voices)
            except Exception:
                pass
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
            # Usa la rappresentazione diretta se disponibile per la scala predefinita
            degree_text = self.scale_degree_patterns.get(nome)
            if degree_text is None:
                # Converti gli intervalli (semitoni) in gradi numerici con alterazioni
                intervalli_base = [0, 2, 4, 5, 7, 9, 11]
                parts = []
                for s in intervalli:
                    octave = 0
                    sval = int(s)
                    if sval >= 12:
                        octave = 1
                        sval = sval % 12

                    # trova il grado diatonico più vicino
                    best_idx = 0
                    best_diff = None
                    for idx, base in enumerate(intervalli_base):
                        diff = sval - base
                        if best_diff is None or abs(diff) < abs(best_diff):
                            best_diff = diff
                            best_idx = idx

                    # costruisci la stringa del grado (1-7, o 8 per ottava se octave e grado=1)
                    degree_num = best_idx + 1
                    if octave == 1 and best_idx == 0:
                        degree_str = '8'
                    else:
                        degree_str = str(degree_num)

                    # aggiungi alterazioni (# o b)
                    if best_diff is not None and best_diff != 0:
                        if best_diff > 0:
                            degree_str += '#' * int(best_diff)
                        else:
                            degree_str += 'b' * int(abs(best_diff))

                    parts.append(degree_str)

                degree_text = " ".join(parts)

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
                try:
                    self.var_voci_pers.set(int(voices))
                except Exception:
                    pass

            # Seleziona la tab delle note personalizzate e aggiorna l'analisi
            try:
                self.notebook.select(self.frame_personalizzate)
            except Exception:
                pass
            self.root.update_idletasks()
            try:
                self.analizza_note()
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare scala: {e}")

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

            self.text_analisi.config(state=tk.NORMAL)
            self.text_analisi.delete("1.0", tk.END)
            lines = []
            lines.append(f"Tono: {tono}")
            lines.append(f"Intervalli (semitoni): {intervalli}")
            lines.append(f"Note MIDI: {scala}")
            lines.append(f"Armonia: {armonia}, Voci: {voices}")

            if voices > 1:
                lines.append("Accordi:")
                for idx, root in enumerate(scala):
                    chord_notes = self.build_chord_notes(root, armonia, voices, scala)
                    chord_note_names = [self.get_note_name(n) for n in chord_notes]
                    chord_label = self.get_chord_label(chord_notes)
                    lines.append(f"  {idx + 1}: {chord_label}")
                    lines.append(f"     Note: {', '.join(chord_note_names)}")

            self.text_analisi.insert(tk.END, "\n".join(lines))
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



