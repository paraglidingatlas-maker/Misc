const rng = seed => () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
function noise(seed, w, h){
  const r = rng(seed), oc = [[4,1],[8,.5],[16,.25]].map(([n,a]) => ({n,a,g:Array.from({length:(n+2)*(n+2)}, r)}));
  const sm = t => t*t*(3-2*t), v = new Float64Array(w*h);
  for (let y=0;y<h;y++) for (let x=0;x<w;x++){ let s=0;
    for (const {n,a,g} of oc){ const N=n+2, fx=x/w*n, fy=y/h*n*.6, ix=fx|0, iy=fy|0, tx=sm(fx-ix), ty=sm(fy-iy), G=(i,j)=>g[j*N+i];
      s += a*((G(ix,iy)*(1-tx)+G(ix+1,iy)*tx)*(1-ty)+(G(ix,iy+1)*(1-tx)+G(ix+1,iy+1)*tx)*ty); }
    v[y*w+x]=s; }
  return v;
}
const dist = (a,b) => Math.hypot(a[0]-b[0], a[1]-b[1]);
const MONO = "Inter, system-ui, sans-serif";
let UID = 0;
function addChk(sel){
  const id = "chk" + (++UID), pat = sel.append("defs").append("pattern").attr("id",id).attr("width",5).attr("height",5).attr("patternUnits","userSpaceOnUse");
  pat.append("rect").attr("width",5).attr("height",5).attr("fill","#fff");
  pat.append("rect").attr("width",2.5).attr("height",2.5).attr("fill","#03100F"); pat.append("rect").attr("x",2.5).attr("y",2.5).attr("width",2.5).attr("height",2.5).attr("fill","#03100F");
  return id;
}
function terrain(sel, seed, W, H, alpha=1){
  const cell = 10, gw = Math.ceil(W/cell)+1, gh = Math.ceil(H/cell)+1, vals = noise(seed, gw, gh), ex = d3.extent(vals);
  const cs = d3.contours().size([gw,gh]).thresholds(d3.range(12).map(k => ex[0]+(ex[1]-ex[0])*(k+.5)/12))(vals);
  sel.append("g").selectAll("path").data(cs).join("path").attr("d", d3.geoPath(d3.geoIdentity().scale(cell)))
    .attr("fill", (d,k) => `rgba(43,212,196,${0.007*k*alpha})`)
    .attr("stroke",(d,k)=>k%4===0?`rgba(160,230,222,${.12*alpha})`:`rgba(160,230,222,${.05*alpha})`).attr("stroke-width",.8);
}

/* ---------------- task generation (km space) ---------------- */
function makeTask(seed){
  const r = rng(seed);
  const TO = [0,0];
  const sss = {c:[0,0], r:[3,4,5,6][r()*4|0], type:"sss", name:"SSS"};
  const rad = () => [0.4,0.4,1,1,2,3][r()*6|0];
  const shape = r(), tps = [];
  let goalC;
  if (shape < .4){            // triangle back towards take-off
    const h0 = r()*Math.PI*2, R = 13 + r()*9, cx = R*Math.cos(h0), cy = R*Math.sin(h0), n = 3;
    let a = h0 + Math.PI + (r()-.5)*.5;
    for (let k=0;k<n;k++){ a += (2*Math.PI/n)*(0.8+r()*.4); tps.push({c:[cx + R*Math.cos(a), cy + R*Math.sin(a)], r:rad()}); }
    goalC = [(r()-.5)*6, (r()-.5)*6 + 4];
  } else if (shape < .7){     // out and return with a dog-leg
    const h = r()*Math.PI*2, L = 24 + r()*14;
    tps.push({c:[8*Math.cos(h+1.4), 8*Math.sin(h+1.4)], r:rad()});
    tps.push({c:[L*Math.cos(h), L*Math.sin(h)], r:rad()});
    tps.push({c:[L*.55*Math.cos(h-.35), L*.55*Math.sin(h-.35)], r:rad()});
    goalC = [L*.15*Math.cos(h+.5), L*.15*Math.sin(h+.5)];
  } else {                    // open-distance zig-zag
    let cur = [0,0], h = r()*Math.PI*2; const n = 3 + (r()*2|0);
    for (let k=0;k<n;k++){ h += (k%2 ? 1 : -1)*(0.5 + r()*.8); const L = 10 + r()*12; cur = [cur[0]+L*Math.cos(h), cur[1]+L*Math.sin(h)]; tps.push({c:cur.slice(), r:rad()}); }
    h += (r()-.5); goalC = [cur[0]+ (8+r()*8)*Math.cos(h), cur[1] + (8+r()*8)*Math.sin(h)];
  }
  tps.forEach((t,k) => { t.type = "tp"; t.name = "TP"+(k+1); });
  const goal = {c:goalC, r: r()<.55 ? 0 : 0.4, type:"goal", name:"GOAL"};
  goal.line = goal.r === 0;
  const cyl = [sss, ...tps, goal];
  // optimised route: TO -> edge of SSS -> touch each TP -> goal
  const P = cyl.map(c => c.c.slice());
  const segClosest = (a,b,c) => { const dx=b[0]-a[0], dy=b[1]-a[1], L=dx*dx+dy*dy||1, t=Math.max(0,Math.min(1,((c[0]-a[0])*dx+(c[1]-a[1])*dy)/L)); return [a[0]+t*dx, a[1]+t*dy]; };
  for (let it=0; it<40; it++) for (let i=0;i<cyl.length;i++){
    const c = cyl[i], prev = i===0 ? TO : P[i-1], next = P[i+1];
    if (!c.r){ P[i] = c.c.slice(); continue; }
    if (!next){ const a = Math.atan2(prev[1]-c.c[1], prev[0]-c.c[0]); P[i] = [c.c[0]+c.r*Math.cos(a), c.c[1]+c.r*Math.sin(a)]; continue; }
    if (c.type !== "sss"){ const q = segClosest(prev,next,c.c); if (dist(q,c.c) <= c.r){ P[i] = q; continue; } }
    let best = Infinity, bp;
    for (let k=0;k<180;k++){ const a = k/180*Math.PI*2, x = [c.c[0]+c.r*Math.cos(a), c.c[1]+c.r*Math.sin(a)], f = dist(prev,x)+dist(x,next); if (f<best){ best=f; bp=x; } }
    P[i] = bp;
  }
  const route = [TO, ...P];
  const legs = route.slice(1).map((p,k) => dist(route[k], p));
  return {TO, cyl, route, legs, total: legs.slice(1).reduce((a,b)=>a+b,0)};
}

/* ---------------- flight simulation (km, metres, seconds) ---------------- */
function simulate(task, seed, thermalR, skill=1){
  const r = rng(seed);
  const launch = 1250 + r()*500, base0 = launch + 800 + r()*600, floor = launch - 400;
  const baseAt = t => base0 + 420*Math.min(1, t/12600);
  const wind = [(r()-.5)*.06, (r()-.5)*.06];
  let pos = task.TO.slice(), alt = launch, t = 0, ti = 1, since = 0, nextTh = 0, head = 0, waited = false;
  const pts = [{p:pos.slice(), alt, t, v:0}];
  const targets = task.route.slice(1);
  const circle = (turns, climbFn) => {
    const dir = r()<.5 ? 1 : -1, tgt = targets[ti-1] || pos;
    const a0 = Math.atan2(pos[1]-tgt[1], pos[0]-tgt[0]) + Math.PI/2*dir;
    const c = [pos[0] - thermalR*Math.cos(a0), pos[1] - thermalR*Math.sin(a0)];
    for (let s=1;s<=turns*14;s++){
      const a = a0 + dir*s/14*Math.PI*2, rr = thermalR*(0.85 + .25*Math.sin(s*.9));
      c[0] += wind[0]*thermalR*.6; c[1] += wind[1]*thermalR*.6;
      pos = [c[0] + rr*Math.cos(a), c[1] + rr*Math.sin(a)];
      const v = climbFn(s); alt = Math.min(baseAt(t), alt + v*26/14); t += 26/14;
      pts.push({p:pos.slice(), alt, t, v, ti, gs: 30 + 6*Math.sin(s*.7)});
    }
  };
  for (let guard=0; guard<6000; guard++){
    const tgt = targets[ti-1]; if (!tgt) break;
    if (dist(pos,tgt) < .35){ ti++; if (ti > targets.length) break; continue; }
    const top = baseAt(t) - 60 - r()*380;
    if ((alt < floor + 300 || since > nextTh) && alt < top - 150){
      const climb = (0.9 + r()*2.4) * skill, turns = Math.max(2, Math.min(18, Math.ceil((top - alt)/(climb*26))));
      circle(turns, () => climb*(0.75+.5*r()));
      since = 0; nextTh = 6 + r()*12;
      if (!waited){ waited = true; const wait = 3 + (r()*4|0);   // hold under base until the start gate opens
        circle(wait, s => Math.sin(s/5)*.9 + (r()-.5)*.6); }
    } else {
      const step = .5, want = Math.atan2(tgt[1]-pos[1], tgt[0]-pos[0]);
      head = want + (r()-.5)*.35;
      pos = [pos[0] + step*Math.cos(head), pos[1] + step*Math.sin(head)];
      const ld = 8 + 2*skill + (r()-.5)*2, spd = 30 + 14*skill;
      alt -= step*1000/ld; t += step/(spd/3600); since += step;
      pts.push({p:pos.slice(), alt, t, v:-(spd/3.6)/ld, ti, gs: spd});
    }
  }
  return {pts, launch, base: baseAt(t)};
}

/* ---------------- fit km → px ---------------- */
function rotateTask(task, th){
  const c = Math.cos(th), sn = Math.sin(th), R = p => [p[0]*c - p[1]*sn, p[0]*sn + p[1]*c];
  return {...task, cyl: task.cyl.map(q => ({...q, c:R(q.c)})), route: task.route.map(R)};
}
function bestFit(task, W, H, pad){
  let best = null;
  for (let k=0;k<36;k++){ const t = rotateTask(task, k*Math.PI/36), f = fitter(t, W, H, pad); if (!best || f.s > best.f.s) best = {t, f}; }
  return best;
}
function fitter(task, W, H, pad){
  const xs = [], ys = [];
  task.cyl.forEach(c => { xs.push(c.c[0]-c.r, c.c[0]+c.r); ys.push(c.c[1]-c.r, c.c[1]+c.r); });
  xs.push(0); ys.push(0);
  const [x0,x1] = d3.extent(xs), [y0,y1] = d3.extent(ys);
  const s = Math.min((W-2*pad[0])/(x1-x0), (H-2*pad[1])/(y1-y0));
  const ox = (W - (x1-x0)*s)/2 - x0*s, oy = (H - (y1-y0)*s)/2 - y0*s;
  const f = p => [ox + p[0]*s, oy + p[1]*s]; f.s = s; return f;
}
function chip(sel, W, H, text, small){
  const fs = small ? 10 : 11, w = text.length*fs*.56 + 18;
  const g = sel.append("g").attr("transform", `translate(${W-w-8},${8})`);
  g.append("rect").attr("width",w).attr("height",fs+11).attr("rx",(fs+11)/2).attr("fill","rgba(3,16,15,.85)").attr("stroke","rgba(255,255,255,.14)");
  g.append("text").attr("x",9).attr("y",fs+4.5).text(text).attr("fill","#FFFFFF").attr("font-family",MONO).attr("font-size",fs).attr("font-weight",600);
}
function drawCyl(sel, task, f, o){
  const g = sel.append("g").attr("opacity", o.alpha ?? 1);
  task.cyl.forEach(c => {
    const [x,y] = f(c.c);
    if (c.line){
      const prev = task.route.at(-2), last = task.route.at(-1), a = Math.atan2(last[1]-prev[1], last[0]-prev[0])*180/Math.PI;
      const L = Math.max(o.big?22:14, .4*f.s);
      g.append("rect").attr("x",-2.5).attr("y",-L/2).attr("width",5).attr("height",L).attr("fill",`url(#${o.chk||"chk"})`).attr("transform",`translate(${x},${y}) rotate(${a})`);
      return;
    }
    const R = Math.max(c.r*f.s, c.type==="goal"?3:2.5);
    g.append("circle").attr("cx",x).attr("cy",y).attr("r",R)
      .attr("fill", c.type==="sss" ? "rgba(43,212,196,.05)" : c.type==="goal" ? "rgba(255,255,255,.08)" : "rgba(43,212,196,.09)")
      .attr("stroke", c.type==="goal" ? "#FFFFFF" : "#2BD4C4").attr("stroke-width", o.big?1.2:1).attr("stroke-dasharray", c.type==="sss" ? "4 3" : null);
    if (o.labels){
      const cen = d3.polygonCentroid(task.cyl.map(q=>f(q.c)).concat(task.cyl.length<3?[[x+1,y+1]]:[])), ang = Math.atan2(y-cen[1], x-cen[0]) || -.8;
      let lx = x + Math.cos(ang)*(R+10), ly = y + Math.sin(ang)*(R+10) + 3, anc = Math.cos(ang) < -.3 ? "end" : Math.cos(ang) > .3 ? "start" : "middle";
      const svgW = +sel.attr("viewBox").split(" ")[2];
      if (anc==="end" && lx < 110){ anc = "start"; lx = x + R + 8; } if (anc==="start" && lx > svgW-110){ anc = "end"; lx = x - R - 8; }
      g.append("text").attr("x", lx).attr("y", ly).attr("text-anchor", anc)
        .attr("paint-order","stroke").attr("stroke","#03100F").attr("stroke-width",3).text(c.type==="tp" ? `${c.name} · ${c.r} km` : c.type==="sss" ? `SSS exit · ${c.r} km` : "GOAL")
        .attr("fill","#B7C9CB").attr("font-family",MONO).attr("font-size",10.5).attr("font-weight",600);
    }
  });
  if (o.labels && task.cyl.at(-1).line){ const [x,y] = f(task.cyl.at(-1).c); g.append("text").attr("x",x+10).attr("y",y+18).text("Goal line").attr("fill","#FFFFFF").attr("font-family",MONO).attr("font-size",10).attr("font-weight",700); }
  return g;
}
function launchMark(sel, f, big){
  const [x,y] = f([0,0]), s = big?7:5;
  sel.append("path").attr("d",`M${x},${y-s} L${x+s*.9},${y+s*.6} L${x-s*.9},${y+s*.6}Z`).attr("fill","#FFC906").attr("stroke","#03100F").attr("stroke-width",1.4);
  if (big) sel.append("text").attr("x",x-10).attr("y",y+21).text("Take-off").attr("text-anchor","middle").attr("fill","#FFC906").attr("font-family",MONO).attr("font-size",10.5).attr("font-weight",600).attr("paint-order","stroke").attr("stroke","#03100F").attr("stroke-width",3);
}
const climbCol = d3.scaleLinear([0.5,1.6,3.2],["#FFC83D","#FF8A3D","#F0432B"]).clamp(true);

