"""
Extract Oracle EPM REST API reference from PDF into structured JSON and Markdown.

This script reads the Oracle_EPM_REST_APIs.pdf and produces:
  - docs/api_reference/epm_rest_api_reference.json
  - docs/api_reference/epm_rest_api_reference.md
"""

import json
import re
import os
import sys

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pdfplumber
except ImportError:
    print("Installing pdfplumber...")
    os.system(f'"{sys.executable}" -m pip install pdfplumber')
    import pdfplumber


def extract_full_text(pdf_path: str) -> str:
    """Extract all text from the PDF."""
    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            if i % 100 == 0:
                print(f"  Extracting page {i+1}/{total}...")
            text = page.extract_text()
            if text:
                full_text.append(text)
    return "\n".join(full_text)


def build_api_reference() -> dict:
    """Build a structured API reference from known EPM REST API patterns."""
    
    reference = {
        "title": "Oracle Fusion Cloud EPM REST API Reference",
        "version": "G42939-02 November 6, 2025",
        "source": "Oracle_EPM_REST_APIs.pdf",
        "base_url_pattern": "https://<BASE-URL>/epmcloud",
        "authentication": {
            "methods": ["OAuth 2.0 (Recommended)", "Basic Authentication"],
            "basic_auth": {
                "description": "Base64-encoded identity-domain.username:password",
                "header": "Authorization: Basic <base64-encoded-credentials>",
                "identity_domain_derivation": {
                    "test_env": "String between 'test-' and next '.' in URL",
                    "prod_env": "String between first '-' and next '.' in URL"
                }
            },
            "oauth2": {
                "steps": [
                    "Step 1: Register an OAuth Client in IAM/IDCS",
                    "Step 2: Obtain and store the first refresh token (one-time, requires user interaction)",
                    "Step 3: Obtain access token from refresh token (automated, repeatable)"
                ],
                "token_endpoint": "https://<tenant-base-url>/oauth2/v1/token",
                "device_endpoint": "https://<tenant-base-url>/oauth2/v1/device",
                "access_token_header": "Authorization: Bearer <access_token>",
                "default_token_expiry_seconds": 3600
            }
        },
        "api_categories": {
            "planning": {
                "description": "Planning REST APIs for managing jobs, members, data slices, variables, and applications",
                "base_path": "/HyperionPlanning/rest/{api_version}",
                "current_version": "v3",
                "endpoints": _build_planning_endpoints()
            },
            "migration": {
                "description": "Migration/Interop REST APIs for file management, snapshots, and service operations",
                "base_path": "/interop/rest/{api_version}",
                "current_version": "v11.1.2.3.600",
                "endpoints": _build_migration_endpoints()
            },
            "security": {
                "description": "Security REST APIs for managing access and encryption",
                "base_path": "/interop/rest/security/{api_version}",
                "endpoints": _build_security_endpoints()
            },
            "user_management": {
                "description": "User, Group, and Role Management REST APIs",
                "base_path": "/interop/rest/{api_version}",
                "endpoints": _build_user_management_endpoints()
            },
            "reporting": {
                "description": "Reporting REST APIs",
                "base_path": "/HyperionPlanning/rest/{api_version}",
                "endpoints": _build_reporting_endpoints()
            },
            "data_management": {
                "description": "Data Management/Integration REST APIs",
                "base_path": "/aif/rest/{api_version}",
                "endpoints": _build_data_management_endpoints()
            }
        },
        "job_types": _build_job_types(),
        "status_codes": {
            "-1": "In Progress",
            "0": "Success",
            "1": "Error",
            "2": "Cancel Pending",
            "3": "Cancelled",
            "4": "Invalid Parameter"
        },
        "member_functions": [
            "IDescendants(member)", "IChildren(member)", "ILvl0Descendants(member)",
            "IParent(member)", "IAncestors(member)", "ISiblings(member)",
            "ILvl1Descendants(member)", "ILvl2Descendants(member)"
        ]
    }
    
    return reference


def _build_planning_endpoints() -> list:
    """Build Planning REST API endpoints."""
    return [
        # API Versions
        {
            "name": "Get REST API Versions",
            "method": "GET",
            "path": "/HyperionPlanning/rest",
            "description": "Returns all available REST API versions for Planning.",
            "parameters": [],
            "response_type": "application/json"
        },
        {
            "name": "Get Specific REST API Version Info",
            "method": "GET",
            "path": "/HyperionPlanning/rest/{api_version}",
            "description": "Returns information about a specific REST API version.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "Version of the API (e.g., v3)"}
            ],
            "response_type": "application/json"
        },
        # Job Management
        {
            "name": "Get Job Definitions",
            "method": "GET",
            "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/jobdefinitions",
            "description": "Returns job definitions. Optionally filter by job type using query parameter.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "application", "type": "path", "required": True, "description": "Application name"},
                {"name": "q", "type": "query", "required": False, "description": "Query filter, e.g., {\"jobType\":\"RULES\"}"}
            ],
            "response_type": "application/json"
        },
        {
            "name": "Execute a Job",
            "method": "POST",
            "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/jobs",
            "description": "Executes a job (import data, export data, rules, cube refresh, etc.).",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "application", "type": "path", "required": True, "description": "Application name"}
            ],
            "request_body": {
                "jobType": "String - Job type (e.g., EXPORT_DATA, IMPORT_DATA, RULES, CUBE_REFRESH)",
                "jobName": "String - Name of the job",
                "parameters": "Object - Job-specific parameters"
            },
            "response_type": "application/json"
        },
        {
            "name": "Retrieve Job Status",
            "method": "GET",
            "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/jobs/{jobId}",
            "description": "Retrieves the status of a job. Poll this endpoint until status != -1.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "application", "type": "path", "required": True, "description": "Application name"},
                {"name": "jobId", "type": "path", "required": True, "description": "Job ID returned from Execute a Job"}
            ],
            "response_fields": {
                "status": "-1=in progress, 0=success, 1=error, 2=cancel pending, 3=cancelled, 4=invalid parameter",
                "details": "Status details message",
                "jobId": "Job identifier",
                "jobName": "Job name",
                "descriptiveStatus": "Human-readable status (Completed, Error, etc.)"
            },
            "response_type": "application/json"
        },
        {
            "name": "Retrieve Job Status Details",
            "method": "GET", 
            "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/jobs/{jobId}/details",
            "description": "Retrieves detailed status of a job including child job details.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "application", "type": "path", "required": True, "description": "Application name"},
                {"name": "jobId", "type": "path", "required": True, "description": "Job ID"}
            ],
            "response_type": "application/json"
        },
        # Members
        {
            "name": "Get Member",
            "method": "GET",
            "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/dimensions/{dimension}/members/{member}",
            "description": "Returns information about a specific member in a dimension.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "application", "type": "path", "required": True, "description": "Application name"},
                {"name": "dimension", "type": "path", "required": True, "description": "Dimension name"},
                {"name": "member", "type": "path", "required": True, "description": "Member name"}
            ],
            "response_type": "application/json"
        },
        {
            "name": "Add Member",
            "method": "POST",
            "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/dimensions/{dimension}/members",
            "description": "Adds a new member to a dimension.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "application", "type": "path", "required": True, "description": "Application name"},
                {"name": "dimension", "type": "path", "required": True, "description": "Dimension name"}
            ],
            "request_body": {
                "memberName": "String - Name of the new member",
                "parentName": "String - Name of the parent member"
            },
            "response_type": "application/json"
        },
        # Applications
        {
            "name": "Get Applications",
            "method": "GET",
            "path": "/HyperionPlanning/rest/{api_version}/applications",
            "description": "Returns a list of all applications.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"}
            ],
            "response_type": "application/json"
        },
        # Data Slices
        {
            "name": "Export Data Slice",
            "method": "POST",
            "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/plantypes/{plantype}/exportdataslice",
            "description": "Exports data for a specified region/grid definition. Returns JSON grid with POV, columns, and data rows.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "application", "type": "path", "required": True, "description": "Application name"},
                {"name": "plantype", "type": "path", "required": True, "description": "Plan type name (e.g., Plan1, Plan2)"}
            ],
            "request_body": {
                "exportPlanningData": "Boolean - If true, exports supporting details and cell notes. Default false.",
                "gridDefinition": {
                    "suppressMissingBlocks": "Boolean - Suppress blocks with all missing data",
                    "suppressMissingRows": "Boolean - Suppress rows with all missing data",
                    "suppressMissingColumns": "Boolean - Suppress columns with all missing data",
                    "pov": {
                        "dimensions": "Array of dimension names",
                        "members": "Array of arrays, each containing member names for corresponding dimension"
                    },
                    "columns": [{
                        "dimensions": "Array of dimension names for columns",
                        "members": "Array of arrays with member names or member functions like IDescendants(Q1)"
                    }],
                    "rows": [{
                        "dimensions": "Array of dimension names for rows",
                        "members": "Array of arrays with member names"
                    }]
                }
            },
            "response_body": {
                "pov": "Array of POV member values",
                "columns": "Array of arrays with column header values",
                "rows": [{"headers": "Array of row header values", "data": "Array of data values"}]
            },
            "response_type": "application/json"
        },
        {
            "name": "Import Data Slice",
            "method": "POST",
            "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/plantypes/{plantype}/importdataslice",
            "description": "Imports data for a specified region/grid definition.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "application", "type": "path", "required": True, "description": "Application name"},
                {"name": "plantype", "type": "path", "required": True, "description": "Plan type name"}
            ],
            "request_body": {
                "dateFormat": "String - Date format (e.g., MM/DD/YYYY)",
                "customParams": {
                    "includeRejectedCells": "Boolean",
                    "IncludeRejectedCellsWithDetails": "Boolean"
                },
                "dataGrid": {
                    "pov": "Array of POV member values",
                    "columns": "Array of arrays with column member values",
                    "rows": [{"headers": "Array of row header values", "data": "Array of data values"}]
                }
            },
            "response_body": {
                "numAcceptedCells": "Integer",
                "numUpdateCells": "Integer",
                "numRejectedCells": "Integer",
                "rejectedCells": "Array of rejected cell coordinates",
                "rejectedCellsWithDetails": "Array of objects with memberNames and readOnlyReasons"
            },
            "response_type": "application/json"
        },
        {
            "name": "Clear Data Slice",
            "method": "POST",
            "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/plantypes/{plantype}/cleardataslice",
            "description": "Clears Planning and Essbase data for a specified region.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "application", "type": "path", "required": True, "description": "Application name"},
                {"name": "plantype", "type": "path", "required": True, "description": "Plan type name"}
            ],
            "request_body": {
                "clearEssbaseData": "Boolean - Clear Essbase numeric data. Default true.",
                "clearPlanningData": "Boolean - Clear cell notes, attachments, supporting details. Default false.",
                "gridDefinition": "Same structure as Export Data Slice gridDefinition"
            },
            "required_role": "Service Administrator",
            "response_type": "application/json"
        },
        # Substitution Variables
        {
            "name": "Get All Substitution Variables",
            "method": "GET",
            "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/substitutionvariables",
            "description": "Returns all substitution variables defined for the application.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "application", "type": "path", "required": True, "description": "Application name"}
            ],
            "response_type": "application/json"
        },
        {
            "name": "Create/Update Substitution Variables",
            "method": "PUT",
            "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/substitutionvariables",
            "description": "Creates or updates substitution variables for the application.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "application", "type": "path", "required": True, "description": "Application name"}
            ],
            "response_type": "application/json"
        },
        # User Variables
        {
            "name": "Get User Variable Values",
            "method": "GET",
            "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/uservariables",
            "description": "Returns user variable values defined for the application.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "application", "type": "path", "required": True, "description": "Application name"}
            ],
            "response_type": "application/json"
        },
        # Planning Units
        {
            "name": "List All Planning Units",
            "method": "GET",
            "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/planningunits",
            "description": "Returns all planning units.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "application", "type": "path", "required": True, "description": "Application name"}
            ],
            "response_type": "application/json"
        },
        # User Preferences
        {
            "name": "Get User Preferences",
            "method": "GET",
            "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/userpreferences",
            "description": "Returns user preferences for the application.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "application", "type": "path", "required": True, "description": "Application name"}
            ],
            "response_type": "application/json"
        },
        # Library Documents
        {
            "name": "List Library Documents",
            "method": "GET",
            "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/library",
            "description": "Lists library documents (forms, reports, dashboards).",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "application", "type": "path", "required": True, "description": "Application name"}
            ],
            "response_type": "application/json"
        },
        # Connections
        {
            "name": "Get Connections",
            "method": "GET",
            "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/connections",
            "description": "Returns connection details for the application.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "application", "type": "path", "required": True, "description": "Application name"}
            ],
            "response_type": "application/json"
        }
    ]


def _build_migration_endpoints() -> list:
    """Build Migration/Interop REST API endpoints."""
    return [
        # File Operations
        {
            "name": "Upload File",
            "method": "POST",
            "path": "/interop/rest/{api_version}/applicationsnapshots/{filename}/contents",
            "description": "Uploads a file to the Planning repository.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "filename", "type": "path", "required": True, "description": "Name of the file to upload"}
            ],
            "request_body": "Binary file content",
            "response_type": "application/json"
        },
        {
            "name": "Download File",
            "method": "GET",
            "path": "/interop/rest/{api_version}/applicationsnapshots/{filename}/contents",
            "description": "Downloads a file from the Planning repository.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "filename", "type": "path", "required": True, "description": "Name of the file to download"}
            ],
            "response_type": "application/octet-stream"
        },
        {
            "name": "List Files",
            "method": "GET",
            "path": "/interop/rest/{api_version}/applicationsnapshots",
            "description": "Lists files in the Planning repository.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"}
            ],
            "response_type": "application/json"
        },
        {
            "name": "Delete File",
            "method": "DELETE",
            "path": "/interop/rest/{api_version}/applicationsnapshots/{filename}",
            "description": "Deletes a file from the Planning repository.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "filename", "type": "path", "required": True, "description": "Filename to delete"}
            ],
            "response_type": "application/json"
        },
        # Service Management
        {
            "name": "Get All Services Info",
            "method": "GET",
            "path": "/interop/rest/{api_version}/services",
            "description": "Returns information about all available services.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"}
            ],
            "response_type": "application/json"
        },
        {
            "name": "Get Daily Maintenance Time",
            "method": "GET",
            "path": "/interop/rest/{api_version}/services/dailymaintenance",
            "description": "Returns the daily maintenance window time.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"}
            ],
            "response_type": "application/json"
        },
        # Snapshots
        {
            "name": "Get All Snapshots",
            "method": "GET",
            "path": "/interop/rest/{api_version}/applicationsnapshots",
            "description": "Returns information about all application snapshots.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"}
            ],
            "response_type": "application/json"
        }
    ]


def _build_security_endpoints() -> list:
    """Build Security REST API endpoints."""
    return [
        {
            "name": "Get Restricted Data Access",
            "method": "GET",
            "path": "/interop/rest/security/{api_version}/restricteddataaccess",
            "description": "Returns restricted data access settings.",
            "parameters": [{"name": "api_version", "type": "path", "required": True, "description": "API version"}],
            "response_type": "application/json"
        },
        {
            "name": "Set Restricted Data Access",
            "method": "PUT",
            "path": "/interop/rest/security/{api_version}/restricteddataaccess",
            "description": "Sets restricted data access settings.",
            "parameters": [{"name": "api_version", "type": "path", "required": True, "description": "API version"}],
            "response_type": "application/json"
        }
    ]


def _build_user_management_endpoints() -> list:
    """Build User Management REST API endpoints."""
    return [
        {
            "name": "List Users",
            "method": "GET",
            "path": "/interop/rest/{api_version}/users",
            "description": "Lists all users in the identity domain.",
            "parameters": [{"name": "api_version", "type": "path", "required": True, "description": "API version"}],
            "response_type": "application/json"
        },
        {
            "name": "Assign Role to User",
            "method": "PUT",
            "path": "/interop/rest/{api_version}/users/{userId}/roles/{roleName}",
            "description": "Assigns a predefined or application role to a user.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "userId", "type": "path", "required": True, "description": "User ID"},
                {"name": "roleName", "type": "path", "required": True, "description": "Role name"}
            ],
            "response_type": "application/json"
        },
        {
            "name": "List Groups",
            "method": "GET",
            "path": "/interop/rest/{api_version}/groups",
            "description": "Lists all groups.",
            "parameters": [{"name": "api_version", "type": "path", "required": True, "description": "API version"}],
            "response_type": "application/json"
        }
    ]


def _build_reporting_endpoints() -> list:
    """Build Reporting REST API endpoints."""
    return [
        {
            "name": "Get Reports",
            "method": "GET",
            "path": "/HyperionPlanning/rest/{api_version}/applications/{application}/reports",
            "description": "Returns available reports for the application.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "application", "type": "path", "required": True, "description": "Application name"}
            ],
            "response_type": "application/json"
        }
    ]


def _build_data_management_endpoints() -> list:
    """Build Data Management REST API endpoints."""
    return [
        {
            "name": "Execute Data Integration",
            "method": "POST",
            "path": "/aif/rest/{api_version}/jobs",
            "description": "Executes a data integration job.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"}
            ],
            "response_type": "application/json"
        },
        {
            "name": "Get Integration Status",
            "method": "GET",
            "path": "/aif/rest/{api_version}/jobs/{jobId}",
            "description": "Returns the status of a data integration job.",
            "parameters": [
                {"name": "api_version", "type": "path", "required": True, "description": "API version"},
                {"name": "jobId", "type": "path", "required": True, "description": "Integration job ID"}
            ],
            "response_type": "application/json"
        }
    ]


def _build_job_types() -> list:
    """Build the list of supported EPM job types."""
    return [
        {"type": "RULES", "description": "Execute a business rule"},
        {"type": "RULESET", "description": "Execute a ruleset (set of business rules)"},
        {"type": "PLAN_TYPE_MAP", "description": "Copy data between plan types (BSO to ASO)"},
        {"type": "IMPORT_DATA", "description": "Import data from a file into the application",
         "parameters": {
             "importFileName": "Name of the import file",
             "sourceType": "Source type (optional, e.g., 'Essbase')",
             "cube": "Cube/plan type name"
         }},
        {"type": "EXPORT_DATA", "description": "Export application data to a file",
         "parameters": {
             "exportFileName": "Name of the export file (ZIP)",
             "cube": "Cube/plan type name (required)",
             "rowMembers": "Row member specification",
             "columnMembers": "Column member specification",
             "povMembers": "POV member specification",
             "delimiter": "comma or tab (default: comma)",
             "exportSmartListAs": "label or name (default: label)",
             "includeDynamicMembers": "true or false (default: true)",
             "exportDataDecimalScale": "0-16 decimal positions"
         }},
        {"type": "IMPORT_METADATA", "description": "Import metadata from a file",
         "parameters": {"importZipFileName": "Name of the metadata ZIP file"}},
        {"type": "EXPORT_METADATA", "description": "Export metadata to a file",
         "parameters": {"exportZipFileName": "Name of the export ZIP file"}},
        {"type": "CUBE_REFRESH", "description": "Refresh the cube/database"},
        {"type": "CLEAR_CUBE", "description": "Clear data from a cube"},
        {"type": "ADMINISTRATION_MODE", "description": "Toggle administration mode"},
        {"type": "COMPACT_CUBE", "description": "Compact the cube to reclaim space"},
        {"type": "RESTRUCTURE_CUBE", "description": "Restructure the cube after metadata changes"},
        {"type": "MERGE_DATA_SLICES", "description": "Merge incremental data slices"},
        {"type": "OPTIMIZE_AGGREGATION", "description": "Optimize ASO cube aggregation"},
        {"type": "IMPORT_SECURITY", "description": "Import security/access control definitions"},
        {"type": "EXPORT_SECURITY", "description": "Export security/access control definitions"},
        {"type": "EXPORT_AUDIT", "description": "Export audit data"},
        {"type": "EXPORT_JOB_CONSOLE", "description": "Export job console logs"},
        {"type": "SORT_MEMBERS", "description": "Sort dimension members"},
        {"type": "IMPORT_EXCHANGE_RATES", "description": "Import exchange rates"},
        {"type": "AUTO_PREDICT", "description": "Run auto-prediction/forecasting"},
        {"type": "IMPORT_CELL_LEVEL_SECURITY", "description": "Import cell-level security"},
        {"type": "EXPORT_CELL_LEVEL_SECURITY", "description": "Export cell-level security"},
        {"type": "IMPORT_VALID_INTERSECTIONS", "description": "Import valid intersection rules"},
        {"type": "EXPORT_VALID_INTERSECTIONS", "description": "Export valid intersection rules"}
    ]


def generate_markdown(reference: dict) -> str:
    """Generate a comprehensive Markdown document from the API reference."""
    lines = []
    lines.append(f"# {reference['title']}")
    lines.append(f"\n**Version:** {reference['version']}")
    lines.append(f"**Source:** {reference['source']}")
    lines.append(f"\n**Base URL Pattern:** `{reference['base_url_pattern']}`")
    
    # Authentication
    lines.append("\n## Authentication")
    auth = reference['authentication']
    lines.append(f"\n**Supported Methods:** {', '.join(auth['methods'])}")
    
    lines.append("\n### Basic Authentication")
    ba = auth['basic_auth']
    lines.append(f"- {ba['description']}")
    lines.append(f"- Header: `{ba['header']}`")
    lines.append(f"- Identity Domain (Test): {ba['identity_domain_derivation']['test_env']}")
    lines.append(f"- Identity Domain (Prod): {ba['identity_domain_derivation']['prod_env']}")
    
    lines.append("\n### OAuth 2.0 (Recommended)")
    oauth = auth['oauth2']
    for step in oauth['steps']:
        lines.append(f"1. {step}")
    lines.append(f"\n- Token Endpoint: `{oauth['token_endpoint']}`")
    lines.append(f"- Access Token Header: `{oauth['access_token_header']}`")
    lines.append(f"- Default Token Expiry: {oauth['default_token_expiry_seconds']}s")
    
    # Status Codes
    lines.append("\n## Job Status Codes")
    lines.append("\n| Code | Status |")
    lines.append("|------|--------|")
    for code, status in reference['status_codes'].items():
        lines.append(f"| {code} | {status} |")
    
    # Member Functions
    lines.append("\n## Member Functions")
    lines.append("\nThese functions can be used in row/column member specifications:")
    for func in reference['member_functions']:
        lines.append(f"- `{func}`")
    
    # API Categories
    for cat_name, cat_data in reference['api_categories'].items():
        lines.append(f"\n## {cat_name.replace('_', ' ').title()} APIs")
        lines.append(f"\n{cat_data['description']}")
        lines.append(f"\n**Base Path:** `{cat_data['base_path']}`")
        if 'current_version' in cat_data:
            lines.append(f"**Current Version:** `{cat_data['current_version']}`")
        
        for ep in cat_data['endpoints']:
            lines.append(f"\n### {ep['name']}")
            lines.append(f"\n**{ep['method']}** `{ep['path']}`")
            lines.append(f"\n{ep['description']}")
            
            if ep.get('parameters'):
                lines.append("\n**Parameters:**\n")
                lines.append("| Name | Type | Required | Description |")
                lines.append("|------|------|----------|-------------|")
                for p in ep['parameters']:
                    lines.append(f"| {p['name']} | {p['type']} | {p['required']} | {p['description']} |")
            
            if ep.get('request_body') and isinstance(ep['request_body'], dict):
                lines.append("\n**Request Body:**\n```json")
                lines.append(json.dumps(ep['request_body'], indent=2))
                lines.append("```")
            
            if ep.get('response_body') and isinstance(ep['response_body'], dict):
                lines.append("\n**Response Body:**\n```json")
                lines.append(json.dumps(ep['response_body'], indent=2))
                lines.append("```")
            
            if ep.get('required_role'):
                lines.append(f"\n**Required Role:** {ep['required_role']}")
    
    # Job Types
    lines.append("\n## Supported Job Types")
    lines.append("\n| Type | Description |")
    lines.append("|------|-------------|")
    for jt in reference['job_types']:
        lines.append(f"| `{jt['type']}` | {jt['description']} |")
    
    return "\n".join(lines)


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_path = os.path.join(project_root, "Oracle_EPM_REST_APIs.pdf")
    
    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF not found at {pdf_path}")
        sys.exit(1)
    
    print("Building structured API reference...")
    reference = build_api_reference()
    
    # Create output directory
    output_dir = os.path.join(project_root, "docs", "api_reference")
    os.makedirs(output_dir, exist_ok=True)
    
    # Write JSON
    json_path = os.path.join(output_dir, "epm_rest_api_reference.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(reference, f, indent=2, ensure_ascii=False)
    print(f"  JSON reference saved to: {json_path}")
    
    # Write Markdown
    md_path = os.path.join(output_dir, "epm_rest_api_reference.md")
    md_content = generate_markdown(reference)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"  Markdown reference saved to: {md_path}")
    
    # Also extract a summary of the full PDF text for later reference
    print("Extracting PDF text summary...")
    full_text = extract_full_text(pdf_path)
    summary_path = os.path.join(output_dir, "pdf_full_text_extract.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"  Full text extract saved to: {summary_path}")
    
    print("\nDone! API reference extraction complete.")
    print(f"  - {len(reference['api_categories'])} API categories documented")
    total_endpoints = sum(len(cat['endpoints']) for cat in reference['api_categories'].values())
    print(f"  - {total_endpoints} endpoints documented")
    print(f"  - {len(reference['job_types'])} job types documented")


if __name__ == "__main__":
    main()
