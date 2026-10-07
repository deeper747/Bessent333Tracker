"""Download the three 3-3-3 indicators from FRED and EIA and write data.json.
Run from the repository root: python scripts/fetch_data.py"""
import csv, io, json, calendar, datetime, subprocess, xlrd
def get(u):
    return subprocess.run(["curl", "-sSfL", "--retry", "3", "-m", "90", "-A", "Mozilla/5.0 (Bessent333Tracker; GitHub Actions)", u], check=True, capture_output=True).stdout
def fred(sid):
    rows = list(csv.reader(io.StringIO(get("https://fred.stlouisfed.org/graph/fredgraph.csv?id=" + sid).decode())))[1:]
    return [(d, float(v)) for d, v in rows if v not in ("", ".")]
def eia(path):
    sh = xlrd.open_workbook(file_contents=get("https://www.eia.gov/dnav/" + path)).sheet_by_index(1)
    out = []
    for i in range(3, sh.nrows):
        d, v = sh.cell_value(i, 0), sh.cell_value(i, 1)
        if d == "" or v == "": continue
        y, m, *_ = xlrd.xldate_as_tuple(d, 0)
        out.append(("%04d-%02d" % (y, m), float(v)))
    return out
START = "2022-01"
# 1. Real GDP growth
saar, yoy = fred("A191RL1Q225SBEA"), dict(fred("A191RO1Q156NBEA"))
def q(d): return "%s Q%d" % (d[:4], (int(d[5:7]) - 1) // 3 + 1)
gdp = [{"p": q(d), "saar": v, "yoy": yoy.get(d)} for d, v in saar if d[:7] >= START]
# 2. Deficit, trailing 12 months, over nominal GDP
bal = fred("MTSDS133FMS")            # $ millions, negative = deficit
ngdp = fred("GDP")                   # $ billions, annual rate
def gdp_for(ym):
    qs = "%s-%02d" % (ym[:4], (int(ym[5:7]) - 1) // 3 * 3 + 1)
    c = [v for d, v in ngdp if d[:7] <= qs]
    return c[-1]
deficit = []
for i in range(11, len(bal)):
    ym = bal[i][0][:7]
    if ym < START: continue
    t12 = -sum(v for _, v in bal[i - 11:i + 1]) / 1000.0
    deficit.append({"p": ym, "t12": round(t12, 1), "gdp": gdp_for(ym), "pct": round(100 * t12 / gdp_for(ym), 2)})
# 3. Oil and gas production, thousand boe/d (6 Mcf gas = 1 boe)
crude = dict(eia("pet/hist_xls/MCRFPUS2m.xls"))      # kb/d
ngpl = dict(eia("pet/hist_xls/MNGFPUS2m.xls"))       # kb/d
gas = dict(eia("ng/hist_xls/N9070US2m.xls"))         # MMcf per month
energy = []
for ym in sorted(set(crude) & set(ngpl) & set(gas)):
    if ym < "2022-01": continue
    days = calendar.monthrange(int(ym[:4]), int(ym[5:7]))[1]
    g = gas[ym] / days / 6.0
    energy.append({"p": ym, "crude": round(crude[ym]), "ngpl": round(ngpl[ym]), "gas": round(g), "boe": round(crude[ym] + ngpl[ym] + g)})
b = [e["boe"] for e in energy if e["p"][:4] == "2024"]
out = {"updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "gdp": gdp, "deficit": deficit,
       "energy": energy, "energyBaseline": round(sum(b) / len(b))}
# Refuse to overwrite good data with a broken download
assert len(gdp) >= 18 and len(deficit) >= 50 and len(energy) >= 50, "series too short"
assert 0 < deficit[-1]["pct"] < 15, "deficit ratio out of range"
assert 30000 < energy[-1]["boe"] < 50000, "energy total out of range"
json.dump(out, open("data.json", "w"), separators=(",", ":"))
print("gdp", gdp[-1], "deficit", deficit[-1], "energy", energy[-1], sep="\n")
