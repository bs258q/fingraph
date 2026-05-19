# fingraph-eval Datasets

## Structure
- `synthetic/` — Generated cases with known ground truth. Safe for CI.

## Contributing Cases

Follow the EvalCase schema:
```json
{
  "id": "kyc-NNN",
  "query": "Natural language compliance question",
  "expected": {"ubos": ["expected ubo name"]},
  "agent_type": "kyc",
  "tags": ["ubo"],
  "notes": "Why this expected answer is correct"
}
```

`agent_type` must be one of: `kyc`, `sanctions`, `fraud`, `aml`, `pep`, `adverse_media`, `counterparty`, `contagion`, `filing`

Submit cases via PR. All cases reviewed for correctness before merge.
