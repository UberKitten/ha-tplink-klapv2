# ha-tplink-klapv2 — temporary KLAP v2 fix for the TP-Link integration

**This is a stopgap. Delete it when python-kasa ships KLAP v2 support.**

TP-Link firmware (rolling out through 2025–2026) switched Kasa devices to
"KLAP v2" local auth (`mgt_encrypt_schm: {encrypt_type: KLAP, lv: 2, new_klap: 1}`),
which changed the credential-hash derivation. python-kasa 0.10.2 — the latest
release, pinned by Home Assistant core — computes the old hash, so every auth
fails with *"Device response did not match our challenge … check that your
e-mail and password (both case-sensitive) are correct."* The credentials were
never wrong; the protocol moved.

Upstream fixes exist but are unmerged:
[python-kasa#1580](https://github.com/python-kasa/python-kasa/pull/1580),
[#1625](https://github.com/python-kasa/python-kasa/pull/1625),
[#1692](https://github.com/python-kasa/python-kasa/pull/1692).
Tracking issues: [python-kasa#1604](https://github.com/python-kasa/python-kasa/issues/1604),
[home-assistant/core#153390](https://github.com/home-assistant/core/issues/153390).

## What this is

- The **unmodified `tplink` integration from HA core 2026.7.0** (Apache-2.0),
  installed as a custom component so it shadows the built-in one.
- A **vendored python-kasa built from PR #1625** (commit `dd92c05`, GPL-3.0)
  under `_vendor/`, plus a tiny `sys.path` shim (`_patched_kasa.py`) imported
  first so the integration uses it instead of the image's 0.10.2.
- Nothing else is changed. Stored config-entry credentials work as-is after a
  restart — no re-auth needed if your credentials were already correct.

Why not a manifest `requirements` override? python-kasa 0.10.2 is baked into
the HA container image, so HA treats any URL requirement for the same package
as already satisfied and never installs it. Vendoring is deterministic.

## Install

HACS → custom repository → this repo (integration) → download → restart HA.

## Uninstall (when upstream ships)

Remove `custom_components/tplink/`, restart. HA falls back to the core
integration.

## Known limitations

- IOT strips on new_klap firmware (KP303/HS300/KP400) may be misdetected as
  single plugs by the PR-branch library (upstream bug, present in #1625 and
  #1692). Single plugs (HS103 etc.) are unaffected.
- Pinned to HA core 2026.7.0's integration code. A future HA core update may
  drift; re-sync the integration files if entities break after a core update.


## v2026.7.0.1 — survives restarts

The initial version restored the devices, but they broke again on the next HA
restart. Cause: the KLAP v2 fallback in the vendored python-kasa only fires when
**real credentials** are present; stock HA keeps credentials in memory only and
relies on the per-device `credentials_hash` for reconnects, and a hash-only
reconnect can't do KLAP v2 (and the persisted hash is the v1 hash regardless).
So after any restart, auth failed until a manual re-auth.

Fix: this build persists the cloud credentials to HA's standard `Store`
(`.storage/tplink_klapv2_credentials`) so `get_credentials()` returns them after
a restart, making the real-credential v2 path fire on every reconnect. Re-auth
once after installing; it survives restarts thereafter.

Note: the credential is stored in HA's `.storage` in plaintext (same as other
integrations that cache cloud creds). Removed when you remove this component.
