# Codebase Issues to Fix

## Critical Issues

### 3. Test Coverage Below Required 95%

**Current Coverage: 23% (Target: 95%)**

#### Zero Coverage Files
- `china_data_downloader.py` (0%)
- `china_data_processor.py` (0%)
- `utils/data_sources/fallback_loader.py` (0%)
- `utils/data_sources/fallback_utils.py` (0%)

#### Critically Low Coverage (<10%)
- `utils/capital/calculation.py` (6%)
- `utils/capital/investment.py` (7%)
- `utils/capital/projection.py` (5%)
- `utils/output/formatters.py` (9%)
- `utils/output/markdown_generator.py` (12%)
- `utils/processor_extrapolation.py` (9%)
- `utils/processor_hc.py` (7%)
- `utils/processor_units.py` (14%)
- `utils/economic_indicators/indicators_calculator.py` (9%)

#### Low Coverage (<25%)
- `utils/data_sources/imf_loader.py` (15%)
- `utils/data_sources/pwt_downloader.py` (22%)
- `utils/data_sources/wdi_downloader.py` (23%)
- `utils/processor_dataframe/merge_operations.py` (14%)
- `utils/processor_dataframe/metadata_operations.py` (16%)
- `utils/processor_dataframe/output_operations.py` (20%)
- `utils/processor_load.py` (18%)
- `utils/economic_indicators/tfp_calculator.py` (21%)
- `utils/extrapolation_methods/arima.py` (23%)
- `utils/extrapolation_methods/linear_regression.py` (23%)
