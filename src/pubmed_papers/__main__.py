from .fetch_papers import fetch_paper_ids, fetch_paper_details, save_to_csv
import argparse

def main():
    parser = argparse.ArgumentParser(description="Fetch research papers from PubMed")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-f", "--file", help="Filename to save output", default=None)
    args = parser.parse_args()

    paper_ids = fetch_paper_ids(args.query)
    papers = fetch_paper_details(paper_ids)

    if args.file:
        save_to_csv(papers, args.file)
        print(f"Results saved to {args.file}")
    else:
        print(papers)

if __name__ == "__main__":
    main()
 
