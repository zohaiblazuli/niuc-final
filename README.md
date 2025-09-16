# PCC NIUC Guard

Utilities and guardrails that help NIUC teams validate and monitor their pipelines.

## Quickstart

```bash
# create and activate a virtual environment, then run:
python tasks.py setup
pre-commit install
python tasks.py lint
python tasks.py test
```

## Features

- Lightweight guardrail primitives for NIUC data checks
- Batteries-included developer workflow (lint, type-check, tests)
- Ready for CI with GitHub Actions

## Project Layout

- `src/pccniuc/` - library source code
- `tests/` - unit tests powered by pytest
- `bench/` - benchmarking harnesses (pytest-benchmark ready)
- `scripts/` - automation scripts
- `docs/` - documentation sources
- `examples/` - runnable usage examples

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on issue triage, coding standards, and release process.

## Security

If you believe you have found a security vulnerability, please review our policy in [SECURITY.md](SECURITY.md) and reach out to the security team.

## License

This project is licensed under the terms of the MIT License. See [LICENSE](LICENSE) for details.
