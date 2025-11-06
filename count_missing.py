import csv

with open('single_chat_metrics_summary_updated.csv', encoding='utf-8') as f:
    data = list(csv.DictReader(f))

missing = [d for d in data if 'Not found' in d['Model KE Claim'] or 'Not found' in d['Grader KE Estimate']]

print(f"\nStill missing KE values: {len(missing)} out of {len(data)} trials\n")
print("Trials with missing values:")
print("-" * 60)

for d in missing:
    model_ke = d['Model KE Claim']
    grader_ke = d['Grader KE Estimate']
    print(f"{d['Model']}, Trial {d['Trial']}")
    print(f"  Model KE: {model_ke}, Grader KE: {grader_ke}")

