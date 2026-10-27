---
name: electrochemical-analysis
description: Process CHI electrochemical measurements with the user's Electrochemical_data_analysis toolbox and create editable OriginPro figures. Use for OCV, LSV, CV, ECSA-related capacitance, EIS, and CP/CA workflows, or routing to the toolbox's Tafel and DearEIS analyses.
---

# Electrochemical analysis

Reuse the user's toolbox calculations and parsers, then use OriginPro for editable figures. This is an offline data-analysis skill, not instrument control.

## Runtime and resources

- Use Windows Python with the dependencies in the repository's requirements.txt and a local licensed Origin installation.
- Locate the user's checkout of Polar-Slater/Electrochemical_data_analysis; pass it as `--toolbox` or set `ELECTROCHEMICAL_TOOLBOX`. If a private `references/local-runtime.md` exists in this installation, use its paths.
- Read [references/workflows.md](references/workflows.md) for processing settings, CSV schemas, and advanced-analysis routing.
- `scripts/process_chi.py` runs the toolbox's file/folder processor and records settings, hashes, and errors.
- `scripts/origin_import.py` inspects or plots the v2.0 processor's CSV schemas without reapplying corrections. Run `--help` for arguments. Both helpers accept paths from other projects.

If a path is missing, locate the user's existing checkout/runtime before installing another copy. Tested versions and limits are in [references/validation.md](references/validation.md). Do not silently pull updates; record the revision used.

## Workflow

User defaults (explicitly authorized): reference-to-RHE offset 0.929 V and LSV iR compensation 90% when unspecified. Explicit task settings override these. Obtain sample-specific resistance and area from recorded information; do not transfer LSV resistance to CP. These defaults replace the need to ask for the two values on each task.

1. Identify measurement type, raw versus processed input, sample grouping, and requested output. Inspect headers and metadata before selecting columns. Keep different samples' scan-rate CVs in separate processing calls.
2. Resolve experimental settings from the user's request, recorded metadata, or an established project configuration. Ask only for missing consequential settings. Folder/file names are hints for area and resistance, not authority to enable compensation. Never reuse the Ni-foil test values as defaults for another sample.
3. For raw CHI input, call the existing toolbox functions through `process_chi.py`; choose a fresh output directory. For processed input, inspect it directly. Do not normalize or correct processed columns a second time.
4. For plotting, use `origin_import.py` or the installed originplot skill. The helper supports single-panel plots from known processor schemas; use the general Origin skills for comparisons, multipanel figures, templates, and custom formatting. The MCP numeric CSV importer cannot directly parse these metadata/units rows.
5. Verify row counts, selected columns, units, signs, and output files. Inspect the exported figure. Report processing failures and skipped files separately from successful outputs; a partial run is not a complete success. Preserve a manifest alongside plots and the editable project.

## Scientific and session constraints

- Preserve original measurements and acquisition order. Do not remove outliers, smooth, average duplicates, choose a fit interval, or change EIS signs without a reason tied to the request.
- Explicitly distinguish reference-electrode potential, potential versus RHE, and overpotential. The processor's corrected LSV column is potential versus RHE, not overpotential.
- `Delta j` in the toolbox ECSA export is already half the anodic/cathodic difference. Do not divide it by two again. Do not call its slope ECSA without the required specific-capacitance convention and units.
- EIS processor output contains area-normalized Z' and **-Z''**. Preserve that for Nyquist plotting; circuit fitting requires signed Z'' in ohms. Keep frequency in Hz.
- EIS figure sets must include impedance magnitude |Z| versus frequency, negative imaginary impedance -Z'' versus frequency, phase versus frequency, and Nyquist plots. Retain impedance plots in ohms. When a positive electrode area is recorded, also provide area-normalized magnitude, -Z'', and Nyquist plots in ohm cm2; multiply raw impedance in ohms by area in cm2 exactly once. Phase is unchanged. Preserve zero/negative -Z'' values using a linear vertical axis and logarithmic frequency axis; do not take absolute values or silently discard points to enable a log scale. Record the area value and source. See references/workflows.md for normalization details.
- The existing CHI parsers may skip malformed rows. Inspect raw tables and investigate unexplained count differences before scientific interpretation; the wrapper does not make upstream parsers strict.
- Use one existing Origin session and one intended project. Check the running instance and current project before editing; if multiple instances make the target ambiguous, resolve that before attaching. Attach/detach without clearing or closing it. Create sample folders inside Project Explorer. Export folders contain figures and logs, not automatic project copies. Save the current project in place; use Save As only when explicitly requested. If it is untitled, establish its intended save path first. Serialize automation operations and close blocking dialogs before automation.
- For Tafel, DRT, circuit fits, or Kramers-Kronig analysis, follow the dedicated toolbox documentation and verify the relevant runtime. Do not imply the CSV/plot smoke test validates those solvers or their scientific assumptions.

Example requests: “Process this sample with these electrode settings and plot its LSV in Origin”; “Compare these EIS CSVs as Nyquist plots”; “Plot the CV scan-rate series and delta-j relation, preserving the selected cycle.”
