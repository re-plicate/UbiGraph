@echo off
REM Example Windows batch to run the preprocessing
python ..\GCL-release\code\data_process_example.py --input-a ..\GCL-release\data_examples\input_a.csv --input-b ..\GCL-release\data_examples\input_b.csv --output-dir ..\GCL-release\output_graphs --n-clusters 15
pause
