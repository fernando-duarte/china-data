# Output Formats

The package generates multiple output formats to support different use cases and workflows.

## Available Formats

### CSV Files

**Location:** `output/csv/`

**Features:**

- Machine-readable format
- Compatible with all data analysis tools
- UTF-8 encoding
- Standardized column names

**File Structure:**

```
output/csv/
├── china_wdi_data.csv
├── china_imf_data.csv
├── china_pwt_data.csv
└── china_combined_data.csv
```

### Excel Workbooks

**Location:** `output/excel/`

**Features:**

- Multiple worksheets per source
- Formatted tables with headers
- Data validation rules
- Charts and visualizations

**Worksheet Structure:**

- Raw Data
- Processed Data
- Economic Indicators
- Summary Statistics
- Charts

### Markdown Reports

**Location:** `output/reports/`

**Features:**

- Human-readable analysis
- Embedded tables and charts
- Statistical summaries
- Trend analysis

**Report Sections:**

- Executive Summary
- Data Quality Assessment
- Key Economic Indicators
- Trend Analysis
- Comparative Analysis

### JSON Data

**Location:** `output/json/`

**Features:**

- API-ready format
- Nested data structures
- Metadata inclusion
- Schema validation

## Configuration

Control output generation:

```bash
# Enable/disable formats
GENERATE_CSV=true
GENERATE_EXCEL=true
GENERATE_MARKDOWN=true
GENERATE_JSON=true

# Output directories
CSV_OUTPUT_DIR=output/csv
EXCEL_OUTPUT_DIR=output/excel
REPORT_OUTPUT_DIR=output/reports
JSON_OUTPUT_DIR=output/json
```

## Custom Templates

### Markdown Templates

Create custom report templates in `templates/`:

```markdown
# {{ title }}

## Data Summary

- Source: {{ source }}
- Period: {{ start_date }} to {{ end_date }}
- Records: {{ record_count }}

## Key Indicators

{% for indicator in indicators %}

- {{ indicator.name }}: {{ indicator.value }}
  {% endfor %}
```

### Excel Templates

Customize Excel output with template files:

```python
EXCEL_TEMPLATE_CONFIG = {
    "header_style": {
        "font": {"bold": True, "color": "FFFFFF"},
        "fill": {"fgColor": "366092"}
    },
    "data_style": {
        "number_format": "#,##0.00"
    }
}
```

## Data Validation

All outputs include validation:

- Schema compliance
- Data type consistency
- Range validation
- Cross-format consistency

## Integration

### Database Export

Export to databases:

```python
from utils.output import DatabaseExporter

exporter = DatabaseExporter("postgresql://...")
exporter.export_data(processed_data)
```

### API Integration

Serve data via REST API:

```python
from utils.output import APIServer

server = APIServer()
server.add_dataset("china_data", processed_data)
server.start()
```

## File Naming Convention

```
{country}_{source}_{type}_{date}.{extension}

Examples:
- china_wdi_processed_20250101.csv
- china_imf_indicators_20250101.xlsx
- china_combined_report_20250101.md
```
