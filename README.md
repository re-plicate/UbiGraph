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


### demo
<p align="center">
  <video src="https://github.com/re-plicate/UbiGraph/raw/main/building_seg.mp4" width="800" controls>
    你的浏览器不支持 HTML5 视频，请点击 <a href="https://github.com/[你的用户名]/[仓库名]/raw/main/building_seg.mp4">这里</a> 下载观看。
  </video>
</p>。
</video>

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

# Self-collected datasets
We fused the two cities' data to build our dataset: 

# Additional Experiments
Some additional experiments on Reinforce Learning and Transfer Learning are conducted to evaluate our system

Notes
- This release intentionally omits model weights, videos, and raw datasets. Placeholders and relative paths are used.
- Review `docs/` for mapping from these sanitized scripts back to original files in your repo.








