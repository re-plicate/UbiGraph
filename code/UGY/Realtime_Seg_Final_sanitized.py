"""Sanitized wrapper of `Realtime_Seg_Final.py` for open release.
- Replaces absolute paths with CLI args
- Omits model weights; user provides `--model-path` and `--cls-model-path`
- Outputs segmented CSV to `--output-dir` as `{prefix}_segmented_buildings_cls.csv`
"""

import argparse
import os
import time
import pandas as pd
from ultralytics import YOLO
import cv2

# NOTE: This is a minimalized, sanitized version intended for public release.
# It preserves the core flow: run segmentation, sample centers, run classification
# and save a CSV with columns ['time','longitude','latitude','class'].


def run_segmentation(video_path, model_path, cls_model_path, output_dir, prefix='input'):
    os.makedirs(output_dir, exist_ok=True)
    # load models (user must provide correct paths)
    model = YOLO(model_path)
    cls_model = YOLO(cls_model_path)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {video_path}")

    seg_records = []
    frame_idx = 0
    save_interval = 10

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model.predict(source=frame, stream=True, conf=0.25, iou=0.45, imgsz=640, device='cpu')
        names = model.names
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for i, (box, cls) in enumerate(zip(boxes.xyxy, boxes.cls)):
                x1, y1, x2, y2 = box[:4].cpu().numpy()
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                # For release, we do not include drone GPS conversion. Record pixel centers as placeholders.
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                # run classifier on cropped box (optional)
                xmin, ymin, xmax, ymax = int(x1), int(y1), int(x2), int(y2)
                crop = frame[ymin:ymax, xmin:xmax]
                cls_name = 'unknown'
                if crop.size != 0:
                    try:
                        cls_res = cls_model.predict(source=crop, imgsz=608, device='cpu', conf=0.25, verbose=False)
                        for cr in cls_res:
                            if hasattr(cr, 'boxes') and cr.boxes is not None and len(cr.boxes.cls) > 0:
                                cls_name = cls_model.names[int(cr.boxes.cls[0].item())]
                                break
                    except Exception:
                        cls_name = 'unknown'
                # placeholder lon/lat from pixel coords
                seg_records.append({'time': timestamp, 'longitude': float(cx), 'latitude': float(cy), 'class': cls_name})
        frame_idx += 1

    cap.release()
    out_csv = os.path.join(output_dir, f"{prefix}_segmented_buildings_cls.csv")
    pd.DataFrame(seg_records).to_csv(out_csv, index=False)
    print(f"Saved segmented CSV: {out_csv}")
    return out_csv


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--video', required=True)
    p.add_argument('--model-path', required=True)
    p.add_argument('--cls-model-path', required=True)
    p.add_argument('--output-dir', default='./predict')
    p.add_argument('--prefix', default='input')
    args = p.parse_args()

    run_segmentation(args.video, args.model_path, args.cls_model_path, args.output_dir, args.prefix)
