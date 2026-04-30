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

## FFT Algorithm

```C++
#include <vector>
#include <complex>
#include <cmath>

void fft(std::vector<std::complex<double>> &v) {
    const size_t n = v.size();
    // Base Case
    if (n == 1)
        return;

    // Divide vector into evens and odds
    std::vector<std::complex<double>> even(n / 2), odd(n / 2);
    for (size_t i = 0; i < n; i += 2) {
        even[i / 2] = v[i];
        odd[i / 2] = v[i + 1];
    }

    // Recursively call on each half
    fft(even);
    fft(odd);

    // Compose twittle factor
    const double theta = -2 * M_PI / n;
    std::complex<double> w(1);
    std::complex<double> wn(cos(theta), sin(theta));

    // Stitch vector back together using the butterfly method
    for (size_t i = 0; i < n / 2; i++) {
        v[i] = even[i] + w * odd[i];
        v[i + n / 2] = even[i] - w * odd[i];
        w *= wn;
    }
}
```