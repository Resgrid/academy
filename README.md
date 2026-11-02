# Resgrid Academy

This is the standalone Resgrid Academy authoring and GitHub Pages repository. It contains the tutorial website,
actual Resgrid screen walkthroughs, 24 text topic guides, English captions, chapter controls,
feature briefs and configuration references. `site/site-manifest.json` records the current
completed video inventory. Illustrated primer recordings remain in the authoring sources
and are not exported.

Published videos require complete screen, caption, audio and browser-playback evidence.
Editable lesson sources and capture plans are retained separately from qualified videos.
The text guides retain their teaching sections, role paths,
search, deep links, transcript downloads and examples for six sectors. The new lessons include examples for fire and EMS,
community care and mental health response, SAR, security, wildland and industrial teams.
Firehouse 51 uses fictional training data. The website is static. Public recording-stack
recipes are included; generated credentials, private certificates and private Descript
editor links stay outside Git.

## Publish the separate repository

1. Create an empty GitHub repository, for example `Resgrid-Academy`, under your chosen
   account or organization. Place this bundle's contents in its root, including `.github`.
   Keep the original media and authoring files in the repository. Deployment also uploads
   the qualified video bytes to GitHub Release assets.
2. Review the files, then commit and push them yourself. Suggested initial commit message:
   `Publish Resgrid Academy on GitHub Pages`.
3. In the new repository, select **Settings → Pages → Build and deployment → Source →
   GitHub Actions**. The first automatic deployment can fail until Pages is enabled;
   the manual action below is the initial deployment after this setting is saved.
4. Select **Actions → Deploy Resgrid Academy → Run workflow** and use the repository's
   default branch. The action validates and packages the site, uploads and verifies new
   Release videos, then deploys the website through the `github-pages` environment. The completed deployment displays
   the actual site URL.

Subsequent changes to `sources/`, `site/`, `scripts/` or the workflow deploy automatically when
pushed to the default branch. Pull requests validate without deployment. The workflow
uses the default branch reported by GitHub, so either `main` or `master` works.
The site uses relative URLs. `pages.json` records the expected hostname, `academy.resgrid.com`; every deployment checks it against GitHub Pages settings.

The preparation agent leaves everything uncommitted. The source project's AGENTS.md
requires human verification before commits and pushes; it says agents never run either.

## Academy hostname

The public hostname is **academy.resgrid.com**. `pages.json` is the versioned domain
configuration. The deployment job reads it on every publish and stops if GitHub Pages
reports a different hostname, preventing an accidental deployment under another address.

GitHub Pages must be enabled once under **Settings → Pages → Source → GitHub Actions**.
Save **academy.resgrid.com** under **Custom domain**. DNS uses a CNAME record named
`academy` pointing to `resgrid.github.io`, with no repository path. Enable **Enforce
HTTPS** when GitHub's certificate is ready.

The custom domain is a repository setting, so replacing the site artifact preserves it.
The workflow reads and checks that setting; it never clears or replaces it. GitHub ignores
artifact `CNAME` files for Actions publishing. The hostname check also accepts GitHub's
HTTP site URL while its TLS certificate is being provisioned, without changing HTTPS settings.

Leave the manual `custom_domain` input blank to use `pages.json`. An explicit input or
`ACADEMY_CUSTOM_DOMAIN` repository variable overrides only the expected-hostname check.
To change the permanent hostname, update `pages.json`, the Pages setting and DNS together.

If `configure-pages` reports **Not Found**, open the repository's Pages settings and
select **GitHub Actions**, then rerun the failed deployment. Automatic Pages enablement
requires separate administrative access; the publishing workflow uses the normal scoped
GitHub token without a stored personal token.

Reference: [GitHub custom-domain setup](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).

## Preview and validate

Python 3.10 or later is sufficient; there are no runtime package dependencies.

```sh
python3 scripts/serve.py
```

Open `http://127.0.0.1:8769/` to test a domain-root deployment, or
`http://127.0.0.1:8769/Resgrid-Academy/` to test a project-path deployment.
The preview serves byte ranges for video playback and chapter seeking.

```sh
python3 scripts/test_academy.py
```

Validation checks relative links and chapter anchors, dynamic player assets, private
editor links, local addresses, temporary signed URLs, symlinks, media checksums and file
sizes. The Pages delivery bundle serves video from permanent GitHub Release URLs, keeping
the website below the [GitHub Pages 1 GB site limit](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
as the library grows. Local preview retains self-contained video playback. See
[Release video delivery](docs/release-video-delivery.md) for packaging and verification.

The test runner checks current tools directly. Historical byte-pinned recipe regressions
run in an isolated copy with their exact retained validator; original receipts, expected
hashes and source files remain unchanged.

## Author and rebuild here

All installed tutorial inputs are in `sources/`: editable course manifests, scripts,
lesson plans, narration exports, raw caption timing, original screenshots, illustrations,
current video masters and source evidence. See [AUTHORING.md](AUTHORING.md) for the
editing and rendering workflow.

```sh
python3 scripts/build.py --local-preview
```

This builds the website from sources in this repository; no separate production folder,
Descript connection or running Resgrid stack is required. The Pages action performs the
same build before packaging and validation. It deploys the smaller Pages bundle and
publishes byte-identical video assets in the repository's `academy-media` Release.

The Academy's shared appearance lives in `sources/brand/academy.css` and
`scripts/academy_brand.py`. The official Resgrid logo and favicon files are included in
`sources/brand/`, with their original file paths and checksums in `provenance.json`.
Update these source files and rebuild to apply branding consistently across the homepage,
topic guides, and video lessons. Navigation and footer resource links share the same template.

Create a new local Resgrid recording stack using the included fictional fixtures:

```sh
python3 scripts/setup_demo.py --plan
python3 scripts/setup_demo.py --core ../Core
```

See [sources/demo/README.md](sources/demo/README.md) for prerequisites, generated login
credentials, ports, safe reuse and recapturing screen states. Without `--core`, setup
acquires the recorded Resgrid revision in an ignored local checkout. Existing department
data is preserved; the seed is applied only on first use.

The expansion lessons retain a separate five-repository source profile and reviewed
recording support patches. Use `python3 scripts/setup_demo.py --source-profile expansion --plan`
to inspect it. See [the expansion reproduction guide](sources/demo/README.expansion.md)
for isolated stack setup, verified app preparation and launch commands. Omitting the
selector keeps the legacy default; an existing saved source selection is reused.

Reference: [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Check before a public commit

Run the credential audit before committing or pushing:

```sh
python3 scripts/audit_public_repo.py --report _reports/public-repo-audit.json
python3 scripts/release_media.py package --site site --destination _reports/pages-site --assets _reports/release-media --repository Resgrid/academy
python3 scripts/validate_site.py --site _reports/pages-site --report _reports/pages-validation.json
```

The audit checks all tracked and non-ignored untracked working files, stored Git blobs and local Git configuration for private
keys, common access-token formats, credentials embedded in URLs and suspicious credential
assignments. It reports paths and rule names without printing credential values. The Pages
workflow repeats the check before deployment. Pattern matching cannot recognize every
possible secret; review unfamiliar files before publishing.

The `.gitignore` excludes local environment files, key files, credential files, private
folders, OS metadata and audit reports. Ignoring a file does not remove it from earlier
commits. If a real credential has already been pushed, rotate it and remove it from history
before treating the repository as safe to publish.
