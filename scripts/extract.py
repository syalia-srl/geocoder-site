import json, sys, osmium
W,S,E,N = -82.4130, 23.1255, -82.3790, 23.1480   # Vedado and the Malecón edge
keep = {"primary","secondary","tertiary","residential","trunk","unclassified","living_street","pedestrian","service"}
class H(osmium.SimpleHandler):
    def __init__(s): super().__init__(); s.ways=[]; s.pois=[]; s.coast=[]
    def way(s, w):
        hw = w.tags.get("highway"); nat = w.tags.get("natural")
        if hw not in keep and nat != "coastline": return
        try: pts=[(n.lon,n.lat) for n in w.nodes]
        except osmium.InvalidLocationError: return
        if not any(W<=x<=E and S<=y<=N for x,y in pts): return
        if nat=="coastline": s.coast.append(pts); return
        s.ways.append({"name":w.tags.get("name",""),"hw":hw,"pts":pts})
    def node(s, n):
        nm=n.tags.get("name")
        if nm and (n.tags.get("tourism") or n.tags.get("amenity") in ("ice_cream","university","hospital","theatre") or n.tags.get("historic")):
            if W<=n.location.lon<=E and S<=n.location.lat<=N: s.pois.append({"name":nm,"pt":(n.location.lon,n.location.lat)})
h=H(); h.apply_file(sys.argv[1], locations=True, idx="sparse_mem_array")
json.dump({"bbox":[W,S,E,N],"ways":h.ways,"coast":h.coast,"pois":h.pois}, open(sys.argv[2],"w"))
print(len(h.ways),"ways",len(h.coast),"coast",len(h.pois),"pois")
