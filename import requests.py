import requests

response = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=cancer+research&retmax=10&retmode=json")
print(response.text)
