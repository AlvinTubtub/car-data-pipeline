import csv
import random
import time
import sys # Import for sys.stderr for logging

# --- CONFIGURATION ---
NUM_ROWS = 550_000 # 10k test dataset
FILENAME = "dirty_car_listings.csv"

# --- BASE DATA FOR GENERATION (Used Car Listings, Philippines) ---
BRANDS = [
    "Toyota", "Honda", "Mitsubishi", "Nissan", "Ford",
    "Hyundai", "Kia", "Suzuki", "Mazda", "Chevrolet",
    "Isuzu", "MG", "Geely", "Foton"
]
MODELS = [
    "Vios", "Wigo", "Fortuner", "Innova", "City",
    "Civic", "CR-V", "Montero Sport", "Xpander", "Mirage",
    "Almera", "Navara", "Ranger", "EcoSport", "Accent",
    "Tucson", "Picanto", "Sportage", "Ertiga", "CX-5",
    "MU-X", "D-Max", "HR-V", "BR-V"
]
TRIMS = ["GLX", "GL", "VGT", "GXL", "Sport", "LE", "XLE", "AT", "MT", ""]
SOURCES = [
    "Carmudi", "AutoDeal", "Facebook Marketplace", "OLX",
    "Toyota Certified Pre-Owned", "Honda Cars Pre-Owned", "SM Auto", "Local Dealer"
]
# Filler words real listings add (also targeted for removal during fingerprinting)
FILLERS = ["RUSH", "NEGO", "Nego", "Negotiable", "URGENT", "Preowned", "Certified"]

# --- HELPER FUNCTIONS ---

def log_progress(message):
    """Prints a progress message to the console (stderr for better logging separation)."""
    # Using sys.stderr to not interfere with potential output redirection
    print(f"[INFO] {message}", file=sys.stderr)

def corrupt_price(base_price: float) -> str:
    """Makes the price dirty (string, symbols, errors)"""
    r = random.random()
    if r < 0.1: return f"${base_price:.2f}" # USD symbol (some listings target OFW buyers)
    if r < 0.2: return f"{base_price:.2f} php" # Suffix
    if r < 0.3: return f"{base_price:.2f}".replace('.', ',') # Comma decimal separator
    if r < 0.35: return "" # Missing price
    if r < 0.4: return str(round(base_price * 100)) # Decimal error (too expensive)
    if r < 0.42: return "0" # Free (error)
    return f"{base_price:.2f}"

def corrupt_name(name: str) -> str:
    """Adds typos, filler words, or changes casing"""
    r = random.random()
    if random.random() < 0.25:
        name = f"{name} {random.choice(FILLERS)}"
    if r < 0.3: return name.lower() # All lowercase
    if r < 0.5: return name.upper() # All uppercase
    if r < 0.6: return name.replace(" ", "  ") # Double space
    if r < 0.7: # Typo (single character removal)
        if len(name) > 1:
            idx = random.randint(0, len(name) - 1)
            return name[:idx] + name[idx + 1:]
        return name
    return name

def corrupt_mileage(base_mileage: int) -> str:
    """Makes the mileage value dirty (units, missing, formatting)"""
    r = random.random()
    if r < 0.1: return "" # Missing value
    if r < 0.2: return f"{base_mileage}km" # No space
    if r < 0.3: return f"{base_mileage:,} KM" # Comma-formatted + caps
    if r < 0.4: return f"{base_mileage} kms" # Plural unit
    return f"{base_mileage} km"

# --- MAIN GENERATION SCRIPT ---

if __name__ == "__main__":
    log_progress(f"Starting generation of {NUM_ROWS:,} dirty car listing rows...")
    start_time = time.time()

    try:
        with open(FILENAME, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write header row
            writer.writerow(["Listing_ID", "Car_Title", "Price_Raw", "Source_Platform", "Date_Scraped", "Mileage_Raw"])

            for i in range(NUM_ROWS):
                # Create a base listing
                brand = random.choice(BRANDS)
                model = random.choice(MODELS)
                trim = random.choice(TRIMS) if random.random() > 0.5 else ""
                full_name = f"{brand} {model} {trim}".strip()

                # Consistent base price in PHP (with two decimals for better corruption)
                base_price = round(random.uniform(150_000.00, 2_000_000.00), 2)

                # Consistent base mileage (km)
                base_mileage = random.randint(500, 250_000)

                # Corrupt the data
                dirty_name = corrupt_name(full_name)
                dirty_price = corrupt_price(base_price)
                dirty_mileage = corrupt_mileage(base_mileage)
                source = random.choice(SOURCES)

                # Random date in March 2024
                day = random.randint(1, 28)
                date = f"2024-03-{day:02d}" # Ensures two digits for day

                writer.writerow([i, dirty_name, dirty_price, source, date, dirty_mileage])

                if (i + 1) % 2_000 == 0:
                    log_progress(f"{i + 1:,} rows generated...")

        end_time = time.time()
        log_progress("-------------------------------------------")
        log_progress(f"✅ Success! File '{FILENAME}' generated with {NUM_ROWS:,} rows.")
        log_progress(f"Total time: {end_time - start_time:.2f} seconds.")
        log_progress("Your turn now: clean this mess in under 2 minutes!")

    except IOError as e:
        log_progress(f"[ERROR] Could not write to file {FILENAME}: {e}")
    except Exception as e:
        log_progress(f"[CRITICAL ERROR] An unexpected error occurred: {e}")