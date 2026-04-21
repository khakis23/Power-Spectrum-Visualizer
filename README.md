## UV Usage

```bash
uv sync
uv run fft.py -f Dreams.wav
```

## Normal pip Usage

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m pip install -U pygame==2.6.0
python3 fft.py -f Dreams.wav
```