Original -> Release mapping

- `realtime_sys/sys_25_7_10/Realtime_Seg_Final.py` -> `GCL-release/code/Realtime_Seg_Final_sanitized.py`
  - Purpose: segmentation + classification producing `predict/*_segmented_buildings_cls.csv`
  - Changes: absolute paths removed, GPS conversion omitted (pixel placeholders), CLI args added.

- `realtime_sys/sys_25_7_10/real_time_seg.py` -> (not directly included) see `Realtime_Seg_Final_sanitized.py` as minimal alternative

- `realtime_sys/sys_25_7_10/test_sim/dataProcess_kmeans15_optimized.py` -> `GCL-release/code/dataProcess_kmeans15_sanitized.py`
  - Purpose: KMeans-15 clustering -> `cluster_drop`, compute `cluster_link`, compute `cluster_across_link`.
  - Changes: CLI args, relative paths, simplified logging.

- `GCL-our/cosimheat/dataProcess_ultra_optimized.py` -> `GCL-release/code/dataProcess_ultra_sanitized.py`
  - Purpose: more complete processing pipeline (add lat/lon, split, dedupe, compute links)
  - Changes: simplified parsing and I/O; functions preserved in simplified form for reuse.

- `GCL-our/graphcl_project/dataset_cluster_drop.py` -> `GCL-release/code/dataset_cluster_drop.py`
  - Purpose: Data loader for GraphCL experiments; preserved with minor path adjustments.

Notes
- Model weights, raw videos, Excel params, and large CSVs are intentionally excluded. Replace placeholders with your real inputs before running.
- If you want, I can sanitize additional helper files (e.g., `pos_tool_equal_work.py`) into `code/` and add example commands to reproduce exact GPS conversion.
