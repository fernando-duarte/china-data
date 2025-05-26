from typing import Union

import pandas as pd
from jinja2 import Template


def render_markdown_table(
    merged_data: pd.DataFrame,
    wdi_date: str | None = None,
    pwt_date: str | None = None,
    imf_date: str | None = None,
) -> str:
    """Render the merged data as a markdown table.

    Args:
        merged_data (pandas.DataFrame): The merged data to render
        wdi_date (str, optional): The download date for WDI data
        pwt_date (str, optional): The download date for PWT data
        imf_date (str, optional): The download date for IMF data

    Returns:
        str: The rendered markdown table
    """
    # Define column mapping
    column_mapping = {
        "year": "Year",
        "GDP_USD": "GDP (USD)",
        "C_USD": "Consumption (USD)",
        "G_USD": "Government (USD)",
        "I_USD": "Investment (USD)",
        "X_USD": "Exports (USD)",
        "M_USD": "Imports (USD)",
        "FDI_pct_GDP": "FDI (% of GDP)",
        "TAX_pct_GDP": "Tax Revenue (% of GDP)",
        "POP": "Population",
        "LF": "Labor Force",
        "rgdpo": "PWT rgdpo",
        "rkna": "PWT rkna",
        "pl_gdpo": "PWT pl_gdpo",
        "cgdpo": "PWT cgdpo",
        "hc": "PWT hc",
    }

    # Create display data by renaming columns without copying the entire DataFrame
    display_data = merged_data.rename(columns=column_mapping)

    # Format the data for display - create a new DataFrame with formatted values
    formatted_data = {}
    for col in display_data.columns:
        if col == "Year":
            formatted_data[col] = [str(int(x)) for x in display_data[col] if not pd.isna(x)]
        elif col in ["Population", "Labor Force"]:
            formatted_data[col] = [f"{x:,.0f}" if not pd.isna(x) else "N/A" for x in display_data[col]]
        else:
            formatted_data[col] = [f"{x:.2f}" if not pd.isna(x) else "N/A" for x in display_data[col]]

    # Create the final display DataFrame
    display_df = pd.DataFrame(formatted_data)
    headers = list(display_df.columns)
    rows = display_df.values.tolist()

    # No default dates - we'll only include dates in the markdown if they're provided

    template = Template(
        """# China Economic Data

Data sources:
- World Bank World Development Indicators (WDI)
- Penn World Table (PWT) version 10.01
- International Monetary Fund. Fiscal Monitor (FM)

## Economic Data (1960-present)

|{% for h in headers %} {{ h }} |{% endfor %}
|{% for h in headers %} --- |{% endfor %}
{% for row in rows %}|{% for cell in row %} {{ cell }} |{% endfor %}
{% endfor %}

**Notes:**
- GDP and its components (Consumption, Government, Investment, Exports, Imports) are in current US dollars
- FDI is shown as a percentage of GDP (net inflows)
- Tax Revenue is shown as a percentage of GDP
- Population and Labor Force are in number of people
- PWT rgdpo: Output-side real GDP at chained PPPs (in millions of 2017 USD)
- PWT rkna: Capital stock at constant 2017 national prices (index: 2017=1)
- PWT pl_gdpo: Price level of GDP (price level of USA GDPo in 2017=1)
- PWT cgdpo: Output-side real GDP at current PPPs (in millions of USD)
- PWT hc: Human capital index, based on years of schooling and returns to education

Sources:
- World Bank WDI data: World Development Indicators, The World Bank. Available at
  https://databank.worldbank.org/source/world-development-indicators.
  {% if wdi_date %}Accessed on {{ wdi_date }}.{% endif %}
- PWT data: Feenstra, Robert C., Robert Inklaar and Marcel P. Timmer (2015),
  "The Next Generation of the Penn World Table" American Economic Review, 105(10), 3150-3182.
  Available at https://www.ggdc.net/pwt. {% if pwt_date %}Accessed on {{ pwt_date }}.{% endif %}
- International Monetary Fund. Fiscal Monitor (FM), https://data.imf.org/en/datasets/IMF.FAD:FM.
  {% if imf_date %}Accessed on {{ imf_date }}.{% endif %}
"""
    )
    return template.render(headers=headers, rows=rows, wdi_date=wdi_date, pwt_date=pwt_date, imf_date=imf_date)
