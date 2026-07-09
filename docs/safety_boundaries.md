# Safety and Environment Boundaries

## Secrets

Local secrets must be stored in `.env`.

The `.env` file must never be committed to git.

Use `.env.example` to document required environment variables without exposing secrets.

## Public data only

This repo uses publicly available biomedical sources only.

For Build 1, the allowed data sources are:

- DailyMed
- RxNorm / RxNav
- PubMed / NCBI E-utilities

The project must not use:

- private patient data
- EHR exports
- proprietary pharma data
- commercial drug databases
- confidential company information

## Medical safety boundary

This project is for educational and technical purposes only.

It must not provide:

- medical advice
- diagnosis
- treatment recommendations
- drug dosing guidance
- personal medication decisions
- patient-specific interaction advice
