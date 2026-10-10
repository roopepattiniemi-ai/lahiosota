#!/usr/bin/env python3
"""Kännitilojen äänet (hikka, yökkäys, kippis, humalarepliikit)."""
import numpy as np
from generoi_aanet import SR, save, t, env, lp_fast, hp_fast
from generoi_aanet_v2 import say
rng = np.random.default_rng(23)

def hiccup(name, f0, seed):
    r = np.random.default_rng(seed); tt = t(0.35)
    f = f0 * (1 + 0.6*np.exp(-tt/0.03)); ph = 2*np.pi*np.cumsum(f)/SR
    v = (np.sin(ph) + 0.5*np.sin(2*ph) + 0.25*np.sin(3*ph)) * env(len(tt), .002, .06)
    click = lp_fast(r.standard_normal(len(tt)), 1800) * env(len(tt), .0005, .01) * 1.5
    save(name, lp_fast(v + click, 3000), 0.7)

def retch(name, dur, seed):
    r = np.random.default_rng(seed); tt = t(dur)
    f = 95 + 40*np.sin(2*np.pi*2.5*tt) + 15*r.standard_normal(len(tt)).cumsum()/np.sqrt(SR)
    ph = 2*np.pi*np.cumsum(f)/SR
    voice = np.tanh((np.sign(np.sin(ph))*0.6 + lp_fast(r.standard_normal(len(tt)), 900)*0.8)*2)
    voice = lp_fast(voice, 1300)
    am = np.clip(np.sin(2*np.pi*1.6*tt), 0, 1)**0.5  # "öök... öök"
    s = voice * am * np.minimum(1, (tt[-1]-tt)/0.2)
    # loiskahdus lopuksi
    st = t(0.5); splash = lp_fast(r.standard_normal(len(st)), 1500)*env(len(st), .005, .12)
    out = np.concatenate([s, splash*1.2])
    save(name, out, 0.75)

def clink_cheers():
    out = np.zeros(int(0.8*SR))
    for dt, f0 in ((0, 1800), (0.012, 2050)):
        tt = t(0.6); s = sum(np.sin(2*np.pi*f0*k*tt)*np.exp(-tt/(0.12/k)) for k in (1, 2.4, 3.9))
        i = int(dt*SR); out[i:i+len(s)] += s
    save("sfx_kippis_kilistys", out, 0.7)

if __name__ == "__main__":
    for i, f in enumerate((180, 230, 140), 1): hiccup(f"sfx_hikka_{i}", f, i)
    retch("sfx_yokkays_1", 1.0, 5); retch("sfx_yokkays_2", 1.4, 6)
    clink_cheers()
    drunk = "asetrate=22050*0.95,aresample=44100,vibrato=f=4:d=0.25,"
    lines = {"laatta_1": "Nyt lentää laatta!", "laatta_2": "Ei hyvä... ei hyvä...", "yks_viela": "Yks vielä!",
             "ups_sori": "Ups, sori!", "kippis": "Kippis!", "baariin": "Baariin!", "hik": "Hik!", "kotiin": "Mää lähen kotiin..."}
    for k, txt in lines.items(): say(f"aani_kanni_{k}", txt, "fi+m3", 42, 135, extra=drunk)
    print("valmis")

def splat():
    r = np.random.default_rng(31); out = np.zeros(int(0.9*SR))
    tt = t(0.6); body = lp_fast(r.standard_normal(len(tt)), 700)*env(len(tt), .003, .09)*2
    thud = np.sin(2*np.pi*(90*tt - 60*tt**2))*env(len(tt), .002, .07)
    out[:len(tt)] += np.tanh(body + thud)
    for _ in range(9):  # roiskeita
        i = int(r.uniform(0.05, 0.55)*SR); dt = t(0.08)
        out[i:i+len(dt)] += lp_fast(r.standard_normal(len(dt)), r.uniform(900, 2200))*env(len(dt), .001, .015)*r.uniform(.3, .7)
    save("sfx_laatta_latsahdys", out, 0.8)

def flies_loop():
    r = np.random.default_rng(32); tt = t(4.0); s = np.zeros(len(tt))
    for k in range(3):
        f = 210 + 25*k + 18*np.sin(2*np.pi*(0.5 + 0.25*k)*tt + k) ; ph = 2*np.pi*np.cumsum(f)/SR
        s += saw(1, ph/(2*np.pi)) * (0.6 + 0.4*np.sin(2*np.pi*(0.3+0.2*k)*tt + 2*k))**2
    s += lp_fast(r.standard_normal(len(tt)), 600)*0.15  # lätän kupliminen
    s = lp_fast(hp_fast(s, 150), 2500)
    xf = int(0.3*SR); s[:xf] = s[:xf]*np.linspace(0,1,xf) + s[-xf:]*np.linspace(1,0,xf); s = s[:-xf]
    save("sfx_laatta_karpaset_loop", s, 0.35)

from generoi_aanet import saw
if __name__ == "__main__":
    splat(); flies_loop()
