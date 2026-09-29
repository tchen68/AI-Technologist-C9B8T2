---
spec_id: INV-CASH-003
category: CASH
effective_date: 2026-01-01
---
Cash Allocation and Repository Specification

ALLOCD_CASH_DATE_MTD records allocated cash by allocation date (ALLOC_DT), site,
operator, client, and date, sorted newest to oldest by ALLOC_DT. Client identity
is unique by CLIENT_ID; duplicate client names may exist, so joins must key on
CLIENT_ID, never on name.

CASH_RPSTRY_MTD is the reconciled store of movement events. Both tables inherit
SITE_NM from the LANID attribution rules (INV-LANID-002), including the
OFFSHR_LAN_ID fallback, and both carry the SITE_PARENT rollup. Reconciliation
compares self-reported operator actions against system-of-record movements to
surface unmatched or misattributed cash.
