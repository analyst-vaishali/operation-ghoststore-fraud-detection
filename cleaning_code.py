"""
Operation GhostStore - Banned Seller Resurrection Detection
Author: Vaishali Desai | Project: Trust & Safety Fraud Detection
Date: Oct 2025

Detects banned sellers creating ghost stores with fake names,
same bank/account fingerprints.
"""

import pandas as pd
import re
import matplotlib.pyplot as plt

# === STEP 1: LOAD DATA ===
# Upload your RAW file: Operation-GhostStore-RAW-MESSY.csv
df = pd.read_csv('Operation-GhostStore-RAW-MESSY.csv')
print(f"Loaded {len(df)} rows")

# === STEP 2: CLEAN SELLER NAMES (Handles 6 evasion tricks) ===
def clean_seller_name(name):
    """Remove HTML, emojis, @ tricks, extra spaces"""
    name = str(name)
    name = re.sub(r'<[^>]+>', '', name)  # Remove <p> <b> <br>
    for bad in ['🔥','💥','™','!!!','**',' - Best Deals','.','  ']:
        name = name.replace(bad, '')
    name = name.replace('@','a').strip()  # Fix G@adget = Gadget
    return name

df['clean_step1'] = df['seller_name_raw'].apply(clean_seller_name)

print("\n--- BEFORE -> AFTER ---")
for i in range(5):
    print(f"{df['seller_name_raw'].iloc[i]} -> {df['clean_step1'].iloc[i]}")

# === STEP 3: MAP TO REAL SELLER (Entity Resolution) ===
def map_to_real_seller(dirty):
    d = str(dirty).lower()
    if 'gadget' in d or 'gaadget' in d:
        return 'GadgetWorld'
    elif 'fashion' in d:
        return 'FashionHub'
    elif 'toy' in d:
        return 'ToyZone'
    elif 'book' in d:
        return 'BookNest'
    elif 'home' in d:
        return 'HomeEssentials'
    else:
        return 'Other'

df['real_seller'] = df['clean_step1'].apply(map_to_real_seller)

# Ghost Report: How many fake names per real seller?
ghost_report = df.groupby('real_seller').agg(
    fake_names=('seller_name_raw','nunique'),
    total_records=('record_id','count')
).reset_index()

print("\n=== GHOST STORE REPORT (Fraud!) ===")
print(ghost_report.to_string(index=False))

# === STEP 4: CLEAN BANK & ADDRESS ===
df['clean_bank'] = df['bank_last4_raw'].astype(str).str.replace(r'[^0-9]','', regex=True)

def clean_address(addr):
    addr = str(addr).lower().replace('street','st').replace('avenue','ave')
    return addr.replace(',','').replace('.','').strip()

df['clean_address'] = df['seller_address_raw'].apply(clean_address)

# === STEP 5: DASHBOARD ===
plt.figure(figsize=(14,5))

plt.subplot(1,2,1)
plt.bar(ghost_report['real_seller'], ghost_report['fake_names'], color='#d62728')
plt.title('Ghost Stores: Fake Names per Real Seller', fontweight='bold')
plt.xticks(rotation=20)
plt.ylabel('Fake Names Count')

plt.subplot(1,2,2)
counts = df['real_seller'].value_counts()
plt.bar(counts.index, counts.values, color='#1f77b4')
plt.title('Total Records per Clean Seller', fontweight='bold')
plt.xticks(rotation=20)

plt.tight_layout()
plt.savefig('My_First_Fraud_Dashboard.png', dpi=150)
plt.show()

# === STEP 6: SAVE CLEANED FILE ===
df.to_csv('GhostStore_CLEANED_By_Me.csv', index=False)
print("\nSaved: GhostStore_CLEANED_By_Me.csv")
print("Saved: My_First_Fraud_Dashboard.png")

print(f"\n=== SUMMARY ===")
print(f"Clean sellers: {df['real_seller'].nunique()}")
print(f"Fake accounts: {ghost_report['fake_names'].sum() - len(ghost_report)}")
