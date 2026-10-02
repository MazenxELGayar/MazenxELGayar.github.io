# Mazen EL-Gayar — Portfolio

A lightweight, responsive portfolio for GitHub Pages. It presents Mazen's software engineering and Flutter/NestJS work alongside independently published MazenX games, open-source packages, selected projects, education, and honors.

## GitHub Pages setup

Recommended repository: `MazenxELGayar.github.io` under the GitHub account `MazenxELGayar`.

1. Sign in to GitHub CLI with repository access: `gh auth login --hostname github.com --git-protocol https --scopes repo`.
2. Create the public user-site repository and push this project: `gh repo create MazenxELGayar.github.io --public --source=. --remote=origin --push`.
3. In **Settings → Pages**, choose **GitHub Actions** as the publishing source.
4. The workflow in `.github/workflows/pages.yml` deploys automatically on each push to `main`. You can also start it from **Actions → Deploy portfolio to GitHub Pages → Run workflow**.
5. After the first successful deployment, the personal site URL should be `https://mazenxelgayar.github.io/`.

The workflow deploys the repository root as a static Pages artifact. No build dependencies, secrets, or frontend API credentials are needed. GitHub Pages recommends configuring a publishing source and supports a custom Actions workflow for deployment; this project uses GitHub's Pages configure, artifact upload, and deploy actions.

## Local preview

Open `index.html` directly, or run a static server in this directory:

```powershell
python -m http.server 8000
```

Then visit `http://localhost:8000`.

## Structure

- `index.html`, `styles.css`, `script.js` — site source
- `assets/` — local project artwork, favicon, and social preview
- `.github/workflows/pages.yml` — GitHub Pages deployment
- `robots.txt`, `sitemap.xml`, `llms.txt` — crawler and search discovery files

Project artwork in `assets/` was selected from the supplied `D:\Programming\flutter_projects` folder. Store, profile, project, and the official Udemy credential links use the supplied URLs.

The public site summarizes education, honors, and certifications. It links to the official Udemy credential; private résumé PDFs, transcripts, and work certificates are not bundled in this public repository.
