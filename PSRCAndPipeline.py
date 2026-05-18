# advanced way to search, saves at the end on choice the csv, tracks teh erros % of matched psr in the whole folder

# the bash command to launch the code:  python3 PSR_ATNF_ADVANCED_match.py -year 2022

import os
import re
import argparse
import pandas as pd
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
from psrqpy import QueryATNF

# ------------------------ FUNCTION DEFINITIONS ------------------------

def parse_filename(filename):
    """Extract period, DM, RA, DEC from filename."""
    period, dm, ra_ex, dec_ex = None, None, None, None
    match_pd = re.search(r'_P(\d+\.\d+)_candDM(\d+\.\d+)', filename)
    match_coords = re.search(r'BS_\d+_(\d{6})\+?(\d{6})_', filename)
    if match_pd:
        period = float(match_pd.group(1))
        dm = float(match_pd.group(2))
    if match_coords:
        ra_str = match_coords.group(1)
        dec_str = match_coords.group(2)
        ra_ex = f"{ra_str[:2]}h{ra_str[2:4]}m{ra_str[4:]}s"
        dec_ex = f"{dec_str[:2]}d{dec_str[2:4]}m{dec_str[4:]}s"
    return period, dm, ra_ex, dec_ex

def convert_atnf_ra_dec(raj, decj):
    """Convert ATNF decimal RA/DEC to sexagesimal format."""
    try:
        ra_deg = float(raj) * 15.0  # Convert hours to degrees
        dec_deg = float(decj)
        coord = SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg, frame='icrs')
        ra_str, dec_str = coord.to_string('hmsdms').split()
        return ra_str, dec_str
    except Exception:
        return None, None

def find_atnf_matches(period, dm, tolerance_ms=1.0, tolerance_dm=1.0):
    """Find ATNF matches within given tolerance."""
    return catalogue[
        (np.abs(catalogue['P0'] * 1000 - period) < tolerance_ms) &
        (np.abs(catalogue['DM'] - dm) < tolerance_dm)
    ]

def calculate_beam_offset(ra1, dec1, ra2, dec2):
    """Calculate angular distance in degrees between two sky positions."""
    try:
        coord1 = SkyCoord(ra1, dec1, frame='icrs')
        coord2 = SkyCoord(ra2, dec2, frame='icrs')
        return coord1.separation(coord2).degree
    except Exception:
        return np.nan

# ------------------------ MAIN SCRIPT ------------------------

def main():
    # ---- ARGPARSE ----
    parser = argparse.ArgumentParser(description="Match pulsar candidates to known ATNF entries.")
    parser.add_argument("-year", required=True, help="Year directory to analyze (e.g. 2022)")
    args = parser.parse_args()
    year = args.year

    main_dir = f'/home/nour/Nancay/Pulsar_findings/final_plots_tar/{year}'

    bs_filenames = []
    for subdir in os.listdir(main_dir):
        full_path = os.path.join(main_dir, subdir)
        if os.path.isdir(full_path) and subdir.startswith("Plots_CAND_"):
            for fname in os.listdir(full_path):
                if fname.startswith('BS_') and fname.endswith('.pdf'):
                    bs_filenames.append(os.path.join(full_path, fname))

    # Query ATNF once
    query = QueryATNF(params=['JNAME', 'P0', 'DM', 'RAJ', 'DECJ', 'GL', 'GB'])
    global catalogue
    catalogue = query.table.to_pandas()

    matched_data = []
    unmatched_data = []

    for full_path in bs_filenames:
        filename = os.path.basename(full_path)
        period, dm, ra_ex, dec_ex = parse_filename(filename)

        if period is None or dm is None or ra_ex is None or dec_ex is None:
            continue

        matches = find_atnf_matches(period, dm)

        if not matches.empty:
            for _, row in matches.iterrows():
                atnf_ra_str, atnf_dec_str = convert_atnf_ra_dec(row['RAJ'], row['DECJ'])
                beam_offset = calculate_beam_offset(ra_ex, dec_ex, atnf_ra_str, atnf_dec_str)
                matched_data.append({
                    'filename': filename,
                    'JNAME': row['JNAME'],
                    'Period (ms)': period,
                    'DM': dm,
                    'RAJ': row['RAJ'],
                    'DECJ': row['DECJ'],
                    'GL': row['GL'],
                    'GB': row['GB'],
                    'beam_offset (deg)': round(beam_offset, 4)
                })
        else:
            unmatched_data.append({
                'filename': filename,
                'Period (ms)': period,
                'DM': dm,
                'candidate_RA': ra_ex,
                'candidate_DEC': dec_ex,
                'RAJ': None,
                'DECJ': None
            })

    # Convert to DataFrames
    matched_df = pd.DataFrame(matched_data)
    unmatched_df = pd.DataFrame(unmatched_data)

    # ---- OUTPUTS ----
    print("\n================ MATCHED PULSARS ================")
    print(matched_df.to_string(index=False) if not matched_df.empty else "None found.")

    print("\n================ UNMATCHED CANDIDATES ================")
    print(unmatched_df.to_string(index=False) if not unmatched_df.empty else "None found.")

    # ---- STATS ---- ADD TO BAUDORIE
    total = len(bs_filenames)
    matched = matched_df['filename'].nunique() if not matched_df.empty else 0
    percent = (matched / total) * 100 if total > 0 else 0
    print(f"\n→ Total BS files: {total}")
    print(f"→ Matched pulsars: {matched}")
    print(f"→ Unmatched pulsars: {total-matched}")
    print(f"→ Match rate: {percent:.2f}%")

    # ---- SAVE TO CSV IF ASKED ----
    save = input("\nDo you want to save the tables to CSV? (y/n): ").strip().lower()
    if save == 'y':
        matched_df.to_csv(f"matched_pulsars_{year}.csv", index=False)
        unmatched_df.to_csv(f"unmatched_candidates_{year}.csv", index=False)
        print(f"CSV files saved: matched_pulsars_{year}.csv and unmatched_candidates_{year}.csv")

if __name__ == "__main__":
    main()

