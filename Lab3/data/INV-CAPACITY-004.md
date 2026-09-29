---
spec_id: INV-CAPACITY-004
category: CAPACITY
effective_date: 2026-01-01
---
Capacity Planning Metric Specification

Capacity is available operator hours versus required hours to work open
inventory. Required hours are estimated by multiplying open inventory line count
(INV-GOAT-001) by the standard handle time for the line's due period category.

Utilization = actual worked hours / available hours. Above 100% signals
under-capacity (backlog risk); below 80% signals over-capacity. Metrics are
grouped by site, parent vendor, client, and business date. Weekend days are
excluded from required-hours targets unless a caveat flag is set.
