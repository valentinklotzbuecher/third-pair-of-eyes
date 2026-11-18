# Skills for Claude chat

Stand-alone skills to upload to Claude chat (claude.ai or the Claude apps), outside the
versioned review suite in `.claude/skills/`. They let a colleague see what the review
agents are told to do, on one document, without Claude Code, a job folder or R.

| Skill | What it does |
|---|---|
| `dkf-document-check` | The first stage of `dkf-review` on its own: identity and versions, consistency with the governing documents, the printed numbers and their arithmetic (recomputed with `scripts/recompute.py`), and the design, estimand and method. It returns findings, a consistency table, a check log and leads for the code review. It does not run the product's code. |

## Using it

1. Download `dkf-document-check.zip`.
2. In Claude, open Customize, then Skills, choose "+", create a skill and upload the
   ZIP. Code execution must be on. An uploaded skill is yours only; it does not reach
   Claude Code or colleagues' accounts.
3. In a new chat, attach the rendered product (PDF) and, if you like, its Quarto
   source and the governing documents (protocol, SAP, registry entry), and ask, for
   example: "Check this sample size estimation with dkf-document-check."

Only documents your data rules allow you to send, never patient-level data: what the
chat reads goes to the model provider under your plan's terms.

## What it is not

One stage of the review, not the review. Without running the product's code it cannot
establish what the code computes; it lists that as leads. There is no fresh-context
challenge, no verdict and no DKF form; for those, run `dkf-review` in Claude Code
(`../README.md`).

## Maintaining it

- `SKILL.md` is the document stage (`.claude/skills/dkf-review/document/SKILL.md`)
  condensed for a chat; its `metadata.based-on` names the suite version it follows.
  When the stage's requirements change, port the change and bump the skill's own
  `metadata.version`.
- `references/` and `LICENSE-research_skills` are unchanged copies of the suite's files;
  the tests fail when they drift.
- `scripts/recompute.py` ports the document stage's helpers from
  `.claude/skills/dkf-review/assets/recompute.R` to the Python standard library, because
  a chat's sandbox may have no R; the tests compare it with `recompute.R` where Rscript
  is installed.
- After any change, rebuild the ZIP and run the tests:

  ```bash
  python3 chat-skills/build_zip.py
  ```

  ```bash
  python3 -m pytest -q -p no:cacheprovider chat-skills/tests
  ```

The skill is derived from research_skills (The Catalogue of Errors Ltd, MIT licence)
through the document stage; see `../.claude/skills/UPSTREAM.md`.
