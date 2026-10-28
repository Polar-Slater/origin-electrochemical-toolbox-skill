"""Run the existing CHI processor without changing its calculations."""
import argparse
import dataclasses
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

DEFAULT_REPO = os.environ.get('ELECTROCHEMICAL_TOOLBOX')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--toolbox', type=Path, default=DEFAULT_REPO, help='Repository root; defaults to ELECTROCHEMICAL_TOOLBOX')
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--folder', type=Path)
    source.add_argument('--files', nargs='+', type=Path)
    parser.add_argument('--settings', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.toolbox is None:
        parser.error('Provide --toolbox or set ELECTROCHEMICAL_TOOLBOX to the toolbox checkout')
    if not (args.toolbox / 'Electrochemical_data_analysis_toolbox v2.0' / 'origin_csv.py').is_file():
        parser.error('Toolbox path does not contain the v2.0 origin_csv.py processor')
    os.environ.setdefault('MPLBACKEND', 'Agg')
    sys.path.insert(0, str(args.toolbox / 'Electrochemical_data_analysis_toolbox v2.0'))
    if not (args.toolbox / 'Electrochemical_data_analysis_toolbox v2.0' / 'correction_settings.py').is_file():
        parser.error('Processing requires toolbox 2.7.2 or later with shared correction validation')
    from origin_csv import ProcessingSettings, process_files, process_sample_folder
    values = json.loads(args.settings.read_text(encoding='utf-8-sig'))
    expected = {f.name for f in dataclasses.fields(ProcessingSettings)}
    if set(values) != expected:
        parser.error(f'Settings keys must match exactly; missing={expected-set(values)}, unknown={set(values)-expected}')
    for key, value in values.items():
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)):
            parser.error(f'{key} must be finite numeric or null')
    for key in ['working_area_cm2', 'reference_potential_v', 'equilibrium_potential_v', 'compensation_percent', 'cp_compensation_percent']:
        if values[key] is None:
            parser.error(f'{key} must be explicit numeric')
    cycle = values['ecsa_cycle_number']
    if cycle is not None and (not isinstance(cycle, int) or cycle < 1):
        parser.error('ecsa_cycle_number must be a positive integer or null')
    settings = ProcessingSettings(**values)
    try:
        settings.validate()
    except ValueError as exc:
        parser.error(str(exc))
    paths = sorted(args.folder.glob('*.txt')) if args.folder else args.files
    if not paths or any(not p.is_file() for p in paths):
        parser.error('No readable source files found')
    if len({p.stem.casefold() for p in paths}) != len(paths):
        parser.error('Duplicate source stems would overwrite outputs; process samples separately')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('Choose a new or empty output directory')
    inputs = [{'path':str(p.resolve()), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
    revision = subprocess.run(['git', '-C', str(args.toolbox), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    report = process_sample_folder(args.folder, settings, args.output) if args.folder else process_files(paths, args.output, settings)
    manifest = {'toolbox':str(args.toolbox.resolve()), 'revision':revision, 'settings':values,
                'inputs':inputs, 'created':[str(p.resolve()) for p in report.created],
                'skipped':list(report.skipped), 'failures':list(report.failures)}
    (args.output / 'processing-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))
    return 1 if report.failures else 0

if __name__ == '__main__':
    raise SystemExit(main())
