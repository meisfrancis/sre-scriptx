import os
import requests
import csv
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read GitHub token from the .env file
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Validate the token
if not GITHUB_TOKEN:
    raise ValueError("GitHub token not found in environment variables. Please add it to the .env file.")

# GitHub API constants
GITHUB_API_URL = "https://api.github.com/search/code"


# Function to perform the search
def search_github_code(query, **kwargs):
    per_page = kwargs.get("per_page", 100)
    page = kwargs.get("page", 1)
    """
    Perform a search on the GitHub code API.

    Args:
        query (str): The search query to execute.
        per_page (int): Results to fetch per page (max 100).
        page (int): Page number of the results to fetch.

    Returns:
        dict: The JSON response from the GitHub API.
    """
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.text-match+json"
    }
    params = {

        "q": query,
        "per_page": per_page,
        "page": page
    }

    response = requests.get(GITHUB_API_URL, headers=headers, params=params)

    if response.status_code == 200:
        json_data = response.json()
        return json_data, json_data.get("total_count") - per_page * page
    else:
        raise Exception(f"GitHub API returned {response.status_code}: {response.text}")


# Function to write results to a CSV file
def write_results_to_csv(results, filename="github_code_search_results.csv"):
    """
    Write search results to a CSV file.

    Args:
        results (list): List of search results to write.
        filename (str): Output CSV file name.
    """
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['repository', '@nestjs/mongoose', 'mongodb', 'mongoose'])
        # Write the header
        writer.writeheader()

        # Write search result data
        writer.writerows(results)


def extract_driver_version(data):
    driver_regex = r'"(?P<name>(@nestjs/mongoose|mongodb|mongoose))":\s*"\^?(?P<version>[\d\.]+)"'
    driver_matrix = {}
    for search_item in data:
        repo = search_item.get("repository", {}).get("name")
        if repo not in driver_matrix:
            driver_matrix[repo] = {}
        for fragment in search_item.get("text_matches", []):
            driver_version = re.search(driver_regex, fragment["fragment"])
            if not driver_version:
                continue
            driver_matrix[repo][driver_version["name"]] = driver_version["version"]
    return driver_matrix


def serialize(data: dict):
    driver_version_arr = []
    for repo, drivers in data.items():
        driver_version_arr.append({'repository': repo, **drivers})
    return driver_version_arr


def paging_query(q):
    page = 1
    result, remain = search_github_code(q, page=1)
    data = result.get("items", [])
    while remain > 0:
        page+=1
        result, remain = search_github_code(q, page=page)
        data.extend(result.get("items", []))
    return data


# Main script
if __name__ == "__main__":
    # Define the search query
    search_query = [
        '"\\"mongoose\\":" org:setel-engineering filename:package.json',
        '"\\"mongodb\\":" org:setel-engineering filename:package.json',
        '"\\"@nestjs/mongoose\\":" org:setel-engineering filename:package.json',
    ]

    try:
        # Search GitHub code
        print("Searching GitHub code...")
        items = []
        for query in search_query:
            items.extend(paging_query(query))

        # Extract items from the search result
        print(f"Found {len(items)} results.")

        driver_version_matrix = extract_driver_version(items)
        if items:
            # Write items to a CSV file
            write_results_to_csv(serialize(driver_version_matrix))
            print("Search results written to 'github_code_search_results.csv'.")
        else:
            print("No results found.")
    except Exception as e:
        print(f"An error occurred: {e}")