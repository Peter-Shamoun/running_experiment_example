import csv
import statistics

# Read the CSV
with open('single_chat_metrics_summary_final.csv', 'r', encoding='utf-8') as f:
    data = list(csv.DictReader(f))

# Get unique models
models = []
for d in data:
    if d['Model'] not in models:
        models.append(d['Model'])

# Calculate medians for each model
median_data = []

for model in models:
    model_trials = [d for d in data if d['Model'] == model]
    
    # Extract numeric values
    correctness_values = []
    completeness_values = []
    model_ke_values = []
    grader_ke_values = []
    
    for trial in model_trials:
        # Parse correctness score (e.g., "18/18" -> 18)
        if '/' in trial['Correctness Score']:
            correctness_values.append(int(trial['Correctness Score'].split('/')[0]))
        
        # Parse completeness score
        if '/' in trial['Completeness Score']:
            completeness_values.append(int(trial['Completeness Score'].split('/')[0]))
        
        # Parse Model KE
        if 'J' in trial['Model KE Claim']:
            model_ke_values.append(float(trial['Model KE Claim'].replace('J', '').strip()))
        
        # Parse Grader KE
        if 'J' in trial['Grader KE Estimate']:
            grader_ke_values.append(float(trial['Grader KE Estimate'].replace('J', '').strip()))
    
    # Calculate medians
    median_correctness = statistics.median(correctness_values) if correctness_values else 0
    median_completeness = statistics.median(completeness_values) if completeness_values else 0
    median_model_ke = statistics.median(model_ke_values) if model_ke_values else 0
    median_grader_ke = statistics.median(grader_ke_values) if grader_ke_values else 0
    
    median_data.append({
        'Model': model,
        'Median Correctness': f"{median_correctness}/18",
        'Median Completeness': f"{median_completeness}/34",
        'Median Model KE Claim': f"{median_model_ke} J",
        'Median Grader KE Estimate': f"{median_grader_ke} J"
    })
    
    print(f"\n{model}:")
    print(f"  Median Correctness: {median_correctness}/18")
    print(f"  Median Completeness: {median_completeness}/34")
    print(f"  Median Model KE Claim: {median_model_ke} J")
    print(f"  Median Grader KE Estimate: {median_grader_ke} J")

# Save to CSV
csv_filename = "single_chat_median_metrics.csv"
with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['Model', 'Median Correctness', 'Median Completeness', 
                  'Median Model KE Claim', 'Median Grader KE Estimate']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(median_data)

print(f"\n{'='*60}")
print(f"Median metrics saved to: {csv_filename}")
print('='*60)

# Create markdown table
md_filename = "SINGLE_CHAT_MEDIAN_METRICS.md"
with open(md_filename, 'w', encoding='utf-8') as f:
    f.write("# Single Chat Median Metrics Summary\n\n")
    f.write("## Median values across 10 trials per model\n\n")
    f.write("| Model | Median Correctness | Median Completeness | Median Model KE | Median Grader KE |\n")
    f.write("|-------|-------------------|---------------------|-----------------|------------------|\n")
    
    for row in median_data:
        f.write(f"| {row['Model']} | {row['Median Correctness']} | {row['Median Completeness']} | "
               f"{row['Median Model KE Claim']} | {row['Median Grader KE Estimate']} |\n")
    
    f.write("\n---\n\n")
    f.write("## Notes\n\n")
    f.write("- **Correctness**: Out of 18 points max\n")
    f.write("- **Completeness**: Out of 34 points max\n")
    f.write("- **Model KE**: Kinetic energy claimed by the model itself\n")
    f.write("- **Grader KE**: Kinetic energy validated/calculated by the grading model\n")
    f.write("- **0 J values**: Indicate designs missing critical components or insufficient data\n")

print(f"Markdown summary saved to: {md_filename}")


