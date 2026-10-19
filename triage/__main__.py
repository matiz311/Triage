import argparse
import json
from pathlib import Path
from .engine import batch

parser = argparse.ArgumentParser(description='Triage offline, nessuna modifica al portale')
parser.add_argument('input', type=Path)
args = parser.parse_args()
try:
    print(json.dumps(batch(json.loads(args.input.read_text())), ensure_ascii=False, indent=2))
except (ValueError, OSError) as exc:
    parser.exit(2, f'Errore: {exc}\n')
