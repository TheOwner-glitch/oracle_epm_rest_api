# Oracle Fusion Cloud EPM REST API Reference

**Version:** G42939-02 November 6, 2025
**Source:** Oracle_EPM_REST_APIs.pdf

**Base URL Pattern:** `https://<BASE-URL>/epmcloud`

## Authentication

**Supported Methods:** OAuth 2.0 (Recommended), Basic Authentication

### Basic Authentication
- Base64-encoded identity-domain.username:password
- Header: `Authorization: Basic <base64-encoded-credentials>`
- Identity Domain (Test): String between 'test-' and next '.' in URL
- Identity Domain (Prod): String between first '-' and next '.' in URL

### OAuth 2.0 (Recommended)
1. Step 1: Register an OAuth Client in IAM/IDCS
1. Step 2: Obtain and store the first refresh token (one-time, requires user interaction)
1. Step 3: Obtain access token from refresh token (automated, repeatable)

- Token Endpoint: `https://<tenant-base-url>/oauth2/v1/token`
- Access Token Header: `Authorization: Bearer <access_token>`
- Default Token Expiry: 3600s

## Job Status Codes

| Code | Status |
|------|--------|
| -1 | In Progress |
| 0 | Success |
| 1 | Error |
| 2 | Cancel Pending |
| 3 | Cancelled |
| 4 | Invalid Parameter |

## Member Functions

These functions can be used in row/column member specifications:
- `IDescendants(member)`
- `IChildren(member)`
- `ILvl0Descendants(member)`
- `IParent(member)`
- `IAncestors(member)`
- `ISiblings(member)`
- `ILvl1Descendants(member)`
- `ILvl2Descendants(member)`

## Planning APIs

Planning REST APIs for managing jobs, members, data slices, variables, and applications

**Base Path:** `/HyperionPlanning/rest/{api_version}`
**Current Version:** `v3`

### Get REST API Versions

**GET** `/HyperionPlanning/rest`

Returns all available REST API versions for Planning.

### Get Specific REST API Version Info

**GET** `/HyperionPlanning/rest/{api_version}`

Returns information about a specific REST API version.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | Version of the API (e.g., v3) |

### Get Job Definitions

**GET** `/HyperionPlanning/rest/{api_version}/applications/{application}/jobdefinitions`

Returns job definitions. Optionally filter by job type using query parameter.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| application | path | True | Application name |
| q | query | False | Query filter, e.g., {"jobType":"RULES"} |

### Execute a Job

**POST** `/HyperionPlanning/rest/{api_version}/applications/{application}/jobs`

Executes a job (import data, export data, rules, cube refresh, etc.).

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| application | path | True | Application name |

**Request Body:**
```json
{
  "jobType": "String - Job type (e.g., EXPORT_DATA, IMPORT_DATA, RULES, CUBE_REFRESH)",
  "jobName": "String - Name of the job",
  "parameters": "Object - Job-specific parameters"
}
```

### Retrieve Job Status

**GET** `/HyperionPlanning/rest/{api_version}/applications/{application}/jobs/{jobId}`

Retrieves the status of a job. Poll this endpoint until status != -1.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| application | path | True | Application name |
| jobId | path | True | Job ID returned from Execute a Job |

### Retrieve Job Status Details

**GET** `/HyperionPlanning/rest/{api_version}/applications/{application}/jobs/{jobId}/details`

Retrieves detailed status of a job including child job details.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| application | path | True | Application name |
| jobId | path | True | Job ID |

### Get Member

**GET** `/HyperionPlanning/rest/{api_version}/applications/{application}/dimensions/{dimension}/members/{member}`

Returns information about a specific member in a dimension.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| application | path | True | Application name |
| dimension | path | True | Dimension name |
| member | path | True | Member name |

### Add Member

**POST** `/HyperionPlanning/rest/{api_version}/applications/{application}/dimensions/{dimension}/members`

Adds a new member to a dimension.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| application | path | True | Application name |
| dimension | path | True | Dimension name |

**Request Body:**
```json
{
  "memberName": "String - Name of the new member",
  "parentName": "String - Name of the parent member"
}
```

### Get Applications

**GET** `/HyperionPlanning/rest/{api_version}/applications`

Returns a list of all applications.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |

### Export Data Slice

**POST** `/HyperionPlanning/rest/{api_version}/applications/{application}/plantypes/{plantype}/exportdataslice`

Exports data for a specified region/grid definition. Returns JSON grid with POV, columns, and data rows.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| application | path | True | Application name |
| plantype | path | True | Plan type name (e.g., Plan1, Plan2) |

**Request Body:**
```json
{
  "exportPlanningData": "Boolean - If true, exports supporting details and cell notes. Default false.",
  "gridDefinition": {
    "suppressMissingBlocks": "Boolean - Suppress blocks with all missing data",
    "suppressMissingRows": "Boolean - Suppress rows with all missing data",
    "suppressMissingColumns": "Boolean - Suppress columns with all missing data",
    "pov": {
      "dimensions": "Array of dimension names",
      "members": "Array of arrays, each containing member names for corresponding dimension"
    },
    "columns": [
      {
        "dimensions": "Array of dimension names for columns",
        "members": "Array of arrays with member names or member functions like IDescendants(Q1)"
      }
    ],
    "rows": [
      {
        "dimensions": "Array of dimension names for rows",
        "members": "Array of arrays with member names"
      }
    ]
  }
}
```

**Response Body:**
```json
{
  "pov": "Array of POV member values",
  "columns": "Array of arrays with column header values",
  "rows": [
    {
      "headers": "Array of row header values",
      "data": "Array of data values"
    }
  ]
}
```

### Import Data Slice

**POST** `/HyperionPlanning/rest/{api_version}/applications/{application}/plantypes/{plantype}/importdataslice`

Imports data for a specified region/grid definition.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| application | path | True | Application name |
| plantype | path | True | Plan type name |

**Request Body:**
```json
{
  "dateFormat": "String - Date format (e.g., MM/DD/YYYY)",
  "customParams": {
    "includeRejectedCells": "Boolean",
    "IncludeRejectedCellsWithDetails": "Boolean"
  },
  "dataGrid": {
    "pov": "Array of POV member values",
    "columns": "Array of arrays with column member values",
    "rows": [
      {
        "headers": "Array of row header values",
        "data": "Array of data values"
      }
    ]
  }
}
```

**Response Body:**
```json
{
  "numAcceptedCells": "Integer",
  "numUpdateCells": "Integer",
  "numRejectedCells": "Integer",
  "rejectedCells": "Array of rejected cell coordinates",
  "rejectedCellsWithDetails": "Array of objects with memberNames and readOnlyReasons"
}
```

### Clear Data Slice

**POST** `/HyperionPlanning/rest/{api_version}/applications/{application}/plantypes/{plantype}/cleardataslice`

Clears Planning and Essbase data for a specified region.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| application | path | True | Application name |
| plantype | path | True | Plan type name |

**Request Body:**
```json
{
  "clearEssbaseData": "Boolean - Clear Essbase numeric data. Default true.",
  "clearPlanningData": "Boolean - Clear cell notes, attachments, supporting details. Default false.",
  "gridDefinition": "Same structure as Export Data Slice gridDefinition"
}
```

**Required Role:** Service Administrator

### Get All Substitution Variables

**GET** `/HyperionPlanning/rest/{api_version}/applications/{application}/substitutionvariables`

Returns all substitution variables defined for the application.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| application | path | True | Application name |

### Create/Update Substitution Variables

**PUT** `/HyperionPlanning/rest/{api_version}/applications/{application}/substitutionvariables`

Creates or updates substitution variables for the application.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| application | path | True | Application name |

### Get User Variable Values

**GET** `/HyperionPlanning/rest/{api_version}/applications/{application}/uservariables`

Returns user variable values defined for the application.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| application | path | True | Application name |

### List All Planning Units

**GET** `/HyperionPlanning/rest/{api_version}/applications/{application}/planningunits`

Returns all planning units.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| application | path | True | Application name |

### Get User Preferences

**GET** `/HyperionPlanning/rest/{api_version}/applications/{application}/userpreferences`

Returns user preferences for the application.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| application | path | True | Application name |

### List Library Documents

**GET** `/HyperionPlanning/rest/{api_version}/applications/{application}/library`

Lists library documents (forms, reports, dashboards).

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| application | path | True | Application name |

### Get Connections

**GET** `/HyperionPlanning/rest/{api_version}/applications/{application}/connections`

Returns connection details for the application.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| application | path | True | Application name |

## Migration APIs

Migration/Interop REST APIs for file management, snapshots, and service operations

**Base Path:** `/interop/rest/{api_version}`
**Current Version:** `v11.1.2.3.600`

### Upload File

**POST** `/interop/rest/{api_version}/applicationsnapshots/{filename}/contents`

Uploads a file to the Planning repository.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| filename | path | True | Name of the file to upload |

### Download File

**GET** `/interop/rest/{api_version}/applicationsnapshots/{filename}/contents`

Downloads a file from the Planning repository.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| filename | path | True | Name of the file to download |

### List Files

**GET** `/interop/rest/{api_version}/applicationsnapshots`

Lists files in the Planning repository.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |

### Delete File

**DELETE** `/interop/rest/{api_version}/applicationsnapshots/{filename}`

Deletes a file from the Planning repository.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| filename | path | True | Filename to delete |

### Get All Services Info

**GET** `/interop/rest/{api_version}/services`

Returns information about all available services.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |

### Get Daily Maintenance Time

**GET** `/interop/rest/{api_version}/services/dailymaintenance`

Returns the daily maintenance window time.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |

### Get All Snapshots

**GET** `/interop/rest/{api_version}/applicationsnapshots`

Returns information about all application snapshots.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |

## Security APIs

Security REST APIs for managing access and encryption

**Base Path:** `/interop/rest/security/{api_version}`

### Get Restricted Data Access

**GET** `/interop/rest/security/{api_version}/restricteddataaccess`

Returns restricted data access settings.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |

### Set Restricted Data Access

**PUT** `/interop/rest/security/{api_version}/restricteddataaccess`

Sets restricted data access settings.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |

## User Management APIs

User, Group, and Role Management REST APIs

**Base Path:** `/interop/rest/{api_version}`

### List Users

**GET** `/interop/rest/{api_version}/users`

Lists all users in the identity domain.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |

### Assign Role to User

**PUT** `/interop/rest/{api_version}/users/{userId}/roles/{roleName}`

Assigns a predefined or application role to a user.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| userId | path | True | User ID |
| roleName | path | True | Role name |

### List Groups

**GET** `/interop/rest/{api_version}/groups`

Lists all groups.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |

## Reporting APIs

Reporting REST APIs

**Base Path:** `/HyperionPlanning/rest/{api_version}`

### Get Reports

**GET** `/HyperionPlanning/rest/{api_version}/applications/{application}/reports`

Returns available reports for the application.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| application | path | True | Application name |

## Data Management APIs

Data Management/Integration REST APIs

**Base Path:** `/aif/rest/{api_version}`

### Execute Data Integration

**POST** `/aif/rest/{api_version}/jobs`

Executes a data integration job.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |

### Get Integration Status

**GET** `/aif/rest/{api_version}/jobs/{jobId}`

Returns the status of a data integration job.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| api_version | path | True | API version |
| jobId | path | True | Integration job ID |

## Supported Job Types

| Type | Description |
|------|-------------|
| `RULES` | Execute a business rule |
| `RULESET` | Execute a ruleset (set of business rules) |
| `PLAN_TYPE_MAP` | Copy data between plan types (BSO to ASO) |
| `IMPORT_DATA` | Import data from a file into the application |
| `EXPORT_DATA` | Export application data to a file |
| `IMPORT_METADATA` | Import metadata from a file |
| `EXPORT_METADATA` | Export metadata to a file |
| `CUBE_REFRESH` | Refresh the cube/database |
| `CLEAR_CUBE` | Clear data from a cube |
| `ADMINISTRATION_MODE` | Toggle administration mode |
| `COMPACT_CUBE` | Compact the cube to reclaim space |
| `RESTRUCTURE_CUBE` | Restructure the cube after metadata changes |
| `MERGE_DATA_SLICES` | Merge incremental data slices |
| `OPTIMIZE_AGGREGATION` | Optimize ASO cube aggregation |
| `IMPORT_SECURITY` | Import security/access control definitions |
| `EXPORT_SECURITY` | Export security/access control definitions |
| `EXPORT_AUDIT` | Export audit data |
| `EXPORT_JOB_CONSOLE` | Export job console logs |
| `SORT_MEMBERS` | Sort dimension members |
| `IMPORT_EXCHANGE_RATES` | Import exchange rates |
| `AUTO_PREDICT` | Run auto-prediction/forecasting |
| `IMPORT_CELL_LEVEL_SECURITY` | Import cell-level security |
| `EXPORT_CELL_LEVEL_SECURITY` | Export cell-level security |
| `IMPORT_VALID_INTERSECTIONS` | Import valid intersection rules |
| `EXPORT_VALID_INTERSECTIONS` | Export valid intersection rules |
