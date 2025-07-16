from bs4 import BeautifulSoup


def scrape_javadoc_fqn(file_path, class_name):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            soup = BeautifulSoup(file, "html.parser")
    except FileNotFoundError:
        print(f"Failed to open {file_path}")
        return None

    header = soup.find("div", class_="header")
    if not header:
        print(f"Header not found in {file_path}")
        return None

    subtitles = header.find_all("div", class_="subTitle")

    package_name = None
    for subtitle in subtitles:
        text = subtitle.get_text(strip=True)
        if text.startswith("java"):
            package_name = text
            break

    if package_name is None:
        for subtitle in subtitles:
            text = subtitle.get_text(strip=True)
            if text.startswith("org"):
                package_name = text
                break

    if package_name is None and subtitles:
        package_name = (
            subtitles[0].get_text(strip=True).split(",")[1].strip()
            if "," in subtitles[0].get_text(strip=True)
            else subtitles[0].get_text(strip=True)
        )

    if package_name:
        return f"{package_name}.{class_name}"
    else:
        print(f"SubTitle not found for {class_name} in {file_path}")
        return None


index_path = "/Users/ooj/Downloads/docs/api/allclasses-noframe.html"

try:
    with open(index_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
except FileNotFoundError:
    print(f"Could not open the index file: {index_path}")
    exit()

links = soup.find_all("a")

fqns = []
for link in links:
    class_name = link.get_text(strip=True)
    href = link.get("href")
    if not href:
        continue

    class_path = f"/Users/ooj/Downloads/docs/api/{href}"
    fqn = scrape_javadoc_fqn(class_path, class_name)
    if fqn:
        print(f"{class_name} -> {fqn}")
        fqns.append(fqn)

with open("fqns.txt", "w", encoding="utf-8") as outfile:
    outfile.write("\n".join(fqns))
