# Validation and limitations

Initial release: 0.1.0 (2026-10-27).

Prior live setup: Windows Python 3.14.6 x64, originpro 1.1.15, OriginExt 1.2.6, Matplotlib 3.11.2, OriginPro 2024b 10.1.5.132. Toolbox revision fbbc0ac34a233598cd916ff088daeadc3ae73356, v2.5.0.

- Three upstream origin_csv integration tests passed on the repository's Ni-foil sample.
- Twelve processed CSVs were generated with no failures; five deposition files were intentionally skipped by folder processing.
- Four local integration tests covered all eight CSV schemas, LSV correction exactly once, EIS signs/area against raw input, and unchanged source hashes.
- Live LSV/EIS imports exported PNG/PDF and saved project files. Subsequent SS310 plotting added 11 graphs from 25 measurements inside one Project Explorer folder.
- Earlier test helpers saved project copies into export folders. The current helper instead saves in place and checks that the project directory/name has not changed before saving. This change passed static validation but has not been live-regression-tested since the reported crash.
- A Windows application error recorded an Origin 2024b ok.dll access violation. Exact cause is unresolved; do not claim that save-behavior changes prevent crashes.

Public tests use synthetic CSVs and do not depend on local sample paths or a running Origin. No advanced solver, 3D Nyquist, or project-reopening validation is claimed. Area-normalized and negative-imaginary frequency figures are required by the skill instructions; generating full figure sets currently requires agent orchestration beyond the single-CSV helper.
