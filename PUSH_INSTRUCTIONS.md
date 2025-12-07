# Push to GitHub - Manual Steps

## Problem
The automated push from this environment is uploading LFS objects but **GitHub is not accepting the branch ref updates** (main and develop are not updating to your latest commits).

## Solution
You must run the push commands from your local machine with stable credentials and network. Follow these steps:

### Option 1: Use the Batch Script (Windows)
```powershell
cd E:\Backup\Tech_up
.\PUSH_TO_GITHUB.bat
```

Then verify on GitHub: https://github.com/maheshdarimireddi/stm32-practice

### Option 2: Run Manually in PowerShell

```powershell
cd E:\Backup\Tech_up

# 1) Install Git LFS (one-time)
git lfs install

# 2) Fetch remote state
git fetch origin

# 3) Show your local branches (verify they have your commits)
git branch -vv

# 4) Show remote branches (before push)
git ls-remote --heads origin

# 5) Push develop branch
git push origin develop

# 6) Push main branch
git push origin main

# 7) Verify remote now shows your commits
git ls-remote --heads origin

# 8) Quick check - show local commits
git log --oneline --graph --decorate -n 5
```

### If `git push` is rejected (non-fast-forward)
Use force-with-lease (safe):
```powershell
git push --force-with-lease origin develop
git push --force-with-lease origin main
```

### After Push Succeeds
1. Open https://github.com/maheshdarimireddi/stm32-practice in your browser
2. Verify:
   - `STM32_AI_Project` folder is visible
   - `develop` branch exists
   - `main` branch shows your commits
   - BRANCHING.md and CI workflow are present

### Troubleshooting

**Problem**: `git push` hangs or times out
- Press Ctrl+C to stop
- Check your internet connection
- Retry after 30 seconds

**Problem**: "Permission denied" or "Not authorized"
- You may need to authenticate with GitHub
- GitHub will prompt for credentials or token
- Use a Personal Access Token (PAT) if prompts appear

**Problem**: "updates were rejected because the tip of your current branch is behind"
- Run: `git pull --rebase origin main`
- Then retry: `git push origin main`

## What Was Done in This Session

1. ✅ Created `STM32_AI_Project` folder structure
2. ✅ Created `develop` branch locally
3. ✅ Added `BRANCHING.md` (branching strategy)
4. ✅ Added `.github/workflows/ci.yml` (CI pipeline)
5. ⏳ Push to GitHub (needs local completion)

## Next Steps After Push
- Enable branch protection for `main` on GitHub UI
- Start feature development on `develop` branch
- Use git flow: feature → develop → main (releases)

