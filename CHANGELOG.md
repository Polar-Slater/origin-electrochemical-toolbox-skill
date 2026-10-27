# Changelog

This project uses semantic versioning. VERSION.txt is the authoritative release version.

## [0.1.0] - 2026-10-27

### Added
- Electrochemical-analysis skill for the CHI toolbox and OriginPro workflow.
- CLI wrapper around existing toolbox calculations, with explicit settings, source hashes, and processing manifests.
- CSV inspection and Origin plotting for eight current toolbox schemas.
- User workflow defaults: 0.929 V reference offset and 90% LSV iR compensation, overridable per experiment.
- EIS plotting guidance for magnitude, negative imaginary impedance, phase, Nyquist, and area-normalized variants.
- Portable configuration, synthetic tests, setup instructions, and dependency attribution.

### Fixed
- Save the current Origin project in place instead of silently creating a project copy in every figure directory.
- Avoid duplicate units in axis labels and reject malformed CSV rows and mismatched CV padding.

### Workspace organization
- Separate reusable skills, generated outputs, and local historical scripts/reports.
- Exclude measurements, projects, recovery backups, environments, and machine-specific configuration from Git.

### Known limits
- The bundled plotting CLI produces one basic graph from one processed CSV; the agent assembles complete EIS figure sets and multi-sample layouts using Origin automation.
- Voltage-stacked 3D Nyquist is a proposed extension, not implemented or validated in this release.
- Advanced fitting and Origin crash prevention are not validated by the helper tests.
