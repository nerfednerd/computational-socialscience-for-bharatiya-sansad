import fitz

pdf_path="D:\css_nlp_research_project\synopsis_analysis\data\Sup+Synopsis-11-06-2014.pdf"
output_file="output.txt"

doc=fitz.open(pdf_path)

all_text=""

for page_num in range(5, len(doc)):
    page=doc[page_num]
    all_text+=page.get_text()

with open(output_file, "w", encoding="utf-8") as f:
    f.write(all_text)


print(f"Text saved to {output_file}")