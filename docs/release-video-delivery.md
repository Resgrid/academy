# Release video delivery

The website remains at **academy.resgrid.com**. Its HTML, images, captions and chapters
use portable relative URLs. Video players and video downloads in the deployment bundle
use public assets from this same repository's `academy-media` GitHub Release.
The workflow derives the repository name from GitHub; the website hostname is independently
kept in `pages.json` and checked against Pages settings on every deployment.

Original video masters, narration, scripts, screenshots, captions, recording fixtures and
review evidence stay in the repository. Packaging copies qualified video bytes without
encoding them again. Asset names contain the complete SHA256, so a revised master gets a
new URL and earlier assets remain available.

## Local build and packaging

```sh
python3 scripts/test_academy.py
python3 scripts/build.py --local-preview
python3 scripts/release_media.py package --site site --destination _reports/pages-site --assets _reports/release-media --repository Resgrid/academy
python3 scripts/validate_site.py --site _reports/pages-site
python3 scripts/release_media.py upload --assets _reports/release-media
```

Use fresh output directories for a new package. The last command only checks local
upload bytes and hashes. It does not contact GitHub or publish anything.
`site/` remains self-contained for local playback; `_reports/pages-site/` is the delivery
bundle. The final delivery validation enforces the Pages size limit and permits only the
listed, hash-named GitHub Release videos. It rejects local videos, missing assets, private
editor links, temporary signed URLs and arbitrary external player URLs.

## Deployment

After a person reviews, commits and pushes the changes, the Pages action:

1. Runs current guards and exact historical-tool regressions, builds once and audits the public repository.
2. Creates and validates the Pages bundle plus its separate video upload inventory.
3. Passes the validated video artifact to a guarded default-branch job with `contents: write`.
4. Reuses matching Release assets and uploads new ones, checking GitHub's SHA256 digest,
   size, uploaded state and permanent download URL. Conflicting assets are preserved and fail the job.
5. Deploys the Pages artifact only after all Release assets pass verification and the hostname matches.

Pull requests have read-only repository access and never publish media or Pages. The
publication job uses GitHub's automatic `GITHUB_TOKEN`; no personal token or private key
is stored in this repository. The uploader's `--execute` mode also independently requires
a default-branch push or manual workflow run in GitHub Actions.

The media Release must allow appending new assets. If it is marked immutable, the uploader
stops before adding assets; select a new appendable media tag in the packaging command
and workflow rather than replacing historical files. No uploader code deletes or overwrites
existing Release assets.

Live Release URL playback can be checked after the human-triggered workflow has uploaded
the assets. Packaging tests and local playback do not claim that an unpublished URL already exists.

References: [Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits),
[Release asset API and digests](https://docs.github.com/en/rest/releases/assets).
