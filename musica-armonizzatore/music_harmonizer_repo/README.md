# Music Harmonizer

Repository standalone contenente solo `music_harmonizer.py`.

## Requisiti

- Python 3.13+
- pygame
- mido

## Installazione

```bash
pip install -r requirements.txt
```

## Uso

```bash
python music_harmonizer.py
```

## Creazione di un eseguibile Windows

```bash
pip install pyinstaller
pyinstaller --onefile --windowed music_harmonizer.py
```

L'eseguibile verrà creato nella cartella `dist/`.
