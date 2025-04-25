import asyncio
import aiohttp
import os
import requests
import csv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read GitHub token from the .env file
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

async def search_github_topics(repo):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.github.com/repos/setel-engineering/{repo}/topics', headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                return result['names']
            else:
                raise Exception(f"GitHub API returned {response.status}: {await response.text()}")


async def main():
    with open('github_code_search_results.csv', 'r') as f:
        reader = csv.DictReader(f)
        tasks={}
        for row in reader:
            repo = row['repository']
            tasks[repo] = asyncio.create_task(search_github_topics(repo))

    data = await asyncio.gather(*tasks.values())
    with open('github_topics.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['repository', 'topics'])
        for repo, row in zip(tasks.keys(), data):
            writer.writerow([repo, ','.join(row)])


if __name__ == "__main__":
    asyncio.run(main())