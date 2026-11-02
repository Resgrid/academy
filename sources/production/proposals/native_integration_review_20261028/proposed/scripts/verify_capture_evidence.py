#!/usr/bin/env python3
"""Validate one lesson's application-capture evidence using only the stdlib.

Run ``python scripts/verify_capture_evidence.py lesson.json --asset-root sources``.
Paths below are relative to --asset-root (default: the JSON file's directory).
The command prints a report with actionable JSON field paths and exits nonzero
on failure. ``verify(path, asset_root=None)`` returns the same report.

Schema version 1 (all times are seconds; all hashes are SHA-256 hex):

  {
    "schema_version": 1, "lesson_id": "incident-draft",
    "video": {
      "file": "media/incident-draft.mp4", "sha256": "<64 hex>",
      "duration_seconds": 30, "width": 1920, "height": 1080,
      "assembled_at": "2026-10-25T12:00:00Z",
      "captions": {"file": "media/incident-draft.vtt", "sha256": "<64 hex>"}
    },
    "screenshots": [{
      "id": "draft", "app": "Core", "kind": "application_screenshot",
      "file": "captures/draft.png", "sha256": "<64 hex>",
      "width": 1280, "height": 720,
      "provenance": {"method": "browser_screenshot",
        "url": "http://localhost:5000/User/Records/Edit/123",
        "captured_at": "2026-10-25T11:59:00Z"},
      "visible_labels": ["Incident record", "Draft", "Save draft"]
    }],
    "scenes": [{
      "id": "save", "kind": "operational", "start": 0, "end": 30,
      "screens": [{"screenshot_id": "draft", "start": 0, "end": 30}],
      "captions": [{"start": 0, "end": 30,
        "text": "Select Save draft to keep this incident record as a Draft.",
        "screenshot_id": "draft", "required_labels": ["Save draft", "Draft"]}]
    }],
    "rendered_segments": [{
      "scene_id": "save", "screenshot_id": "draft", "start": 0, "end": 30,
      "frame": {"file": "proof/frame.png", "sha256": "<64 hex>",
        "width": 1920, "height": 1080, "time": 15,
        "video_sha256": "<same video hash>", "application_visible": true,
        "visible_labels": ["Save draft", "Draft"],
        "caption_text": "Select Save draft to keep this incident record as a Draft."}
    }],
    "browser_playback": [{
      "position": "beginning", "video_sha256": "<same video hash>",
      "url": "http://localhost:8000/lessons/incident-draft",
      "current_src": "http://localhost:8000/media/incident-draft.mp4",
      "captured_at": "2026-10-25T12:01:00Z",
      "previous_time": 1, "current_time": 2, "duration_seconds": 30,
      "video_width": 1920, "video_height": 1080,
      "ready_state": 4, "network_state": 1, "paused": false, "ended": false,
      "media_error": null, "console_errors": [],
      "captions": {"mode": "showing", "text": "<active caption text>"},
      "screenshot": {"file": "proof/beginning.png", "sha256": "<64 hex>",
        "width": 1280, "height": 720}
    }]
  }

Supply all three playback positions: beginning (0-15%), middle (35-65%),
and end (85-100%, before ended). Each must demonstrate advancing playback,
matching dimensions/duration/hash, active captions and a browser screenshot.
The observations come from HTMLMediaElement and the browser capture session.

Every scene, including optional kind="context", must be backed by application
screenshots from Core, Dispatch, Responder, Unit or IC. Scenes and their screen
intervals must cover the complete video without gaps or overlaps (50ms timing
tolerance). Every screen
interval needs a matching rendered segment and a real extracted video frame.
Each caption maps an on-screen instruction to one screenshot and its required
visible labels; the screenshot must cover that caption's whole time interval.
VTT/SRT cues must match those mappings. Silent intervals between cues are fine.
Narrative-only cues may explicitly set instructional=false and required_labels=[];
every operational scene still needs at least one caption with a required UI
label. This allows normal subtitle chunking without inventing control names.
Every rendered frame must show its screen's mapped UI labels and an active caption.
PNG/JPEG dimensions are checked from file headers, and every asset is hashed.

Icon-only controls may be recorded separately from literal visible_labels:
visible_controls=[{accessible_name: "Send", role: "button",
rect: {x: 100, y: 100, width: 32, height: 32}, icon_only: true,
provenance: "browser_dom"}]. Rectangles are full DOM control boxes in raw-image
pixel coordinates, never a clipped intersection. Names must be actual specific
accessible names. An opaque modal, clipping ancestor or overlay must be checked
in the image review; metadata alone cannot establish visibility.

Nonempty visible_controls requires capture_review={passed:true, reviewer,
reviewed_at, sha256:<same image>, controls_sha256:visible_controls_digest(list),
application_visible:true, no_errors:true, controls_reviewed:true,
controls_fully_visible:true, controls_unobstructed:true}. Review follows capture.
Changing names/roles/rectangles invalidates that review. Existing literal-only
records remain compatible; do not insert accessible names into visible_labels.

Extracted video frames have no DOM. To demonstrate icons, frame may separately
record reviewed_control_names=["Send"] and control_review with the same review
fields, controls_sha256:visible_controls_digest(reviewed_control_names), plus
video_sha256 and source_screenshot_sha256. Names must already be validated in
the mapped source screenshot; review binds the actual extracted frame hash and
follows assembly. Rendering never creates a passed review or playback proof.

An explicitly reviewed scene may carry visual_required_labels and an
instruction_review={passed:true, reviewer, reviewed_at,
correspondence_reviewed:true, no_unseen_controls:true,
mapping_sha256:instruction_scene_digest(scene, screenshots_by_id)}. Every visual
requirement must occur in that scene's real screenshot sequence. Cue controls
still must occur in their exact mapped image. A cue may use spoken_references
such as {"Save & close": "Save and close"}; the phrase must actually occur in
that unchanged cue. The digest binds complete cue text/times, references, screen
intervals and source records. This lets reviewed natural speech explain an
actual UI without reciting all contextual labels, including a tab name split
across adjacent cues while its screen persists. It does not infer aliases or
prove semantic correctness. Without this review, the legacy literal-name rule
continues to apply.

This is a traceability gate, not OCR or media decoding: visible_labels, DOM
control names/bounds, image/frame reviews,
application_visible, browser observations, and provenance must be recorded by
the capture/review process, never invented from a storyboard. A hash proves
asset identity, not that its pixels depict a genuine application. Human visual
review and actual browser/media checks remain necessary. Legitimate UI states
such as an incident record labeled "Draft" are accepted; there is no word ban.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import struct
from urllib.parse import unquote, urlsplit


APPS = frozenset({"Core", "Dispatch", "Responder", "Unit", "IC"})
# Core workflow lessons may show the actual local SMTP receiver, with a truthful
# app identity. Authored plan/evidence supporting_applications must declare
# {app:"Mailpit",for_app:"Core",role:"controlled_local_receiver",purpose:...}.
# Evidence also records primary_app="Core". Only loopback receiver URLs qualify;
# these images never supply the authored primary app's configuration controls.
# All ordinary image identity, visual review, frame and playback gates still run.
LOCAL_RECEIVER_APP = "Mailpit"
EPSILON = 0.05
SHA256 = re.compile(r"[0-9a-f]{64}\Z", re.IGNORECASE)
CONTROL_ROLES = frozenset({"button", "link", "checkbox", "radio", "switch", "combobox", "textbox", "tab", "menuitem", "menuitemcheckbox", "menuitemradio", "slider", "spinbutton", "treeitem"})
GENERIC_CONTROL_NAME = re.compile(r"(?:button|icon(?:\s*button)?|control|link|image|img|svg|generic|unknown|unnamed|unlabelled|unlabeled|undefined|null|none|n/?a|click(?:\s+here|\s+me)?)(?:\s*[-_#]?\s*\d+)?\Z", re.I)
TIMING = re.compile(
    r"(?:(\d+):)?(\d{2}):(\d{2})[.,](\d{3})\s+-->\s+"
    r"(?:(\d+):)?(\d{2}):(\d{2})[.,](\d{3})(?:\s.*)?\Z"
)


def _normalized(text):
    return " ".join(text.split()).casefold() if isinstance(text, str) else ""


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def visible_controls_digest(controls):
    """Bind a visual review to the exact ordered DOM-control observations.

    This authenticates metadata identity, not pixels or the truth of a review.
    Controls must come from actual browser DOM observations and image inspection.
    """
    if not isinstance(controls, list):
        raise ValueError("visible_controls must be a list")
    encoded = json.dumps(controls, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def instruction_scene_digest(scene, screenshots):
    """Bind an explicit scene/speech correspondence review to current evidence.

    This does not infer semantic correspondence. A reviewer must inspect the
    exact pictured UI while reading the unchanged, actually timed speech.
    """
    fields = {key: scene.get(key) for key in ("id", "title", "kind", "start", "end", "visual_required_labels")}
    fields["screens"] = [{key: screen.get(key) for key in ("screenshot_id", "start", "end")} for screen in scene.get("screens", [])]
    fields["captions"] = [dict({key: caption.get(key) for key in ("start", "end", "text", "screenshot_id", "required_labels")},
                               instructional=caption.get("instructional", True), spoken_references=caption.get("spoken_references", {})) for caption in scene.get("captions", [])]
    ids = sorted({screen["screenshot_id"] for screen in fields["screens"]})
    fields["source_images"] = {ident: screenshots[ident] for ident in ids}
    return hashlib.sha256(json.dumps(fields, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _image_dimensions(path):
    """Read PNG/JPEG headers; do not claim to decode or visually inspect pixels."""
    with path.open("rb") as stream:
        head = stream.read(24)
        if head.startswith(b"\x89PNG\r\n\x1a\n") and head[12:16] == b"IHDR" and len(head) == 24:
            return struct.unpack(">II", head[16:24])
        stream.seek(0)
        if stream.read(2) != b"\xff\xd8":
            raise ValueError("expected a PNG or JPEG screenshot/frame, not an illustration document")
        while True:
            byte = stream.read(1)
            if not byte:
                break
            if byte != b"\xff":
                continue
            while byte == b"\xff":
                byte = stream.read(1)
            if not byte:
                break
            marker = byte[0]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                continue
            if marker in (0xD9, 0xDA):
                break
            size_bytes = stream.read(2)
            if len(size_bytes) != 2:
                break
            size = struct.unpack(">H", size_bytes)[0]
            if size < 2:
                break
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                data = stream.read(5)
                if len(data) == 5:
                    height, width = struct.unpack(">HH", data[1:])
                    return width, height
                break
            stream.seek(size - 2, 1)
    raise ValueError("image dimensions could not be read from the PNG/JPEG header")


def _caption_cues(text):
    cues = []
    blocks = re.split(r"\n\s*\n", text.replace("\r\n", "\n").lstrip("\ufeff").strip())
    for block in blocks:
        lines = block.splitlines()
        timing_index = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if timing_index is None:
            continue
        match = TIMING.fullmatch(lines[timing_index].strip())
        if not match:
            raise ValueError("invalid VTT/SRT cue timing: " + lines[timing_index])
        values = [int(part or 0) for part in match.groups()]
        start = values[0] * 3600 + values[1] * 60 + values[2] + values[3] / 1000
        end = values[4] * 3600 + values[5] * 60 + values[6] + values[7] / 1000
        if start >= end or values[1] > 59 or values[2] > 59 or values[5] > 59 or values[6] > 59:
            raise ValueError("invalid VTT/SRT cue range: " + lines[timing_index])
        body = re.sub(r"<[^>]*>", "", " ".join(lines[timing_index + 1:]))
        if not body.strip():
            raise ValueError("VTT/SRT cue has no text")
        cues.append((start, end, _normalized(body)))
    if not cues:
        raise ValueError("no VTT/SRT caption cues found")
    return cues


class _Validator:
    def __init__(self, root, native_context=None):
        self.root = Path(root).resolve()
        self.native_context = native_context
        self.issues = []

    def error(self, field, message):
        self.issues.append(f"{field}: {message}")

    def capture_provenance(self, item, field, primary_app=None):
        provenance = self.mapping(item.get("provenance"), field + ".provenance")
        method = provenance.get("method")
        if method == "browser_screenshot":
            if "native_evidence" in item:
                self.error(field, "native evidence cannot be relabeled as a browser screenshot")
            self.url(provenance.get("url"), field + ".provenance.url")
            return None
        if method == "ios_simulator_screenshot":
            try:
                from native_capture_source import validate_native_source
                return validate_native_source(item, self.root, primary_app, self.native_context)
            except (ValueError, OSError, KeyError, TypeError) as exc:
                self.error(field + ".native_evidence", str(exc))
                return None
        self.error(field + ".provenance.method", "require actual browser_screenshot or explicitly verified ios_simulator_screenshot provenance")
        # Preserve legacy invalid-browser URL diagnostics for unknown methods.
        self.url(provenance.get("url"), field + ".provenance.url")
        return None

    def supporting_applications(self, declarations, primary_app, field="supporting_applications"):
        """Permit one explicitly authored local receiver, never another lesson app."""
        if not isinstance(declarations, list):
            self.error(field, "must be a list of explicit supporting application declarations")
            return {}
        result = {}
        for index, declaration in enumerate(declarations):
            df = f"{field}[{index}]"
            item = self.mapping(declaration, df)
            app = item.get("app")
            if app != LOCAL_RECEIVER_APP or primary_app != "Core" or item.get("for_app") != "Core" or item.get("role") != "controlled_local_receiver":
                self.error(df, "only Core's explicitly declared Mailpit controlled_local_receiver is supported")
            self.text(item.get("purpose"), df + ".purpose")
            if isinstance(app, str):
                if app in result:
                    self.error(df, "duplicate supporting application declaration")
                result[app] = item
        return result

    def application(self, item, field, supporting=None):
        app = item.get("app")
        if isinstance(app, str) and app in APPS:
            return
        if app != LOCAL_RECEIVER_APP or not supporting or app not in supporting:
            self.error(field + ".app", "must be Core, Dispatch, Responder, Unit or IC, or an explicitly declared controlled local Mailpit receiver")
            return
        try:
            url = urlsplit(item.get("provenance", {}).get("url", ""))
            if url.scheme not in ("http", "https") or url.hostname not in ("localhost", "127.0.0.1", "::1") or url.username or url.password:
                raise ValueError()
        except (AttributeError, TypeError, ValueError):
            self.error(field + ".provenance.url", "supporting Mailpit evidence requires a credential-free loopback local receiver URL")

    def mapping(self, value, field):
        if not isinstance(value, dict):
            self.error(field, "must be an object")
            return {}
        return value

    def items(self, value, field):
        if not isinstance(value, list) or not value:
            self.error(field, "must be a nonempty array")
            return []
        return value

    def text(self, value, field):
        if not isinstance(value, str) or not value.strip():
            self.error(field, "must be a nonempty string")
            return ""
        return value

    def labels(self, value, field, allow_empty=False):
        values = [] if allow_empty and value == [] else self.items(value, field)
        result = [self.text(label, f"{field}[{i}]") for i, label in enumerate(values)]
        return {_normalized(label) for label in result if label}

    def accepted_image(self, item, field):
        """Explicit rejection or a blocked viewport cannot become operation proof."""
        state = str(item.get("state", "")).strip().casefold()
        review_status = str(item.get("review_status", "")).strip().casefold()
        if (any(item.get(flag) is False for flag in ("accepted", "publication_eligible", "eligible_for_lesson"))
                or item.get("contains_private_ui") is True or item.get("blocked") is True
                or isinstance(item.get("capture_review"), dict) and item["capture_review"].get("passed") is False
                or state.startswith(("blocked", "excluded", "loading", "error", "failed", "rejected", "unreviewed", "pending"))
                or review_status.startswith(("blocked", "failed", "rejected", "unreviewed", "pending"))):
            self.error(field, "rejected, private, blocked or unreviewed images are not operational evidence")

    def control_review(self, value, item, field, digest, captured_at=None):
        review = self.mapping(value, field)
        if review.get("passed") is not True:
            self.error(field + ".passed", "record a passed actual image/control review")
        self.text(review.get("reviewer"), field + ".reviewer")
        reviewed_at = self.timestamp(review.get("reviewed_at"), field + ".reviewed_at")
        if reviewed_at and (reviewed_at > datetime.now(timezone.utc) or captured_at and reviewed_at < captured_at):
            self.error(field + ".reviewed_at", "review must follow the actual capture/assembly and cannot be in the future")
        if not isinstance(item.get("sha256"), str) or review.get("sha256") != item.get("sha256"):
            self.error(field + ".sha256", "image review must bind this exact asset hash")
        if review.get("controls_sha256") != digest:
            self.error(field + ".controls_sha256", "review must bind these exact ordered control observations; re-review changed metadata")
        for flag in ("application_visible", "no_errors", "controls_reviewed", "controls_fully_visible", "controls_unobstructed"):
            if review.get(flag) is not True:
                self.error(field + "." + flag, "requires actual visual review of fully visible, unobstructed controls")
        return review

    def visible_controls(self, item, field):
        if "visible_controls" not in item or item.get("visible_controls") == []:
            return set()
        controls = self.items(item.get("visible_controls"), field + ".visible_controls")
        result, seen = set(), set()
        width, height = item.get("width"), item.get("height")
        for index, raw in enumerate(controls):
            cf = f"{field}.visible_controls[{index}]"
            control = self.mapping(raw, cf)
            name = self.text(control.get("accessible_name"), cf + ".accessible_name").strip()
            if not any(character.isalpha() for character in name) or GENERIC_CONTROL_NAME.fullmatch(name) or len(name) > 200:
                self.error(cf + ".accessible_name", "use the actual specific accessible control name, not a generic or invented label")
            if not isinstance(control.get("role"), str) or control.get("role") not in CONTROL_ROLES:
                self.error(cf + ".role", "record an actual interactive accessibility role")
            if control.get("icon_only") is not True or control.get("provenance") != "browser_dom":
                self.error(cf, "icon-only control observations require icon_only=true and provenance=browser_dom")
            if control.get("clipped") is True or control.get("occluded") is True or control.get("fully_visible") is False:
                self.error(cf, "clipped or occluded controls cannot satisfy an instruction")
            rect = self.mapping(control.get("rect"), cf + ".rect")
            x, y, w, h = (rect.get(key) for key in ("x", "y", "width", "height"))
            if not all(_number(value) for value in (x, y, w, h)) or not _number(width) or not _number(height) or x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > width or y + h > height:
                self.error(cf + ".rect", "record the full positive DOM control bounds inside the screenshot; offscreen/clipped controls are forbidden")
            else:
                role = control.get("role") if isinstance(control.get("role"), str) else ""
                identity = (name, role, x, y, w, h)
                if identity in seen:
                    self.error(cf, "duplicate control observation")
                seen.add(identity)
            if name:
                result.add(_normalized(name))
        try:
            digest = visible_controls_digest(controls)
        except (TypeError, ValueError) as exc:
            self.error(field + ".visible_controls", str(exc))
            digest = None
        provenance = self.mapping(item.get("provenance"), field + ".provenance")
        if provenance.get("method") != "browser_screenshot":
            self.error(field + ".provenance.method", "icon evidence requires an actual browser screenshot")
        captured_at = self.timestamp(provenance.get("captured_at"), field + ".provenance.captured_at")
        self.control_review(item.get("capture_review"), item, field + ".capture_review", digest, captured_at)
        self.accepted_image(item, field)
        return result

    def observations(self, item, field):
        self.accepted_image(item, field)
        controls = self.visible_controls(item, field)
        labels = self.labels(item.get("visible_labels"), field + ".visible_labels", allow_empty=bool(controls))
        return labels | controls

    def spoken_references(self, caption, labels, field, reviewed_mode=False):
        references = caption.get("spoken_references", {})
        if not isinstance(references, dict):
            self.error(field + ".spoken_references", "use exact UI labels mapped to explicit unchanged spoken phrases")
            references = {}
        if references and not reviewed_mode:
            self.error(field + ".spoken_references", "natural references need an explicit reviewed scene-coverage mapping")
        normalized = {}
        for label, phrase in references.items():
            key = _normalized(self.text(label, field + ".spoken_references.label"))
            phrase = _normalized(self.text(phrase, field + ".spoken_references.phrase"))
            if key not in labels or not phrase or phrase not in _normalized(caption.get("text")):
                self.error(field + ".spoken_references", "reference an actually required visible control with an exact phrase from this speech cue")
            normalized[key] = phrase
        for label in labels:
            if label not in _normalized(caption.get("text")) and not (reviewed_mode and normalized.get(label)):
                self.error(field + ".text", f"caption must name its required visible label {label!r}, or provide its explicit reviewed spoken reference")

    def instruction_review(self, scene, screenshots, observed, field, primary_app=None):
        required = self.labels(scene.get("visual_required_labels"), field + ".visual_required_labels")
        union = set()
        for screen in scene.get("screens", []):
            if isinstance(screen, dict) and isinstance(screen.get("screenshot_id"), str):
                ident = screen["screenshot_id"]
                if primary_app is None or screenshots.get(ident, {}).get("app") == primary_app:
                    union.update(observed.get(ident, set()))
        if not required <= union:
            self.error(field + ".visual_required_labels", "every required scene label must be visible in the reviewed real screenshot sequence from the primary application; supporting receiver images cannot supply Resgrid configuration controls")
        review = self.mapping(scene.get("instruction_review"), field + ".instruction_review")
        self.text(review.get("reviewer"), field + ".instruction_review.reviewer")
        reviewed_at = self.timestamp(review.get("reviewed_at"), field + ".instruction_review.reviewed_at")
        if reviewed_at and reviewed_at > datetime.now(timezone.utc):
            self.error(field + ".instruction_review.reviewed_at", "review cannot be in the future")
        for flag in ("passed", "correspondence_reviewed", "no_unseen_controls"):
            if review.get(flag) is not True:
                self.error(field + ".instruction_review." + flag, "requires actual review of this frozen speech and corresponding visible screens")
        try:
            if review.get("mapping_sha256") != instruction_scene_digest(scene, screenshots):
                self.error(field + ".instruction_review.mapping_sha256", "review must bind the exact current scene, speech, references, intervals and source images")
            for screen in scene.get("screens", []):
                shot = screenshots[screen["screenshot_id"]]
                captured_at = self.timestamp(shot.get("provenance", {}).get("captured_at"), field + ".instruction_review.source_capture")
                if reviewed_at and captured_at and reviewed_at < captured_at:
                    self.error(field + ".instruction_review.reviewed_at", "instruction review predates its source screenshot")
        except (TypeError, ValueError, KeyError, AttributeError) as exc:
            self.error(field + ".instruction_review", "cannot bind malformed scene/source observations: " + str(exc))

    def timestamp(self, value, field):
        try:
            if not isinstance(value, str):
                raise ValueError()
            result = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if result.tzinfo is None:
                raise ValueError()
            return result
        except ValueError:
            self.error(field, "record an ISO-8601 timestamp with timezone, such as 2026-10-25T12:00:00Z")
            return None

    def url(self, value, field):
        try:
            url = urlsplit(value) if isinstance(value, str) else None
            if url and url.scheme in {"http", "https"} and url.hostname and not url.username and not url.password:
                return url
        except ValueError:
            pass
        self.error(field, "record the actual http(s) browser URL without embedded credentials")
        return None

    def dimensions(self, item, field, prefix=""):
        width, height = item.get(prefix + "width"), item.get(prefix + "height")
        if not all(isinstance(v, int) and not isinstance(v, bool) and v >= minimum for v, minimum in [(width, 240), (height, 180)]):
            self.error(field, f"{prefix}width/{prefix}height must be integer dimensions of at least 240x180")
            return None
        return width, height

    def asset(self, item, field, image=False):
        item = self.mapping(item, field)
        name = self.text(item.get("file"), field + ".file")
        digest = item.get("sha256")
        valid_hash = isinstance(digest, str) and SHA256.fullmatch(digest)
        if not valid_hash:
            self.error(field + ".sha256", "record the SHA-256 of the existing asset (64 hexadecimal characters)")
        path = self.root / name
        try:
            resolved = path.resolve()
            if not name or Path(name).is_absolute() or self.root not in resolved.parents:
                self.error(field + ".file", "must be an asset path relative to and inside asset_root")
                return None
            if not resolved.is_file() or resolved.stat().st_size == 0:
                self.error(field + ".file", f"asset is missing or empty: {name}")
                return None
            if valid_hash and _hash(resolved) != digest.lower():
                self.error(field + ".sha256", f"hash mismatch for {name}; recapture or regenerate evidence for the current asset")
            if image:
                dimensions = self.dimensions(item, field)
                actual = _image_dimensions(resolved)
                if dimensions and dimensions != actual:
                    self.error(field, f"declared image dimensions {dimensions} differ from asset header {actual}")
            return resolved
        except (OSError, ValueError) as exc:
            self.error(field + ".file", str(exc))
            return None

    def interval(self, item, field, bounds):
        start, end = item.get("start"), item.get("end")
        if not _number(start) or not _number(end) or start < 0 or end <= start:
            self.error(field, "start/end must be finite seconds with 0 <= start < end")
            return None
        if bounds and (start < bounds[0] - EPSILON or end > bounds[1] + EPSILON):
            self.error(field, f"interval {start:g}-{end:g}s is outside {bounds[0]:g}-{bounds[1]:g}s")
        return start, end

    def coverage(self, intervals, bounds, field):
        if not bounds:
            return
        cursor = bounds[0]
        for start, end in sorted(intervals):
            if start > cursor + EPSILON:
                self.error(field, f"coverage gap from {cursor:g}s to {start:g}s; add the missing real screen/scene interval")
            elif start < cursor - EPSILON:
                self.error(field, f"overlapping coverage at {start:g}s; record one unambiguous screen/scene timeline")
            cursor = max(cursor, end)
        if cursor < bounds[1] - EPSILON:
            self.error(field, f"coverage gap from {cursor:g}s to {bounds[1]:g}s")


def verify_document(document, asset_root, native_context=None):
    """Validate an already-loaded evidence document; see the module schema."""
    v = _Validator(asset_root, native_context)
    data = v.mapping(document, "$ (lesson evidence)")
    if data.get("schema_version") != 1 or isinstance(data.get("schema_version"), bool):
        v.error("schema_version", "must equal 1")
    lesson_id = v.text(data.get("lesson_id"), "lesson_id")
    video = v.mapping(data.get("video"), "video")
    v.asset(video, "video")
    video_dimensions = v.dimensions(video, "video")
    duration = video.get("duration_seconds")
    if not _number(duration) or duration <= 0:
        v.error("video.duration_seconds", "must be a positive finite number")
        duration = None
    assembled_at = v.timestamp(video.get("assembled_at"), "video.assembled_at")
    video_hash = video.get("sha256")
    caption_path = v.asset(video.get("captions"), "video.captions")
    asset_cues = []
    if caption_path:
        try:
            asset_cues = _caption_cues(caption_path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, ValueError) as exc:
            v.error("video.captions", str(exc))

    primary_app = data.get("primary_app")
    supporting = v.supporting_applications(data.get("supporting_applications", []), primary_app)
    screenshots, screenshot_control_names, screenshot_hashes, screenshot_records, native_reports = {}, {}, {}, {}, {}
    for i, raw in enumerate(v.items(data.get("screenshots"), "screenshots")):
        field = f"screenshots[{i}]"
        item = v.mapping(raw, field)
        ident = v.text(item.get("id"), field + ".id")
        if ident in screenshots:
            v.error(field + ".id", f"duplicate screenshot ID {ident!r}")
        v.application(item, field, supporting)
        if item.get("kind") != "application_screenshot":
            v.error(field + ".kind", "must be application_screenshot; an illustrated substitute is not application evidence")
        v.asset(item, field, image=True)
        v.accepted_image(item, field)
        provenance = v.mapping(item.get("provenance"), field + ".provenance")
        native = v.capture_provenance(item, field, primary_app)
        if native is not None:
            native_reports[ident] = native
        captured = v.timestamp(provenance.get("captured_at"), field + ".provenance.captured_at")
        if captured and assembled_at and captured > assembled_at:
            v.error(field + ".provenance.captured_at", "application screenshot was captured after this video was assembled")
        controls = v.visible_controls(item, field)
        labels = v.labels(item.get("visible_labels"), field + ".visible_labels", allow_empty=bool(controls))
        if ident:
            screenshots[ident] = labels | controls
            screenshot_control_names[ident] = controls
            screenshot_hashes[ident] = item.get("sha256")
            screenshot_records[ident] = item

    scenes, scene_intervals, expected_segments, mapped_cues = {}, [], [], []
    for i, raw in enumerate(v.items(data.get("scenes"), "scenes")):
        field = f"scenes[{i}]"
        item = v.mapping(raw, field)
        reviewed_mode = "visual_required_labels" in item
        ident = v.text(item.get("id"), field + ".id")
        if ident in scenes:
            v.error(field + ".id", f"duplicate scene ID {ident!r}")
        if item.get("kind") not in ("operational", "context"):
            v.error(field + ".kind", "must be operational or context; every scene needs actual application screens")
        interval = v.interval(item, field, (0, duration) if duration else None)
        if interval:
            scene_intervals.append(interval)
        screens = []
        for j, raw_screen in enumerate(v.items(item.get("screens"), field + ".screens")):
            sf = f"{field}.screens[{j}]"
            screen = v.mapping(raw_screen, sf)
            sid = v.text(screen.get("screenshot_id"), sf + ".screenshot_id")
            if sid not in screenshots:
                v.error(sf + ".screenshot_id", f"unknown application screenshot {sid!r}")
            span = v.interval(screen, sf, interval)
            if span:
                screens.append((sid, span))
                expected_segments.append((ident, sid, span))
        v.coverage([span for _, span in screens], interval, field + ".screens")
        captions = []
        mapped_screens = set()
        for j, raw_caption in enumerate(v.items(item.get("captions"), field + ".captions")):
            cf = f"{field}.captions[{j}]"
            caption = v.mapping(raw_caption, cf)
            span = v.interval(caption, cf, interval)
            text = v.text(caption.get("text"), cf + ".text")
            sid = v.text(caption.get("screenshot_id"), cf + ".screenshot_id")
            instructional = caption.get("instructional", True)
            if not isinstance(instructional, bool):
                v.error(cf + ".instructional", "must be true or false when present")
            labels = v.labels(caption.get("required_labels"), cf + ".required_labels", allow_empty=instructional is False)
            missing = labels - screenshots.get(sid, set())
            if missing:
                v.error(cf + ".required_labels", f"required visible control/label(s) {sorted(missing)!r} are not observed in screenshot {sid!r}")
            v.spoken_references(caption, labels, cf, reviewed_mode)
            if span:
                if not any(screen_id == sid and span[0] >= screen_span[0] - EPSILON and span[1] <= screen_span[1] + EPSILON for screen_id, screen_span in screens):
                    v.error(cf + ".screenshot_id", "mapped screenshot must be displayed for this caption's entire interval; split captions at screen cuts")
                cue = (*span, _normalized(text))
                mapped_cues.append(cue)
                captions.append((span, text, sid, labels))
                mapped_screens.add(sid)
                if not any(abs(cue[0] - actual[0]) <= EPSILON and abs(cue[1] - actual[1]) <= EPSILON and cue[2] == actual[2] for actual in asset_cues):
                    v.error(cf, "caption text/timing does not match a cue in the hashed VTT/SRT asset")
        for sid, _ in screens:
            if sid not in mapped_screens:
                v.error(field + ".captions", f"screen {sid!r} needs a caption-to-required-visible-label mapping")
        if item.get("kind") == "operational" and not any(c[3] for c in captions):
            v.error(field + ".captions", "an operational scene needs at least one instructional caption mapped to required visible UI labels")
        if reviewed_mode:
            v.instruction_review(item, screenshot_records, screenshots, field, primary_app if supporting else None)
        if ident:
            scenes[ident] = {"interval": interval, "screens": screens, "captions": captions}
    v.coverage(scene_intervals, (0, duration) if duration else None, "scenes")
    for cue in asset_cues:
        if duration and cue[1] > duration + EPSILON:
            v.error("video.captions", f"cue ends past the video at {cue[1]:g}s")
        if not any(abs(cue[0] - mapped[0]) <= EPSILON and abs(cue[1] - mapped[1]) <= EPSILON and cue[2] == mapped[2] for mapped in mapped_cues):
            v.error("video.captions", f"cue at {cue[0]:g}s has no scene/screenshot/required-label mapping")

    def active_caption(time, scene_id=None):
        return [caption for ident, scene in scenes.items() if scene_id is None or ident == scene_id for caption in scene["captions"] if caption[0][0] <= time < caption[0][1]]

    actual_segments = []
    for i, raw in enumerate(v.items(data.get("rendered_segments"), "rendered_segments")):
        field = f"rendered_segments[{i}]"
        segment = v.mapping(raw, field)
        ident = v.text(segment.get("scene_id"), field + ".scene_id")
        sid = v.text(segment.get("screenshot_id"), field + ".screenshot_id")
        scene = scenes.get(ident, {})
        if not scene:
            v.error(field + ".scene_id", "reference an existing scene")
        span = v.interval(segment, field, scene.get("interval"))
        if span:
            actual_segments.append((ident, sid, span))
            if not any(ident == ei and sid == es and abs(span[0] - ep[0]) <= EPSILON and abs(span[1] - ep[1]) <= EPSILON for ei, es, ep in expected_segments):
                v.error(field, "rendered segment does not match a planned scene/screenshot interval")
        frame = v.mapping(segment.get("frame"), field + ".frame")
        v.asset(frame, field + ".frame", image=True)
        v.accepted_image(frame, field + ".frame")
        if video_dimensions and (frame.get("width"), frame.get("height")) != video_dimensions:
            v.error(field + ".frame", "extracted frame dimensions must match the assembled video")
        if not isinstance(video_hash, str) or frame.get("video_sha256") != video_hash:
            v.error(field + ".frame.video_sha256", "frame proof must reference the current assembled video's hash")
        if frame.get("application_visible") is not True:
            v.error(field + ".frame.application_visible", "review and record that the real application is visible in the rendered frame")
        if sid in native_reports:
            try:
                from native_capture_source import verify_native_frame
                verify_native_frame(frame, video_hash, native_reports[sid], video.get("assembled_at"))
            except (ValueError, OSError, KeyError, TypeError) as exc:
                v.error(field + ".frame.native_frame_review", str(exc))
        reviewed_names = frame.get("reviewed_control_names", [])
        frame_controls = set()
        if reviewed_names != []:
            frame_controls = v.labels(reviewed_names, field + ".frame.reviewed_control_names")
            if not frame_controls <= screenshot_control_names.get(sid, set()):
                v.error(field + ".frame.reviewed_control_names", "frame controls must reference validated DOM controls from this source screenshot")
            try:
                digest = visible_controls_digest(reviewed_names)
            except (TypeError, ValueError) as exc:
                v.error(field + ".frame.reviewed_control_names", str(exc))
                digest = None
            review = v.control_review(frame.get("control_review"), frame, field + ".frame.control_review", digest, assembled_at)
            if review.get("video_sha256") != video_hash or review.get("source_screenshot_sha256") != screenshot_hashes.get(sid):
                v.error(field + ".frame.control_review", "frame control review must bind the current video and exact source screenshot hashes")
        observed_labels = v.labels(frame.get("visible_labels"), field + ".frame.visible_labels", allow_empty=bool(frame_controls)) | frame_controls
        time = frame.get("time")
        if not _number(time) or not span or not span[0] <= time < span[1]:
            v.error(field + ".frame.time", "sample a frame inside this rendered interval")
        else:
            captions = [c for c in active_caption(time, ident) if c[2] == sid and _normalized(c[1]) == _normalized(frame.get("caption_text"))]
            if not captions:
                v.error(field + ".frame.caption_text", "sample a frame with an active mapped caption and record that exact caption text")
            required = set().union(*(c[3] for c in scene.get("captions", []) if c[2] == sid))
            if not required <= observed_labels:
                v.error(field + ".frame.visible_labels", "required caption controls/labels are not observed in the assembled frame")
    for ident, sid, span in expected_segments:
        matches = [actual for actual in actual_segments if ident == actual[0] and sid == actual[1] and abs(span[0] - actual[2][0]) <= EPSILON and abs(span[1] - actual[2][1]) <= EPSILON]
        if len(matches) != 1:
            v.error("rendered_segments", f"scene {ident!r}, screen {sid!r}, {span[0]:g}-{span[1]:g}s needs exactly one rendered segment and extracted frame (found {len(matches)})")

    positions = {}
    bands = {"beginning": (0, 0.15), "middle": (0.35, 0.65), "end": (0.85, 1)}
    for i, raw in enumerate(v.items(data.get("browser_playback"), "browser_playback")):
        field = f"browser_playback[{i}]"
        proof = v.mapping(raw, field)
        position = v.text(proof.get("position"), field + ".position")
        if position not in bands:
            v.error(field + ".position", "must be beginning, middle or end")
        else:
            positions[position] = positions.get(position, 0) + 1
        if not isinstance(video_hash, str) or proof.get("video_sha256") != video_hash:
            v.error(field + ".video_sha256", "stale-video playback proof; recapture playback of the current assembled video")
        v.url(proof.get("url"), field + ".url")
        current_src = v.url(proof.get("current_src"), field + ".current_src")
        video_file = video.get("file") if isinstance(video.get("file"), str) else ""
        if current_src and Path(unquote(current_src.path)).name != Path(video_file).name:
            v.error(field + ".current_src", "browser is playing a different asset filename than video.file")
        captured = v.timestamp(proof.get("captured_at"), field + ".captured_at")
        if captured and assembled_at and captured < assembled_at:
            v.error(field + ".captured_at", "playback proof predates assembly; record a fresh browser check")
        if video_dimensions and (proof.get("video_width"), proof.get("video_height")) != video_dimensions:
            v.error(field, "browser video_width/video_height must match the assembled video; zero dimensions are not playable")
        observed_duration = proof.get("duration_seconds")
        if not _number(observed_duration) or not duration or abs(observed_duration - duration) > EPSILON:
            v.error(field + ".duration_seconds", "browser duration must match the current assembled video")
        if proof.get("ready_state") not in (3, 4) or isinstance(proof.get("ready_state"), bool):
            v.error(field + ".ready_state", "HTMLMediaElement.readyState must be 3 or 4")
        if proof.get("network_state") not in (1, 2) or isinstance(proof.get("network_state"), bool):
            v.error(field + ".network_state", "HTMLMediaElement.networkState must be IDLE (1) or LOADING (2)")
        if proof.get("paused") is not False or proof.get("ended") is not False:
            v.error(field, "record advancing playback with paused=false and ended=false")
        if "media_error" not in proof or proof["media_error"] is not None or proof.get("console_errors") != []:
            v.error(field, "record media_error=null and console_errors=[] from the browser; resolve errors before capture")
        previous, current = proof.get("previous_time"), proof.get("current_time")
        if not _number(previous) or not _number(current) or previous < 0 or current <= previous:
            v.error(field, "previous_time/current_time must demonstrate forward playback progress")
        if _number(current):
            if duration and (not 0 < current < duration or position in bands and not bands[position][0] <= current / duration <= bands[position][1]):
                v.error(field + ".current_time", "seek and play within the declared beginning/middle/end percentage band")
            captions = v.mapping(proof.get("captions"), field + ".captions")
            if captions.get("mode") != "showing" or not _normalized(captions.get("text")):
                v.error(field + ".captions", "captions must be showing with visible active text")
            elif not any(_normalized(captions.get("text")) == _normalized(c[1]) for c in active_caption(current)):
                v.error(field + ".captions.text", "visible playback caption does not match the mapped caption at current_time")
        v.asset(proof.get("screenshot"), field + ".screenshot", image=True)
    for position in bands:
        if positions.get(position) != 1:
            v.error("browser_playback", f"supply exactly one {position} browser playback proof (found {positions.get(position, 0)})")

    return {"passed": not v.issues, "lesson_id": lesson_id, "issues": v.issues}


def verify(evidence_path, asset_root=None, native_context=None):
    """Read and validate one lesson JSON. Missing/malformed inputs fail cleanly."""
    evidence_path = Path(evidence_path)
    try:
        document = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"passed": False, "lesson_id": None, "issues": [f"evidence: cannot read {evidence_path}: {exc}"]}
    return verify_document(document, asset_root or evidence_path.resolve().parent, native_context)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate one lesson's actual-application capture, render, caption and browser-playback evidence.")
    parser.add_argument("evidence", type=Path, help="lesson evidence JSON")
    parser.add_argument("--asset-root", type=Path, help="base directory for relative asset paths")
    from native_capture_source import add_native_arguments, context_from_arguments
    add_native_arguments(parser)
    args = parser.parse_args(argv)
    try:
        report = verify(args.evidence, args.asset_root, context_from_arguments(args))
    except ValueError as exc:
        report = {"passed": False, "issues": [str(exc)]}
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
