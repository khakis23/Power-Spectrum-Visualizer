from src.Visualizer.Visualizer import Visualizer
from src.util.arg_parger import get_file_path
from src.util.dft_loader import wav_to_spectra_file
from pathlib import Path


AUDIO_DIR = Path("audio")
SPEC_DIR = Path("spectra")

# usage:  python3 fft.py -f Dreams.wav
if __name__ == "__main__":
    file_path_name = get_file_path()   # exclude extension

    # This could be done in C++
    wav_to_spectra_file(AUDIO_DIR / (file_path_name + ".wav"), SPEC_DIR / (file_path_name + ".spa"), fps=30)

    vis = Visualizer()
    vis.set_n_bars(128)
    vis.set_bar_color("gradient", ((203, 142, 223), (145, 223, 151)))
    vis.set_gain(0.7)
    vis.set_dynamic_range(80)
    vis.set_background_color("image", "assets/space_background.jpg")

    # This load the .spa file and the .wav file form the AUDIO and SPECTRA directories
    vis.visualize_from_file(SPEC_DIR / (file_path_name + ".spa"), AUDIO_DIR / (file_path_name + ".wav"), fps=30)
