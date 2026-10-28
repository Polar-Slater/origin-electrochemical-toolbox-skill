"""Integration checks against the sibling toolbox checkout when available."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOLBOX = ROOT.parent / 'Electrochemical_data_analysis'
SCRIPT = ROOT / 'skills/electrochemical-analysis/scripts/process_chi.py'
SETTINGS = dict(working_area_cm2=1, reference_potential_v=0, equilibrium_potential_v=1.23,
                solution_resistance_ohm=None, compensation_percent=100, ecsa_cycle_number=None,
                cp_solution_resistance_ohm=None, cp_compensation_percent=0)


@unittest.skipUnless((TOOLBOX / 'Electrochemical_data_analysis_toolbox v2.0/correction_settings.py').is_file(),
                     'Sibling toolbox 2.7.2 checkout is required')
class ProcessingValidationTests(unittest.TestCase):
    def run_processor(self, folder, name, settings):
        source = folder / name
        source.write_text('date\nLinear Sweep Voltammetry\nPotential/V,Current/A\n0.5,0.01\n')
        config = folder / 'settings.json'
        config.write_text(json.dumps(settings))
        output = folder / 'out'
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), '--toolbox', str(TOOLBOX),
                                 '--files', str(source), '--settings', str(config), '--output', str(output)],
                                capture_output=True, text=True,
                                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        return result, output

    def test_filename_resistance_allowed_and_missing_resistance_reported(self):
        for name, expected_code in [('LSV 2 ohm.txt', 0), ('LSV.txt', 1)]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                result, output = self.run_processor(Path(directory), name, SETTINGS)
                self.assertEqual(result.returncode, expected_code, result.stderr)
                manifest = json.loads((output / 'processing-manifest.json').read_text())
                self.assertEqual(len(manifest['failures']), expected_code)
                self.assertEqual(len(list(output.glob('*.csv'))), 1 - expected_code)

    def test_invalid_settings_fail_before_creating_outputs(self):
        for update in [{'working_area_cm2': float('nan')}, {'compensation_percent': 101},
                       {'solution_resistance_ohm': -1}]:
            with self.subTest(update=update), tempfile.TemporaryDirectory() as directory:
                result, output = self.run_processor(Path(directory), 'LSV.txt', SETTINGS | update)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
