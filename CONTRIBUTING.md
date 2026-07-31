# Contributing to AI Engineering Orchestrator

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

### Branch Strategy

- `main` - Production-ready code, protected, requires PR approval
- `develop` - Integration branch for features
- `feature/*` - Feature branches (e.g., `feature/llm-integration`)
- `fix/*` - Bug fix branches
- `docs/*` - Documentation updates

### Workflow

1. Fork the repo and create your branch from `develop`
2. If you've added code, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes (`make test`)
5. Ensure linting passes (`make lint`)
6. Issue a pull request into `develop`

### Conventional Commits

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: correct issue
docs: update documentation
test: add tests
refactor: restructure code
chore: maintenance tasks
ci: CI/CD changes
style: formatting changes
```

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the CHANGELOG.md with details of changes
3. The PR will be merged once you have the sign-off of maintainers
4. Make sure your PR description clearly describes the problem and solution

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Alaashamel/ai-engineering-orchestrator.git
cd ai-engineering-orchestrator

# Install dependencies
make api-deps
make web-deps

# Set up environment
cp .env.example .env

# Run tests
make test

# Run linters
make lint
```

## Code Quality

- **Python**: Follow PEP 8, use type hints, run `ruff check`
- **TypeScript**: Follow project conventions, run `tsc --noEmit`
- **Tests**: Aim for >80% coverage on new code
- **Documentation**: Document public APIs and complex logic

## Any contributions you make will be under the MIT Software License

When you submit code changes, your submissions are understood to be under the same [MIT License](LICENSE) that covers the project.

## Report bugs using Github's [issue tracker](https://github.com/Alaashamel/ai-engineering-orchestrator/issues)

We use GitHub issues to track public bugs. Report a bug by opening a new issue.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
