import tkinter as tk
import pyaudio
import numpy as np
from threading import Thread
from typing import Union


'''

Stardew Simon
Simon Says Listener for Stardew Valley

Author: thirdtype
https://github.com/thethirdtype

'''


class StardewSimonApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Stardew Simon")
        self.geometry("345x230")

        self.rate: int = 44100
        self.chunk: int = 1024

        self.colors: dict = {
            "Purple": 1046.50,  # C6
            "Green": 1567.98,   # G6
            "Red": 2093.00,     # C7
            "Blue": 2349.32,    # D7
            "Yellow": 2637.02   # E7
        }

        self.clear_button = None
        self.color_sequence_text = None
        self.listening = True
        self.pa = None
        self.stream = None
        self.thread = None

        self.create_widgets()
        self.setup_audio()

        self.color_sequence: list = []

        # Bind the destroy event to stop_listening method
        self.protocol("WM_DELETE_WINDOW", self.stop_listening)

    def clear_colors(self) -> None:
        self.color_sequence_text.delete("1.0", tk.END)
        self.color_sequence.clear()

    def create_widgets(self) -> None:
        self.color_sequence_text = tk.Text(self, height=10, width=40)
        self.color_sequence_text.grid(row=0, column=0, padx=10, pady=10)

        self.clear_button = tk.Button(self, text="Clear History", command=self.clear_colors)
        self.clear_button.grid(row=1, column=0, pady=10)

    def detect_frequency(self, data: np.ndarray) -> float:
        fft_data = np.fft.fft(data)
        freqs = np.fft.fftfreq(len(fft_data), 1.0 / self.rate)
        idx = np.argmax(np.abs(fft_data))
        dominant_freq = freqs[idx]

        return dominant_freq

    def display_color(self, color: str) -> None:
        if color:
            if self.color_sequence and self.color_sequence[-1] == color:
                return

            self.color_sequence.append(color)
            current_text = ", ".join(self.color_sequence)
            self.color_sequence_text.delete("1.0", tk.END)
            self.color_sequence_text.insert(tk.END, current_text + "\n")

            # Set foreground color for each color in the sequence
            start_pos = "1.0"
            for word in current_text.split(", "):
                word_len = len(word)
                for i in range(word_len):
                    char_start_pos = f"{start_pos}+{i}c"
                    char_end_pos = f"{start_pos}+{i + 1}c"
                    self.color_sequence_text.tag_add(word, char_start_pos, char_end_pos)
                    self.color_sequence_text.tag_config(word, foreground=word, font=("Arial", 12, "bold"))
                start_pos = f"{start_pos}+{word_len + 2}c"  # Move to the next word, accounting for comma and space

    def get_color_by_frequency(self, frequency: float) -> Union[str, None]:
        for color, freq in self.colors.items():
            if abs(float(frequency) - freq) < 128:  # Adjust this threshold as needed
                return color
        return None

    def setup_audio(self) -> None:
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format=pyaudio.paInt16,
                                   channels=1,
                                   rate=self.rate,
                                   input=True,
                                   frames_per_buffer=self.chunk)
        self.thread = Thread(target=self.listen_microphone)
        self.thread.start()

    def listen_microphone(self) -> None:
        while self.listening:
            data = np.frombuffer(self.stream.read(self.chunk), dtype=np.int16)
            freq = self.detect_frequency(data)
            if freq:
                color = self.get_color_by_frequency(freq)
                if color:
                    self.display_color(color)

    def stop_listening(self) -> None:
        self.listening = False
        if self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
        self.pa.terminate()
        self.thread.join()

        self.destroy()


if __name__ == "__main__":
    app = StardewSimonApp()
    app.mainloop()
