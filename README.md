# jubr.app

A tiny one-page overview of all projects running on `*.jubr.app`, hosted with GitHub Pages.

## How it updates itself

- **Project list**: every 6 hours, a GitHub Action (`.github/workflows/update.yml`) runs `scripts/update.py`. It finds every subdomain with a valid certificate (via [crt.sh](https://crt.sh) certificate transparency logs), reads each site's `<title>` and meta description, and commits the result into `index.html`. A new project shows up on its own once it has an HTTPS certificate.
- **Status dots**: checked in the visitor's browser and refreshed every minute (green = reachable, red = not).

Run it by hand under **Actions → Update project list → Run workflow**, or locally with `python3 scripts/update.py`.

## Customize

Edit `overrides.json`:

```json
{
  "hide": ["www", "staging"],
  "projects": {
    "gotthard": { "name": "Gotthard Verkehr Live", "desc": "Optional custom description" }
  }
}
```

## Deploy

1. Repo **Settings → Pages** → Source: *Deploy from a branch*, branch `main`, folder `/ (root)`.
2. Point DNS for `jubr.app` at GitHub Pages (A records `185.199.108.153`, `.109.153`, `.110.153`, `.111.153`).
   The `CNAME` file already sets the custom domain.
