import pandas as pd

def parse_snipe_csv(snipe_file, subteam_file):
    """Parses the snipe CSV file and returns a dictionary of snipers with their snipe counts, 
    ensuring snipes within the same subteam are not counted.
    """
    
    # Read snipes CSV
    snipes_df = pd.read_csv(snipe_file)

    # Read subteams CSV
    subteams_df = pd.read_csv(subteam_file)

    # Create a dictionary mapping names to their subteam(s)
    subteam_map = {}
    for index, row in subteams_df.iterrows():
        name = row["Name"]
        subteam_map[name] = row["Subteam"].split(", ")  # Handle multiple subteams

    # Initialize sniper count dictionary
    sniper_counts = {}

    # Iterate through snipes
    for index, row in snipes_df.iterrows():
        sniper = row["Sniper"]
        target = row["Who got Sniped"]

        # Get sniper and target subteams
        sniper_subteams = subteam_map.get(sniper, [])
        target_subteams = subteam_map.get(target, [])

        # Skip snipes if both belong to at least one common subteam
        if any(sub in sniper_subteams for sub in target_subteams):
            continue  # Ignore this snipe

        # Count valid snipes
        sniper_counts[sniper] = sniper_counts.get(sniper, 0) + 1

    # Sort dictionary in descending order by number of snipes
    sorted_snipers = dict(sorted(sniper_counts.items(), key=lambda item: item[1], reverse=True))

    return sorted_snipers

if __name__ == "__main__":
    snipe_file = "data/snipe_logs.csv" 
    subteam_file = "data/subteams.csv"

    sniper_stats = parse_snipe_csv(snipe_file, subteam_file)

    print("Sniper Rankings (Descending Order):")
    for sniper, count in sniper_stats.items():
        print(f"{sniper}: {count}") 
