# markdown-link-checker

A lightweight, zero‑dependency command‑line tool that validates HTTP/HTTPS links inside Markdown (`.md`) files.

## Features
- Scans a single file or an entire directory recursively.
- Reports HTTP status codes and flags time‑outs.
- Outputs a concise, color‑coded summary.
- Ideal for CI/CD integration.

## Installation
```bash
# Clone the repo and install
git clone https://github.com/yourusername/markdown-link-checker.git
cd markdown-link-checker
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt  # (currently empty, no deps)
```

## Usage
```bash
# Check a single file
python link_checker.py path/to/readme.md

# Check all markdown files under a directory
python link_checker.py path/to/docs/ --recursive
```

## Exit Codes
- `0` – All links are reachable.
- `1` – One or more broken links were found.
- `2` – Usage error / file not found.

## Contributing
Feel free to open issues or submit PRs. Please adhere to the `CONTRIBUTING.md` guidelines (to be added).

## License
MIT – see the `LICENSE` file for details.
