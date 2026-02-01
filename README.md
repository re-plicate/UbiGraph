# UbiGraph: Towards Ubiquitous Parking Search and Inference with
Graph Learning on Drone Sensing

This folder collects the minimal, sanitized code and instructions to reproduce the dataset generation pipeline used in the YOLO11 project for GraphCL experiments.

What is included
- `code/` — sanitized processing and inference helper scripts (relative paths, CLI args).
- `data_examples/` — tiny placeholder CSVs showing required input format.
- `scripts/` — run helper scripts (Windows `.bat` example).
- `docs/` — short notes and mapping to original project files.
- `requirements.txt`, `LICENSE`, `.gitignore`.

High-level workflow
1. Run segmentation+classification inference to produce segmented CSVs with columns `time,longitude,latitude,class`.
2. Run the processing script to produce `cluster_drop`, `cluster_link`, and `cluster_across_link` CSVs.
3. Use the `code/dataset_cluster_drop.py` loader in GraphCL experiments.

Quick start
1. Install dependencies:

```bash
pip install -r GCL-release/requirements.txt
```

2. Place or generate two input CSVs (see `data_examples/` for headers):
- `input_a.csv` (e.g., shiken_segmented_buildings_cls.csv)
- `input_b.csv` (e.g., other_segmented_buildings_cls.csv)

3. Run preprocessing (example):

```bash
python GCL-release/code/data_process_example.py --input-a input_a.csv --input-b input_b.csv --output-dir ./GCL-release/output_graphs
```

Notes
- This release intentionally omits model weights, videos, and raw datasets. Placeholders and relative paths are used.
- Review `docs/` for mapping from these sanitized scripts back to original files in your repo.

