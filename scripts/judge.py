#!/usr/bin/env python3
import json, os
m = json.load(open('rollout/state.json')) if os.path.exists('rollout/state.json') else {'progress': 0}
verdict = 'proceed' if m.get('progress',0) >= 5 else 'rollback'
print(json.dumps({'verdict': verdict}))
