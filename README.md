# Audio Spectrum Visualizer
### Authors: Tyler Black, Dayton Singer

The Audio Spectrum Visualizer is an example application for the Fast Fourier Transform (FFT) algorithm.
The program displays an accurate representation of the real-time audio spectrum.

## Features
- Customizable graphics (colors/images, number of bars, FPS, view size)
- Can play any `.wav` audio file
- Logarithmic scaling for accurate visualization
- Adjustable _pseudo_ gain and dynamic range
- Supports cross-language FFT processing via `.spa` files


## Usage

1. Place a `.wav` audio file in the `audio` directory.

2. Run the program using the following command:

```bash
python3 fft.py -f <audio-file-name>
```

*Optionally adjust `fft.py` to use any path or preprocess audio in a different program.

### UV Example

```bash
uv sync
uv run fft.py -f Dreams.wav
```

### Normal pip Example

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m pip install -U pygame==2.6.0
python3 fft.py -f Dreams.wav
```