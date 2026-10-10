#!/usr/bin/env python3
"""Lähiösota v2 -äänet. Käyttää generoi_aanet.py:n apufunktioita. Aja: python3 generoi_aanet_v2.py"""
import numpy as np, subprocess, os
from generoi_aanet import SR, D, save, t, env, lp_fast, hp_fast, saw, nf
rng = np.random.default_rng(11)

def engine(name, f_idle, f_top, dur, rough, cutoff, loop=False, pulse=0.6):
    tt = t(dur)
    if loop: f = f_idle + 3 * np.sin(2*np.pi*0.7*tt)
    else: f = f_idle + (f_top - f_idle) * np.clip((tt - 0.2) / (dur * 0.5), 0, 1)
    ph = 2*np.pi*np.cumsum(f)/SR
    s = np.sign(np.sin(ph)) * pulse + np.sin(2*ph) * 0.3 + np.sin(0.5*ph) * 0.4
    s += lp_fast(rng.standard_normal(len(tt)), 1500) * rough
    s = np.tanh(lp_fast(s, cutoff) * 2.5)
    if loop:
        xf = int(0.1*SR); s[:xf] *= np.linspace(0,1,xf); s[-xf:] *= np.linspace(1,0,xf)
    else:
        s *= np.minimum(1, tt/0.05) * np.minimum(1, (tt[-1]-tt)/0.3)
    save(name, s, 0.7)

def shot(gain_crack=1.5, body_cut=900, body_d=0.12, thump_f=70, length=0.5):
    tt = t(length); nz = rng.standard_normal(len(tt))
    return np.tanh((hp_fast(nz,1500)*env(len(tt),.0002,.015)*gain_crack + lp_fast(nz,body_cut)*env(len(tt),.001,body_d)*2
                    + np.sin(2*np.pi*thump_f*tt)*env(len(tt),.001,.06)*2)*2)

def burst(name, n, gap, **kw):
    s1 = shot(**kw); out = np.zeros(int(gap*n*SR) + len(s1))
    for k in range(n):
        i = int(k*gap*SR); out[i:i+len(s1)] += s1 * (0.85 + 0.3*rng.random())
    save(name, out, 0.9)

def knife():
    tt = t(0.35); f = 2500 + 3000*np.sin(np.pi*tt/0.2).clip(0)
    sw = hp_fast(rng.standard_normal(len(tt)), 1500) * np.sin(np.pi*np.clip(tt/0.2,0,1))**2 * 0.6
    st = t(0.15); stab = lp_fast(rng.standard_normal(len(st)), 500)*env(len(st),.001,.03)*2
    sw[int(.18*SR):int(.18*SR)+len(st)] += stab
    save("sfx_puukko", sw, 0.8)

def molotov():
    # heitto: lasi vinkuu ilmassa + särkyminen + liekin humahdus
    out = np.zeros(int(1.6*SR)); tt = t(0.35)
    out[:len(tt)] += hp_fast(rng.standard_normal(len(tt)),2000)*np.sin(np.pi*tt/tt[-1])**2*0.3
    gt = t(0.4)
    glass = sum(np.sin(2*np.pi*f*gt)*np.exp(-gt/d) for f,d in ((3100,.05),(4700,.04),(6100,.03),(5300,.06)))*0.4
    glass += hp_fast(rng.standard_normal(len(gt)),3000)*env(len(gt),.0005,.05)
    i=int(.35*SR); out[i:i+len(gt)] += glass
    ft = t(1.1); whoosh = lp_fast(rng.standard_normal(len(ft)), 700)*np.minimum(1,ft/0.08)*np.exp(-ft/0.5)*2
    i=int(.4*SR); out[i:i+len(ft)] += whoosh
    save("sfx_molotovi", np.tanh(out), 0.85)
    # sateessa: sihahdus ja sammuminen
    out = np.zeros(int(1.3*SR)); out[i:i+len(gt)] += glass*0.8
    ht = t(0.8); hiss = hp_fast(rng.standard_normal(len(ht)),2500)*np.exp(-ht/0.25)*0.6
    out[int(.42*SR):int(.42*SR)+len(ht)] += hiss
    save("sfx_molotovi_sammuu", out, 0.75)

def siren():
    # suomalainen kaksisävel "tyy-tyy"
    tt = t(3.2); f = np.where((tt*1.25)%1 < 0.5, 650, 870).astype(float)
    f = lp_fast(f, 30)
    ph = 2*np.pi*np.cumsum(f)/SR
    s = saw(1, ph/(2*np.pi))*0.5 + np.sign(np.sin(ph))*0.3
    s = lp_fast(s, 3500) * np.minimum(1, tt/0.1) * np.minimum(1,(tt[-1]-tt)/0.3)
    save("sfx_poliisi_sireeni", s, 0.6)

def rain():
    dur = 8; tt = t(dur); s = lp_fast(hp_fast(rng.standard_normal(len(tt)), 400), 6000) * 0.25
    drops = np.zeros(len(tt))
    for _ in range(900):
        i = rng.integers(0, len(tt)-2000); dt = t(0.02)
        drops[i:i+len(dt)] += np.sin(2*np.pi*rng.uniform(1500,4000)*dt)*np.exp(-dt/0.004)*rng.uniform(.1,.5)
    s = s + drops
    xf = int(0.5*SR); s[:xf] = s[:xf]*np.linspace(0,1,xf) + s[-xf:]*np.linspace(1,0,xf); s = s[:-xf]
    save("sfx_sade_loop", s, 0.5)

def trimmer():
    tt = t(1.5); f = 180 + 20*np.sin(2*np.pi*3*tt); ph = 2*np.pi*np.cumsum(f)/SR
    s = np.tanh((saw(1,ph/(2*np.pi)) + lp_fast(rng.standard_normal(len(tt)),3000)*0.4)*3)
    s = hp_fast(lp_fast(s, 5000), 200) * np.minimum(1,tt/0.1)*np.minimum(1,(tt[-1]-tt)/0.2)
    save("sfx_trimmeri", s, 0.6)

def grill():
    tt = t(2.0); s = hp_fast(rng.standard_normal(len(tt)), 2000)*0.15
    for _ in range(120):
        i = rng.integers(0, len(tt)-500); s[i:i+300] += hp_fast(rng.standard_normal(300),3000)*np.exp(-np.arange(300)/60)*0.8
    save("sfx_grilli_kary", s, 0.55)
    # makkaran sylkäisy
    tt = t(0.4); f = 300*np.exp(-tt*6)+90; ph = 2*np.pi*np.cumsum(f)/SR
    s = np.sin(ph)*env(len(tt),.002,.12) + lp_fast(rng.standard_normal(len(tt)),1200)*env(len(tt),.001,.05)
    save("sfx_grilli_ampuu", s, 0.75)

def mortar():
    out = np.zeros(int(2.2*SR)); tt = t(0.4)
    out[:len(tt)] += np.tanh((np.sin(2*np.pi*90*tt)*2 + lp_fast(rng.standard_normal(len(tt)),600))*env(len(tt),.001,.08)*2)
    wt = t(1.0); f = 1800 - 900*wt; ph = 2*np.pi*np.cumsum(f)/SR
    out[int(.3*SR):int(.3*SR)+len(wt)] += np.sin(ph)*0.15*np.minimum(1,wt/0.3)
    et = t(0.9); boom = lp_fast(rng.standard_normal(len(et)),500)*env(len(et),.002,.3)*3 + np.sin(2*np.pi*50*et)*env(len(et),.001,.2)*2
    out[int(1.3*SR):int(1.3*SR)+len(et)] += np.tanh(boom)
    save("sfx_parveke_ampuu", out, 0.9)

def rollator():
    tt = t(1.4); s = np.zeros(len(tt))
    for k in range(10):
        i = int(k*0.14*SR + rng.integers(0,800)); ct = t(0.05)
        c = sum(np.sin(2*np.pi*f*ct) for f in (900,1700,2600))*np.exp(-ct/0.01)*0.3 + lp_fast(rng.standard_normal(len(ct)),2000)*np.exp(-ct/0.008)
        s[i:i+len(ct)] += c
    s += lp_fast(rng.standard_normal(len(tt)),400)*0.15
    save("sfx_rollaattori", s, 0.6)

def crash():
    tt = t(1.0); nz = rng.standard_normal(len(tt))
    s = lp_fast(nz,800)*env(len(tt),.002,.2)*2 + sum(np.sin(2*np.pi*f*tt)*np.exp(-tt/.15) for f in (430,970,1610))*0.4
    save("sfx_ajoneuvo_tormays", np.tanh(s), 0.85)

def jingle():
    # lyhyt torvifanfaari + virvelipärinä
    out = np.zeros(int(1.9*SR))
    for m, st, d in ((60,0,.1),(60,.12,.1),(67,.24,.35),(65,.62,.12),(67,.76,.6)):
        tt = t(d+0.25)
        v = sum(saw(nf(m)*det, tt) for det in (0.997,1.003)) * np.minimum(1, tt/0.02) * np.exp(-np.maximum(0,tt-d)/0.08)
        v = lp_fast(v, 2200 + 800*np.exp(-0)) 
        i = int(st*SR); out[i:i+len(v)] += v*0.35
    for k in range(10):
        st = t(0.08); sn = hp_fast(rng.standard_normal(len(st)),1500)*env(len(st),.001,.03)
        i = int((k*0.024)*SR); out[i:i+len(st)] += sn*0.25*(0.5+k/20)
    save("sfx_tapahtuma_jingle", np.tanh(out*1.5), 0.8)

def say(name, text, voice="fi+m3", pitch=40, speed=155, extra=""):
    raw = os.path.join(D, "_tmp.wav")
    subprocess.run(["espeak-ng","-v",voice,"-p",str(pitch),"-s",str(speed),"-w",raw,text], check=True)
    filt = extra + "highpass=f=250,lowpass=f=3800,acompressor=threshold=-18dB:ratio=4,volume=1.5,aresample=44100"
    for ext, args in (("ogg",["-c:a","libvorbis","-q:a","5"]),("mp3",["-c:a","libmp3lame","-b:a","128k"])):
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",raw,"-af",filt,"-ac","1",*args,os.path.join(D,f"{name}.{ext}")], check=True)
    os.remove(raw)

UNITS = {
  "parvekeampuja": ("fi+m2", 40, [("valittu","Parvekkeella ollaan."),("kuittaus_1","Kohde näkyy."),("kuittaus_2","Tähtään."),("hyokkays","Tulta parvekkeelta!"),("baariin","Mää käyn yhellä.")]),
  "mummo":         ("fi+f2", 75, [("valittu","No mitäs nyt, kultaseni?"),("kuittaus_1","Kyllä mummo ehtii."),("kuittaus_2","Hiljaa hyvä tulee."),("hyokkays","Nyt saa rollaattorista!"),("baariin","Yksi sherry vain.")]),
  "isa_trimmeri":  ("fi+m1", 25, [("valittu","Mitä se nyt taas?"),("kuittaus_1","Isä hoitaa."),("kuittaus_2","Pusikko pois."),("hyokkays","Trimmeriä naamaan!"),("baariin","Mää käyn yhellä saunakaljalla.")]),
  "grillimestari": ("fi+m3", 35, [("valittu","Makkarat tulilla."),("kuittaus_1","Selvä pomo."),("kuittaus_2","Hiilet hehkuu."),("hyokkays","Syökää makkaraa!"),("baariin","Grilli jäähtyy, mää käyn yhellä.")]),
  "volvo":         ("fi+m1", 30, [("valittu","Volvo käy."),("kuittaus_1","Kaasu pohjaan."),("kuittaus_2","Hypätkää kyytiin."),("hyokkays","Jyrätään!")]),
  "dnepr":         ("fi+m3", 45, [("valittu","Dnepr valmiina."),("kuittaus_1","Sivuvaunu täynnä."),("hyokkays","Emma laulaa!")]),
  "monkija":       ("fi+m3", 60, [("valittu","Mönkkäri käy."),("kuittaus_1","Maastoon!")]),
  "lada":          ("fi+m2", 40, [("valittu","Lada starttas."),("kuittaus_1","Jos se vaan lähtee.")]),
}
EVENTS = {
  "poliisipartio": "Poliisipartio liikkeellä! Humalaiset putkaan.",
  "alkon_alennus": "Alkossa alennusmyynti!",
  "sadekuuro": "Sadekuuro! Molotovit eivät syty.",
  "panttiautomaatti_rikki": "Pantinpalautusautomaatti rikki!",
  "pihakirppis": "Pihakirppis! Tölkkejä tarjolla.",
  "saunailta": "Saunailta Peltolammilla.",
  "taloyhtion_kokous": "Taloyhtiön kokous Multisillassa.",
  "bussi3_myohassa": "Bussi kolme myöhässä.",
  "kesajuhlat": "Kesäjuhlat! Aselepo ja tuplapantit.",
}

if __name__ == "__main__":
    engine("sfx_dnepr", 30, 55, 2.0, 0.35, 2200); engine("sfx_dnepr_loop", 32, 32, 3.0, 0.35, 2200, loop=True)
    engine("sfx_volvo", 22, 40, 2.2, 0.2, 900, pulse=0.8); engine("sfx_volvo_loop", 24, 24, 3.0, 0.2, 900, loop=True, pulse=0.8)
    engine("sfx_monkija", 45, 80, 1.6, 0.3, 3000); engine("sfx_lada", 26, 45, 2.0, 0.5, 1400)
    burst("sfx_laukaus_emma", 8, 0.11, body_cut=700, body_d=0.15, thump_f=55)
    burst("sfx_laukaus_suomikp", 6, 0.07, body_cut=1100, body_d=0.09, thump_f=80)
    knife(); molotov(); siren(); rain(); trimmer(); grill(); mortar(); rollator(); crash(); jingle()
    for unit, (voice, pitch, lines) in UNITS.items():
        for key, text in lines: say(f"aani_{unit}_{key}", text, voice, pitch)
    for ev, text in EVENTS.items(): say(f"aani_tapahtuma_{ev}", text, "fi+m3", 30, 145)
    print("valmis")
