---
spec_id: INV-LANID-002
category: LANID
effective_date: 2026-01-01
---
LANID Site Attribution Specification

Site attribution maps each inventory line to the operating site. Resolution
order: (1) look up the operator LAN_ID in RA_SITE_LAN_ID_MAP to obtain SITE_NM;
(2) if not found, fall back to OFFSHR_LAN_ID and match LAN_ID to LOC_NM, using
that as SITE_NM.

SITE_PARENT is derived from SITE_NM: Chennai and Manila roll up to Accenture;
Gurugram rolls up to Concentrix. Operator prefixes such as BPAB indicate the
parent when SITE_NM alone is ambiguous. Attribution is grouped by the date of
cash movement for per-site, per-operator, per-client, per-date reporting.
