# Creating the repository on GitHub, and finishing the licence

Step by step, from nothing. Done once — except section 7, which is the day-to-day
workflow once it is running.

The repository is named **`Subaru-ESP32-SLOW`** throughout; substitute your own
name if you use a different one.

## 0. Prerequisites

- **Git installed.** Check in a terminal:
  ```bash
  git --version
  ```
  If no version number appears, install it from
  [git-scm.com/downloads](https://git-scm.com/downloads).
- **A GitHub account.** Free at [github.com](https://github.com/) — private
  repositories are included in the free plan.
- **The project folder**, containing this file. Every command below is run from
  inside it.

## 1. Set your Git identity

Only needed once per machine. If you have used Git here before, skip it.

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

If this repository will be made public later and you would rather not expose that
address, set it per-repository instead: run the same two commands **without**
`--global` from inside the project folder, after step 2.

## 2. Initialise the repository

The project files live in the working folder already. Turn that folder into a Git
repository and make the first commit:

```bash
cd "Subaru_SLOW_ESP32"
git init -b main
git add -A
git commit -m "docs: Subaru-ESP32-SLOW v0.1 - retromod SSM2 gauge + speed-based central locking"
git log --oneline
```

You should see exactly one commit.

> **A note on Google Drive.** The working folder currently sits inside a synced
> Drive folder. Drive syncing a `.git/` directory — thousands of small object
> files that change constantly — is a known way to end up with a corrupted
> repository. If you hit strange Git errors later, move the folder somewhere
> outside Drive and keep Drive for sharing exports rather than for the live
> repository.

## 3. Create the empty repository on GitHub

1. Sign in at [github.com](https://github.com/).
2. Top right, click **+** → **New repository**.
3. **Repository name:** `Subaru-ESP32-SLOW`.
4. **Description:** optional, e.g. "Retromod SSM2 gauge + speed-based central locking for a Subaru Legacy 3.0R, on two ESP32 nodes".
5. **Visibility:** **Private** for now (it can be made public later without losing history).
6. **Important:** leave all three "Initialize this repository with" boxes
   **unchecked** (README, .gitignore, License). They already exist in the local
   repository — ticking them here makes GitHub create its own commit, and the
   first `push` then fails with unrelated histories. GitHub's own documentation
   says the same: if you are importing an existing repository, choose none of
   those options.
7. Click **Create repository**.

GitHub shows a page of commands. Use the section titled *"…or push an existing
repository from the command line"*, not the "create a new repository" one — our
repository already has content.

## 4. Connect the local repository and push

GitHub gives you a URL like `https://github.com/your-user/Subaru-ESP32-SLOW.git`
(HTTPS) or `git@github.com:your-user/Subaru-ESP32-SLOW.git` (SSH). Either works;
the difference is only how you authenticate. With the URL you copied:

```bash
git remote add origin <the-URL-you-copied>
git branch -M main
git push -u origin main
```

### Authentication: GitHub no longer accepts your account password for `git push`

Pick one of these.

**Option A — HTTPS + token (simplest to start):**

1. On GitHub: your profile picture (top right) → **Settings** → **Developer
   settings** (bottom of the left menu) → **Personal access tokens** →
   **Fine-grained tokens** → **Generate new token**. GitHub recommends
   fine-grained tokens over classic ones.
2. Give it a name, choose an expiry, and under "Repository access" select the
   repository you just created (or "All repositories" if you prefer).
3. Under "Permissions", grant **Contents: Read and write**.
4. Generate the token and **copy it immediately** — it is not shown again.
5. When `git push` asks for a username and password, use your GitHub username,
   and **paste the token where the password goes**.

**Option B — SSH (no credentials to type again):**

1. If you do not already have a key: `ssh-keygen -t ed25519 -C "you@example.com"`
   (press Enter to accept the defaults).
2. Copy the public key: `cat ~/.ssh/id_ed25519.pub`
3. On GitHub: **Settings** → **SSH and GPG keys** → **New SSH key** → paste and
   save.
4. Use the SSH URL (`git@github.com:...`) in `git remote add origin`.

After `git push -u origin main`, refresh the repository page — everything should
be there, with 1 commit in the history.

## 5. Finish the software licence (GPL-3.0)

`LICENSE-SOFTWARE.txt` carries the SPDX identifier and the explanation, but
**not the full legal text** — it could not be fetched verbatim from an
authoritative source in the session where this repository was built, so it was
left to be inserted properly rather than retyped from memory. Complete it on
GitHub, which inserts the official text for you:

1. On your repository page, click **Add file** → **Create new file**.
2. In the filename field type `LICENSE-SOFTWARE.txt` (so it replaces the current
   one) — or `LICENSE` if you prefer the standard name, and then delete the old
   `.txt` file.
3. Below the filename a **Choose a license template** button appears — click it.
4. In the list on the left, choose **GNU General Public License v3.0**.
5. Click **Review and submit**.
6. Click **Commit changes…**, confirm the commit message, then **Commit changes**.

GitHub inserts the complete official text automatically — nothing copied by hand.
If you used the name `LICENSE` instead of replacing `LICENSE-SOFTWARE.txt`, delete
the old file and update the references in `README.md` and `CONTRIBUTING.md` so
there are not two software licence files.

Pull the change back to your local copy with `git pull`.

## 6. Final check

- [ ] The repository shows as **private** on GitHub.
- [ ] `git log` locally and the history on GitHub show the same commit.
- [ ] `LICENSE-SOFTWARE.txt` (or `LICENSE`) now contains the full GPL-3.0 text,
      not just the explanation.
- [ ] `LICENSE-HARDWARE.txt` already carried the full CERN-OHL-S v2 text in the
      project folder from the start — it needs nothing.
- [ ] The figures render correctly on GitHub in **dark mode** (they are drawn for
      it) — open `docs/01-hardware/node-b-gauge.md` and check.

## 7. Day to day

Once you are working on the circuit and firmware:
[`CONTRIBUTING.md`](CONTRIBUTING.md) covers the branch-and-review workflow for one
or two collaborators, and [`docs/decisions/README.md`](docs/decisions/README.md)
covers when to write a new decision record. In short, for each piece of work:

```bash
git checkout -b hw/branch-name
# ... changes ...
git add <files>
git commit -m "hw: short description"   # see Conventional Commits in CONTRIBUTING.md
git push -u origin hw/branch-name
```

Then open a pull request on GitHub and review before merging into `main`.
