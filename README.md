# Semantic Layer Builder

Semantic Layer Builder is a Python application that analyzes technical metadata and business documentation, validates data relationships, builds a structured semantic model, and generates validated LookML projects.

The project combines a deterministic data-processing pipeline, a multi-agent architecture based on Google Agent Development Kit, and a FastAPI interface.

## Project Goals

The project was created to explore how AI agents and deterministic validation tools can collaborate to automate the construction of reliable semantic layers.

The main objectives are:

- analyze CSV metadata;
- extract business definitions from documentation;
- compare technical data with documented rules;
- validate primary keys and relationships;
- detect orphan foreign keys;
- determine table cardinalities;
- build an intermediate semantic model;
- generate LookML views and models;
- validate generated LookML locally;
- expose the pipeline through a REST API;
- preserve human review for sensitive or ambiguous decisions.

## Main Features

### Metadata Analysis

The metadata pipeline can:

- inspect CSV files;
- identify columns and semantic types;
- count null and unique values;
- calculate data-quality indicators;
- identify primary-key candidates;
- distinguish technical candidates from confirmed business keys.

### Business Documentation Analysis

The documentation pipeline can:

- read Markdown and TXT documents;
- extract table descriptions;
- extract column definitions;
- identify documented primary keys;
- extract business rules;
- detect documented relationships;
- identify sensitive fields;
- report missing information.

### Consistency Analysis

The consistency engine compares technical observations with business documentation.

It validates:

- table names;
- column presence;
- semantic types;
- required fields;
- uniqueness constraints;
- primary keys;
- verifiable business rules.

The engine distinguishes between:

- confirmed consistency;
- real inconsistencies;
- warnings;
- elements that cannot be verified from a static dataset.

### Relationship Validation

The relationship engine validates foreign-key relationships between tables.

It checks:

- join-column existence;
- type compatibility;
- null foreign keys;
- orphan foreign keys;
- foreign-key match ratio;
- source and target uniqueness;
- detected cardinality;
- consistency with documented cardinality.

The demonstration dataset validates:

```text
ORDERS.CLIENT_ID -> CLIENTS.CLIENT_ID
```

with the following relationship:

```text
many-to-one
```

### Semantic Model Construction

The project builds a structured intermediate representation before generating LookML.

The semantic model contains:

- views;
- dimensions;
- primary keys;
- measures;
- joins;
- sensitive fields;
- documented business rules;
- validation statuses;
- warnings and recommendations.

This intermediate layer separates source analysis from code generation.

### LookML Generation

The LookML pipeline generates:

```text
clients.view.lkml
orders.view.lkml
sales.model.lkml
```

The generated project includes:

- physical table declarations;
- dimensions;
- validated primary keys;
- count measures;
- proposed numeric measures;
- Explores;
- validated joins;
- warnings for sensitive fields and automatically proposed measures.

### Local LookML Validation

Before writing files, the local validator checks:

- balanced braces;
- view declarations;
- file and view-name consistency;
- duplicate dimensions;
- duplicate measures;
- primary-key declarations;
- local field references;
- model connection;
- includes;
- Explores;
- joined views;
- referenced views.

Invalid artifacts are not written to disk.

### Secure File Writing

The writer:

- restricts output to an authorized root directory;
- rejects path traversal;
- validates `.view.lkml` and `.model.lkml` extensions;
- rejects duplicate file names;
- refuses overwriting by default;
- supports explicit overwriting;
- writes UTF-8 files atomically.

## Multi-Agent Architecture

The project contains a Supervisor Agent and six specialized agents:

```text
semantic_layer_supervisor
├── metadata_agent
├── documentation_agent
├── consistency_agent
├── relationship_agent
├── semantic_model_agent
└── lookml_generator_agent
```

### Metadata Agent

Analyzes one CSV file and extracts technical metadata.

### Documentation Agent

Analyzes one Markdown or TXT business document.

### Consistency Agent

Compares one CSV file with its documentation.

### Relationship Agent

Validates keys, referential integrity, and cardinality between two CSV files.

### Semantic Model Agent

Builds a structured semantic specification without generating LookML.

### LookML Generator Agent

Runs the complete generation pipeline, validates the artifacts, and optionally writes the files.

Specialized agents use task mode so that control automatically returns to the Supervisor after task completion.

## Deterministic Pipeline

The main pipeline is deterministic and can run without an LLM:

```text
CSV files
    +
business documentation
    ↓
technical metadata analysis
    ↓
business documentation analysis
    ↓
consistency validation
    ↓
relationship validation
    ↓
semantic model specification
    ↓
LookML rendering
    ↓
local validation
    ↓
secure file writing
```

The LLM is used for conversation, task routing, and result presentation. Technical decisions and file generation remain validated by deterministic Python tools.

## API

The project exposes a FastAPI application.

### Start the API

```powershell
python -m uvicorn app.api.main:app --host 127.0.0.1 --port 8001
```

Open Swagger:

```text
http://127.0.0.1:8001/docs
```

### Available Endpoints

```text
GET  /
GET  /health

POST /api/v1/metadata/analyze
POST /api/v1/documentation/analyze
POST /api/v1/consistency/analyze
POST /api/v1/relationships/analyze
POST /api/v1/semantic-model/build
POST /api/v1/lookml/preview
POST /api/v1/lookml/generate
```

### Preview LookML

The preview endpoint generates and validates LookML in memory without writing files:

```text
POST /api/v1/lookml/preview
```

### Generate LookML Files

The generation endpoint validates and writes the files:

```text
POST /api/v1/lookml/generate
```

The standard output directory is:

```text
data/outputs/lookml
```

## Installation

### Requirements

- Python 3.13 or another compatible Python version;
- PowerShell or a standard terminal;
- Google ADK for conversational agent execution;
- Gemini API access only for ADK Web agent tests.

The deterministic pipeline and FastAPI application do not require Gemini.

### Clone the Repository

```powershell
git clone <repository-url>
cd semantic-layer-builder
```

### Create a Virtual Environment

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### Configure Environment Variables

Copy the example file:

```powershell
Copy-Item .env.example .env
```

Never commit the real `.env` file or API keys.

## Configuration

Application configuration is centralized in:

```text
app/config.py
```

Supported environment variables include:

```dotenv
APP_NAME=semantic-layer-builder
APP_VERSION=0.1.0
APP_ENV=development
AGENT_MODEL=gemini-flash-latest
LOG_LEVEL=INFO
LOG_FILE_NAME=semantic_layer_builder.log
GOOGLE_API_KEY=replace_with_your_api_key
```

## Running the Tests

Run the complete test suite:

```powershell
python -m pytest -v
```

Run only the end-to-end pipeline tests:

```powershell
python -m pytest tests\test_end_to_end_lookml_pipeline.py -v
```

Run only the API tests:

```powershell
python -m pytest tests\test_api.py tests\test_analysis_api.py -v
```

The test suite covers:

- Pydantic schemas;
- metadata extraction;
- documentation parsing;
- consistency rules;
- relationship integrity;
- semantic-model construction;
- LookML rendering;
- LookML validation;
- secure file writing;
- final pipeline orchestration;
- API endpoints;
- agent configuration;
- Supervisor hierarchy;
- logging and configuration.

## Logging

The application writes structured logs to:

```text
logs/semantic_layer_builder.log
```

Logs include:

- API startup and shutdown;
- request identifiers;
- HTTP methods and paths;
- response status codes;
- request duration;
- LookML pipeline lifecycle;
- technical errors.

The logger does not intentionally record:

- API keys;
- full CSV contents;
- full documentation contents;
- personal values;
- generated LookML contents.

Each HTTP response contains:

```text
X-Request-ID
```

## Project Structure

```text
semantic-layer-builder/
├── app/
│   ├── agent.py
│   ├── config.py
│   ├── logging_config.py
│   ├── agents/
│   ├── api/
│   ├── schemas/
│   └── tools/
│
├── data/
│   ├── documentation/
│   ├── inputs/
│   └── outputs/
│
├── tests/
├── docs/
├── examples/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Example Data Model

The demonstration model contains two tables.

### CLIENTS

Primary key:

```text
CLIENT_ID
```

Sensitive field:

```text
CLIENT_NAME
```

### ORDERS

Primary key:

```text
ORDER_ID
```

Foreign key:

```text
CLIENT_ID
```

Validated relationship:

```text
ORDERS.CLIENT_ID -> CLIENTS.CLIENT_ID
```

Cardinality:

```text
many-to-one
```

## Generated Measures

The project generates validated count measures and proposes numeric aggregations.

For `ORDERS.AMOUNT`, the proposed measures are:

```text
total_amount
average_amount
minimum_amount
maximum_amount
```

Automatically generated numeric measures remain marked with warnings until business validation.

## Reliability Principles

The project follows several reliability principles:

1. Technical observations are separated from documented business facts.
2. A primary-key candidate is not automatically treated as a confirmed business key.
3. Sample uniqueness is not treated as a business uniqueness constraint.
4. Non-verifiable information is not automatically considered incorrect.
5. Invalid relationships block generation readiness.
6. LookML is validated before it is written.
7. File overwriting requires explicit authorization.
8. Sensitive fields are reported but not automatically secured.
9. LLM responses do not replace deterministic validation.
10. Every major component is covered by automated tests.

## Current Limitations

The current version:

- uses CSV files as technical sources;
- supports Markdown and TXT documentation;
- demonstrates the workflow with CLIENTS and ORDERS;
- does not connect directly to a production database;
- does not deploy generated LookML to a Looker instance;
- does not automatically create Looker access grants;
- requires human validation for automatically proposed measures;
- uses a local structural validator rather than the official Looker validator.

## Future Improvements

Possible future developments include:

- support for arbitrary table collections;
- database schema introspection;
- BigQuery integration;
- automatic schema and dataset discovery;
- composite primary keys;
- multiple foreign-key relationships;
- configurable measure-generation policies;
- Looker SDK validation;
- direct Git branch generation;
- user interface for source selection and model review;
- authentication and authorization;
- background jobs for large datasets;
- production monitoring.

## Portfolio Value

This project demonstrates skills in:

- Python application architecture;
- FastAPI;
- Pydantic;
- automated testing with Pytest;
- multi-agent systems;
- Google Agent Development Kit;
- semantic-layer modeling;
- Looker and LookML;
- data-quality validation;
- referential-integrity analysis;
- secure file generation;
- API design;
- logging and observability;
- separation between LLM reasoning and deterministic execution.

## License

Add the selected project license here.