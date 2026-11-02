import os
import sys
import tkinter as tk
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import music_harmonizer


class MusicHarmonizerAppTests(unittest.TestCase):
    def test_init_continues_when_pygame_audio_fails(self):
        root = tk.Tk()
        root.withdraw()
        try:
            with patch("music_harmonizer.pygame.mixer.init", side_effect=Exception("audio unavailable")):
                app = music_harmonizer.MusicHarmonizerApp(root)
            self.assertFalse(app.audio_available)
            self.assertIn("audio unavailable", app.audio_error)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
