import json, math, heapq, random, sys
d=json.load(open('vedado.json')); W,S,E,N=d['bbox']
k=math.cos(math.radians((S+N)/2)); VW=1000; VH=round(VW*(N-S)/((E-W)*k))
def P(lon,lat): return ((lon-W)/(E-W)*VW, (N-lat)/(N-S)*VH)
def mdist(a,b): return math.hypot((a[0]-b[0])*k,(a[1]-b[1]))*111320
def path(pts): 
    q=[P(*p) for p in pts]; return "M"+" L".join(f"{x:.1f} {y:.1f}" for x,y in q)
cls={"trunk":3,"primary":3,"secondary":2.4,"tertiary":1.8,"residential":1.1,"unclassified":1.1,"living_street":.9,"pedestrian":.8,"service":.5}
layers={}
for w in d['ways']: layers.setdefault(cls[w['hw']],[]).append(path(w['pts']))
# sea: join coast segments, close along the top edge
bins={}
for lon,lat in (p for seg in d['coast'] for p in seg if W-.005<=p[0]<=E+.005):
    b=int((lon-W)/(E-W)*250)
    if b not in bins or lat>bins[b][1]: bins[b]=(lon,lat)
coast=[bins[b] for b in sorted(bins)]
coast=[p for i,p in enumerate(coast) if not (0<i<len(coast)-1 and p[1] < min(coast[i-1][1],coast[i+1][1]) - 0.0015)]
coast=[p for p in coast if p[1] > 23.128 or p[0] > -82.40]
sea="M"+" L".join(f"{x:.1f} {y:.1f}" for x,y in (P(*p) for p in coast))+f" L{VW+20} -20 L-20 -20 Z"
byname={}
for w in d['ways']: byname.setdefault({'Calle 23 (La Rampa)':'Calle 23'}.get(w['name'],w['name']),[]).append(w['pts'])
def nodes(n): return [tuple(p) for pl in byname[n] for p in pl]
def inter(a,b):
    A=set(nodes(a)); B=nodes(b); sh=[p for p in B if p in A]
    if sh: return sh[0]
    return min(((pa,pb) for pa in A for pb in B), key=lambda t:mdist(*t))[0]
# graph for routing
G={}
for w in d['ways']:
    if w['hw'] in ('service',): continue
    pts=[tuple(p) for p in w['pts']]
    for a,b in zip(pts,pts[1:]):
        L=mdist(a,b); G.setdefault(a,[]).append((b,L)); G.setdefault(b,[]).append((a,L))
def near(pt): return min(G,key=lambda n:mdist(n,pt))
def route(a,b):
    a,b=near(a),near(b); dist={a:0}; prev={}; h=[(0,a)]
    while h:
        dd,u=heapq.heappop(h)
        if u==b: break
        if dd>dist[u]: continue
        for v,L in G[u]:
            if dd+L<dist.get(v,1e18): dist[v]=dd+L; prev[v]=u; heapq.heappush(h,(dd+L,v))
    p=[b]
    while p[-1]!=a: p.append(prev[p[-1]])
    return p[::-1], dist[b]
def seg_on(name, p1, p2):
    # the polyline of `name` between its nodes nearest p1 and p2
    best=None
    for pl in byname[name]:
        i=min(range(len(pl)),key=lambda j:mdist(pl[j],p1)); j=min(range(len(pl)),key=lambda j:mdist(pl[j],p2))
        sc=mdist(pl[i],p1)+mdist(pl[j],p2)
        if best is None or sc<best[0]: best=(sc,pl[min(i,j):max(i,j)+1])
    return best[1]
poi={p['name']:p['pt'] for p in d['pois']}
def midpoint(pl):
    # the point halfway along the polyline, by length
    L=[mdist(a,b) for a,b in zip(pl,pl[1:])]; half=sum(L)/2
    for (a,b),l in zip(zip(pl,pl[1:]),L):
        if half<=l: t=half/l if l else 0; return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)
        half-=l
    return pl[-1]
def label(name):
    best=max(byname[name], key=lambda pl: sum(mdist(a,b) for a,b in zip(pl,pl[1:])))
    m=midpoint(best); i=min(range(len(best)-1), key=lambda j: mdist(best[j],m))
    (x1,y1),(x2,y2)=P(*best[i]),P(*best[i+1]); ang=math.degrees(math.atan2(y2-y1,x2-x1))
    if ang>90: ang-=180
    if ang<-90: ang+=180
    x,y=P(*m); return {"t":name,"x":round(x,1),"y":round(y,1),"a":round(ang,1)}
ex=[]
def add(q,kind,pt,r,line=None,note=""):
    x,y=P(*pt); scale=VW/((E-W)*k*111320)
    ex.append({"q":q,"kind":kind,"x":round(x,1),"y":round(y,1),"r":round(max(r,12)*scale,1),"rm":round(r),"line":path(line) if line else "","note":note,
               "lat":round(pt[1],5),"lon":round(pt[0],5)})
a=inter("Calle 23","Calle L"); b=inter("Calle 23","Calle M"); s=seg_on("Calle 23",a,b)
mid=midpoint(s); add("Calle 23 e/ L y M, Vedado","tramo",mid,mdist(a,b)/2,s,"tramo de Calle 23 entre L y M")
add("23 esq. a L, Vedado","esquina",a,15,None,"esquina de Calle 23 y Calle L")
c=inter("Calle L","Calle 25"); s2=seg_on("Calle L",a,c); add("Calle L e/ 23 y 25, Vedado","tramo",midpoint(s2),mdist(a,c)/2,s2,"tramo de Calle L entre 23 y 25")
add("Hotel Nacional","lugar",poi["Hotel Nacional"],30,None,"punto de interés de OpenStreetMap")
add("Hotel Riviera","lugar",poi["Hotel Riviera"],30,None,"punto de interés de OpenStreetMap")
rp,rl=route(poi["Hotel Nacional"],poi["Museo Nacional del Deporte"])
xs=[P(*q) for q in rp]; bx=[min(x for x,_ in xs),min(y for _,y in xs),max(x for x,_ in xs),max(y for _,y in xs)]
rt={"from":"Hotel Nacional","to":"Museo Nacional del Deporte","m":round(rl),"line":path(rp),"bbox":[round(v,1) for v in bx]}
random.seed(7); allpts=[tuple(p) for w in d['ways'] if w['hw'] in ('residential','tertiary') for p in w['pts']]
lote=[P(*p) for p in random.sample(allpts,60)]
labels=[label(n) for n in ["Calle 23","Línea","Malecón","Paseo","Calle L","Calle 25","Calle 21","Avenida de los Presidentes"] if n in byname]
out={"labels":labels,"vw":VW,"vh":VH,"sea":sea,"layers":{str(k_):"".join(v) for k_,v in layers.items()},"ex":ex,"route":rt,
     "lote":[[round(x,1),round(y,1)] for x,y in lote]}
json.dump(out,open('mock.json','w'))
print(VW,VH,len(ex),"examples; route",rt['m'],"m; json",len(json.dumps(out))//1024,"KB")
