from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def scrape_debate(url, output_file):
    # setup selenium chromedriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    driver.get(url)
    time.sleep(20)  # wait for JS to load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    # locate debate text inside the table
    table = soup.find("div", id="__next").find("table")
    tbody = table.find("tbody")
    debate_td = tbody.find("tr").find_all("td")[1]

    paragraphs = []
    for p in debate_td.find_all("p"):
        text = " ".join(span.get_text(strip=True) for span in p.find_all("span"))
        if text.strip():
            paragraphs.append(text)

    # save into structured text file
    with open(output_file, "w", encoding="utf-8") as f:
        for para in paragraphs:
            f.write(f"{para}\n\n")  # just paragraphs, no numbering

    print(f"Saved {len(paragraphs)} paragraphs to {output_file}")


debate_links={
    "16_4_24Feb2015":"https://sansad.in/ls/debates/view-debate?ls=16&session=4&dbslno=2624",
    "16_4_25Feb2015":"https://sansad.in/ls/debates/view-debate?ls=16&session=4&dbslno=2683",
    "16_4_26Feb2015":"https://sansad.in/ls/debates/view-debate?ls=16&session=4&dbslno=2782",
    "16_4_27Feb2015":"https://sansad.in/ls/debates/view-debate?ls=16&session=4&dbslno=2816",
    "16_7_24Feb2016":"https://sansad.in/ls/debates/view-debate?ls=16&session=7&dbslno=6167",
    "16_7_25Feb2016":"https://sansad.in/ls/debates/view-debate?ls=16&session=7&dbslno=6250",
    "16_7_26Feb2016":"https://sansad.in/ls/debates/view-debate?ls=16&session=7&dbslno=6757",
    "16_7_02Mar2016":"https://sansad.in/ls/debates/view-debate?ls=16&session=7&dbslno=6582",
    "16_11_07Feb2017":"https://sansad.in/ls/debates/view-debate?ls=16&session=11&dbslno=9905",
    "16_14_06Feb2018":"https://sansad.in/ls/debates/view-debate?ls=16&session=14&dbslno=13239",
    "16_14_07Feb2018":"https://sansad.in/ls/debates/view-debate?ls=16&session=14&dbslno=13239",
    "16_17_05Feb2019":"https://sansad.in/ls/debates/view-debate?ls=16&session=17&dbslno=15697",
    "16_17_07Feb2019":"https://sansad.in/ls/debates/view-debate?ls=16&session=17&dbslno=15389",
    "17_1_24Jun2019":"https://sansad.in/ls/debates/view-debate?ls=17&session=1&dbslno=322",
    "17_1_25Jun2019":"https://sansad.in/ls/debates/view-debate?ls=17&session=1&dbslno=690",
    "17_3_03Feb2020":"https://sansad.in/ls/debates/view-debate?ls=17&session=3&dbslno=3338",
    "17_3_04Feb2020":"https://sansad.in/ls/debates/view-debate?ls=17&session=3&dbslno=3629",
    "17_3_05Feb2020":"https://sansad.in/ls/debates/view-debate?ls=17&session=3&dbslno=3835",
    "17_3_06Feb2020":"https://sansad.in/ls/debates/view-debate?ls=17&session=3&dbslno=3434"
}

for key, value in debate_links.items():
    try:
        scrape_debate(value, f"debate_{key}.txt")
    except Exception as e:
        print(f"Failed to scrape {key}: {e}")



