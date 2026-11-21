# jubr.app

A tiny one-page overview of all projects running on `*.jubr.app`, hosted with GitHub Pages.

## Add a project

Edit the `PROJECTS` list in [`index.html`](index.html):

```js
{ name: "My App", sub: "myapp", desc: "What it does" },
```

`sub` is the subdomain, so this links to `https://myapp.jubr.app`. Each card shows a status dot (green = reachable, red = not).

## Deploy

1. Repo **Settings → Pages** → Source: *Deploy from a branch*, branch `main`, folder `/ (root)`.
2. Point DNS for `jubr.app` at GitHub Pages (A records `185.199.108.153`, `.109.153`, `.110.153`, `.111.153`).
   The `CNAME` file already sets the custom domain.
