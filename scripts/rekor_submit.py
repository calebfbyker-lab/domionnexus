#!/usr/bin/env python3
import sys
print('rekor_submit: noop (placeholder). file=', sys.argv[sys.argv.index('--file')+1] if '--file' in sys.argv else None)
