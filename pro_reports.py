"""Run selected tradermonty/claude-trading-skills scripts and publish their reports.

The skills repo is cloned by the workflow into ./trading-skills. Each skill
writes Markdown reports; the newest one per skill is copied to docs/reports/
and listed in docs/reports/index.json for the Pro Reports page.

Usage: python pro_reports.py daily|sunday|all
FMP_API_KEY must be set in the environment (a GitHub Actions secret).
"""
import glob
import re
import json
import os
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone

SKILLS_DIR = "trading-skills/skills"
WORK_DIR = "pro-out"
DOCS_DIR = "docs/reports"
INDEX_PATH = os.path.join(DOCS_DIR, "index.json")

# The FMP free plan only serves prices for a small sample of symbols, so every
# skill runs through yahoo_bridge.py, which answers FMP price requests from
# Yahoo Finance. Only earnings and company-profile requests reach FMP.
REPORTS = {
    "vcp": {
        "title": "VCP Screener",
        "about": "Mark Minervini Volatility Contraction Patterns: Stage 2 stocks forming tight bases near a breakout pivot.",
        "schedule": "Weekdays",
        "group": "daily",
        "calls": "0 (Yahoo prices)",
    },
    "ftd": {
        "title": "Follow-Through Day",
        "about": "William O'Neil's market-bottom signal for the S&P 500 and Nasdaq: is a new uptrend confirmed?",
        "schedule": "Weekdays",
        "group": "daily",
        "calls": "0 (Yahoo prices)",
    },
    "distribution": {
        "title": "Distribution Days",
        "about": "IBD distribution-day count on QQQ and SPY: how much institutional selling is hitting the market, and what exposure that suggests.",
        "schedule": "Weekdays",
        "group": "daily",
        "calls": "0 (Yahoo prices)",
    },
    "momentum": {
        "title": "Momentum Bursts",
        "about": "Pradeep Bonde (Stockbee) momentum bursts: stocks that just broke out 4%+ on rising volume from a quiet base, for 3-5 day swing moves.",
        "schedule": "Weekdays",
        "group": "daily",
        "calls": "0 (Yahoo prices)",
    },
    "earnings": {
        "title": "Earnings Calendar",
        "about": "Companies over $2B reporting earnings in the coming week, so you can avoid holding through surprises.",
        "schedule": "Sundays",
        "group": "sunday",
        "calls": "~5",
    },
    "pead": {
        "title": "Post-Earnings Drift",
        "about": "Stocks that gapped up on earnings in the last two weeks and are forming a continuation setup.",
        "schedule": "Sundays",
        "group": "sunday",
        "calls": "~100 (earnings from FMP)",
    },
}


def script(skill, name):
    return os.path.join(SKILLS_DIR, skill, "scripts", name)


def bridged(skill, name, *args):
    return [sys.executable, "yahoo_bridge.py", script(skill, name), *args]


def write_universe(out):
    """S&P 500 symbols, one per line, for skills that take a universe file."""
    from breadth_update import get_tickers
    path = os.path.join(out, "sp500.txt")
    with open(path, "w") as fh:
        fh.write("\n".join(get_tickers()))
    return path


def commands(key, out):
    if key == "vcp":
        return [bridged("vcp-screener", "screen_vcp.py", "--full-sp500", "--output-dir", out)]
    if key == "ftd":
        return [bridged("ftd-detector", "ftd_detector.py", "--output-dir", out)]
    if key == "distribution":
        return [bridged("ibd-distribution-day-monitor", "ibd_monitor.py",
                        "--symbols", "QQQ,SPY", "--output-dir", out)]
    if key == "momentum":
        return [bridged("stockbee-momentum-burst-screener", "screen_momentum_burst.py",
                        "--universe-file", write_universe(out), "--max-symbols", "520",
                        "--max-api-calls", "2000", "--output-dir", out)]
    if key == "pead":
        return [bridged("pead-screener", "screen_pead.py",
                        "--max-api-calls", "200", "--output-dir", out)]
    raise KeyError(key)


def run(cmd, timeout, stdout=None):
    """Run a skill script, echo its log, and raise with its last error lines."""
    proc = subprocess.run(cmd, stdout=stdout or subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, timeout=timeout)
    if stdout is None and proc.stdout:
        print(proc.stdout, flush=True)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr, flush=True)
    if proc.returncode != 0:
        lines = [l for l in ((proc.stdout or "") + "\n" + proc.stderr).splitlines() if l.strip()]
        raise RuntimeError(" | ".join(lines[-3:]) or f"exit code {proc.returncode}")


def run_earnings(out):
    start = date.today() + timedelta(days=1)
    end = start + timedelta(days=6)
    data = os.path.join(out, "earnings_data.json")
    with open(data, "w") as fh:
        run(bridged("earnings-calendar", "fetch_earnings_fmp.py",
                    start.isoformat(), end.isoformat()), timeout=900, stdout=fh)
    run([sys.executable, script("earnings-calendar", "generate_report.py"),
         data, os.path.join(out, f"earnings_calendar_{start.isoformat()}.md")], timeout=300)


def newest_markdown(out):
    files = glob.glob(os.path.join(out, "**", "*.md"), recursive=True)
    return max(files, key=os.path.getmtime) if files else None


# The distribution-day skill writes a few fixed phrases in Japanese.
TRANSLATIONS = [
    (re.compile(r"(\S+)は本日Distribution Day該当。"), r"\1 had a Distribution Day today."),
    (re.compile(r"(\S+)は本日Distribution Day非該当。"), r"\1 had no Distribution Day today."),
    (re.compile(r"5/15/25セッション経過以内の有効Distribution Dayはそれぞれ (\S+) 件。"),
     r"Active Distribution Days within the last 5/15/25 sessions: \1."),
    (re.compile(r"5/15/25セッション経過以内: "), "within 5/15/25 sessions: "),
    (re.compile(r"リスク判定: (\S+?)。"), r"Risk level: \1."),
]


def publish(md, dest):
    with open(md, encoding="utf-8") as fh:
        text = fh.read()
    for pattern, repl in TRANSLATIONS:
        text = pattern.sub(repl, text)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(text)


def load_index():
    try:
        with open(INDEX_PATH) as fh:
            return json.load(fh)
    except Exception:
        return {"reports": {}}


def main():
    group = sys.argv[1] if len(sys.argv) > 1 else "daily"
    keys = [k for k, r in REPORTS.items() if group == "all" or r["group"] == group]
    os.makedirs(DOCS_DIR, exist_ok=True)
    index = load_index()
    index["reports"] = {k: v for k, v in index.get("reports", {}).items() if k in REPORTS}
    has_key = bool(os.environ.get("FMP_API_KEY"))
    index["has_key"] = has_key
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for key, meta in REPORTS.items():
        entry = index["reports"].setdefault(key, {})
        entry.update({k: meta[k] for k in ("title", "about", "schedule", "calls")})

    published = 0
    for key in keys:
        entry = index["reports"][key]
        entry["last_attempt"] = now
        if not has_key:
            entry["status"] = "no_key"
            continue
        out = os.path.join(WORK_DIR, key)
        shutil.rmtree(out, ignore_errors=True)
        os.makedirs(out)
        print(f"=== {REPORTS[key]['title']}", flush=True)
        try:
            if key == "earnings":
                run_earnings(out)
            else:
                for cmd in commands(key, out):
                    run(cmd, timeout=1800)
            md = newest_markdown(out)
            if not md:
                raise RuntimeError("no Markdown report was produced")
            publish(md, os.path.join(DOCS_DIR, f"{key}.md"))
            entry.update({"status": "ok", "updated": now, "error": None})
            published += 1
            print(f"Published {md}", flush=True)
        except Exception as e:
            entry.update({"status": "error", "error": str(e)[:300]})
            print(f"{key} failed: {e}", flush=True)

    index["generated"] = now
    with open(INDEX_PATH, "w") as fh:
        json.dump(index, fh, indent=1)
    print(f"Done: {published}/{len(keys)} reports published")
    if not has_key:
        print("FMP_API_KEY secret is not set; reports were skipped")


if __name__ == "__main__":
    main()
