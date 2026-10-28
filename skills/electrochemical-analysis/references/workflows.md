# Toolbox workflows and schemas

Source: https://github.com/Polar-Slater/Electrochemical_data_analysis

## Raw measurement processing

Import `origin_csv` from `Electrochemical_data_analysis_toolbox v2.0` (current tested VERSION.txt: 2.5.0). `process_files(paths, output_dir, settings)` handles selected files. `process_sample_folder(folder, settings, output_dir)` handles top-level `.txt` files and skips deposition `_it` files. Individual-file mode can process deposition files. Both return `ProcessingReport(created, skipped, failures)`.

Create a JSON settings file with all these fields, using values established for the actual experiment:

- `working_area_cm2`: positive electrode area.
- `reference_potential_v`: additive reference-to-RHE offset in V, under the experimental conditions. Do not guess from an electrode name alone.
- `equilibrium_potential_v`: equilibrium potential in V versus RHE appropriate to the requested reaction. Recorded by the processor; not subtracted from its LSV corrected-potential column.
- `solution_resistance_ohm`: explicit resistance shared by selected LSV files, or null to resolve each filename independently. Missing resistance is allowed when compensation is zero.
- `compensation_percent`: finite value from 0 to 100. Nonzero compensation requires a resistance supplied explicitly or found in that file's name; otherwise that LSV file fails without writing its CSV. Requires toolbox 2.7.2 or later.
- `ecsa_cycle_number`: positive cycle number, or null for the toolbox's last-cycle behavior.
- `cp_solution_resistance_ohm` and `cp_compensation_percent`: separate CP correction settings. CA does not use potential correction.

For irrelevant fields use documented neutral values and identify them as unused; do not present those as measured settings. Batch processing across mixed types requires resolving the settings for every affected measurement.

```powershell
& '<Windows Python>' '<skill>/scripts/process_chi.py' --toolbox '<toolbox repository>' --folder '<sample folder>' --settings '<settings.json>' --output '<fresh output folder>'
```

The helper requires a fresh or empty output directory to avoid upstream's unconditional file replacement. Its nonzero exit status means failures were recorded; inspect `processing-manifest.json`. Source hashes allow checking that inputs stayed unchanged.

## Processed CSV to Origin

`scripts/origin_import.py --csv FILE --inspect` prints schema and plot mappings without connecting to Origin. `--output FRESH_FOLDER` imports the table, makes a basic plot, exports PNG/PDF, and saves the existing Origin project in place. The intended project must already be saved. No OPJU is created in the export directory. The helper records metadata and the project location in its JSON manifest and units/labels in the workbook. It performs **no scientific corrections**.

| Schema | Plot mapping | Special handling |
|---|---|---|
| OCV | Time vs Potential | raw potential in V, not automatically RHE |
| Activation CV | Potential vs Current | acquisition sequence, V and A |
| LSV | corrected potential vs current density | File and Point columns retained; no second iR correction |
| EIS | Z' vs -Z'' | ohm cm2; frequency retained; basic auto-scaled axes, adjust physical aspect for equal-unit Nyquist geometry when requested |
| CA | Time vs Current density | original current also retained |
| CP | Time vs corrected Potential | reference/iR settings in metadata |
| ECSA cycle CV | every potential/current-density pair | third row contains scan-rate labels; trailing empty pairs permitted |
| ECSA delta j | scan rate vs Delta j | formula text retained; slope is capacitance per area after consistent unit conversion |

Unknown or legacy formats need explicit schema adaptation; do not infer a header merely because a row contains numbers. Old `Processed data` exports differ from current `Processed` outputs.

## Calculations already implemented upstream

LSV: `E_RHE_corrected = E_original + E_reference - I_A * Rs * fraction`; `j_mA_cm2 = I_A * 1000 / area`. Overpotential is a separate derived quantity `eta = E_RHE_corrected - E_equilibrium`.

EIS: `Z_real_export = area * Z_real_ohm`; `minus_Z_imag_export = -area * Z_imag_ohm`. For DearEIS fitting, divide area-normalized impedances by the recorded positive area and undo the minus sign, or use the original raw input. Never take an absolute value to force a semicircle.

ECSA-related export: half the branch-current difference at the toolbox-selected midpoint, normalized by area, versus scan rate. Numerically, (mA/cm2)/(mV/s) yields F/cm2. Converting Cdl to ECSA requires an explicitly chosen specific capacitance and normalization convention.

### Required EIS figure set (user preference)

Include |Z| vs frequency, -Z'' vs frequency, phase vs frequency, and Nyquist. Use logarithmic frequency; use logarithmic magnitude only for strictly positive values and linear -Z'' so negative or zero data remain visible. Frequency stays in Hz and phase in degrees.

Retain raw-ohm impedance figures. If a positive electrode area A in cm2 is available, additionally plot A|Z| vs frequency, A(-Z'') vs frequency, and the Nyquist pair (AZ', A(-Z'')), with impedance axes labelled ohm cm2 (or Ω·cm²). Do not divide by area when converting raw ohms to ohm cm2. If the input is already area-normalized, use it directly and recover raw ohms only by dividing by its recorded normalization area; do not multiply twice. If area is unavailable, provide raw-ohm plots and explain why normalized variants are omitted. For SS310 A=1 cm2, normalized and raw curves have the same numerical values but distinct units. This does not authorize estimating electrochemically active surface area.

## Advanced tool routing

- `Tafel fitter/README.md`: modern Python 3 fitter, separate from legacy `Tafel_Fitter_v1.51`. It reads raw and processed LSV, reconstructs corrected values from original E/I, and avoids repeated correction. Inspect the fit domain, reaction/sign convention, baseline and selection method. Preserve fit parameters and provenance.
- `EIS Analysis/README.md`: adapted DearEIS for circuit fitting, DRT, Kramers-Kronig, Z-HIT. Separate environment and dependencies; inspect its setup and tests before use. Do not install it into the plotting environment without checking compatibility.
- `DRTtools modified`: a separate workflow; its presence does not mean the Python helper runs it.

Read applicable AGENTS.md before modifying toolbox source. No toolbox source modifications are needed for this skill.
