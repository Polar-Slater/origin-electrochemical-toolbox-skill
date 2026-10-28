# Origin electrochemical toolbox skill

Version **0.1.1**. A reusable agent skill that connects [Polar-Slater's electrochemical toolbox](https://github.com/Polar-Slater/Electrochemical_data_analysis) to editable OriginPro figures. It reuses the toolbox's calculations rather than introducing new electrochemical methods.

## Repository layout

```text
skills/electrochemical-analysis/  Skill instructions, helpers, references
tests/                          Synthetic tests (no experiment data)
VERSION.txt                     Authoritative version
CHANGELOG.md                    Release history
outputs/                        Local generated figures/logs (ignored)
local/                          Local scripts/reports/config (ignored)
```

Third-party checkouts and virtual environments are local dependencies, not included in this repository. The original workspaces may retain their existing dependency paths to keep installed MCP servers working.

## Install

Requires Windows, a licensed Origin/OriginPro installation, and Windows Python. The author's live tests used OriginPro 2024b 64-bit 10.1.5.132 with Python 3.14.6. Other versions need their own compatibility check.

Processing with this release requires toolbox 2.7.2 or later for strict
correction validation and per-file resistance provenance.

```powershell
git clone https://github.com/Polar-Slater/origin-electrochemical-toolbox-skill.git
cd origin-electrochemical-toolbox-skill
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
git clone https://github.com/Polar-Slater/Electrochemical_data_analysis.git toolbox
$env:ELECTROCHEMICAL_TOOLBOX = (Resolve-Path toolbox).Path
```

Install `skills/electrochemical-analysis` into your agent's skill directory. For the existing Codex user installation, the directory is `~/.codex/skills/electrochemical-analysis`. Copy the entire skill directory, not only SKILL.md. An optional private `references/local-runtime.md` can record the Python and toolbox paths for that installation; do not commit it.

The `originplot` and `origin-pro-mcp` skills are complementary third-party tools, not bundled here. This skill's Python helper uses `originpro` directly and does not require an MCP server.

## Usage

Ask your agent: “Use electrochemical-analysis to process this sample and create Origin graphs in a folder inside the current project.” Provide electrode area, resistance, and any overrides to the configured reference offset and compensation defaults. The defaults 0.929 V and 90% LSV compensation are the author's workflow preferences, not universal electrochemical constants.

For direct processing, create the settings JSON described in [workflows.md](skills/electrochemical-analysis/references/workflows.md), then run:

```powershell
& .\.venv\Scripts\python.exe skills/electrochemical-analysis/scripts/process_chi.py --toolbox toolbox --folder '<sample>' --settings '<settings.json>' --output 'outputs/run/processed'
& .\.venv\Scripts\python.exe skills/electrochemical-analysis/scripts/origin_import.py --csv '<processed.csv>' --inspect
& .\.venv\Scripts\python.exe skills/electrochemical-analysis/scripts/origin_import.py --csv '<processed.csv>' --output 'outputs/run/figure'
```

Before live plotting, open and save the intended Origin project and resolve multiple running instances. The helper adds a worksheet/graph in the active Project Explorer folder, exports PNG/PDF, and saves the **same project**. It does not create a project in the output directory. It does not close or reset Origin. Choose a fresh output directory for each run.

## Supported and planned behavior

The CSV helper recognizes OCV, LSV, EIS, activation CV, CP, CA, scan-rate CV, and half-current-difference schemas from toolbox v2.0. Full EIS figure sets, formatting, and comparisons are agent workflows documented by the skill; the CLI alone is a basic single-CSV plotter. Circuit fitting, DRT, Kramers–Kronig, and Tafel analysis route to the existing toolbox applications and require separate setup/validation. Voltage-stacked 3D Nyquist remains planned.

Tests and prior live checks are summarized in [validation.md](skills/electrochemical-analysis/references/validation.md). A crash was observed in Origin 2024b's ok.dll during the broader workflow; its cause is unresolved. Corrected project-save behavior does not constitute a crash fix.

## Tests and versioning

```powershell
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests use temporary synthetic CSVs and do not launch Origin or modify measurements. For each subsequent release, update VERSION.txt and CHANGELOG.md together. No raw data or generated project files should be committed.

## Attribution

- Processing algorithms: [Electrochemical_data_analysis](https://github.com/Polar-Slater/Electrochemical_data_analysis), tested revision `fbbc0ac34a233598cd916ff088daeadc3ae73356` (toolbox version 2.5.0).
- Origin automation: OriginLab's `originpro` package and local OriginPro installation.
- Complementary skills: [deliuou/originplot-skill](https://github.com/deliuou/originplot-skill) and [leima-max/origin-pro-mcp-skill](https://github.com/leima-max/origin-pro-mcp-skill).

Third-party software retains its own license terms; this repository does not redistribute those source trees or grant rights to them.
