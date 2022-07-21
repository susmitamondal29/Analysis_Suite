#!/usr/bin/env python3
from pathlib import Path

hdfs_name = 'dteague'
user_name = Path().owner()

hdfs_area = Path(f'/hdfs/store/user/{hdfs_name}')
submit_area = Path(f'/nfs_scratch/{user_name}')
analysis_area = Path(f'{__file__}').resolve().parents[2]
workspace_area = analysis_area / 'workspace'
if not workspace_area.exists():
    workspace_area.mkdir()
