# Environment Setup

## 1. Create a virtual environment

```bash
python -m venv venv
```

---

## 2. Activate the virtual environment

### Windows (PowerShell)

```bash
venv\Scripts\activate
```

---

## 3. Install project dependencies

```bash
pip install -r requirements.txt
```

---

# First Part

## Automated Data Collection

This step downloads the monthly CSV files for both datasets:

- `https://dados.ons.org.br/dataset/restricao_coff_eolica_usi`
- `https://dados.ons.org.br/dataset/restricao_coff_eolica_detail`

---

### Running the Download Script

Choose the desired date range and execute the script using the following format:

```bash
python src/extract/download_data.py --start YYYY-MM --end YYYY-MM
```

---

### Example

```bash
python src/extract/download_data.py --start 2025-10 --end 2026-03
```

This command downloads all monthly files between October 2025 and March 2026 for both datasets.

---

### Output

Files are saved in:

- data/raw/wind_farm/
- data/raw/spe/

---

## Data Consolidation

This step consolidates all monthly CSV files into unified datasets.

---

### Running the Consolidation Script

Execute the following command from the project root:

```bash
python src/transform/consolidate_data.py
```
---

### Output

Files are saved in:

- data/interim/spe_consolidated.csv
- data/interim/wind_farm_consolidated.csv

---

## Data Quality 

This step is responsible for ensuring the reliability and consistency of the consolidated datasets. The pipeline performs data validation, cleansing, and generates a structured data quality report.

---

### Running the Data Quality Script

Execute the following command from the project root:

```bash
python python src/transform/data_quality.py
```
---

### Output

Files are saved in:

- data/processed/spe_clean.csv
- data/processed/wind_farm_clean.csv
- data/reports/data_quality_report.json

---

## Casa dos Ventos Filtering

This step filters the dataset to keep only SPEs belonging to Casa dos Ventos and their associated wind farm complexes.

---

### Running the Filtering Script

Execute the following command from the project root:

```bash
python src/transform/filter_cdv.py
```

---

### Output

Files are saved in:

- data/filtered/spe_cdv_filtered.csv
- data/filtered/wind_cdv_filtered.csv

---

## Dataset Join Strategy

The SPE detail dataset and the Wind Farm dataset were joined using a business key based on the wind complex name.

### Join Key Investigation

Although both datasets contain the `id_ons` column, the field represents different hierarchical entities:

- In the SPE dataset, `id_ons` identifies the individual SPE.
- In the Wind Farm dataset, `id_ons` identifies the wind complex.

Because of this semantic mismatch, `id_ons` was not used as the join key.

After investigating the available columns, the logical relationship between datasets was identified as:

```text
spe.nom_conjuntousina ↔ wind.nom_usina
```

Example:

```text
Conj. Paulino Neves ↔ CONJ. PAULINO NEVES
```

To guarantee matching consistency, both fields were normalized by:

- converting text to uppercase
- trimming spaces
- removing duplicated spaces

---

### Join Type

A `LEFT JOIN` strategy was used, preserving the SPE dataset as the primary granular layer.

This approach guarantees that:

- all SPE records remain in the final dataset
- Wind Farm information is added whenever a valid match exists

The final dataset therefore keeps the original SPE granularity while enriching records with aggregated Wind Farm attributes.

---

### Cardinality Handling

The Wind Farm dataset contains multiple temporal records for the same wind complex. To avoid a many-to-many merge explosion and excessive memory usage, duplicates were removed before the join using the normalized business key.

---

### Selected Wind Farm Attributes

The following columns from the Wind Farm dataset were incorporated into the final joined dataset:

- `nom_subsistema`
- `nom_estado`
- `val_geracao`
- `val_disponibilidade`
- `val_geracaoreferencia`
- `val_geracaoreferenciafinal`

Operational restriction fields such as:

- `val_geracaolimitada`
- `cod_razaorestricao`
- `cod_origemrestricao`
- `dsc_restricao`

were intentionally excluded from the final dataset to keep the model focused on generation and availability metrics.

---

### Possible Merge Losses

Potential merge losses may occur due to:

- naming inconsistencies between datasets
- missing or malformed wind complex names
- unmatched normalized keys

Join quality metrics were calculated to validate merge coverage and identify unmatched records.

---

### Running the Dataset Join Script

Execute the following command from the project root:

```bash
python src/transform/join_spe_wind.py
```

---

### Output

File is saved in:

- data/processed/cdv_spe_wind_joined.csv

---

## Data Persistence

The final consolidated dataset was persisted in **Parquet** format using partitioning by:

- `year`
- `month`

Both columns were extracted from `din_instante`.

---

### Partition Strategy

The dataset was partitioned by time (`year/month`) because the data represents time-series energy generation records.

This strategy improves performance for queries filtered by temporal windows, such as:

- monthly analysis
- yearly reports
- historical comparisons

---

### Running the Persistence Script

Execute the following command from the project root:

```bash
python src/load/save_parquet.py
```

---

### Output 

The partitioned Parquet dataset will be saved to:

- data/final_parquet/

Example structure:

```text
data/final_parquet/
├── year=2025/
│   ├── month=10/
│   ├── month=11/
│   └── month=12/
│
└── year=2026/
    ├── month=1/
    ├── month=2/
    └── month=3/
```

---