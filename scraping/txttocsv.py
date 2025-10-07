import re
import pandas as pd
import os

# Folder paths
input_folder = "transcripts"
output_folder = "csv_files"

# Make output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Regex to capture valid speakers
speaker_pattern = re.compile(
    r"""
    (?:                                # allowed honorifics
       HON\.?\s*(?:[A-Z]+\s*)?SPEAKER  # HON. SPEAKER, HON. DEPUTY SPEAKER
      |Hon\.?                          # Hon., Hon
      |Dr\.?                           # Dr, Dr.
      |Shri
      |SHRI
      |Shrimati
      |Smt\.?
      |Sri
      |श्री
      |श्रीमती
      |माननीय
    )
    [^:\n]{0,50}                       # allow name/constituency (no colon or newline)
    :                                  # must end with colon
    """,
    re.IGNORECASE | re.VERBOSE
)

def extract_speeches_strict(input_file, output_csv):
    # Read debate text
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    # Find all speaker markers
    matches = list(speaker_pattern.finditer(text))

    data = []
    for i, match in enumerate(matches):
        # Clean speaker name
        speaker = match.group().rstrip(":").strip()
        speaker = re.sub(r"\s+", " ", speaker)  # collapse newlines/multiple spaces

        # Get speech span
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        speech = text[start:end].strip()

        # Filter: ignore procedural/garbage
        if not speech:
            continue
        if re.search(r"\b(seconded by|laid on the Table|dress had said|now the House)\b", speech, re.IGNORECASE):
            continue

        data.append({"Speaker": speaker, "Speech": speech})

    # Save cleaned pairs
    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"✅ Saved {len(df)} clean Speaker–Speech pairs to {output_csv}")


# Loop over all .txt files in scraping folder
for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        input_path = os.path.join(input_folder, filename)
        output_filename = filename.replace(".txt", "_cleaned.csv")
        output_path = os.path.join(output_folder, output_filename)
        extract_speeches_strict(input_path, output_path)
