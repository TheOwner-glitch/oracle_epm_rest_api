# Oracle EPM Cloud REST API Reference (JSON + Markdown)

A machine-readable version of Oracle's EPM Cloud REST API documentation, extracted from the official 1,155-page PDF and structured into JSON and Markdown formats.

Source: [Oracle Fusion Cloud EPM REST APIs](https://docs.oracle.com/en/cloud/saas/enterprise-performance-management-common/prest/index.html) (Document G42939-02, November 2025)

## Why This Exists

Oracle publishes their EPM REST API reference as a PDF. That format works for reading, but falls short for building software, especially when working with AI coding assistants and agentic development tools that need structured context to generate correct API integrations.

This repo provides the same API reference in formats that code and AI tools can actually consume.

## What's Included

```
docs/
├── epm_rest_api_reference.json     # Structured JSON (989 lines, ~33 KB)
├── epm_rest_api_reference.md       # Human-readable Markdown (652 lines, ~18 KB)
└── pdf_full_text_extract.txt       # Raw extracted text (~1.8 MB)

scripts/
└── extract_api_reference.py        # Python extraction script (750 lines)
```

## Coverage

**6 API categories, 34 endpoints, 25 job types**

| Category | Endpoints | Base Path |
|----------|-----------|-----------|
| Planning | 19 | `/HyperionPlanning/rest/{api_version}` |
| Migration | 7 | `/interop/rest/{api_version}` |
| Security | 2 | `/interop/rest/security/{api_version}` |
| User Management | 3 | `/interop/rest/{api_version}` |
| Reporting | 1 | `/HyperionPlanning/rest/{api_version}` |
| Data Management | 2 | `/aif/rest/{api_version}` |

Each endpoint includes: HTTP method, path, description, parameters (name, type, required, description), request/response body schemas, and required roles where applicable.

Also includes: authentication methods (Basic Auth + OAuth 2.0), identity domain derivation rules, job status codes, member functions, and all 25 supported job types.

## Quick Look

```json
{
  "name": "Execute a Job",
  "method": "POST",
  "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/jobs",
  "description": "Executes a job (import data, export data, rules, cube refresh, etc.).",
  "parameters": [
    {"name": "api_version", "type": "path", "required": true},
    {"name": "application", "type": "path", "required": true}
  ],
  "request_body": {
    "jobType": "String - Job type (e.g., EXPORT_DATA, IMPORT_DATA, RULES, CUBE_REFRESH)",
    "jobName": "String - Name of the job",
    "parameters": "Object - Job-specific parameters"
  }
}
```

## Running the Extraction Yourself

If you have the Oracle PDF and want to regenerate the outputs:

```bash
pip install pdfplumber
python scripts/extract_api_reference.py
```

Place `Oracle_EPM_REST_APIs.pdf` in the project root. The script produces all three output files under `docs/`.

## Use Cases

**AI-Assisted Development**: Drop the JSON file into your project so coding assistants have full endpoint context when generating EPM integration code.

**Code Generation**: Parse the JSON to auto-generate API client methods, request/response types, or SDK scaffolding in any language.

**Documentation Sites**: Use the Markdown output as a starting point for internal wikis or developer portals.

**Validation**: Cross-reference your existing EPM integrations against the structured endpoint definitions to catch incorrect paths or missing parameters.

## License

The structured extraction is provided as-is for developer productivity. The original API documentation is the property of Oracle Corporation. Refer to [Oracle's documentation site](https://docs.oracle.com/en/cloud/saas/enterprise-performance-management-common/prest/index.html) for the canonical reference.
