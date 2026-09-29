---
spec_id: INV-GOAT-001
category: GOAT
owner: Revenue Management
effective_date: 2026-01-01
---
GOAT Inventory Source Specification

The GOAT schema (DB2 z/OS) is the system of record for account inventory. The
primary inventory table stores one row per receivable line item, keyed by
RT_LN_ID, and carries the due period category (DUE_PD_CATEG), coverage period
begin date (COVRD_PER_BEG_DT), and the last operator identifier (LAST_OPER_ID).

Open inventory is defined as active RT_LN_ID rows with no closure flag whose
coverage period is current as of the reporting date. Closed or written-off lines
are excluded from open inventory but retained for audit history. Counts are
grouped by client and by site.

Refresh cadence: GOAT is extracted nightly; the capacity pipeline reads the
previous business day's snapshot to avoid partial intraday data.
