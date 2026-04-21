import argparse
from pathlib import Path


def _get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, required=True, help="Audio File to load (must be .wav)")
    return parser.parse_args()


def get_file_path(audio_dir: Path = Path("audio")):
    """
    Gets and verifies the file, and returns the file name without `.wav` extension.

    :return: File path and name without .wav intention
    """
    args = _get_args()
    file_path = args.file

    if not file_path.endswith(".wav"):
        raise ValueError("File must have extension `.wav`.")
    if len(file_path) <= 4:
        raise ValueError("File is unnamed.")
    if not Path(audio_dir / file_path).is_file():
        raise FileNotFoundError(f"{file_path} not found.")
    if len(Path(file_path).parts) > 1:
        raise ValueError(f"Audio file must be located in the `{audio_dir}` directory. "
                         f"\nCorrect usage: `python main.py -f <file_name>.wav`")

    return file_path[:-4]
