#!/usr/bin/env python3
"""Lähiösota: kaikki äänet generoidaan tällä skriptillä (100 % itse tehtyä, ei samplejä).
Vaatii: numpy, ffmpeg, espeak-ng (puheet). Aja: python3 generoi_aanet.py"""
import numpy as np, subprocess, os, wave
SR = 44100
D = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)

def save(name, x, vol=0.9):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1: x = np.stack([x, x], 1)
    x = x / (np.max(np.abs(x)) + 1e-9) * vol
    tmp = os.path.join(D, name + ".wav")
    with wave.open(tmp, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())
    for ext, args in (("ogg", ["-c:a", "libvorbis", "-q:a", "5"]), ("mp3", ["-c:a", "libmp3lame", "-b:a", "160k"])):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, *args, os.path.join(D, f"{name}.{ext}")], check=True)
    os.remove(tmp)

def t(sec): return np.arange(int(sec * SR)) / SR
def env(n, a=0.002, d=0.2):
    tt = np.arange(n) / SR
    return np.minimum(1, tt / a) * np.exp(-tt / d)
def lp(x, a):  # yksinkertainen 1-napainen alipäästö, a in (0,1)
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s += a * (x[i] - s); y[i] = s
    return y
def lp_fast(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / cutoff) ** 4); return np.fft.irfft(X, len(x))
def hp_fast(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (cutoff / np.maximum(f, 1)) ** 4); return np.fft.irfft(X, len(x))
def saw(f, tt): return 2 * ((f * tt) % 1) - 1
def nf(m): return 440 * 2 ** ((m - 69) / 12)

# ---------------- Taistelukappale ----------------
def battle_track():
    bpm = 112; beat = 60 / bpm; bar = 4 * beat; bars = 48
    N = int(bars * bar * SR); mix = np.zeros((N, 2))
    def add(sig, start, pan=0.0, g=1.0):
        i = int(start * SR); j = min(N, i + len(sig))
        if i >= N: return
        mix[i:j, 0] += sig[:j - i] * g * (1 - pan) ; mix[i:j, 1] += sig[:j - i] * g * (1 + pan)
    # soundit
    kt = t(0.35); kick = np.sin(2 * np.pi * (45 * kt + 90 * 0.04 * (1 - np.exp(-kt / 0.04)))) * env(len(kt), 0.001, 0.12)
    kick = np.tanh(kick * 3)
    st = t(0.3); snare = (rng.standard_normal(len(st)) * env(len(st), 0.001, 0.08) + 0.5 * np.sin(2 * np.pi * 190 * st) * env(len(st), 0.001, 0.05))
    snare = np.tanh(hp_fast(snare, 300) * 2)
    ht = t(0.06); hat = hp_fast(rng.standard_normal(len(ht)), 7000) * env(len(ht), 0.0005, 0.015)
    at = t(0.6)  # metallinen "alasin"-isku: epäharmoniset osasävelet
    anvil = sum(np.sin(2 * np.pi * f * at) * np.exp(-at / d) for f, d in ((523, .25), (1307, .15), (2093, .1), (3311, .07))) * env(len(at), 0.0005, 1)
    # riffi (E-mollin power chordit, drop-D-henkinen)
    riff_A = [40, 40, 0, 40, 43, 0, 40, 38]  # kahdeksasosat, 0 = tauko
    riff_B = [36, 36, 0, 36, 38, 0, 38, 40]
    chords = [40, 40, 36, 38]  # E E C D
    for b in range(bars):
        t0 = b * bar
        sec = b // 8  # 6 osaa x 8 tahtia
        intro = sec == 0; breakdown = sec == 3
        # rummut
        for q in range(4):
            tq = t0 + q * beat
            if not intro or b >= 4:
                if not breakdown or q in (0, 2): add(kick, tq, g=0.9)
                if q in (1, 3) and not breakdown: add(snare, tq, g=0.55)
            if intro and q == 0: add(kick, tq, g=0.9)
            if not intro:
                for e in (0, 0.5): add(hat, tq + e * beat, pan=0.3, g=0.18)
            if (not intro and q == 1 and b % 2 == 1 and not breakdown) or (b == 7 and q in (2, 3)): add(snare, tq + beat / 2, g=0.35)
        if b % 4 == 0 or (breakdown and b % 2 == 0) or intro: add(anvil, t0, pan=-0.4, g=0.35 if not intro else 0.5)
        if intro and b < 4: continue
        # basso + kitara
        riff = riff_A if (b % 4) < 2 else riff_B
        if sec in (2, 4): riff = [chords[b % 4]] * 8
        for e, m in enumerate(riff):
            if m == 0: continue
            dur = beat / 2 * 0.92; tt = t(dur)
            st0 = t0 + e * beat / 2
            # basso
            bs = saw(nf(m - 12), tt) * env(len(tt), 0.003, 0.4)
            add(np.tanh(lp_fast(bs, 900) * 3), st0, g=0.35)
            if breakdown and e % 2: continue
            # kitara: power chord, 2 tuplattua kanavaa
            for pan, det in ((-0.7, 0.997), (0.7, 1.003)):
                g = sum(saw(nf(m + iv) * det, tt + rng.random() * 0.001) for iv in (0, 7, 12))
                g = np.tanh(g * 9) * env(len(tt), 0.002, 0.25 if sec not in (2, 4) else 1.5)
                g = lp_fast(hp_fast(g, 90), 4200)
                add(g, st0, pan=pan, g=0.16)
        # syntikkamelodia (lead) osissa 2 ja 4 — sotilaallinen fanfaari
        if sec in (2, 4):
            mel = [64, 0, 64, 67, 66, 64, 62, 0] if b % 2 == 0 else [64, 0, 71, 69, 67, 66, 64, 0]
            for e, m in enumerate(mel):
                if m == 0: continue
                tt = t(beat / 2 * 0.95)
                l = (np.sign(np.sin(2 * np.pi * nf(m) * tt)) * 0.5 + saw(nf(m) * 1.005, tt) * 0.5) * env(len(tt), 0.01, 0.3)
                add(lp_fast(l, 3000), t0 + e * beat / 2, pan=0.2, g=0.12)
        # jousimatto (pad) breakdownissa ja lopussa
        if sec in (3, 5) and b % 2 == 0:
            tt = t(bar * 2); m = chords[(b // 2) % 4] + 24
            p = sum(saw(nf(m + iv) * d, tt) for iv in (0, 3, 7) for d in (0.996, 1.004))
            p = lp_fast(p, 1800) * np.minimum(1, tt / 0.5) * np.minimum(1, (tt[-1] - tt) / 0.5 + 1e-3)
            add(p, t0, g=0.03)
    # crossfade loppu alkuun saumattomaksi loopiksi
    xf = int(0.05 * SR); mix[:xf] *= np.linspace(0, 1, xf)[:, None]; mix[-xf:] *= np.linspace(1, 0, xf)[:, None]
    mix = np.tanh(mix * 1.4)
    save("musiikki_taistelu", mix, 0.85)

# ---------------- Efektit ----------------
def can_clink():
    out = np.zeros(int(0.5 * SR))
    for k, (dt, f0) in enumerate(((0, 2900), (0.07, 3400), (0.16, 2600))):
        tt = t(0.3)
        s = sum(np.sin(2 * np.pi * f0 * r * tt) * np.exp(-tt / (0.06 / r)) for r in (1, 1.52, 2.31, 3.1))
        s += hp_fast(rng.standard_normal(len(tt)), 3000) * env(len(tt), 0.0003, 0.004) * 2
        i = int(dt * SR); out[i:i + len(s)] += s * (1 - 0.25 * k)
    save("sfx_tolkki_kilina", out, 0.8)

def gunshot(name, n_shots=1, gap=0.09):
    out = np.zeros(int((0.6 + gap * n_shots) * SR))
    for k in range(n_shots):
        tt = t(0.6); nz = rng.standard_normal(len(tt))
        crack = hp_fast(nz, 1500) * env(len(tt), 0.0002, 0.015)
        body = lp_fast(nz, 900) * env(len(tt), 0.001, 0.12)
        thump = np.sin(2 * np.pi * 70 * tt) * env(len(tt), 0.001, 0.06)
        s = np.tanh((crack * 1.5 + body * 2 + thump * 2) * 2)
        i = int(k * gap * SR); out[i:i + len(s)] += s
    save(name, out, 0.9)

def capture_done():
    notes = [(60, 0, .12), (64, .12, .12), (67, .24, .12), (72, .36, .5)]
    out = np.zeros(int(1.2 * SR))
    for m, st, d in notes:
        tt = t(d + 0.2)
        s = (np.sign(np.sin(2 * np.pi * nf(m) * tt)) * 0.4 + saw(nf(m + 12), tt) * 0.3) * env(len(tt), 0.005, d)
        i = int(st * SR); out[i:i + len(s)] += lp_fast(s, 5000)
    tt = t(0.6); out[int(.36 * SR):int(.36 * SR) + len(tt)] += np.sin(2 * np.pi * 80 * tt) * env(len(tt), .001, .15) * 0.8
    save("sfx_valtaus_valmis", out, 0.8)

def capture_lost():
    notes = [(67, 0, .15), (63, .15, .15), (58, .3, .5)]
    out = np.zeros(int(1.1 * SR))
    for m, st, d in notes:
        tt = t(d + 0.2); s = saw(nf(m), tt) * env(len(tt), 0.005, d)
        i = int(st * SR); out[i:i + len(s)] += lp_fast(s, 2500)
    save("sfx_valtaus_menetetty", out, 0.8)

def moped():
    tt = t(1.6); f = 38 + 22 * np.minimum(1, tt / 0.6) + 2 * np.sin(2 * np.pi * 7 * tt)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sign(np.sin(ph)) * 0.6 + np.sin(2 * ph) * 0.3 + lp_fast(rng.standard_normal(len(tt)), 2000) * 0.2
    s = np.tanh(lp_fast(s, 2500) * 2) * np.minimum(1, tt / 0.05) * np.minimum(1, (tt[-1] - tt) / 0.2)
    save("sfx_mopo", s, 0.7)

def explosion():
    tt = t(1.8); nz = rng.standard_normal(len(tt))
    s = lp_fast(nz, 600) * env(len(tt), 0.002, 0.5) * 3 + np.sin(2 * np.pi * 45 * tt) * env(len(tt), .001, .3) * 2
    save("sfx_rakennus_tuhoutui", np.tanh(s), 0.9)

def ui_click():
    tt = t(0.05); save("sfx_ui_klikkaus", np.sin(2 * np.pi * 1200 * tt) * env(len(tt), .0005, .01), 0.6)


def snore_fall():
    out = np.zeros(int(3.2 * SR))
    tt = t(0.5); thud = lp_fast(rng.standard_normal(len(tt)), 300) * env(len(tt), .002, .08) * 2 + np.sin(2*np.pi*60*tt) * env(len(tt), .001, .1)
    out[:len(tt)] += thud
    for k, st in enumerate((0.7, 2.0)):
        tt = t(1.0); f = 55 + 10 * np.sin(np.pi * tt)
        ph = 2*np.pi*np.cumsum(f)/SR
        buzz = (np.sign(np.sin(ph)) * 0.5 + lp_fast(rng.standard_normal(len(tt)), 900) * 0.5)
        sn = lp_fast(buzz, 700) * np.sin(np.pi * tt / tt[-1]) ** 2
        i = int(st * SR); out[i:i+len(sn)] += sn * 0.8
    save("sfx_sammui", out, 0.75)

def death():
    tt = t(0.8); f = 400 * np.exp(-tt * 2.5) + 80
    ph = 2*np.pi*np.cumsum(f)/SR
    s = saw(1, ph/(2*np.pi)) * env(len(tt), .005, .4)
    s = lp_fast(s, 1500) + lp_fast(rng.standard_normal(len(tt)), 400) * env(len(tt), .001, .1)
    save("sfx_kuolema", np.tanh(s * 2), 0.8)

def training_done():
    out = np.zeros(int(0.7 * SR))
    for m, st in ((67, 0), (72, .1)):
        tt = t(0.4); s = (np.sign(np.sin(2*np.pi*nf(m)*tt))*.5 + np.sin(2*np.pi*nf(m+12)*tt)*.5) * env(len(tt), .003, .15)
        i = int(st*SR); out[i:i+len(s)] += lp_fast(s, 4000)
    save("sfx_koulutus_valmis", out, 0.7)

# ---------------- Yksiköiden kuittaukset (espeak-ng, suomi) ----------------
LINES = {
    "tolkkijussi": [("valittu", "No mitä nyt?", 35), ("kuittaus_1", "Selvä pomo!", 35), ("kuittaus_2", "Tölkit talteen.", 35), ("kuittaus_3", "Joo joo, mennään.", 35), ("baariin", "Mää käyn yhellä...", 35)],
    "lahiojermu":  [("valittu", "Häh? Mitä?", 45), ("kuittaus_1", "Selvä pomo!", 45), ("kuittaus_2", "Mennään!", 45), ("hyokkays", "Turpaan!", 45), ("kanni", "Mää lähen kotiin...", 38), ("baariin", "Mää käyn yhellä... tai kahella.", 45)],
    "mopopoika":   [("valittu", "Mitä?", 70), ("kuittaus_1", "Kaasu pohjaan!", 70), ("kuittaus_2", "Mopolla mennään!", 70), ("hyokkays", "Ne on meidän tölkit!", 70), ("baariin", "Pikaset kaljat!", 70)],
}
def voices():
    for unit, lines in LINES.items():
        for key, text, pitch in lines:
            raw = os.path.join(D, "_tmp.wav")
            speed = 135 if key == "kanni" else 160
            subprocess.run(["espeak-ng", "-v", "fi+m3", "-p", str(pitch), "-s", str(speed), "-w", raw, text], check=True)
            name = f"aani_{unit}_{key}"
            # "radiopuhelin"-sävy: kaistanrajaus + kevyt särö
            filt = "highpass=f=250,lowpass=f=3800,acompressor=threshold=-18dB:ratio=4,volume=1.5,aresample=44100"
            if key == "kanni": filt = "asetrate=22050*0.92,aresample=44100,vibrato=f=3:d=0.3," + filt
            for ext, args in (("ogg", ["-c:a", "libvorbis", "-q:a", "5"]), ("mp3", ["-c:a", "libmp3lame", "-b:a", "128k"])):
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", filt, "-ac", "1", *args, os.path.join(D, f"{name}.{ext}")], check=True)
            os.remove(raw)

import sys
if __name__ == "__main__" and "--vain-uudet" in sys.argv:
    snore_fall(); death(); training_done(); voices(); sys.exit()
if __name__ == "__main__":
    can_clink(); gunshot("sfx_laukaus_rk62"); gunshot("sfx_laukaus_jatimatic", 4, 0.07)
    capture_done(); capture_lost(); moped(); explosion(); ui_click(); snore_fall(); death(); training_done(); voices()
    battle_track()
    print("valmis")
