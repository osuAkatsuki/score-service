# score-service CLAUDE.md

This file provides guidance to Claude Code specific to the score-service repository.

## Git Repository Guidelines

**CRITICAL: score-service is a fork from RealistikOsu/USSR. Always PR to the correct repository:**

- **❌ NEVER:** Create PRs to `RealistikOsu/USSR` (upstream fork source)
- **✅ ALWAYS:** Create PRs to `osuAkatsuki/score-service` (our repository)
- **✅ DO:** Use `gh pr create -R osuAkatsuki/score-service` to ensure correct target repository
- Verify git remote configuration before creating PRs (origin should be osuAkatsuki)

**Correct PR creation:**
```bash
# Always specify the repository explicitly
gh pr create -R osuAkatsuki/score-service --title "..." --body "..."

# NOT just "gh pr create" which may default to upstream
```

**Git Remote Configuration:**
```
origin   git@github.com:osuAkatsuki/score-service.git (our repo - PR here)
upstream git@github.com:RealistikOsu/USSR.git (fork source - NEVER PR here)
```

## Development Workflow

1. Create feature branch from `master`
2. Make changes
3. Run linters: `pre-commit run --all-files`
4. Run type checking: `mypy .`
5. Commit changes
6. Push to origin: `git push -u origin <branch>`
7. Create PR to osuAkatsuki/score-service: `gh pr create -R osuAkatsuki/score-service`

## Code Style

- Python 3.11+
- Type hints required (mypy strict mode)
- Black formatter (line length 88)
- Import sorting with reorder_python_imports
- Trailing commas enforced
- Use pre-commit hooks for automatic formatting

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_achievements.py

# Run with coverage
pytest --cov=app --cov-report=html
```

## Achievement System

See `.github/plans/ACHIEVEMENTS_ANALYSIS.md` in the monorepo root for the comprehensive achievement system overhaul plan.

**Key Files:**
- `app/usecases/user.py` - Achievement unlock logic
- `app/constants/mode.py` - Game mode definitions
- `app/state/cache.py` - Achievement condition loading
- Future: `app/achievements/` - Decorator-based achievement system (planned)
