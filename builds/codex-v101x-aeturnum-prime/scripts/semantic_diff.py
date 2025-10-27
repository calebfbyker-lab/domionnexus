#!/usr/bin/env python3
import json, sys
a=json.loads(open(sys.argv[1]).read())
b=json.loads(open(sys.argv[2]).read())
ka=set(a.keys()); kb=set(b.keys())
print("added:", sorted(kb-ka))
print("removed:", sorted(ka-kb))
print("changed:", sorted([k for k in ka&kb if a[k]!=b[k]])[:50])
