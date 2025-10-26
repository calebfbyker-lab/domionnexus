import os
import time

# Set SOURCE_DATE_EPOCH and other envs for deterministic builds
os.environ['SOURCE_DATE_EPOCH'] = os.environ.get('SOURCE_DATE_EPOCH', str(int(time.time())))
os.environ['TZ'] = 'UTC'
print('determinism env set: SOURCE_DATE_EPOCH=%s TZ=%s' % (os.environ['SOURCE_DATE_EPOCH'], os.environ['TZ']))
