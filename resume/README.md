# CV

`build_resume.py` builds six CV variants from `template.docx` and exports them to PDF, using
Pages on macOS or Microsoft Word on Windows:

| Variant | One page | Full |
|---|---|---|
| Software Engineer | `Mazen_EL-Gayar_Software_Engineer_1Page` | `Mazen_EL-Gayar_Software_Engineer_Full` |
| Game Developer | `Mazen_EL-Gayar_Game_Developer_1Page` | `Mazen_EL-Gayar_Game_Developer_Full` |
| General | `Mazen_EL-Gayar_General_1Page` | `Mazen_EL-Gayar_General_International_Full` |

## How the CVs get published

The GitHub Pages deploy (`.github/workflows/pages.yml`) builds every CV on each push to `main`,
with LibreOffice and Microsoft's Arial fonts, and publishes all six PDFs next to this file, e.g.
`https://mazenxelgayar.github.io/resume/Mazen_EL-Gayar_Game_Developer_1Page.pdf`. The full
Software Engineer CV is also published as `resume/Mazen-EL-Gayar-CV.pdf`, the file the portfolio's
"Download CV" buttons link to.

So to update the CV: edit `build_resume.py`, push, and the live PDFs are replaced.

The deploy also saves all six PDFs in [`resume/pdf/`](pdf/) so you can open any version on
GitHub, and the folder's history keeps every earlier version. It only does this when
`build_resume.py` or `template.docx` changed, in a commit by `github-actions[bot]` marked
`[skip ci]` (so it doesn't deploy again). Run `git pull` afterwards before your next push.

The CVs and the site are separate jobs. If the CV job fails (for example, a one-page CV runs onto a
second page), the site still deploys and keeps the CVs that were already live, and the run shows a
warning. Every run attaches the CVs it built as "cvs-check", so you can see what went wrong.

## Build locally

```bash
pip3 install python-docx
python3 resume/build_resume.py
```

- `--no-pdf` builds the Word files only.
- `--role software` builds one role; repeat it for more.
- `--strict` fails if a one-page CV runs over one page; `--publish DIR` copies every PDF into DIR.

Output goes to `resume/output/` (git-ignored). PDFs are exported with Pages on macOS, Microsoft
Word on Windows and LibreOffice on Linux.

## Editing

All the wording lives at the top of `build_resume.py`: summaries, experience, skills, projects,
education and links. `template.docx` only provides the fonts, spacing and the name and contact
header.

## Why Pages on macOS (local builds)

Word for Mac (16.x) rejects the "save as PDF" command when a script sends it, so the script
exports with Pages instead. The CV uses Arial, so the PDF looks the same as Word's. The first
export may ask you to allow Terminal to control Pages; click OK.
