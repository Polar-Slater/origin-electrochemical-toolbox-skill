# Repository maintenance

- Keep reusable code in skills/, synthetic tests in tests/, generated artifacts in outputs/, and machine-specific material in local/.
- Do not commit raw measurements, Origin projects, virtual environments, credentials, personal absolute paths, or downloaded third-party source trees.
- VERSION.txt is authoritative. Every source or documentation change after a release must increment the version appropriately and add a corresponding CHANGELOG.md entry (patch for compatible fixes, minor for features, major for breaking changes).
- Run `python -m unittest discover -s tests -v` after changes. Validate skill metadata with skill-creator's quick_validate.py when available. Live Origin checks are separate; never clear a user's project to run them.
- Preserve one intended Origin session/project, use Project Explorer folders for samples, and save in place. Do not silently Save As into export directories.
- Keep claims of tested behavior distinct from planned figure types or scientific validation.
