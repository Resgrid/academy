# Resgrid Academy

This is the standalone Resgrid Academy authoring and GitHub Pages repository. It contains the tutorial website,
24 illustrated primer videos, seven detailed videos with actual Resgrid screens, the
introductory Firehouse 51 walkthrough, English captions, chapter controls, 173 feature
briefs, 336 configuration references and examples for five department sectors.

The full course is still in production: 23 detailed workflows and human voice review
remain. Firehouse 51 uses fictional training data. The website is static. The repository includes public recording-stack recipes; generated
credentials, private certificates and private Descript editor links stay outside Git.

## Publish the separate repository

1. Create an empty GitHub repository, for example `Resgrid-Academy`, under your chosen
   account or organization. Place this bundle's contents in its root, including `.github`.
   Keep the actual media files in `site/`; the bundle ZIP itself is a download convenience.
2. Review the files, then commit and push them yourself. Suggested initial commit message:
   `Publish Resgrid Academy on GitHub Pages`.
3. In the new repository, select **Settings → Pages → Build and deployment → Source →
   GitHub Actions**. The first automatic deployment can fail until Pages is enabled;
   the manual action below is the initial deployment after this setting is saved.
4. Select **Actions → Deploy Resgrid Academy → Run workflow** and use the repository's
   default branch. The action validates the site, uploads the website artifact, then
   deploys it through the `github-pages` environment. The completed deployment displays
   the actual site URL.

Subsequent changes to `sources/`, `site/`, `scripts/` or the workflow deploy automatically when
pushed to the default branch. Pull requests validate without deployment. The workflow
uses the default branch reported by GitHub, so either `main` or `master` works.
The site does not hardcode an owner, repository name or hostname.

The preparation agent leaves everything uncommitted. The source project's AGENTS.md
requires human verification before commits and pushes; it says agents never run either.

## Add your custom domain

All internal links, thumbnails, videos and captions use relative URLs. The same files
work at a GitHub project address and at the root of your custom domain, with no rebuild
or URL rewriting required.

1. Verify your domain with GitHub, then save it under **Settings → Pages → Custom domain**.
2. Configure DNS for your domain using [GitHub's custom-domain instructions](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).
   A subdomain CNAME points to the account or organization's `github.io` hostname,
   without a repository path. Use the documented A/ALIAS/ANAME records for an apex domain.
3. Enable **Enforce HTTPS** when GitHub's certificate is available.
4. Run deployment. Leave the action's `custom_domain` field blank to use the existing
   Pages setting. Optionally enter the configured domain, without `https://` or a path,
   to have the workflow verify it before publishing. For automatic runs, the optional
   repository variable `ACADEMY_CUSTOM_DOMAIN` supplies the same check.

The optional field verifies the domain; it does not change DNS or repository settings.
With an Actions publishing source, GitHub reads the domain from Pages settings and
ignores a `CNAME` file in the artifact. No extra administrative token is needed.

## Preview and validate

Python 3.10 or later is sufficient; there are no runtime package dependencies.

```sh
python3 scripts/serve.py
```

Open `http://127.0.0.1:8769/` to test a domain-root deployment, or
`http://127.0.0.1:8769/Resgrid-Academy/` to test a project-path deployment.
The preview serves byte ranges for video playback and chapter seeking.

```sh
python3 -m unittest discover -s scripts/tests -v
python3 scripts/validate_site.py --site site --report _reports/pages-validation.json
```

Validation checks relative links and chapter anchors, dynamic player assets, private
editor links, local addresses, temporary signed URLs, symlinks, media checksums and file
sizes. The current site is approximately 380 MB; its largest file is approximately
44 MB. It is within the [GitHub Pages 1 GB site limit](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
and the [GitHub regular-file limit](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).
Media growth beyond these limits requires external media hosting; deployment validation
will stop rather than upload an oversized site.

## Author and rebuild here

All installed tutorial inputs are in `sources/`: editable course manifests, scripts,
lesson plans, narration exports, raw caption timing, original screenshots, illustrations,
current video masters and source evidence. See [AUTHORING.md](AUTHORING.md) for the
editing and rendering workflow.

```sh
python3 scripts/build.py
```

This builds the website from sources in this repository; no separate production folder,
Descript connection or running Resgrid stack is required. The Pages action performs the
same build before validation and deployment. It uploads only `site/`.

Create a new local Resgrid recording stack using the included fictional fixtures:

```sh
python3 scripts/setup_demo.py --plan
python3 scripts/setup_demo.py --core ../Core
```

See [sources/demo/README.md](sources/demo/README.md) for prerequisites, generated login
credentials, ports, safe reuse and recapturing screen states. Without `--core`, setup
acquires the recorded Resgrid revision in an ignored local checkout. Existing department
data is preserved; the seed is applied only on first use.

Reference: [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Check before a public commit

Run the credential audit before committing or pushing:

```sh
python3 scripts/audit_public_repo.py --report _reports/public-repo-audit.json
python3 scripts/validate_site.py --site site --report _reports/pages-validation.json
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
