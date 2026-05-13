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

# First Part - Data Preparation and Integration

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

# Second Part — Dimensional Modeling

## Dimensional Model

A dimensional model following the **Star Schema** approach was designed for the constrained-off wind generation domain.

The model separates:

- **Fact table** → generation and operational metrics
- **Dimension tables** → descriptive business context

---

### Fact Table

#### `fact_generation`

The fact table stores the wind generation measurements and operational metrics.

#### Granularity

The chosen granularity is:

> One record per SPE per timestamp (`din_instante`).

This granularity preserves the original detail level from the SPE dataset and allows temporal analysis at the individual wind plant level.

---

#### Metrics

The following numerical metrics were included:

- `val_ventoverificado`
- `val_geracaoestimada`
- `val_geracaoverificada`
- `val_geracao`
- `val_disponibilidade`
- `val_geracaoreferencia`
- `val_geracaoreferenciafinal`

---

#### Foreign Keys

The fact table contains the following foreign keys:

- `spe_key`
- `conjunto_key`
- `tempo_key`

---

### Dimension Tables

#### `dim_spe`

Stores descriptive information about individual SPEs.

##### Attributes

- `spe_key` (Primary Key)
- `nom_usina`
- `id_ons`
- `ceg`
- `projeto`
- `nom_modalidadeoperacao`

---

#### `dim_conjunto`

Stores information about wind complexes/conjuntos.

##### Attributes

- `conjunto_key` (Primary Key)
- `nom_conjuntousina`
- `id_subsistema`
- `nom_subsistema`
- `id_estado`
- `nom_estado`

---

#### `dim_tempo`

Stores temporal attributes extracted from `din_instante`.

##### Attributes

- `tempo_key` (Primary Key)
- `din_instante`
- `ano`
- `mes`
- `dia`
- `hora`

---

### Relationships

The dimensional model relationships are:

- `fact_generation.spe_key` → `dim_spe.spe_key`
- `fact_generation.conjunto_key` → `dim_conjunto.conjunto_key`
- `fact_generation.tempo_key` → `dim_tempo.tempo_key`

---

### Running the Modeling Script

Execute the following command from the project root:

```bash
python src/modeling/build_star_schema.py
```

---

### Output

The generated dimensional model tables will be saved to:

- data/warehouse/

Structure:

```text
data/
└── warehouse/
    ├── dimensions/
    │   ├── dim_spe.parquet
    │   ├── dim_conjunto.parquet
    │   └── dim_tempo.parquet
    │
    └── facts/
        └── fact_generation.parquet
```

---

## Design Decisions

### Fact Table Granularity

The fact table granularity was defined as:

> One record per SPE per timestamp (`din_instante`).

This granularity was chosen because the SPE dataset already represents the most detailed operational level available in the source data.

Using this level of detail allows:

- temporal analysis of wind generation
- comparisons between SPEs
- project-level aggregations
- future analytical flexibility without losing information

It also preserves the original business semantics of the ONS detailed dataset.

---

### Slowly Changing Dimensions (SCD)

At the current scope of the project, there is no strong need for Slowly Changing Dimensions.

The descriptive attributes used in the dimensions are relatively stable, such as:

- project
- SPE
- conjunto
- subsystem
- state

However, in a production-grade environment, some dimensions could eventually require:

#### SCD Type 2

Especially for attributes that may change historically over time, such as:

- project ownership
- operational classification
- regional organization

SCD Type 2 would preserve historical versions of the records while maintaining analytical consistency over time.

For this project, dimensions were implemented as static snapshots.

---

### Denormalization Decisions

A small amount of denormalization was intentionally applied in the dimensional model.

For example:

- subsystem information
- state information

were kept directly inside `dim_conjunto`.

This decision was made because:

- these attributes have low cardinality
- they rarely change
- it simplifies analytical queries
- it reduces unnecessary joins

The goal was to prioritize simplicity and query performance while maintaining a clean star schema structure.

---

### Modeling Strategy Summary

The dimensional model was designed to:

- preserve the SPE-level analytical granularity
- optimize BI and aggregation queries
- reduce redundancy in the fact table
- simplify analytical exploration
- follow common Data Warehouse best practices

---

## Model Implementation

The dimensional model was implemented programmatically using:

- Python
- Pandas
- Parquet

The implementation consumes the consolidated dataset generated in Part 1 and transforms it into a Star Schema structure composed of:

- dimension tables
- fact table

---

### Input Dataset

The modeling process uses the following dataset:

```text
data/processed/cdv_spe_wind_joined.csv
```

---

### Generated Tables

#### Dimension Tables

- `dim_spe.parquet`
- `dim_conjunto.parquet`
- `dim_tempo.parquet`

Saved in:

- data/warehouse/dimensions/

---

#### Fact Table

- `fact_generation.parquet`

Saved in:

- data/warehouse/facts/

---

# Third Part - 