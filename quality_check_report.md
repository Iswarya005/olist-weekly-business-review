# Part B — Data Quality Check Report

## 1. Objective

The purpose of the data quality checks is to validate the Olist dataset before it is used for business analysis. The pipeline must stop when a quality check fails.

## 2. Quality Check Results

| No. | Quality check | Observed result | Status |
|---|---|---:|---|
| 1 | NULL order IDs | 0 | Passed |
| 2 | Duplicate order IDs | 0 | Passed |
| 3 | Invalid delivery dates | 0 | Passed |
| 4 | Payment mismatches | 303 | Failed |
| 5 | Orders without matching customers | 0 | Passed |

## 3. Payment Mismatch Investigation

The payment validation identified 303 orders where the aggregated item-plus-freight total differed from the aggregated payment total by more than 0.01.

The ten orders with the largest absolute differences were retrieved for investigation. For each order, the following values were examined:

- Order ID
- Total item price plus freight
- Total recorded payment
- Difference between the two totals

These results provide examples for investigating the discrepancies. The mismatches have not been confirmed as data errors, and no records have been deleted or modified.

### Corrective Action

The 303 mismatches remain flagged as a data-quality issue. Further investigation is required to determine the cause of each discrepancy before making any correction. The strict quality check remains enabled, so the pipeline stops when these mismatches are detected.

## 4. Failure Handling

The Python quality-check script logs the result of each check. If any check reports failing records, it raises a RuntimeError with a summary of the failed checks. The main pipeline invokes the quality-check script and logs the pipeline failure.

## 5. Corrective Actions

- Investigate the 303 payment mismatches using order-level item totals and payment totals.
- Record the mismatch count and representative order IDs for further analysis.
- Do not silently delete or modify mismatched orders.
- Correct records only when the source data and business rules support the correction.
- Rerun the quality checks after any approved correction.
- Confirm that the pipeline stops whenever a strict quality check fails.

## 6. Conclusion

Four checks returned zero failing records, while the payment mismatch check identified 303 discrepancies. The payment validation therefore remains unresolved until the discrepancies are investigated and documented. The strict quality gate prevents the pipeline from reporting a successful completion when a check fails.