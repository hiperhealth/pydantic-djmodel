# Release notes

## 0.2.0

- Generate models inside the consuming Django app, with standard migrations.
- Preserve scalar types, optional fields, and common defaults. Use JSON fields
  for JSON-compatible structured data.
- Test the installed wheel on Django 5.2 and 6.0.

Review the [upgrade guide](installation.md#upgrade-from-010) before migrating
models created with 0.1.0.
