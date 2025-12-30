---
id: 0002
title: Untracked .next folder guidance
stage: general
date: 2025-12-12
surface: agent
model: gpt-5.1-codex-max-low
feature: none
branch: main
user: donia_batool
command: Advised on untracked .next handling
labels: ["git","cleanup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - none
tests:
 - none
---

## Prompt

@bash (304-313) ye aaraha hai , kya jo files untracked show horai hain unko push kernay ki zaroorat nai hai? ager push na kiya tou project pe asar tou nai parayga ?break tou nai hoga ?ager in files aur folder ko push nai kerna tou gitignore mae add kerdain ?

## Response snapshot

.next sirf build output hai; push karne ki zaroorat nahi, project break nahi hoga. Clean with `rm -rf frontend/.next` and add to .gitignore (`frontend/.next/`) if missing to avoid future untracked noise.

## Outcome

- ✅ Impact: clarified untracked build artifacts handling
- 🧪 Tests: none
- 📁 Files: none changed
- 🔁 Next prompts: optionally add .next to .gitignore and delete folder
- 🧠 Reflection: keep build artifacts out of git to avoid clutter

## Evaluation notes (flywheel)

- Failure modes observed: untracked build outputs causing git noise
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): add .next to gitignore automatically in templates

