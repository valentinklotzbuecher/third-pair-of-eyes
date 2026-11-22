# Consistency review (the form)

The layout the human consistency review uses, which `render_review.py` reproduces.
For reference; the rendered form is generated from `ISSUES.md`.

```org
*** CONSISTENCY REVIEW
**** Assignment
- Name of the statistical product: <file>
- Important issues for reviewer:
  - <question>
- Other documents this document depends on:
  - <document>
**** Review
***** Decision
- [ ] Statistical product needs minor changes in the text
- [ ] Statistical product needs major changes in the text (second review necessary)
- [ ] Statistical product needs minor changes in the R programming
- [ ] Statistical product needs major changes in the R programming (second review necessary)
- [ ] Clarifications required about code or methods (meeting or communication)
***** General Comments
***** Major Issues
***** Minor Issues
***** Answer to issues listed in 'Assignment'
```

Reviewers also leave `REVIEW` comments in the Quarto source; `annotate_source.py`
writes them into a copy (`work/annotated/<file>.REVIEW.qmd`).
