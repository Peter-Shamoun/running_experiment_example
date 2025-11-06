import os
import re
import csv

# Models to process
MODELS = [
    "claude-sonnet-4-5-20250929",
    "deepseek-ai-deepseek-v3.1",
    "gemini-2.5-pro",
    "gpt-5",
    "meta-llama-3.1-8b-instruct",
    "mistralai-mistral-small-24b-instruct",
    "qwen-qwen3-4b-free"
]

def extract_metrics_from_file(filepath):
    """Extract the 4 key metrics from a grading response file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract grading model
        grader_match = re.search(r'\[Graded by: ([^\]]+)\]', content)
        grader = grader_match.group(1) if grader_match else "Unknown"
        
        # Extract correctness score
        correctness_match = re.search(r'SCORE 1.*?Correctness:?\s*(\d+)/(\d+)', content, re.IGNORECASE)
        if correctness_match:
            correctness = f"{correctness_match.group(1)}/{correctness_match.group(2)}"
        else:
            correctness = "Not found"
        
        # Extract design completeness score
        completeness_match = re.search(r'SCORE 2.*?(?:Design )?Completeness:?\s*(\d+)/(\d+)', content, re.IGNORECASE)
        if completeness_match:
            completeness = f"{completeness_match.group(1)}/{completeness_match.group(2)}"
        else:
            completeness = "Not found"
        
        # Extract original model's KE claim
        model_ke_match = re.search(r'SCORE 3.*?(?:Original )?Model.*?KE.*?:?\s*([\d.]+)\s*J', content, re.IGNORECASE)
        if model_ke_match:
            model_ke = f"{model_ke_match.group(1)} J"
        else:
            model_ke = "Not found"
        
        # Extract grading model's KE estimate
        grader_ke_match = re.search(r'SCORE 4.*?Grading Model.*?KE.*?:?\s*([\d.]+)\s*J', content, re.IGNORECASE)
        if grader_ke_match:
            grader_ke = f"{grader_ke_match.group(1)} J"
        else:
            grader_ke = "Not found"
        
        return {
            'grader': grader,
            'correctness': correctness,
            'completeness': completeness,
            'model_ke': model_ke,
            'grader_ke': grader_ke
        }
    except Exception as e:
        return {
            'grader': 'Error',
            'correctness': f'Error: {str(e)}',
            'completeness': 'Error',
            'model_ke': 'Error',
            'grader_ke': 'Error'
        }

# Collect all data
all_data = []

for model in MODELS:
    model_dir = f"single_chat_grades/{model}"
    if not os.path.exists(model_dir):
        print(f"Warning: Directory not found: {model_dir}")
        continue
    
    for trial in range(1, 11):
        trial_dir = f"{model_dir}/trial_{trial}"
        grading_file = f"{trial_dir}/grading_response.txt"
        
        if os.path.exists(grading_file):
            metrics = extract_metrics_from_file(grading_file)
            all_data.append({
                'Model': model,
                'Trial': trial,
                'Graded By': metrics['grader'],
                'Correctness Score': metrics['correctness'],
                'Completeness Score': metrics['completeness'],
                'Model KE Claim': metrics['model_ke'],
                'Grader KE Estimate': metrics['grader_ke']
            })
            print(f"[OK] Processed {model} - Trial {trial}")
        else:
            print(f"[MISSING] {grading_file}")

# Create CSV
csv_filename = "single_chat_metrics_summary_updated.csv"
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Model', 'Trial', 'Graded By', 'Correctness Score', 'Completeness Score', 
                  'Model KE Claim', 'Grader KE Estimate']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_data)

print(f"\n[SUCCESS] Updated CSV created: {csv_filename}")

# Create a formatted markdown report
md_filename = "SINGLE_CHAT_METRICS_REPORT_UPDATED.md"
with open(md_filename, 'w', encoding='utf-8') as f:
    f.write("# Single Chat Metrics Report (Updated)\n")
    f.write("## Slingshot Design Challenge - All Models & Trials\n\n")
    f.write(f"**Total Trials Analyzed:** {len(all_data)}\n")
    f.write(f"**Note:** 25 trials were regraded to ensure all KE values are present\n\n")
    f.write("---\n\n")
    
    # Group by model
    for model in MODELS:
        model_data = [d for d in all_data if d['Model'] == model]
        if not model_data:
            continue
        
        f.write(f"## Model: `{model}`\n\n")
        f.write(f"**Total Trials:** {len(model_data)}\n\n")
        
        # Create table
        f.write("| Trial | Graded By | Correctness | Completeness | Model's KE | Grader's KE |\n")
        f.write("|-------|-----------|-------------|--------------|------------|-------------|\n")
        
        for data in sorted(model_data, key=lambda x: x['Trial']):
            f.write(f"| {data['Trial']} | {data['Graded By']} | {data['Correctness Score']} | "
                   f"{data['Completeness Score']} | {data['Model KE Claim']} | "
                   f"{data['Grader KE Estimate']} |\n")
        
        f.write("\n")
        
        # Calculate averages if possible
        try:
            correctness_scores = []
            completeness_scores = []
            model_kes = []
            grader_kes = []
            
            for data in model_data:
                # Parse correctness
                if '/' in data['Correctness Score']:
                    correctness_scores.append(int(data['Correctness Score'].split('/')[0]))
                
                # Parse completeness
                if '/' in data['Completeness Score']:
                    completeness_scores.append(int(data['Completeness Score'].split('/')[0]))
                
                # Parse KE values
                model_ke_key = "Model KE Claim"
                grader_ke_key = "Grader KE Estimate"
                if 'J' in data[model_ke_key] and 'Not found' not in data[model_ke_key]:
                    model_kes.append(float(data[model_ke_key].replace('J', '').strip()))
                
                if 'J' in data[grader_ke_key] and 'Not found' not in data[grader_ke_key]:
                    grader_kes.append(float(data[grader_ke_key].replace('J', '').strip()))
            
            if correctness_scores:
                f.write(f"**Average Correctness Score:** {sum(correctness_scores)/len(correctness_scores):.1f}/18\n\n")
            if completeness_scores:
                f.write(f"**Average Completeness Score:** {sum(completeness_scores)/len(completeness_scores):.1f}/34\n\n")
            if model_kes:
                f.write(f"**Average Model's KE Claim:** {sum(model_kes)/len(model_kes):.2f} J\n\n")
            if grader_kes:
                f.write(f"**Average Grader's KE Estimate:** {sum(grader_kes)/len(grader_kes):.2f} J\n\n")
            
            # Check for missing values
            missing_count = sum(1 for d in model_data if 'Not found' in d['Model KE Claim'] or 'Not found' in d['Grader KE Estimate'])
            if missing_count > 0:
                f.write(f"**WARNING:** {missing_count} trials still have missing KE values\n\n")
        except Exception as e:
            f.write(f"*Could not calculate averages: {e}*\n\n")
        
        f.write("---\n\n")

print(f"[SUCCESS] Updated markdown report created: {md_filename}")
print(f"\n[SUCCESS] All metrics extracted successfully!")

