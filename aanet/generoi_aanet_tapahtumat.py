#!/usr/bin/env python3
"""Tapahtumien ennakkovaroitus- ja loppumisäänet."""
import numpy as np
from generoi_aanet import SR, save, t, env, lp_fast, saw, nf

def warning():
    out = np.zeros(int(1.3*SR))
    for k in range(2):  # kaksi matalaa "radiopiippausta"
        tt = t(0.25); s = (np.sign(np.sin(2*np.pi*nf(57)*tt))*0.5 + np.sin(2*np.pi*nf(69)*tt)*0.5)*np.minimum(1,tt/0.01)*np.minimum(1,(tt[-1]-tt)/0.02)
        i = int(k*0.45*SR); out[i:i+len(s)] += lp_fast(s, 2500)
    tt = t(0.6); rise = saw(1, np.cumsum(nf(57)*(1+0.3*tt/tt[-1]))/SR)*np.minimum(1,tt/0.3)*np.exp(-tt/0.4)
    out[int(0.7*SR):int(0.7*SR)+len(tt)] += lp_fast(rise, 1500)*0.4
    save("sfx_tapahtuma_varoitus", out, 0.6)

def ended():
    out = np.zeros(int(0.9*SR))
    for m, st in ((67, 0), (60, .15)):
        tt = t(0.5); s = (np.sign(np.sin(2*np.pi*nf(m)*tt))*.4 + np.sin(2*np.pi*nf(m+12)*tt)*.4)*env(len(tt), .004, .18)
        i = int(st*SR); out[i:i+len(s)] += lp_fast(s, 3500)
    save("sfx_tapahtuma_loppui", out, 0.6)

if __name__ == "__main__":
    warning(); ended()
