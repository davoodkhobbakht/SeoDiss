# site_audit.py
import subprocess
import json

# Run Lighthouse audit for a specific URL
def run_lighthouse_audit(url, output_file='lighthouse_report.json'):
    try:
        # Run Lighthouse with JSON output
        result = subprocess.run(
            ['lighthouse', url, '--output=json', '--output-path', output_file, '--quiet'],
            capture_output=True, text=True
        )
        # Read the generated report from the file
        with open(output_file, 'r') as file:
            audit_report = json.load(file)
        return audit_report
    except Exception as e:
        print(f"Failed to run Lighthouse audit: {e}")
        return {}

# Analyze the Lighthouse report for key SEO metrics
def analyze_lighthouse_report(report):
    seo_score = report['categories']['seo']['score'] * 100
    performance_score = report['categories']['performance']['score'] * 100
    accessibility_score = report['categories']['accessibility']['score'] * 100

    issues = []
    for audit in report['audits'].values():
        if audit['score'] is not None and audit['score'] < 1:
            issues.append({
                'title': audit['title'],
                'description': audit.get('description', ''),
                'details': audit.get('details', '')
            })

    return {
        'seo_score': seo_score,
        'performance_score': performance_score,
        'accessibility_score': accessibility_score,
        'issues': issues
    }

# Example usage of the functions
if __name__ == "__main__":
    url = 'https://example.com/product-a'

    # Run Lighthouse audit
    audit_report = run_lighthouse_audit(url)
    print(f"Lighthouse report for {url}: {audit_report}")

    # Analyze the Lighthouse report
    audit_analysis = analyze_lighthouse_report(audit_report)
    print(f"Audit Analysis for {url}:\nSEO Score: {audit_analysis['seo_score']}\nPerformance Score: {audit_analysis['performance_score']}\nAccessibility Score: {audit_analysis['accessibility_score']}\nIssues: {audit_analysis['issues']}")
