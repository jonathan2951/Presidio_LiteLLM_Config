# Presidio_LiteLLM_Config
scripts and docker config for a Presidio+LiteLLM connection

## Presidio 

Presidio is a suite of tools for detecting and de-identifying PII in text, images, and structured data.

- https://microsoft.github.io/presidio/tutorial/00_getting_started/

How the thresholds work:

  The threshold values (0.0 to 1.0) represent the minimum confidence score required to trigger masking. Presidio will only mask entities that meet or exceed the threshold.

  Current configuration:
  presidio_score_thresholds:
    CREDIT_CARD: 0.95      # Only mask if 95%+ confident
    EMAIL_ADDRESS: 0.95    # Only mask if 95%+ confident
    PERSON: 0.95           # Only mask if 95%+ confident
    PHONE_NUMBER: 0.95     # Only mask if 95%+ confident

  Example scenarios:

  1. High threshold (0.95) - Very strict, only masks when very confident:
    - Presidio detects "John" as PERSON with score 0.80 → NOT masked (below 0.95)
    - Presidio detects "john@email.com" as EMAIL with score 0.98 → Masked (above 0.95)
  2. Medium threshold (0.6) - More permissive:
    - Presidio detects "John" as PERSON with score 0.65 → Masked
    - Presidio detects "john@email.com" as EMAIL with score 0.98 → Masked
  3. Low threshold (0.3) - Very permissive, masks even uncertain matches:
    - Almost everything detected gets masked

  Best practices for setting thresholds:

## presidio_score_thresholds:
```
High-risk PII - use strict thresholds (avoid false positives)
    CREDIT_CARD: 0.95
    US_SSN: 0.95

Medium-risk PII - moderate thresholds
    EMAIL_ADDRESS: 0.85
    PHONE_NUMBER: 0.85

Low-risk PII - lower thresholds (avoid false negatives)
    PERSON: 0.6
    LOCATION: 0.5
```

## Threshold values in this repo

```yaml
presidio_score_thresholds:
        CREDIT_CARD: 0.9
        CRYPTO: 0.9
        DATE_TIME: 0.9
        EMAIL_ADDRESS: 0.9
        IBAN_CODE: 0.9
        IP_ADDRESS: 0.9
        MAC_ADDRESS: 0.9
        NRP: 0.9
        LOCATION: 0.9
        PERSON: 0.9
        PHONE_NUMBER: 0.9
        MEDICAL_LICENSE: 0.9
        URL: 0.9
        US_BANK_NUMBER: 0.9
        US_DRIVER_LICENSE: 0.9
        US_ITIN: 0.9
        US_MBI: 0.9
        US_PASSPORT: 0.9
        US_SSN: 0.9
      pii_entities_config:
        CREDIT_CARD: "MASK"
        CRYPTO: "MASK"
        DATE_TIME: "MASK"
        EMAIL_ADDRESS: "MASK"
        IBAN_CODE: "MASK"
        IP_ADDRESS: "MASK"
        MAC_ADDRESS: "MASK"
        NRP: "MASK"
        LOCATION: "MASK"
        PERSON: "MASK"
        PHONE_NUMBER: "MASK"
        MEDICAL_LICENSE: "MASK"
        URL: "MASK"
        US_BANK_NUMBER: "MASK"
        US_DRIVER_LICENSE: "MASK"
        US_ITIN: "MASK"
        US_MBI: "MASK"
        US_PASSPORT: "MASK"
        US_SSN: "MASK"
```

# Example

## Threshold at 0.1

- input query to the agent:
```
text = """use the databricks_get_categorical_col_statistics tool on:
    - catalog: psfa-demo
    - schema: silver
    - table: supply_chain
    - column: supplier_name"""
```

- agent response:
```
Here are the statistics for the `supplier_name` column in the `supply_chain` table of the `psfa-demo` catalog and `silver` schema:

- L3Harris: 1
- Boeing Defense: 1
- Lockheed Martin: 1
- Northrop Grumman: 1
- Leonardo DRS: 1
- Defense Contractor <US_DRIVER_LICENSE>: 2 (Note: This value appears more than once)
- Raytheon Technologies: 1
- General Dynamics: 1
```

we see 2 wrong masking defense contractor `<US_DRIVER_LICENSE>` : reason defense contractor U4 (real value) has u4 masked as part of a `DRIVER_LICENSE`

### Reason
Running Presidio Detection shows the score and locations

```
================================================================================
1. TESTING PRESIDIO ANALYZER
================================================================================
Original text: 
        - L3Harris: 1 occurrence
        - Boeing Defense: 1 occurrence
        - Lockheed Martin: 1 occurrence
        - Northrop Grumman: 1 occurrence
        - Leonardo DRS: 1 occurrence
        - Defense Contractor L2: 1 occurrence
        - Defense Contractor U4: 1 occurrence
        - Raytheon Technologies: 1 occurrence
        - General Dynamics: 1 occurrence
    

Status: 200

Entities detected: 2
  - US_DRIVER_LICENSE: 'L2' (score: 0.30) - start: 220 - end:222
  - US_DRIVER_LICENSE: 'U4' (score: 0.30) - start: 266 - end:268
```

This is indeed confirmed by running the PII detection only: L2 and U4 have both a low score to be detected as a US_DRIVER_LICENSE

## Threshold at 0.9

- input
```
text = """use the databricks_get_categorical_col_statistics tool on:
    - catalog: psfa-demo
    - schema: silver
    - table: supply_chain
    - column: supplier_name"""
```

- agent response
```
The categorical statistics for the `supplier_name` column in the `psfa-demo.silver.supply_chain` table are as follows:

- L3Harris: 1 occurrence
- Boeing Defense: 1 occurrence
- Lockheed Martin: 1 occurrence
- Northrop Grumman: 1 occurrence
- Leonardo DRS: 1 occurrence
- Defense Contractor L2: 1 occurrence
- Defense Contractor U4: 1 occurrence
- Raytheon Technologies: 1 occurrence
- General Dynamics: 1 occurrence
```

this is a test to commit in the UI
