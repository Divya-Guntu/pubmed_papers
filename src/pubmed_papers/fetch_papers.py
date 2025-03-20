import requests
import pandas as pd
import argparse
import csv

import xml.etree.ElementTree as ET

PUBMED_API_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def fetch_paper_ids(query):
    """Fetches paper IDs from PubMed"""
    params = {"db": "pubmed", "term": query, "retmax": 10, "retmode": "json"}
    response = requests.get(PUBMED_API_URL, params=params)
    response.raise_for_status()
    return response.json().get("esearchresult", {}).get("idlist", [])



def fetch_paper_details(paper_ids):
    """Fetches details for the given paper IDs from PubMed."""
    if not paper_ids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(paper_ids),
        "retmode": "xml"
    }

    response = requests.get(PUBMED_FETCH_URL, params=params)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    papers = []
    
    for article in root.findall(".//PubmedArticle"):
        pubmed_id = article.findtext(".//PMID")
        title = article.findtext(".//ArticleTitle")
        pub_date = article.findtext(".//PubDate/Year")
        authors = []

        for author in article.findall(".//Author"):
            last_name = author.findtext("LastName")
            first_name = author.findtext("ForeName")
            affiliation = author.findtext(".//Affiliation")

            if affiliation and "university" not in affiliation.lower():
                authors.append({
                    "name": f"{first_name} {last_name}",
                    "affiliation": affiliation
                })

        company_affiliations = [a["affiliation"] for a in authors]
        corresponding_author_email = article.findtext(".//AffiliationInfo/Affiliation/Email")

        papers.append({
            "PubmedID": pubmed_id,
            "Title": title,
            "Publication Date": pub_date,
            "Non-academic Author(s)": ", ".join([a["name"] for a in authors]),
            "Company Affiliation(s)": ", ".join(company_affiliations),
            "Corresponding Author Email": corresponding_author_email or "N/A"
        })

    return papers

def save_to_csv(papers, filename):
    """Saves research papers to a CSV file with required fields."""
    fields = ["PubmedID", "Title", "Publication Date", "Non-academic Author(s)", "Company Affiliation(s)", "Corresponding Author Email"]

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(papers)

    print(f"✅ Results saved to {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch research papers from PubMed")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-f", "--file", help="Filename to save output", default="results.csv")
    args = parser.parse_args()

    paper_ids = fetch_paper_ids(args.query)
    papers = fetch_paper_details(paper_ids)

    if papers:
        save_to_csv(papers, args.file)
    else:
        print("❌ No relevant papers found.")

