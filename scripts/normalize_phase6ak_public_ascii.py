#!/usr/bin/env python3
"""Mechanical typography normalization for one already-approved record."""
import json
from pathlib import Path

for post_id in (103, 204, 212):
    path = next(Path('content/posts').glob(f'{post_id}-*.json'))
    post = json.loads(path.read_text(encoding='utf-8'))
    post['body_html'] = post['body_html'].replace('“', '&quot;').replace('”', '&quot;').replace('’', "'")
    path.write_text(json.dumps(post, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(path)
