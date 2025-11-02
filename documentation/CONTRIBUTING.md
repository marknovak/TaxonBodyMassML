## Contributing Guide

How to set up, code, test, review, and release so contributions meet our Definition of Done.

## Code of Conduct

Reference the project/community behavior expectations and reporting process.

## Getting Started

List prerequisites, setup steps, environment variables/secrets handling, and how to run the app locally.

## Branching & Workflow

Describe the workflow (e.g., trunk-based or GitFlow), default branch, branch naming, and when to rebase vs. merge.

## Issues & Planning

Explain how to file issues, required templates/labels, estimation, and triage/assignment practices.

We will use GitHub Issues

## Commit Messages

We will use Conventional Commits, which follow the template: type(scope): description

Examples:
- docs(contributing): completed the commit messages section in contributing.md
- feat(data): log transformed the species mass data
- feat(ui): included histograms on data visualization tab

Reference issues by including either "Fixes #xyz" or "Refs #xyz" at the end of a commit.

## Code Style, Linting & Formatting

Name the formatter/linter, config file locations, and the exact commands to check/fix locally.

## Testing

Define required test types, how to run tests, expected coverage thresholds, and when new/updated tests are mandatory.

## Pull Requests & Reviews

Outline PR requirements (template, checklist, size limits), reviewer expectations, approval rules, and required status checks.

## CI/CD

Link to pipeline definitions, list mandatory jobs, how to view logs/re-run jobs, and what must pass before merge/release.

Located in ./github/workflows and triggers after every push or PR to the main branch

## Security & Secrets

State how to report vulnerabilities, prohibited patterns (hard-coded secrets), dependency update policy, and scanning tools.

## Documentation Expectations

Specify what must be updated (README, docs/, API refs, CHANGELOG) and docstring/comment standards.

## Release Process

Describe versioning scheme, tagging, changelog generation, packaging/publishing steps, and rollback process.

## Support & Contact

Provide maintainer contact channel, expected response windows, and where to ask questions.

