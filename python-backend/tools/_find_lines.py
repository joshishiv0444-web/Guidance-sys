from pathlib import Path
p=Path('../server.py').read_text().splitlines()
for i,l in enumerate(p,1):
    if 'class GuidanceRequest' in l:
        print('GuidanceRequest at',i)
    if "if req.session_id not in sessions" in l:
        print('session check at',i)
    if '@app.post("/api/v1/fraud/url")' in l:
        print('fraud url route at',i)
    if "@app.post(\"/api/v1/guidance\")" in l:
        print('guidance route at',i)
    if 'def get_guidance' in l:
        print('get_guidance def at',i)
