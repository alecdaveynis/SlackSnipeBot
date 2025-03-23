import pandas as pd

def parse_subteam_leaderboard(snipes_file, subteams_file):
    """Parses snipes CSV and subteams CSV to generate a leaderboard where snipes within the same subteam do not count."""

    # Load subteam data, ensuring multi-subteam entries are read correctly
    subteams_df = pd.read_csv(subteams_file, dtype=str, keep_default_na=False)

    # Load snipes data
    snipes_df = pd.read_csv(snipes_file)

    # Create a dictionary mapping names to their subteam(s)
    subteam_map = {}
    for index, row in subteams_df.iterrows():
        name = row["Name"]
        subteam_map[name] = row["Subteam"].split(", ")  # Handle multiple subteams correctly

    # Initialize subteam snipe counts
    subteam_snipe_counts = {}

    # Iterate through each snipe event
    for index, row in snipes_df.iterrows():
        sniper = row["Sniper"]
        target = row["Who got Sniped"]

        # Get the subteams of both sniper and target
        sniper_subteams = subteam_map.get(sniper, [])
        target_subteams = subteam_map.get(target, [])

        # Check if sniper and target share any subteam (skip if true)
        if any(sub in sniper_subteams for sub in target_subteams):
            continue  # Skip this snipe

        # Assign snipes to the sniper's first subteam (assuming first-listed subteam is primary)
        if sniper_subteams:
            main_subteam = sniper_subteams[0]  # Take the first subteam as the main one
            subteam_snipe_counts[main_subteam] = subteam_snipe_counts.get(main_subteam, 0) + 1

    # Sort the dictionary in descending order
    sorted_subteam_snipe_counts = dict(sorted(subteam_snipe_counts.items(), key=lambda item: item[1], reverse=True))

    return sorted_subteam_snipe_counts

if __name__ == "__main__":
    snipes_file = "data/snipe_logs.csv" 
    subteams_file = "data/subteams.csv" 

    subteam_leaderboard = parse_subteam_leaderboard(snipes_file, subteams_file)

    print("Subteam Leaderboard (Descending Order):")
    for subteam, count in subteam_leaderboard.items():
        print(f"{subteam}: {count}")
