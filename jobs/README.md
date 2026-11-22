# jobs/

One folder per review. Everything in this folder except this file is ignored by git:
job folders hold the documents under review (and, where cleared, data) and never
leave the machine through this repository.

Create a job with

```bash
python3 .claude/skills/stats-review/scripts/new_job.py jobs/<yyyy-mm>_<product> \
  --product <rendered product and source, or the product folder> \
  --governing <protocol, SAP, registry entry> --lit <cited sources>
```

then fill in `00_ASSIGNMENT.md`. Layout of a job (the review adds `review/`,
`analysis/`, `work/` and its outputs):

```
00_ASSIGNMENT.md   written by the statistician who asks for the review
01_product/        the product as delivered (rendered document + Quarto source tree)
02_governing/      protocol, SAP, SSE, registry entry, CRF or data dictionary
03_previous/       earlier versions of the product
04_data/           patient-level data — only in data mode `shared`
05_synthetic/      codebook or dummy data — only in data mode `synthetic`
lit/               sources the product cites
```

The review's deliverable is `CONSISTENCY_REVIEW.html` (with `.md` and `.org`) at the
job root; `SYNTHESIS.md` is the full record behind it.
