import csv
import re


try:
    with open("output.txt", "r", encoding="utf-8") as file:
        text_content=file.read()
except:
    print("Error occured while reading the file")
    exit()


# followed by a name, and then a colon. This is a bit more robust.
pattern = re.compile(r'\n(SHRI |SHRIMATI |THE MINISTER|ADV\.)[\s\S]*?(?=\n(SHRI |SHRIMATI |THE PRIME|ADV\.|$))')

speakers_and_speeches = {}
last_speaker = None
last_speech = ""

# Find all matches of the pattern
matches = pattern.finditer(text_content)
for match in matches:
    part = match.group(0).strip()
    
    # Split the part into speaker name and speech
    speaker_name_end = part.find(':')
    if speaker_name_end != -1:
        speaker = part[:speaker_name_end].strip()
        speech = part[speaker_name_end+1:].strip()
        
        # Add to dictionary
        speakers_and_speeches[speaker] = speech

# Handle the last part of the text if it doesn't end with a speaker pattern
if not speakers_and_speeches:
    print("Could not find any speaker-speech pairs. The pattern might be incorrect.")
else:
    # Convert dictionary to a list of dictionaries for CSV
    csv_data = [{'Speaker': speaker, 'Speech': speech} for speaker, speech in speakers_and_speeches.items()]

    # Define the CSV file name and fieldnames
    csv_file = 'speaker_speech_pairs.csv'
    fieldnames = ['Speaker', 'Speech']

    # Save to CSV
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)
        print(f"Successfully saved to {csv_file}")
    except Exception as e:
        print(f"An error occurred while writing to CSV: {e}")

    # Print the extracted dictionary
    print("\n--- Extracted Speaker-Speech Dictionary ---")
    import json
    print(json.dumps(speakers_and_speeches, indent=4))