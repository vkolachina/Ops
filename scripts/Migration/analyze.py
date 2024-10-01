# analyze_dry_runs.py
import os
import json

def analyze_dry_run(repo_name):
    dry_run_path = f"./dry_runs/{repo_name}/results.json"
    if not os.path.exists(dry_run_path):
        return None

    with open(dry_run_path, 'r') as f:
        data = json.load(f)

    total_items = data['total_count']
    converted_items = data['converted_count']
    conversion_rate = (converted_items / total_items) * 100 if total_items > 0 else 0

    return {
        'repo': repo_name,
        'conversion_rate': conversion_rate,
        'total_items': total_items,
        'converted_items': converted_items
    }

def main():
    repos = [d for d in os.listdir('./dry_runs') if os.path.isdir(os.path.join('./dry_runs', d))]
    results = [analyze_dry_run(repo) for repo in repos]
    results = [r for r in results if r is not None]

    results.sort(key=lambda x: x['conversion_rate'], reverse=True)

    for result in results:
        print(f"Repo: {result['repo']}")
        print(f"Conversion Rate: {result['conversion_rate']:.2f}%")
        print(f"Total Items: {result['total_items']}")
        print(f"Converted Items: {result['converted_items']}")
        print("---")

    avg_conversion_rate = sum(r['conversion_rate'] for r in results) / len(results)
    print(f"Average Conversion Rate: {avg_conversion_rate:.2f}%")

if __name__ == "__main__":
    main()