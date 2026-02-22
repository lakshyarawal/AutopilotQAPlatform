# GitHub Upload Guide

## 1) Initialize git (if needed)

```bash
git init
git branch -M main
```

## 2) Review ignored artifacts

```bash
git status --short
```

Expected: `.env`, `.venv`, `autopilot.db`, and generated data files are not staged.

## 3) Commit

```bash
git add .
git commit -m "feat: autopilot dataset discovery and label QA platform"
```

## 4) Create a new GitHub repo

Create an empty repo in GitHub UI, then run:

```bash
git remote add origin git@github.com:<your-username>/<repo-name>.git
git push -u origin main
```

## 5) Optional repo metadata

- Add topics: `autonomous-driving`, `data-engineering`, `mlops`, `fastapi`, `streamlit`, `kafka`, `spark`.
- Pin this project in your profile.
- Add screenshots in `README.md` once hosted.
