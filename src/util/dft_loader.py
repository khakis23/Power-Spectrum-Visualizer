import numpy.typing as npt
import numpy as np
from scipy.io import wavfile


def wav_to_spectra_file(in_file, out_file, fps=30):
    """
    data.shape = (frames/time, DFT bins)

    :param in_file:
    :param out_file:
    :param fps:
    :return:
    """
    # read sample rate and data from file
    fs, data = wavfile.read(in_file)

    # convert to mono
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)

    # normalize data (0 < 1)
    data = data / np.max(np.abs(data))

    chuck_size = int(fs / fps)
    n_chucks = len(data) // chuck_size

    spectra = []

    for i in range(n_chucks):
        cur_chuck = data[i * chuck_size : (i + 1) * chuck_size]

        # window to smooth edges
        # cur_chuck = np.hanning(len(cur_chuck)) * cur_chuck

        # add spectrum to list
        spectra.append(
            np.abs(np.fft.rfft(cur_chuck))
        )

    # build file header so fs can live in the same file
    header = np.zeros((1, spectra[0].shape[0]))
    header[0, 0] = fs

    with open(out_file, "wb") as f:
        np.save(f, np.vstack([header, spectra]))


def load_spectra_from_file(in_file) -> tuple[npt.NDArray, int]:
    """
    spectra.shape = (frames/time, DFT bins)

    :param in_file: file path of the spectra.spa file
    :return: spectra, sample rate
    """
    data = np.load(in_file)
    return data[1:], data[0][0]
