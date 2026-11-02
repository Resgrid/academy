Use the v2 author for new final inputs after the actual listening review.

python3 -B sources/production/author_app_reference_take_01_v2_20261030.py --lesson all --projection-review-sha256 7a51ff03570288093bfbb4c996c3edb728499a2d76ed93e37bfd79d2d9f399d6

The default verifies actual existing sources, derived captions, decoded audio QA and instruction mapping. It creates no final plan or video.

For one approved lesson, use --lesson dispatch, ic or responder with --assemble, --listening-review-sha256 containing the exact genuine User receipt hash and --root-timing-review-sha256 c438f5f44138417c3f1faf5b63d49fa37c031fdc96dac723b2a1bc616ca2e254. IC additionally requires the projection review hash above. Read the script help for a safe public source-relative receipt override.

The existing v1 author is retained. Its source annotation used a historical caption parser whose floating-point addition order could differ by one bit from the renderer. v2 first proves identical words/endpoints within one-billionth of a second, then uses the renderer's exact SRT arithmetic to compute instruction digests. No SRT, source span, audio sample, frozen source, prior receipt or privacy gate changes. Actual renderer-expanded cue-digest roundtrips pass for every scene in all three lessons.

Nine targeted guards pass, including the real three-lesson renderer-cue regression. No actual listening receipt, final assembly, render, readiness or publication is supplied by these tests. Final input directories end in -v2 and refuse existing output.
