#!/usr/bin/env python3
"""Lähiösota: lisämusiikit (piiritys, kännirynnäkkö, valikko). Kaikki synteesiä, ei samplejä."""
import numpy as np
from generoi_aanet import SR, save, t, env, lp_fast, hp_fast, saw, nf
rng = np.random.default_rng(99)

class Mix:
    def __init__(s, bpm, bars):
        s.beat = 60/bpm; s.bar = 4*s.beat; s.N = int(bars*s.bar*SR); s.m = np.zeros((s.N, 2))
    def add(s, sig, start, pan=0.0, g=1.0):
        i = int(start*SR); j = min(s.N, i+len(sig))
        if i >= s.N: return
        s.m[i:j, 0] += sig[:j-i]*g*(1-pan); s.m[i:j, 1] += sig[:j-i]*g*(1+pan)
    def done(s, name, drive=1.4, vol=0.85):
        xf = int(0.04*SR); s.m[:xf] *= np.linspace(0,1,xf)[:,None]; s.m[-xf:] *= np.linspace(1,0,xf)[:,None]
        save(name, np.tanh(s.m*drive), vol)

def kick(f0=45, d=0.12):
    kt = t(0.4); return np.tanh(np.sin(2*np.pi*(f0*kt + 90*0.04*(1-np.exp(-kt/0.04))))*env(len(kt),.001,d)*3)
def snare(tone=190, d=0.08):
    st = t(0.3); x = rng.standard_normal(len(st))*env(len(st),.001,d) + 0.5*np.sin(2*np.pi*tone*st)*env(len(st),.001,.05)
    return np.tanh(hp_fast(x, 300)*2)
def hat():
    ht = t(0.06); return hp_fast(rng.standard_normal(len(ht)), 7000)*env(len(ht),.0005,.015)
def anvil(base=523):
    at = t(0.7); return sum(np.sin(2*np.pi*base*r*at)*np.exp(-at/d) for r,d in ((1,.3),(2.5,.18),(4,.1),(6.33,.07)))*env(len(at),.0005,1)
def guitar(m, dur, sustain=0.25, drive=9):
    tt = t(dur); g = sum(saw(nf(m+iv), tt + rng.random()*0.001) for iv in (0,7,12))
    return lp_fast(hp_fast(np.tanh(g*drive)*env(len(tt),.002,sustain), 90), 4000)
def bass(m, dur, d=0.4):
    tt = t(dur); return np.tanh(lp_fast(saw(nf(m-12), tt)*env(len(tt),.003,d), 800)*3)
def pad(ms, dur, cut=1600):
    tt = t(dur); p = sum(saw(nf(m)*dt, tt) for m in ms for dt in (0.995,1.005))
    return lp_fast(p, cut)*np.minimum(1,tt/0.6)*np.minimum(1,(tt[-1]-tt)/0.6+1e-3)
def accordion(m, dur):
    tt = t(dur); vib = 1 + 0.004*np.sin(2*np.pi*5.5*tt)
    ph = np.cumsum(nf(m)*vib)/SR
    a = sum(np.sign(np.sin(2*np.pi*ph*dt))*w for dt,w in ((1,.4),(1.006,.3),(2.003,.15)))
    return lp_fast(a, 2800)*np.minimum(1,tt/0.02)*np.minimum(1,(tt[-1]-tt)/0.03+1e-3)

# ---------- 1) PIIRITYS, 95 BPM ----------
def piiritys():
    M = Mix(95, 40); b8 = M.beat/2; b16 = M.beat/4
    riff = [38,0,38,38,41,0,38,36, 38,0,38,38,43,41,38,0]  # 16-osat yhdessä tahdissa (2 tahtia = 16 kahdeksasosaa)
    chords = [38,38,34,36]
    for b in range(40):
        t0 = b*M.bar; sec = b//8
        # marssirumpu: 16-osa-virvelikuvio + bassorumpu 1 ja 3 (half-time)
        for q in range(4):
            if True:
                if q in (0,2): M.add(kick(40,.18), t0+q*M.beat, g=1.0)
                if q == 2: M.add(snare(170,.12), t0+q*M.beat, g=0.6)
            for s16 in range(4):
                pat = (1,0,1,1) if q % 2 == 0 else (1,1,0,1)
                if pat[s16] and sec != 3: M.add(snare(230,.03), t0+q*M.beat+s16*b16, pan=0.25, g=0.13 + (0.1 if s16==0 else 0))
            if sec >= 1 and sec != 3: M.add(hat(), t0+q*M.beat+b8, pan=-0.3, g=0.12)
        if b % 2 == 0: M.add(anvil(440), t0, pan=-0.4, g=0.3)
        if sec in (1,2,4):
            half = (b % 2)*8
            for e in range(8):
                m = riff[half+e]
                if not m: continue
                M.add(bass(m, b8*0.9, .5), t0+e*b8, g=0.4)
                for pan, det in ((-0.7,0),(0.7,0.08)):
                    M.add(guitar(m-2+det*0, b8*0.9, .3), t0+e*b8, pan=pan, g=0.15)
        else:  # osa 3: hidas sointumatto + kuoro, osa 0 loppu
            m = chords[b % 4]
            M.add(guitar(m, M.bar*0.95, 2.0), t0, pan=-0.6, g=0.12); M.add(guitar(m, M.bar*0.95, 2.0), t0, pan=0.6, g=0.12)
            M.add(bass(m, M.bar*0.95, 2.0), t0, g=0.35)
        if sec in (2,4):  # raskas vaskimelodia
            mel = [62,0,62,65,64,62,60,57] if b%2==0 else [62,0,69,67,65,64,62,0]
            for e, m in enumerate(mel):
                if m: M.add(pad([m, m-12], b8*1.6, 2400), t0+e*b8, pan=0.1, g=0.08)
        if sec in (3,4) and b % 2 == 0:
            M.add(pad([62,65,69], M.bar*2, 1400), t0, g=0.035)
    M.done("musiikki_piiritys")

# ---------- 2) KÄNNIRYNNÄKKÖ, 130 BPM, polkkaa + industrialia ----------
def kannirynnakko():
    M = Mix(130, 64); b8 = M.beat/2
    prog = [45,45,40,40, 45,45,40,45, 50,50,45,45, 40,40,45,45]   # Am Am E E ... (MIDI-juuret)
    minor = {45:(0,3,7), 40:(0,4,7), 50:(0,3,7)}
    melA = [69,72,76,76,74,72,71,72, 71,68,64,64,68,71,74,71, 69,72,76,79,77,76,74,72, 71,74,71,68,69,0,69,0]
    for b in range(64):
        t0 = b*M.bar; sec = b//16; root = prog[b % 16]
        rock = sec in (1,3)  # vuorotellen polkkaa ja rokkia
        if rock:
            for q in range(4):
                M.add(kick(48,.1), t0+q*M.beat, g=0.9)
                if q in (1,3): M.add(snare(200,.08), t0+q*M.beat, g=0.55)
                M.add(hat(), t0+q*M.beat+b8, pan=0.3, g=0.15)
            for e in range(8):
                m = root - 12 + (0 if e not in (3,6) else 3)
                M.add(bass(m+12, b8*0.9, .3), t0+e*b8, g=0.35)
                M.add(guitar(m+12, b8*0.9, .2), t0+e*b8, pan=-0.7, g=0.14); M.add(guitar(m+12, b8*0.9, .2), t0+e*b8, pan=0.7, g=0.14)
        else:
            # umpa-pa: basso 1 ja 3, sointu 2 ja 4 (offbeat), virveli takapotkuna
            for q in range(4):
                if q % 2 == 0:
                    M.add(kick(55,.08), t0+q*M.beat, g=0.8)
                    M.add(bass(root + (0 if q == 0 else 7), M.beat*0.8, .2), t0+q*M.beat, g=0.45)
                else:
                    ch = sum(np.pad(accordion(root+12+iv, M.beat*0.35), (0,0)) for iv in minor[root])
                    M.add(ch, t0+q*M.beat, pan=-0.3, g=0.09)
                    M.add(snare(240,.04), t0+q*M.beat, g=0.3)
                    M.add(guitar(root+12, M.beat*0.3, .08, drive=6), t0+q*M.beat, pan=0.6, g=0.08)
                M.add(hat(), t0+q*M.beat+b8, pan=0.3, g=0.08)
        # melodia: polkkaosissa harmonikka, rokkiosissa särökitara + harmonikka
        if sec != 0 or b >= 4:
            ph = (b % 4)*8
            for e in range(8):
                m = melA[ph+e]
                if not m: continue
                if rock and b % 8 >= 4: m += 12 if m < 70 else 0
                M.add(accordion(m, b8*0.92), t0+e*b8, pan=0.15, g=0.11 if not rock else 0.09)
                if rock: M.add(guitar(m-12, b8*0.92, .3, drive=4), t0+e*b8, pan=-0.15, g=0.06)
        if b % 8 == 0: M.add(anvil(587), t0, pan=-0.4, g=0.3)
        if b % 16 == 15:  # hikka-fill tahdin lopussa :)
            for k in range(3): M.add(np.sin(2*np.pi*nf(84)*t(0.06))*env(int(0.06*SR),.001,.02), t0+3*M.beat+k*M.beat/3, g=0.15)
    M.done("musiikki_kannirynnakko", drive=1.3)

# ---------- 3) VALIKKO, 80 BPM, ~48 s ----------
def valikko():
    M = Mix(80, 16); b8 = M.beat/2
    chords = [[38,45,50],[34,41,46],[36,43,48],[33,40,45]]
    ost = [50,50,57,50,53,50,57,55]
    for b in range(16):
        t0 = b*M.bar; c = chords[(b//2) % 4]
        if b % 2 == 0: M.add(pad([n+12 for n in c], M.bar*2, 1300), t0, g=0.05)
        M.add(bass(c[0]+12, M.bar*0.95, 3.0), t0, g=0.3)
        for e, m in enumerate(ost):
            tt = t(b8*0.9); s = (np.sign(np.sin(2*np.pi*nf(m+12)*tt))*0.5)*env(len(tt),.003,.12)
            M.add(lp_fast(s, 1800 + 300*(b//4)), t0+e*b8, pan=(-0.4 if e%2 else 0.4), g=0.06)
        if b >= 4:
            M.add(kick(40,.2), t0, g=0.8); M.add(kick(40,.2), t0+2*M.beat, g=0.6)
        if b >= 8:
            M.add(snare(160,.15), t0+M.beat, g=0.3); M.add(snare(160,.15), t0+3*M.beat, g=0.3)
        if b % 4 == 0: M.add(anvil(392), t0, pan=0.3, g=0.35)
        if b >= 12:
            for e in range(8): M.add(guitar(c[0]+12, b8*0.9, .25), t0+e*b8, pan=(-0.7 if e%2 else 0.7), g=0.07)
    M.done("musiikki_valikko", drive=1.2, vol=0.8)

if __name__ == "__main__":
    import sys
    for f in (sys.argv[1:] or ["piiritys","kannirynnakko","valikko"]): globals()[f]()
    print("valmis")
