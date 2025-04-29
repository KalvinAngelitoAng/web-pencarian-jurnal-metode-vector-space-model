import json

def load_journal_titles(json_path="journals.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []
    journal_data = []
    for journal in data["journals"]:
        articles = journal.get("articles", [])
        for article in articles:
            title = article.get("title", "")
            if title:
                documents.append(title)
                journal_data.append({
                    "title": title,
                    "journal_name": journal.get("basic_info", {}).get("name", ""),
                    "url": journal.get("basic_info", {}).get("url", ""),
                })
    return documents, journal_data
