# Branching Strategy

This repository follows a simple Git flow optimized for embedded product development.

Branches
- `main` — stable production-ready code. Only merge from `develop` via pull requests after verification.
- `develop` — active development branch. All feature branches merge here first.
- `feature/*` — short-lived branches for feature work, branched from `develop`.
- `hotfix/*` — urgent fixes branched from `main`, merged back to both `main` and `develop`.

Workflow
1. Create feature branch from `develop`: `git checkout -b feature/<name> develop`
2. Work, commit, push feature branch: `git push -u origin feature/<name>`
3. Open Pull Request into `develop` and request review + CI passing
4. When `develop` is stable and a release is needed, open PR from `develop` → `main`. Run release checks.
5. Protect `main` with required status checks (CI) and PR reviews.

Best Practices
- Keep PRs small and focused.
- Use meaningful commit messages.
- Run desktop unit tests and linters locally before pushing.
- Use `git rebase` for local cleanup, prefer merge commits for PR merges if you want a visible history.
- Track large binary assets with Git LFS.

Branch Protection (recommended on GitHub)
- Require pull request reviews before merging to `main`.
- Require status checks (CI) to pass.
- Enable `Require linear history` to prevent merge commits if desired.

Release Process
- Tag releases on `main` with semantic versioning: e.g. `v1.0.0`.
- Create release notes summarizing changes from `develop`.

This file is a quick reference; adapt rules to your team and CI requirements.
