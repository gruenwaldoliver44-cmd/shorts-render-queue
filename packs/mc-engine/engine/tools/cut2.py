import json,numpy as np,sys
sys.argv=['x','/dev/null']
src=open('tools/cut.py').read().split("for s,(r,n) in SHEETS")[0]
exec(src)
meta=json.load(open('tools/sprites.json'))
cut('old',2,['o_dish','o_nerv','o_hide','o_back','o_bed','o_sit','mug_f','mug_s'])
cut('close',2,['cu_grin','cu_laugh','cu_shock','cu_sad'])
import os
if os.path.exists(A+'grocer.png'):cut('grocer',1,['g_read','g_scratch','g_talk','g_shrug'])
json.dump(meta,open('tools/sprites.json','w'))
