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