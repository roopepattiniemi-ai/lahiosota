#!/usr/bin/env python3
"""V4-efektit. Aja: python3 generoi_aanet_v4.py"""
import numpy as np
from generoi_aanet import SR, save, t, env, lp_fast, hp_fast, saw, nf
rng = np.random.default_rng(404)
def bp(x, lo, hi): return lp_fast(hp_fast(x, lo), hi)

def bileet():  # vaimea seinän läpi kuuluva diskojumputus + puheensorina, loop 8 s
    dur = 8.0; tt = t(dur); s = np.zeros(len(tt)); beat = 60/126
    for k in range(int(dur/beat)):
        kt = t(0.3); i = int(k*beat*SR)
        kick = np.sin(2*np.pi*(50*kt + 60*0.03*(1-np.exp(-kt/0.03))))*env(len(kt), .001, .1)
        s[i:i+len(kt)] += kick[:len(s)-i]
        m = [45, 45, 48, 43][(k//4) % 4]; bt = t(beat*0.45); j = int((k+0.5)*beat*SR)
        s[j:j+len(bt)] += (saw(nf(m), bt)*env(len(bt), .003, .1)*0.5)[:len(s)-j]
    s = lp_fast(s, 350)*1.5   # seinä vaimentaa
    crowd = bp(rng.standard_normal(len(tt)), 300, 1500)*(0.5 + 0.5*lp_fast(np.abs(rng.standard_normal(len(tt))), 3))*0.35
    s += crowd
    for _ in range(6):  # satunnaisia "WOOO"-huutoja
        i = rng.integers(0, len(tt)-SR); wt = t(0.6); f = 300 + 200*np.sin(np.pi*wt/0.6)
        s[i:i+len(wt)] += bp(saw(1, np.cumsum(f)/SR), 300, 1500)*np.sin(np.pi*wt/0.6)*0.25
    xf = int(0.3*SR); s[:xf] = s[:xf]*np.linspace(0,1,xf) + s[-xf:]*np.linspace(1,0,xf); s = s[:-xf]
    save("sfx_bileet_loop", s, 0.6)

def naapurit():  # varoitus: luudanvarrella kopautus kattoon x3
    out = np.zeros(int(1.2*SR))
    for k in range(3):
        kt = t(0.2); k_ = lp_fast(rng.standard_normal(len(kt)), 600)*env(len(kt), .001, .03) + np.sin(2*np.pi*120*kt)*env(len(kt), .001, .04)
        i = int(k*0.28*SR); out[i:i+len(kt)] += k_
    save("sfx_naapurit_valittaa", np.tanh(out*2), 0.8)

def haato():  # ovi rämähtää auki, ihmisiä lentää ulos, ovi paukahtaa kiinni
    out = np.zeros(int(2.0*SR)); tt = t(0.4)
    creak = bp(saw(1, np.cumsum(180 + 120*tt/tt[-1])/SR), 400, 3000)*np.sin(np.pi*tt/tt[-1])*0.4
    out[:len(tt)] += creak
    for k in range(4):
        ft = t(0.3); thud = lp_fast(rng.standard_normal(len(ft)), 400)*env(len(ft), .002, .06)*1.5
        i = int((0.45 + k*0.22 + rng.uniform(0, .05))*SR); out[i:i+len(ft)] += thud
    st = t(0.5); slam = lp_fast(rng.standard_normal(len(st)), 900)*env(len(st), .001, .08)*2 + np.sin(2*np.pi*80*st)*env(len(st), .001, .1)*1.5
    out[int(1.4*SR):int(1.4*SR)+len(st)] += slam
    save("sfx_haato", np.tanh(out*1.5), 0.85)

def loyly():  # vettä kiukaalle: sihahdus + kivien rätinä
    tt = t(2.2); hiss = hp_fast(rng.standard_normal(len(tt)), 1800)*np.minimum(1, tt/0.05)*np.exp(-tt/0.6)
    sp = t(0.2); splash = lp_fast(rng.standard_normal(len(sp)), 2000)*env(len(sp), .002, .04)
    hiss[:len(sp)] += splash
    for _ in range(40):
        i = int(rng.uniform(0.05, 1.8)*SR); ct = t(0.01)
        hiss[i:i+len(ct)] += hp_fast(rng.standard_normal(len(ct)), 2500)*np.exp(-ct/.002)*rng.uniform(.3, 1)
    save("sfx_sauna_loyly", hiss, 0.75)

def lumimyrsky():  # tuulen ulvonta, loop 8 s
    tt = t(8.4); n = rng.standard_normal(len(tt)); out = np.zeros(len(tt)); blk = int(0.05*SR); h = np.hanning(2*blk)
    for i in range(0, len(tt)-2*blk, blk):
        p = i/len(tt); fc = 500 + 350*np.sin(2*np.pi*p*2) + 200*np.sin(2*np.pi*p*5 + 1)
        out[i:i+2*blk] += bp(n[i:i+2*blk], fc*0.8, fc*1.25)*h
    out = out*3 + lp_fast(n, 250)*0.4 + hp_fast(n, 5000)*0.05
    xf = int(0.4*SR); out[:xf] = out[:xf]*np.linspace(0,1,xf) + out[-xf:]*np.linspace(1,0,xf); out = out[:-xf]
    save("sfx_lumimyrsky_loop", out, 0.6)

def tekstari():  # vanhan kännykän viestiääni
    out = np.zeros(int(0.8*SR))
    for k, (m, st, d) in enumerate(((88, 0, .08), (88, .12, .08), (91, .24, .18))):
        tt = t(d); s = np.sign(np.sin(2*np.pi*nf(m)*tt))*0.5*np.minimum(1, (tt[-1]-tt)/0.005)
        i = int(st*SR); out[i:i+len(s)] += lp_fast(s, 6000)
    save("sfx_tekstiviesti", out, 0.55)

def hemuli_muutos():  # nouseva taikasointi + jumalallinen kuoro + rumpujyrähdys
    out = np.zeros(int(3.2*SR)); tt = t(2.0)
    f = 200*2**(3*tt/tt[-1]); sweep = np.sin(2*np.pi*np.cumsum(f)/SR)*np.minimum(1, tt/0.3)*0.3
    out[:len(tt)] += sweep
    ct = t(1.6); choir = sum(saw(nf(m)*d, ct) for m in (57, 64, 69, 73) for d in (0.996, 1.004))
    choir = lp_fast(choir, 2500)*np.minimum(1, ct/0.3)*np.minimum(1, (ct[-1]-ct)/0.5)*0.12
    out[int(1.3*SR):int(1.3*SR)+len(ct)] += choir
    bt = t(1.2); boom = lp_fast(rng.standard_normal(len(bt)), 200)*env(len(bt), .002, .4)*2 + np.sin(2*np.pi*45*bt)*env(len(bt), .001, .4)*2
    out[int(1.9*SR):int(1.9*SR)+len(bt)] += np.tanh(boom)
    save("sfx_hemuli_muodonmuutos", out, 0.85)

def potku():  # kenkä osuu palloon + vihellys ilmassa
    out = np.zeros(int(0.9*SR)); kt = t(0.15)
    out[:len(kt)] += (np.sin(2*np.pi*140*kt) + lp_fast(rng.standard_normal(len(kt)), 2500)*0.8)*env(len(kt), .0005, .025)*2
    wt = t(0.6); out[int(.05*SR):int(.05*SR)+len(wt)] += bp(rng.standard_normal(len(wt)), 800, 3000)*np.sin(np.pi*wt/wt[-1])*0.2
    save("sfx_pallo_potku", np.tanh(out), 0.85)
    ht = t(0.3); hit = (np.sin(2*np.pi*110*ht) + lp_fast(rng.standard_normal(len(ht)), 1200))*env(len(ht), .001, .05)*2
    save("sfx_pallo_osuma", np.tanh(hit), 0.85)

if __name__ == "__main__":
    bileet(); naapurit(); haato(); loyly(); lumimyrsky(); tekstari(); hemuli_muutos(); potku(); print("valmis")
