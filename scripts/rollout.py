#!/usr/bin/env python3
import json, time, os
os.makedirs('rollout', exist_ok=True)
st = {'started': int(time.time()), 'progress': 5, 'state': 'canary'}
open('rollout/state.json','w').write(json.dumps(st))
print(json.dumps(st))
