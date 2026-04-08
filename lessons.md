# Vault Lessons Learned

Operational lessons from building and maintaining the wiki. Claude Code should follow these.

---

## Transcript Reading

- Always read transcripts in full using chunked sequential reads. Never process a transcript based on partial content. For files exceeding the token limit, read in sequential chunks (200 lines at a time) covering the entire file before generating wiki pages.

## Wiki Links and Filenames

- Use underscores in filenames but natural spacing in wiki-link display text. Example: filename is `Unit_Economics.md` but link is `[[Unit_Economics|Unit Economics]]`.

## Entity Page Creation

- Only create entity pages for entities with substantive discussion (key data points, strategy insights, multiple mentions). Do not create entity pages for brands/people mentioned once in passing. Those should only appear in the source summary's "Entities Mentioned" section.

## Filename Sanitization

- Some YouTube video titles contain special Unicode characters (curly quotes `\u2018\u2019\u201c\u201d`, rupee sign `₹`, etc.) that cause file read issues with tools. When saving raw transcripts, strip or replace all non-ASCII characters in filenames. Keep content intact — only filenames need ASCII-safe names.

## Avoiding Duplicates

- Before creating any new page, search existing wiki pages for similar names to avoid duplicates like `Series_C_Drought.md` and `Series C Drought.md`. Use the canonical name and alias the other in frontmatter `aliases:` field.
