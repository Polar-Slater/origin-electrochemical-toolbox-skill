"""Inspect or plot current toolbox Origin CSVs, retaining units and metadata."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

def read_table(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.reader(stream))
    found = None
    for i, row in enumerate(rows):
        if row == ['Frequency', "Z'", "-Z''", 'Z', 'Phase']:
            found = (i, 'EIS', [(1,2)], set(range(5)), False)
        elif (len(row) == 6 and row[:4] == ['File', 'Point', 'Original Potential', 'Original Current']
              and row[4] in ['Potential (V vs. RHE, iR-corrected)', 'Potential (V vs. RHE)']
              and row[5] == 'Current density'):
            found = (i, 'LSV', [(4,5)], set(range(1,6)), False)
        elif row[:2] == ['Scan rate', 'Delta j mA/cm^2'] and len(row) == 3:
            found = (i, 'ECSA delta j', [(0,1)], {0,1}, False)
        elif len(row) >= 2 and len(row)%2 == 0 and row == ['Potential', 'Current density']*(len(row)//2):
            found = (i, 'ECSA cycle CV', [(j,j+1) for j in range(0,len(row),2)], set(range(len(row))), True)
        elif row == ['Potential', 'Current']:
            found = (i, 'CV', [(0,1)], {0,1}, False)
        elif row == ['Time', 'Potential']:
            found = (i, 'OCV', [(0,1)], {0,1}, False)
        elif row == ['Time', 'Original Current', 'Current density']:
            found = (i, 'CA', [(0,2)], {0,1,2}, False)
        elif row == ['Time', 'Original Potential', 'Potential', '']:
            found = (i, 'CP', [(0,2)], {0,1,2}, False)
        if found:
            break
    if found is None:
        raise ValueError('Unknown CSV schema; inspect and adapt explicitly')
    index, kind, pairs, numeric, cycles = found
    names = rows[index]
    units = rows[index+1]
    if len(units) != len(names):
        raise ValueError('Units row does not match header')
    labels = rows[index+2] if cycles else ['']*len(names)
    start = index + (3 if cycles else 2)
    columns = [[] for _ in names]
    for lineno, row in enumerate(rows[start:], start+1):
        if not any(row):
            continue
        if len(row) != len(names):
            raise ValueError(f'Ragged row at line {lineno}')
        for col, value in enumerate(row):
            if col in numeric:
                if not value and cycles:
                    value = float('nan')
                else:
                    value = float(value)
                    if not math.isfinite(value):
                        raise ValueError(f'Non-finite value at line {lineno}')
            columns[col].append(value)
    if not columns[0]:
        raise ValueError('Empty data table')
    if cycles:
        for x,y in pairs:
            ended = False
            for a,b in zip(columns[x], columns[y]):
                missing = math.isnan(a), math.isnan(b)
                if missing[0] != missing[1] or (ended and not missing[0]):
                    raise ValueError('CV gaps must be paired trailing padding')
                ended = ended or missing[0]
    return dict(kind=kind, names=names, units=units, labels=labels, pairs=pairs,
                columns=columns, metadata=rows[:index], rows=len(columns[0]))

def plot(path, output):
    table = read_table(path)
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError('Choose a new or empty output directory')
    output.mkdir(parents=True, exist_ok=True)
    import originpro as op
    op.attach()
    try:
        if not op.path('p'):
            raise RuntimeError('Save the intended Origin project once before plotting; this helper will not choose a project location.')
        project_directory = op.path('p')
        project_name = op.get_lt_str('%G')
        wks = op.new_sheet('w', lname=Path(path).stem)
        for i, values in enumerate(table['columns']):
            wks.from_list(i, values, lname=table['names'][i], units=table['units'][i], comments=table['labels'][i])
        graph = op.new_graph(lname=Path(path).stem, template='line')
        layer = graph[0]
        for x,y in table['pairs']:
            layer.add_plot(wks, colx=x, coly=y, type='l')
        layer.rescale()
        x,y = table['pairs'][0]
        def label(i):
            name, unit = table['names'][i], table['units'][i]
            if unit and unit not in name:
                name = f'{name} ({unit})'
            return name.replace('"', '')
        layer.lt_exec(f'xb.text$="{label(x)}"; yl.text$="{label(y)}";')
        if len(table['pairs']) == 1:
            layer.lt_exec('legend.show=0;')
        for ext in ['png', 'pdf']:
            target = output / f'figure.{ext}'
            graph.save_fig(str(target.resolve()))
            if not target.is_file() or target.stat().st_size < 1000:
                raise RuntimeError(f'Export failed: {target}')
        if op.path('p') != project_directory or op.get_lt_str('%G') != project_name:
            raise RuntimeError('Active project changed during plotting; stopped before saving')
        if not op.save():
            raise RuntimeError('Saving the existing project failed; check Origin dialogs')
        manifest = {k:v for k,v in table.items() if k != 'columns'}
        manifest.update(source=str(Path(path).resolve()), sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(), worksheet=wks.name, graph=graph.name, origin_version=op.lt_float('@V'), project_directory=project_directory, project_name=project_name, saved_existing_project=True)
        (output / 'plot-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        print(json.dumps(manifest, indent=2))
    finally:
        op.detach()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--inspect', action='store_true')
    mode.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.inspect:
        print(json.dumps({k:v for k,v in read_table(args.csv).items() if k != 'columns'}, indent=2))
    else:
        plot(args.csv, args.output)

if __name__ == '__main__':
    main()
