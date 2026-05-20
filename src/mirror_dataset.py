import os
import numpy as np

print("🔄 Mirror Dataset Started...")
print("📌 This converts right-hand samples to left-hand by flipping x coordinates")

# -----------------------
# SETTINGS
# -----------------------
DATASET_FOLDER = r"C:\Handtalk\HandSigns"
FEATURE_SIZE   = 65  # 63 landmarks + 2 spread features

# -----------------------
# PROCESS EACH LETTER
# -----------------------
total_mirrored = 0

for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":

    letter_folder = os.path.join(DATASET_FOLDER, letter)

    if not os.path.isdir(letter_folder):
        print(f"⚠️  Skipping {letter} — folder not found")
        continue

    # get all existing .npy files
    existing_files = [f for f in os.listdir(letter_folder) if f.endswith(".npy")]

    # skip if already has mirrored files (avoid duplicating)
    mirrored_files = [f for f in existing_files if "_mirror" in f]

    if mirrored_files:
        print(f"⏭️  {letter}: already has {len(mirrored_files)} mirrored files — skipping")
        continue

    mirrored_count = 0

    for file in existing_files:
        file_path = os.path.join(letter_folder, file)
        data      = np.load(file_path)

        # -----------------------
        # MIRROR X COORDINATES
        # landmarks are stored as x,y,z x,y,z x,y,z...
        # x is at index 0, 3, 6, 9... (every 3rd starting at 0)
        # flip x by doing 1.0 - x
        # -----------------------
        mirrored = data.copy()

        if data.shape == (65,):
            # flip x for all 21 landmarks (indices 0,3,6,...,60)
            for i in range(0, 63, 3):
                mirrored[i] = 1.0 - data[i]

            # recalculate spread features with mirrored x
            # index tip x = landmark 8 x = index 8*3 = 24
            # middle tip x = landmark 12 x = index 12*3 = 36
            spread_x = abs(mirrored[24] - mirrored[36])
            mirrored[63] = spread_x  # feature 64 (spread_x)
            # spread_y stays the same (y not flipped)

        elif data.shape == (63,):
            # old format — flip x only
            for i in range(0, 63, 3):
                mirrored[i] = 1.0 - data[i]

        else:
            print(f"⚠️  Unexpected shape {data.shape} in {file} — skipping")
            continue

        # save mirrored file with _mirror suffix
        mirror_filename = file.replace(".npy", "_mirror.npy")
        mirror_path     = os.path.join(letter_folder, mirror_filename)

        np.save(mirror_path, mirrored)
        mirrored_count += 1

    total_mirrored += mirrored_count
    print(f"✅ {letter}: mirrored {mirrored_count} samples")

print(f"\n Done! Total mirrored samples created: {total_mirrored}")
