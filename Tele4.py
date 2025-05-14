import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os

default_sample_rate = 44100
default_duration = 5

def record_audio(duration, sample_rate):
    print(f"\nNagrywanie przez {duration} sekund przy {sample_rate} Hz...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    return audio.flatten()

def save_wav(filename, data, sample_rate):
    scaled = np.int16(data / np.max(np.abs(data)) * 32767)
    wav.write(filename, sample_rate, scaled)
    print(f"Zapisano jako: {filename}")

def load_wav(filename):
    sample_rate, data = wav.read(filename)
    return sample_rate, data.astype(np.float32) / 32768.0

def play_audio(data, sample_rate):
    print(f"\nOdtwarzanie ({sample_rate} Hz)...")
    sd.play(data, sample_rate)
    sd.wait()
    print("Odtwarzanie zakończone.")

def quantize(signal, bit_depth):
    max_amplitude = np.max(np.abs(signal))
    levels = 2 ** bit_depth
    step = 2 * max_amplitude / (levels - 1)
    quantized = np.round(signal / step) * step
    return quantized

def compute_snr(original, quantized):
    noise = original - quantized
    signal_power = np.mean(original ** 2)
    noise_power = np.mean(noise ** 2)
    return 10 * np.log10(signal_power / noise_power) if noise_power != 0 else float('inf')

def process_selected_sample_rate(original, original_sr, selected_sr, bit_depths, base_filename):
    print(f"\nWybrana częstotliwość próbkowania: {selected_sr} Hz")
    if selected_sr != original_sr:
        indices = np.round(np.linspace(0, len(original) - 1, int(len(original) * selected_sr / original_sr))).astype(int)
        indices = np.clip(indices, 0, len(original) - 1)
        sampled = original[indices]
    else:
        sampled = original

    for bd in bit_depths:
        print(f"  -> Kwantyzacja: {bd} bitów")
        quantized = quantize(sampled, bd)
        filename = f"{base_filename}_{selected_sr}Hz_{bd}bit.wav"
        save_wav(filename, quantized, selected_sr)
        snr = compute_snr(sampled, quantized)
        print(f"SNR: {snr:.2f} dB")

def list_wav_files():
    return [f for f in os.listdir() if f.lower().endswith(".wav")]

def menu():
    sample_rate = default_sample_rate
    duration = default_duration
    bit_depths = [4, 8, 16]
    selected_sample_rate = sample_rate

    while True:
        print("\n======= MENU GŁÓWNE =======")
        print("1. Nagraj dźwięk i zapisz pod nazwą")
        print("2. Wygeneruj wersje z różnym próbkowaniem i kwantyzacją z pliku WAV")
        print("3. Odtwórz plik WAV")
        print("4. Zmień parametry nagrania (czas i częstotliwość)")
        print("5. Wyjdź")
        wybor = input("Wybierz opcję (1-5): ")

        if wybor == "1":
            nazwa = input("Podaj nazwę pliku (bez rozszerzenia): ")
            filename = f"{nazwa}.wav"
            audio = record_audio(duration, sample_rate)
            save_wav(filename, audio, sample_rate)

        elif wybor == "2":
            nazwa = input("Podaj nazwę istniejącego pliku WAV (bez rozszerzenia): ")
            filename = f"{nazwa}.wav"
            if not os.path.exists(filename):
                print("Plik nie istnieje. Najpierw nagraj lub skopiuj plik.")
                continue
            sr, data = load_wav(filename)
            print(f"Generowanie wersji z częstotliwością {selected_sample_rate} Hz...")
            process_selected_sample_rate(data, sr, selected_sample_rate, bit_depths, nazwa)

        elif wybor == "3":
            nazwa = input("Podaj nazwę pliku do odtworzenia (bez rozszerzenia): ")
            filename = f"{nazwa}.wav"
            if not os.path.exists(filename):
                print("Plik nie istnieje.")
                continue
            try:
                sr, data = load_wav(filename)
                play_audio(data, sr)
            except Exception as e:
                print(f"Błąd podczas odczytu: {e}")

        elif wybor == "4":
            try:
                selected_sample_rate = int(input("Nowa częstotliwość próbkowania (np. 44100): "))
                duration = float(input("Nowy czas nagrania (w sekundach): "))
                sample_rate = selected_sample_rate
                print(f"Ustawiono: {sample_rate} Hz, {duration} s")
            except ValueError:
                print("Błędne dane. Spróbuj ponownie.")

        elif wybor == "5":
            print("Program zakończony.")
            break

        else:
            print("Nieznana opcja. Wybierz od 1 do 5.")

if __name__ == "__main__":
    menu()
