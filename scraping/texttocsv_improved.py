import re
import pandas as pd
from pathlib import Path

# ---------------- CONFIG ----------------
INPUT_DIR = Path("transcripts")   # folder where all .txt files are kept
OUTPUT_DIR = Path("csv_files_improved")    # where csv files will be saved
PRESERVE_PARAGRAPHS = False       # set True if you want to keep paragraph breaks
# ----------------------------------------

# ---------- utility functions ----------
def fix_hyphenation(text):
    return re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)

def clean_speaker(s):
    s = s.replace("\n", " ").replace("\r", " ")
    s = re.sub(r'\s+', ' ', s).strip()
    return s.strip("* -")

def clean_speech(s, preserve_paragraphs=False):
    s = s.strip().replace("\r\n", "\n").replace("\r", "\n")
    if preserve_paragraphs:
        s = re.sub(r'\n{3,}', '\n\n', s)
        s = re.sub(r'[ \t]+', ' ', s)
        s = re.sub(r'(?<!\n)\n(?!\n)', ' ', s)
        s = re.sub(r' {2,}', ' ', s)
    else:
        s = re.sub(r'\s+', ' ', s)
    return s.strip()

def contains_devanagari(s):
    return bool(re.search(r'[\u0900-\u097F]', s))

def build_primary_header_regex():
    honorifics = [
        r"HON(?:'?\s*BLE|OURABLE|\.?BLE|\.?)",
        r"Hon(?:'?ble|\.?)",
        r"SHRI", r"SRI", r"SHRIMATI", r"SMT(?:\.)?",
        r"श्री(?:मति|)|श्रीमती|श्रीमति",
        r"माननीय"
    ]
    prefix = r"(?:%s)" % "|".join(honorifics)
    pattern = rf"^(?:\*{{1,2}}\s*)?\s*(?P<speaker>{prefix}[\s\S]{{0,300}}?):"
    return re.compile(pattern, re.IGNORECASE | re.MULTILINE)

def build_fallback_uppercase_regex():
    return re.compile(r"^(?:\*{1,2}\s*)?\s*([A-Z][A-Z0-9\.\-'\(\) ]{8,}?):", re.MULTILINE)

def find_headers(text, header_re):
    matches = list(header_re.finditer(text))
    headers = []
    for m in matches:
        headers.append({"start": m.start(), "end": m.end(), "speaker_raw": m.group("speaker")})
    return headers

def merge_and_sort_headers(primary, fallback):
    combined = primary[:]
    existing_starts = {h["start"] for h in primary}
    for h in fallback:
        if not any(abs(h["start"] - s) < 5 for s in existing_starts):
            combined.append(h)
            existing_starts.add(h["start"])
    combined.sort(key=lambda x: x["start"])
    return combined

def extract_segments(text, headers):
    segments = []
    if not headers:
        return [{"speaker": "Preamble", "speech": text.strip()}]
    if headers[0]["start"] > 0:
        preamble = text[:headers[0]["start"]].strip()
        if preamble:
            segments.append({"speaker": "Preamble", "speech": preamble})
    for i, h in enumerate(headers):
        seg_start = h["end"]
        seg_end = headers[i+1]["start"] if i+1 < len(headers) else len(text)
        speech = text[seg_start:seg_end]
        segments.append({"speaker": h["speaker_raw"], "speech": speech})
    return segments

def detect_year(filename: str):
    """Return year (2015–2020) if found in filename, else 'misc'."""
    m = re.search(r"\b(201[5-9]|2020)\b", filename)
    return m.group(1) if m else "misc"

def process_file(txt_path: Path, output_dir: Path):
    text = txt_path.read_text(encoding="utf-8")
    text = fix_hyphenation(text)

    # Primary pass
    primary_re = build_primary_header_regex()
    headers = find_headers(text, primary_re)
    segments = extract_segments(text, headers)

    # Coverage check
    orig_wc = len(text.split())
    extr_wc = sum(len(seg["speech"].split()) for seg in segments)
    if orig_wc and extr_wc / orig_wc < 0.9:  # try fallback
        fallback_re = build_fallback_uppercase_regex()
        fallback_headers = find_headers(text, fallback_re)
        headers = merge_and_sort_headers(headers, fallback_headers)
        segments = extract_segments(text, headers)

    # Clean up
    rows = []
    for seg in segments:
        speaker = clean_speaker(seg["speaker"])
        speech = clean_speech(seg["speech"], PRESERVE_PARAGRAPHS)
        rows.append({
            "Speaker": speaker,
            "Speech": speech,
            "Words_in_Speech": len(speech.split()),
            "Language": "hi" if contains_devanagari(speech) else "en"
        })

    df = pd.DataFrame(rows)

    # Decide output path
    year = detect_year(txt_path.name)
    subdir = output_dir / year
    subdir.mkdir(parents=True, exist_ok=True)
    csv_out = subdir / (txt_path.stem + ".csv")

    df.to_csv(csv_out, index=False, encoding="utf-8-sig")
    print(f"✅ {txt_path.name} -> {csv_out} ({len(df)} rows)")

# -------------- RUN --------------
def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    txt_files = list(INPUT_DIR.glob("*.txt"))
    if not txt_files:
        print(f"No .txt files found in {INPUT_DIR}")
        return

    for f in txt_files:
        process_file(f, OUTPUT_DIR)

if __name__ == "__main__":
    main()
