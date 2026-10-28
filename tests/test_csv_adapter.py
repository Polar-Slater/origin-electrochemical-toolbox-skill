import csv
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/electrochemical-analysis/scripts'
spec = importlib.util.spec_from_file_location('origin_import', SCRIPTS / 'origin_import.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)

class CsvAdapterTests(unittest.TestCase):
    def read(self, rows):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'data.csv'
            with path.open('w', newline='', encoding='utf-8-sig') as stream:
                csv.writer(stream).writerows(rows)
            return adapter.read_table(path)

    def test_known_schemas_and_plot_columns(self):
        cases = [
            ('OCV', ['Time','Potential'], ['sec','V'], [1,.3], [(0,1)]),
            ('CV', ['Potential','Current'], ['V','A'], [.3,.001], [(0,1)]),
            ('CA', ['Time','Original Current','Current density'], ['sec','A','mA/cm2'], [1,.002,1], [(0,2)]),
            ('CP', ['Time','Original Potential','Potential',''], ['sec','V','V vs RHE',''], [1,.5,1.429,''], [(0,2)]),
            ('ECSA delta j', ['Scan rate','Delta j mA/cm^2','Fitted line formula'], ['mV s-1','mA/cm2',''], [10,.2,'y = .02*x'], [(0,1)]),
        ]
        for kind, header, units, row, pairs in cases:
            with self.subTest(kind=kind):
                table = self.read([header, units, row])
                self.assertEqual(table['kind'], kind)
                self.assertEqual(table['pairs'], pairs)
                self.assertEqual(table['rows'], 1)

    def test_eis_keeps_sign_units_metadata(self):
        table = self.read([
            ['Working area (cm^2)', '2', '', '', ''],
            ['Frequency', "Z'", "-Z''", 'Z', 'Phase'],
            ['Hz','ohm cm2','ohm cm2','ohm cm2','deg'],
            [1000,4,-2,4.47,26.565], [10,6,2,6.32,-18.435]])
        self.assertEqual(table['columns'][2], [-2,2])
        self.assertEqual(table['columns'][1], [4,6])
        self.assertEqual(table['metadata'][0][1], '2')
        self.assertEqual(table['pairs'], [(1,2)])

    def test_lsv_keeps_already_corrected_values_and_filename(self):
        table = self.read([
            ['File','Point','Original Potential','Original Current','Potential (V vs. RHE, iR-corrected)','Current density'],
            ['','','V','mA','V vs. RHE, iR-corrected','mA/cm2'],
            ['sample.txt',1,.5,10,1.32253,10]])
        self.assertEqual(table['columns'][4], [1.32253])
        self.assertEqual(table['columns'][0], ['sample.txt'])
        self.assertEqual(table['pairs'], [(4,5)])

    def test_uncorrected_lsv_label_and_provenance(self):
        table = self.read([
            ['Resistance source', 'not supplied', 'iR correction applied', 'no'],
            ['File','Point','Original Potential','Original Current','Potential (V vs. RHE)','Current density'],
            ['','','V','mA','V vs. RHE','mA/cm2'],
            ['sample.txt',1,.5,10,1.429,10]])
        self.assertEqual(table['kind'], 'LSV')
        self.assertEqual(table['columns'][4], [1.429])
        self.assertEqual(table['metadata'][0][-1], 'no')
        self.assertNotIn('iR-corrected', table['names'][4])

    def test_cv_trailing_padding_and_scan_labels(self):
        rows = [['Potential','Current density']*2, ['V','mA/cm2']*2,
                ['10 mV/s']*2+['20 mV/s']*2, [.2,1,.2,2], [.3,1.5,'','']]
        table = self.read(rows)
        self.assertEqual(table['kind'], 'ECSA cycle CV')
        self.assertEqual(table['labels'][2], '20 mV/s')
        self.assertEqual(table['pairs'], [(0,1),(2,3)])
        rows[-1] = [.3,1.5,.3,'']
        with self.assertRaises(ValueError): self.read(rows)

    def test_reject_unknown_ragged_and_nonfinite(self):
        for rows in [
            [['a','b'],[1,2]],
            [['Time','Potential'],['sec','V'],[1]],
            [['Time','Potential'],['sec','V'],[1,'nan']],
        ]:
            with self.subTest(rows=rows), self.assertRaises(ValueError): self.read(rows)

    def test_inspection_cli_does_not_require_origin(self):
        result = subprocess.run([sys.executable, str(SCRIPTS/'origin_import.py'), '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--inspect', result.stdout)

if __name__ == '__main__':
    unittest.main()
