# Patient resources website

A simple one-page website listing the patient and clinician resources I use.
It is free to host on GitHub Pages and checks every link automatically each day.

## What's in this folder

| File / folder | What it is |
|---|---|
| `resources.toml` | **The list of resources. This is the file you edit.** |
| `site.toml` | Your name, subtitle, clinic line, intro and disclaimer. |
| `files/` | Saved copies of every PDF (kept automatically). |
| `data/` | Link-check records (kept automatically — don't edit). |
| `scripts/` | The programs that build the site and check links. |
| `.github/workflows/site.yml` | Tells GitHub to check links daily and publish the site. |
| `resources links.docx` | Your original list (no longer used; safe to keep or delete). |

## Adding a resource

1. Open `resources.toml` (on GitHub: click the file, then the ✏️ pencil icon).
2. Copy an existing `[[resource]]` block, paste it where you want it, and change the text.
3. Save (on GitHub: **Commit changes**).

The site updates within about two minutes. New resources are treated as approved,
and a copy of any new PDF is saved automatically.

To remove a resource, delete its block. To move it, move its block.

## How the daily link check works

Every morning GitHub opens each link and compares it with the version you approved:

* **No change:** nothing happens.
* **Changed content:** you get an email showing what changed.
  * **Web pages / calculators** are hidden from the site ("temporarily unavailable
    while being reviewed") until you approve them again.
  * **PDFs** keep working, because the site serves your saved, approved copy.
    Only the "original source" link is hidden until you approve.
* **Link gone (page not found two days in a row):** handled the same way as a change.
* **Site couldn't be reached for 3 days** (outage, or the site blocks automated checks):
  you get one email, and the link stays up.

For web pages, the email shows the changed text, so a menu tweak is easy to tell
apart from a real content change.

### Approving after a change

GitHub → your repository → **Actions** → **Check links & publish** → **Run workflow**:

* **What to do:** `approve`
* **Resource id:** the id from the email (or `all`)
* **Keep saved copy:** tick this if the PDF changed and you want to keep showing
  your old version. Leave it unticked to replace your saved copy with the new one.

This works from a phone browser. If you'd rather point to a different resource,
edit the `url` in `resources.toml` instead. That counts as approval.

### Sites that block automatic checking

The two **Cancer Care Ontario** links block automated tools, so they have
`check = "off"`. They always show on the site but aren't monitored.
Their PDF also couldn't be saved automatically. To keep a copy, download it in your
browser and add it to `files/`, named after the resource id:
`files/post-polypectomy-surveillance-recommendations.pdf`. The site will then serve it.

## One-time setup (about 20 minutes)

1. **Create a free GitHub account** at github.com.
2. **Create a new repository** (for example `patient-resources`). Choose *Public*,
   because free GitHub Pages needs a public repository. The site has no patient
   information, so this is fine.
3. **Upload this folder:** on the new repository page choose *uploading an existing file*
   and drag in everything in this folder. The `.github` folder is hidden in Finder
   (press <kbd>Cmd</kbd>+<kbd>Shift</kbd>+<kbd>.</kbd> to show it), and it **must** be included.
   You can skip `_site`. Alternatively, use the GitHub Desktop app.
4. **Turn on the website:** repository **Settings → Pages → Source: GitHub Actions**.
5. **Run it once:** **Actions** → **Check links & publish** → **Run workflow**.
   Your site address appears in **Settings → Pages**
   (for example `https://yourname.github.io/patient-resources/`).

### Getting emails

**Option A, no setup needed:** when something changes, the checker opens an
*Issue* in your repository, and GitHub emails you about it automatically.
Check that **github.com → Settings → Notifications → Email** is turned on.
Approving a resource closes its issue.

**Option B, direct email (optional):** add these under repository
**Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Example (Gmail) |
|---|---|
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | `you@gmail.com` |
| `SMTP_PASSWORD` | a Gmail **app password** (Google Account → Security → App passwords) |
| `NOTIFY_EMAIL` | the address that should receive alerts |

### A short web address for your business card

A `github.io` address works, but a short one like `drzhou.ca` is easier to type.
Buy a domain from any registrar (about $15–25/year). Then go to repository
**Settings → Pages → Custom domain**, enter it, and follow GitHub's DNS instructions.
Tick **Enforce HTTPS**. A QR code of the address on the card also helps.

## Previewing on your own computer (optional)

```bash
python3 scripts/check_links.py
```

```bash
python3 scripts/build.py && open _site/index.html
```

Requires Python 3.11 or newer (your Mac already has it via Homebrew). No other software is needed.
