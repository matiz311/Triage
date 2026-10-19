import argparse
import json
from pathlib import Path
from .engine import batch

parser = argparse.ArgumentParser(description='Triage offline, nessuna modifica al portale')
parser.add_argument('input', type=Path)
parser.add_argument('--format', choices=('json', 'note'), default='json')
args = parser.parse_args()
try:
    result = batch(json.loads(args.input.read_text()))
    print('\n\n'.join(r['technical_report']['note_text'] for r in result) if args.format == 'note' else json.dumps(result, ensure_ascii=False, indent=2))
except (ValueError, OSError) as exc:
    parser.exit(2, f'Errore: {exc}\n')
