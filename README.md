# Pong AI Classroom Project

This repository is for learning collaborative development with Git while building and testing a Pong AI.

Students should:
1. Clone the repository.
2. Create a feature branch.
3. Improve `StudentAI`.
4. Push their branch.
5. Open a pull request.

## 1. Learning Goals

- Use Git in a team workflow (clone, branch, commit, push, PR).
- Use conda environments so everyone has the same Python dependencies.
- Implement and evaluate a basic game AI.
- Beat a built-in `ReferenceAI` to pass.

## 2. Repository Structure

- `pong.py`: game loop, modes, rendering, benchmark runner.
- `ai_opponents.py`: AI classes (`StudentAI`, `ReferenceAI`, etc.).
- `AI_GUIDE.md`: strategy and AI development guide.
- `environment.yml`: pinned conda environment for consistent setup.

## 3. Tooling Prerequisites

You need:
- Git
- Conda (recommended: Miniforge)

### 3.1 What Conda Is (and why we use it)

Conda is an environment and package manager.
- An environment is an isolated Python setup.
- This project ships `environment.yml`, which lists required packages.
- Everyone installs from the same file, so version mismatch problems are reduced.

### 3.2 Install Git

Windows:
- Install Git for Windows from [git-scm.com/download/win](https://git-scm.com/download/win).
- During install, default options are fine for this class.

macOS:
- Run:

```bash
xcode-select --install
```

Ubuntu:
- Run:

```bash
sudo apt update
sudo apt install -y git
```

### 3.3 Install Conda (recommended: Miniforge)

Windows:
- Download and install Miniforge from [github.com/conda-forge/miniforge](https://github.com/conda-forge/miniforge).
- After install, open `Miniforge Prompt` (or Anaconda Prompt equivalent).

macOS:
- Install Miniforge from [github.com/conda-forge/miniforge](https://github.com/conda-forge/miniforge).
- If using terminal installer, run the downloaded installer script and restart terminal.

Ubuntu:
- Download Linux installer from [github.com/conda-forge/miniforge](https://github.com/conda-forge/miniforge).
- Then run:

```bash
bash Miniforge3-Linux-$(uname -m).sh
```

- Follow prompts, then restart terminal.

### 3.4 Verify Install

Run:

```bash
git --version
conda --version
```

If `conda` is not found:
- run `conda init`
- close terminal
- open terminal again

## 4. Exact First-Time Setup (Windows, macOS, Ubuntu)

Use this sequence exactly after prerequisites are installed.

### 4.1 Clone the repository

```bash
git clone https://github.com/sameerkhanna786/project_trampoline_pong.git
cd project_trampoline_pong
```

Replace:
- If you fork this repository, replace the URL with your own fork URL.
- `project_trampoline_pong` is the default local folder name after clone.

### 4.2 Create the project environment

Run once:

```bash
conda env create -f environment.yml
```

### 4.3 Activate environment

Run every new terminal session:

```bash
conda activate pong-classroom
```

### 4.4 Start the game

```bash
python pong.py --mode pvp
```

If needed on some Windows setups:

```bash
py -3 pong.py --mode pvp
```

### 4.5 OS-specific copy/paste setup blocks

Windows (PowerShell or Miniforge Prompt):

```powershell
git clone https://github.com/sameerkhanna786/project_trampoline_pong.git
cd project_trampoline_pong
conda env create -f environment.yml
conda activate pong-classroom
python pong.py --mode pvp
```

macOS (Terminal):

```bash
git clone https://github.com/sameerkhanna786/project_trampoline_pong.git
cd project_trampoline_pong
conda env create -f environment.yml
conda activate pong-classroom
python pong.py --mode pvp
```

Ubuntu (Terminal):

```bash
git clone https://github.com/sameerkhanna786/project_trampoline_pong.git
cd project_trampoline_pong
conda env create -f environment.yml
conda activate pong-classroom
python pong.py --mode pvp
```

If your folder name contains spaces, wrap it in quotes:

```bash
cd "<REPO_FOLDER WITH SPACES>"
```

## 5. Running the Project

### 5.1 Available modes

```bash
# Two human players
python pong.py --mode pvp

# Human (left) vs selected AI (right)
python pong.py --mode human-vs-ai --opponent tracking

# Human (left) vs StudentAI (right)
python pong.py --mode human-vs-student

# Watch AI vs AI
python pong.py --mode ai-vs-ai --left-ai reference --right-ai student

# Pass/fail benchmark: StudentAI vs ReferenceAI
python pong.py --mode benchmark
```

### 5.2 Controls

- Left paddle: `W` (up), `S` (down)
- Right paddle in `pvp`: `Up Arrow` (up), `Down Arrow` (down)
- `Esc`: exit game window

## 6. AI Assignment Requirements

Required work:
1. Edit `StudentAI.choose_move(...)` in `ai_opponents.py`.
2. Keep core game logic unchanged unless instructed by the teacher.
3. Test by playing against your AI.
4. Run benchmark mode before pushing.

Return values expected from `StudentAI.choose_move(...)`:
- `-1` move up
- `0` stay
- `1` move down

Read `AI_GUIDE.md` for strategy milestones and tips.

## 7. Benchmark and Pass Rule

Benchmark command:

```bash
python pong.py --mode benchmark
```

How grading works:
- Runs multiple matches: `ReferenceAI` (left) vs `StudentAI` (right).
- Draws do not count in win-rate denominator.
- Default pass rule: at least `60%` decisive-match win rate.
- Any `StudentAI` runtime error causes automatic fail.

Optional tuning:

```bash
python pong.py --mode benchmark --matches 30 --pass-win-rate 0.60 --seed 2026
```

## 8. Full Git Workflow (Clone to PR)

Use this for each assignment.

### 8.1 Get latest `main`

```bash
git checkout main
git pull origin main
```

### 8.2 Create your branch

```bash
git checkout -b feature/<your-ai-name>
```

Examples:
- `feature/predictive-ai`
- `feature/defensive-ai`

### 8.3 Make changes and test

```bash
python pong.py --mode human-vs-student
python pong.py --mode benchmark
```

### 8.4 Stage and commit

```bash
git status
git add ai_opponents.py
git commit -m "Improve StudentAI with ball prediction"
```

If you changed docs too:

```bash
git add README.md AI_GUIDE.md
git commit -m "Document StudentAI strategy and benchmark results"
```

### 8.5 Push your branch

```bash
git push -u origin feature/<your-ai-name>
```

### 8.6 Open pull request

- Open the repository page in browser.
- Create PR from your branch into `main`.
- Include:
  - short summary of AI strategy
  - benchmark result
  - what you tested

### 8.7 Continue after review feedback

```bash
git add <files>
git commit -m "Address PR feedback"
git push
```

## 9. Daily Update Workflow

Before new work each day:

```bash
git checkout main
git pull origin main
git checkout feature/<your-ai-name>
git merge main
```

If merge conflicts happen:
- resolve conflicts in editor
- run tests/game again
- commit merge result

## 10. Conda Cheat Sheet

What conda is:
- Conda is a package manager and environment manager for Python and other tools.
- It lets you create isolated environments, so each project can have its own package versions.

Why conda is useful for this class:
- Everyone installs from the same `environment.yml`, reducing "works on my machine" issues.
- It prevents one project’s dependencies from breaking another project.
- You can easily reset or recreate the project environment if something goes wrong.

Key idea:
- The first time you set up this repo, create the environment.
- Every time you open a new terminal to work, activate that environment.

Create environment (first-time setup):

```bash
conda env create -f environment.yml
```

Activate environment (each new terminal session):

```bash
conda activate pong-classroom
```

Deactivate environment:

```bash
conda deactivate
```

Update environment if `environment.yml` changes:

```bash
conda env update -f environment.yml --prune
```

Remove environment completely:

```bash
conda env remove -n pong-classroom
```

## 11. Troubleshooting

### `ModuleNotFoundError: No module named 'pygame'`

You are likely not in the project environment.

```bash
conda activate pong-classroom
```

If still broken:

```bash
conda env update -f environment.yml --prune
```

### `conda: command not found`

- run `conda init`
- restart terminal
- try again

### `git push` rejected

Your branch may be behind remote.

```bash
git pull --rebase origin feature/<your-ai-name>
git push
```

### Benchmark always fails

- Check that `StudentAI.choose_move(...)` returns only `-1`, `0`, or `1`.
- Add debug prints carefully, then remove before commit.
- Test with:

```bash
python pong.py --mode human-vs-student
python pong.py --mode ai-vs-ai --left-ai reference --right-ai student
```

## 12. Submission Checklist

Before submitting PR, confirm:
- branch created from latest `main`
- game runs in your conda environment
- `human-vs-student` mode works
- benchmark command runs
- commit message is clear
- PR includes summary + benchmark result
