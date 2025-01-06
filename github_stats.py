import os
import pandas as pd
from github import Github
from datetime import datetime, timedelta

def analyze_issues(repo_name):
    """Analyze GitHub issues and generate statistics."""
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(repo_name)
    
    thirty_days_ago = datetime.now() - timedelta(days=30)
    issues = repo.get_issues(state='all', since=thirty_days_ago)
    
    issues_data = []
    for issue in issues:
        issues_data.append({
            'number': issue.number,
            'state': issue.state,
            'created_at': issue.created_at,
            'closed_at': issue.closed_at,
            'comments': issue.comments,
            'labels': [l.name for l in issue.labels]
        })
    
    df = pd.DataFrame(issues_data)
    
    avg_time_to_close = 0
    if not df.empty and 'closed_at' in df.columns:
        closed_issues = df[df['closed_at'].notna()]
        if not closed_issues.empty:
            avg_time_to_close = (closed_issues['closed_at'] - closed_issues['created_at']).mean().total_seconds() / 3600
    
    stats = {
        'total_issues': len(df),
        'open_issues': len(df[df['state'] == 'open']) if not df.empty else 0,
        'closed_issues': len(df[df['state'] == 'closed']) if not df.empty else 0,
        'avg_time_to_close': avg_time_to_close,
        'most_common_labels': pd.Series([l for labels in df['labels'] for l in labels]).value_counts().head(5).to_dict() if not df.empty else {}
    }
    
    with open('github_stats.md', 'w') as f:
        f.write(f"# GitHub Issues Statistics\n\n")
        f.write(f"## Last 30 Days Summary\n")
        f.write(f"- Total Issues: {stats['total_issues']}\n")
        f.write(f"- Open Issues: {stats['open_issues']}\n")
        f.write(f"- Closed Issues: {stats['closed_issues']}\n")
        f.write(f"- Average Time to Close: {stats['avg_time_to_close']:.1f} hours\n\n")
        f.write("## Most Common Labels\n")
        for label, count in stats['most_common_labels'].items():
            f.write(f"- {label}: {count}\n")

if __name__ == "__main__":
    repo_name = os.environ["GITHUB_REPOSITORY"]
    analyze_issues(repo_name)