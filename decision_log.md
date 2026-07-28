# Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-07-28 | Binary main label (unfair = 1/0), with an `uncertain` flag as a separate field | With ~25-33 reviews per language, a 3-class scheme spreads counts too thin for stable agreement statistics; uncertainty is still captured in its own field |
| 2026-07-28 | Raw review texts are kept out of the public repo (`data/raw/` and `data/processed/` are gitignored); only labels, review_ids and a small demo sample are published | Re-publication rights for Steam reviews are unconfirmed and full texts could expose user information; reproducibility does not require the data itself, since anyone can rebuild the corpus with the collection scripts and review_ids |
