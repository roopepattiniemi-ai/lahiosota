#!/usr/bin/env python3
"""V3: metsäpeikot ja vesihiisi. Aja: python3 generoi_aanet_olennot.py"""
import numpy as np, subprocess, os
from generoi_aanet import SR, D, save, t, env, lp_fast, hp_fast, saw, nf
from generoi_aanet_v2 import say
rng = np.random.default_rng(77)

def bandpass(x, lo, hi): return lp_fast(hp_fast(x, lo), hi)

# ---------- VESIHIISI ----------
def hiisi_sihina(name, dur, seed, rise=True):
    """Kaameaa, eläimellistä sihinää: kaistanpäästetty kohina, jonka formantti liukuu + kurkun rahina."""
    r = np.random.default_rng(seed); tt = t(dur); n = r.standard_normal(len(tt))
    # kaksi liikkuvaa "suun" formanttia, toteutetaan paloittain
    out = np.zeros(len(tt)); blk = int(0.03*SR); hann = np.hanning(2*blk)
    for i in range(0, len(tt)-2*blk, blk):
        p = i/len(tt); fc = 2500 + 2500*(p if rise else 1-p) + 600*np.sin(2*np.pi*3*p + seed)
        seg = n[i:i+2*blk]
        out[i:i+2*blk] += bandpass(seg, fc*0.6, fc*1.6)*hann
    hiss = out + hp_fast(n, 6000)*0.25
    # kurkun rahina (amplitudimoduloitu matala sorina)
    rasp = lp_fast(np.sign(np.sin(2*np.pi*np.cumsum(70 + 25*r.standard_normal(len(tt)).cumsum()/SR*3)/SR)), 1200)*0.25
    am = 1 + 0.6*np.sin(2*np.pi*(9 + 4*r.random())*tt)
    s = (hiss*am + rasp*(0.5 + 0.5*np.sin(np.pi*tt/dur)))
    s *= np.minimum(1, tt/(0.25 if rise else 0.05)) * np.minimum(1, (tt[-1]-tt)/0.35)
    # aavemainen kaiku
    d = int(0.13*SR); e = np.zeros(len(s)+3*d); e[:len(s)] += s
    for k, g in ((1,.35),(2,.15),(3,.06)): e[k*d:k*d+len(s)] += s*g
    save(name, e, 0.8)

def kuplat(name, dur, seed, loop=False):
    r = np.random.default_rng(seed); tt = t(dur); s = np.zeros(len(tt))
    for _ in range(int(dur*14)):
        i = r.integers(0, len(tt)-4000); bt = t(r.uniform(0.03, 0.09))
        f0 = r.uniform(250, 900); f = f0*(1 + 1.5*bt/bt[-1])   # kupla: nouseva sävel
        b = np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-bt/0.02)*r.uniform(.3,1)
        s[i:i+len(bt)] += b
    s += lp_fast(r.standard_normal(len(tt)), 300)*0.15   # syvä vesimurina
    if loop:
        xf = int(0.3*SR); s[:xf] = s[:xf]*np.linspace(0,1,xf) + s[-xf:]*np.linspace(1,0,xf); s = s[:-xf]
    else: s *= np.minimum(1, tt/0.4)
    save(name, s, 0.6)

def loiske(name, big, seed):
    r = np.random.default_rng(seed); dur = 1.6 if big else 1.0; tt = t(dur)
    body = lp_fast(r.standard_normal(len(tt)), 1800 if big else 2500)*env(len(tt), .005, .25 if big else .15)*2
    thump = np.sin(2*np.pi*(60 if big else 90)*tt)*env(len(tt), .002, .1)
    drops = np.zeros(len(tt))
    for _ in range(25 if big else 12):
        i = int(r.uniform(.1, dur-.1)*SR); dt = t(0.03)
        drops[i:i+len(dt)] += np.sin(2*np.pi*r.uniform(800,2500)*dt)*np.exp(-dt/.006)*r.uniform(.1,.4)
    save(name, np.tanh(body + thump + drops), 0.8)

def hiisi_hyokkays():
    out = np.zeros(int(1.3*SR)); tt = t(0.5)
    # märkä lyönti + karjahdus-sihahdus
    whip = bandpass(rng.standard_normal(len(tt)), 800, 5000)*np.sin(np.pi*np.clip(tt/0.18,0,1))**2
    out[:len(tt)] += whip*0.5
    st = t(0.3); smack = lp_fast(rng.standard_normal(len(st)), 1500)*env(len(st), .001, .04)*2
    out[int(.18*SR):int(.18*SR)+len(st)] += smack
    ht = t(0.9); hiss = bandpass(rng.standard_normal(len(ht)), 2500, 7000)*env(len(ht), .01, .3)*0.8
    out[int(.2*SR):int(.2*SR)+len(ht)] += hiss
    save("sfx_vesihiisi_hyokkays", np.tanh(out*1.5), 0.85)

# ---------- PEIKKO ----------
def growl(name, dur, f0, seed, loud=1.0, roar=False):
    r = np.random.default_rng(seed); tt = t(dur)
    jitter = lp_fast(r.standard_normal(len(tt)), 15)*0.25*f0*30
    shape = np.sin(np.pi*np.clip(tt/dur, 0, 1))**(0.5 if roar else 1)
    f = f0*(1 + (0.5*shape if roar else 0.1*np.sin(2*np.pi*1.3*tt))) + jitter
    ph = 2*np.pi*np.cumsum(f)/SR
    src = saw(1, ph/(2*np.pi)) + 0.7*np.sign(np.sin(ph*0.5))   # subharmoninen rahina
    src += lp_fast(r.standard_normal(len(tt)), 2500)*(0.8 if roar else 0.4)
    # vokaaliformantit (öö -> aa karjunnassa)
    v = bandpass(src, 250, 900) + bandpass(src, 600 if not roar else 900, 1600)*0.7 + bandpass(src, 2000, 3500)*(0.4 if roar else 0.15)
    am = 1 + 0.35*np.sin(2*np.pi*(22 + 6*r.random())*tt)   # kurkun pärinä
    s = np.tanh(v*am*2.5*loud)*shape*np.minimum(1, (tt[-1]-tt)/0.15)
    save(name, s, 0.6 if roar else 0.85)

def kivi():
    out = np.zeros(int(1.2*SR)); tt = t(0.3)
    out[:len(tt)] += lp_fast(rng.standard_normal(len(tt)), 600)*np.sin(np.pi*tt/tt[-1])*0.5   # heitto-ähkäisy
    ft = t(0.45); whoosh = bandpass(rng.standard_normal(len(ft)), 400, 2500)*np.sin(np.pi*ft/ft[-1])**2*0.4
    out[int(.15*SR):int(.15*SR)+len(ft)] += whoosh
    save("sfx_peikko_kivi_heitto", out, 0.7)
    ht = t(0.6); hit = lp_fast(rng.standard_normal(len(ht)), 900)*env(len(ht), .001, .07)*2 + np.sin(2*np.pi*75*ht)*env(len(ht), .001, .08)*1.5
    for _ in range(6):  # sora rapisee
        i = int(rng.uniform(.05, .4)*SR); dt = t(0.02); hit[i:i+len(dt)] += hp_fast(rng.standard_normal(len(dt)), 2000)*np.exp(-dt/.005)*0.4
    save("sfx_peikko_kivi_osuma", np.tanh(hit), 0.85)

def peikko_askel():
    out = np.zeros(int(1.2*SR))
    for k in range(2):
        tt = t(0.4); s = np.sin(2*np.pi*48*tt)*env(len(tt), .003, .12) + lp_fast(rng.standard_normal(len(tt)), 300)*env(len(tt), .002, .06)
        i = int(k*0.55*SR); out[i:i+len(tt)] += s
    save("sfx_peikko_askel", np.tanh(out*2), 0.8)

def peikko_kaatuu():
    out = np.zeros(int(2.0*SR)); tt = t(0.9)
    g = np.zeros(1)  # placeholder
    growl("_tmp_kaatuu", 0.9, 60, 9, roar=False)
    for ext in ("ogg","mp3"): os.remove(os.path.join(D, f"_tmp_kaatuu.{ext}"))
    # kaatumisen tömähdys + valitus synteesinä suoraan
    tt = t(0.9); f = 110*np.exp(-tt*1.2); ph = 2*np.pi*np.cumsum(f)/SR
    moan = np.tanh(bandpass(saw(1, ph/(2*np.pi)) + lp_fast(rng.standard_normal(len(tt)),1500)*0.4, 200, 1200)*3)*np.sin(np.pi*tt/tt[-1])
    out[:len(tt)] += moan*0.8
    bt = t(1.0); boom = lp_fast(rng.standard_normal(len(bt)), 250)*env(len(bt), .003, .2)*3 + np.sin(2*np.pi*40*bt)*env(len(bt), .002, .25)*2
    out[int(.8*SR):int(.8*SR)+len(bt)] += np.tanh(boom)
    save("sfx_peikko_kaatuu", out, 0.85)

def creature_voice(name, text, pitch, speed, chain):
    raw = os.path.join(D, "_tmp.wav")
    subprocess.run(["espeak-ng","-v","fi+m1","-p",str(pitch),"-s",str(speed),"-w",raw,text], check=True)
    for ext, args in (("ogg",["-c:a","libvorbis","-q:a","5"]),("mp3",["-c:a","libmp3lame","-b:a","128k"])):
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",raw,"-af",chain,"-ac","1",*args,os.path.join(D,f"{name}.{ext}")], check=True)
    os.remove(raw)

if __name__ == "__main__":
    # vesihiisi – sihinät (Roopen erityistoive): 3 vaihtelua + pitkä ennakkosihinä
    hiisi_sihina("sfx_vesihiisi_sihina_1", 1.6, 1); hiisi_sihina("sfx_vesihiisi_sihina_2", 2.2, 2, rise=False)
    hiisi_sihina("sfx_vesihiisi_sihina_3", 1.1, 3); hiisi_sihina("sfx_vesihiisi_ennakko", 4.0, 4)
    kuplat("sfx_vesihiisi_kuplat", 3.0, 5); kuplat("sfx_vesihiisi_kuplat_loop", 4.0, 6, loop=True)
    loiske("sfx_vesihiisi_nousu", True, 7); loiske("sfx_vesihiisi_sukellus", False, 8); hiisi_hyokkays()
    # peikko
    growl("sfx_peikko_murina_1", 1.4, 55, 11); growl("sfx_peikko_murina_2", 1.0, 48, 12); growl("sfx_peikko_murina_3", 1.8, 62, 13)
    growl("sfx_peikko_karjunta_1", 1.6, 70, 14, roar=True, loud=1.5); growl("sfx_peikko_karjunta_2", 2.0, 60, 15, roar=True, loud=1.5)
    kivi(); peikko_askel(); peikko_kaatuu()
    # olentojen huudot puhekuplien pariksi
    troll = "asetrate=22050*0.62,aresample=44100,atempo=1.25,lowpass=f=2500,acompressor=threshold=-15dB:ratio=5,volume=2,loudnorm=I=-16:TP=-1.5"
    for k, txt in (("mun_metsa","Mun metsä!"),("tolkit","Anna tölkit!"),("pois","Pois täältä!"),("nalka","Peikko nälkä!")):
        creature_voice(f"aani_peikko_{k}", txt, 20, 120, troll)
    hiisi = "asetrate=22050*0.8,aresample=44100,atempo=1.1,flanger=delay=3:depth=4,aecho=0.7:0.6:90:0.4,highpass=f=300,volume=1.8,loudnorm=I=-16:TP=-1.5"
    for k, txt in (("tulkaa","Tulkaa veteen..."),("syvyyksiin","Syvyyksiin!"),("sss","Ssssss...")):
        creature_voice(f"aani_vesihiisi_{k}", txt, 60, 110, hiisi)
    say("aani_tapahtuma_peikot", "Metsäpeikot heräsivät! Varokaa metsiä.", "fi+m3", 30, 145)
    say("aani_tapahtuma_vesihiisi", "Vesihiisi liikkuu! Pysykää kaukana rannasta.", "fi+m3", 30, 145)
    print("valmis")
