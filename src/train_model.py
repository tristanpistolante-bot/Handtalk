import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
import os

# -----------------------
# SETTINGS
# -----------------------
dataset_path    = r"C:\Handtalk\HandSigns"
model_save_path = r"C:\Handtalk\model.h5"

# [CHANGED] updated to 65 (63 landmarks + 2 spread features)
FEATURE_SIZE = 65

print("📁 Dataset path:", dataset_path)

# -----------------------
# LOAD DATASET (.NPY)
# -----------------------
X = []
y = []
class_names = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

skipped = 0

for label_idx, class_name in enumerate(class_names):
    class_folder = os.path.join(dataset_path, class_name)

    if not os.path.isdir(class_folder):
        continue

    for file in os.listdir(class_folder):
        if file.endswith(".npy"):
            file_path = os.path.join(class_folder, file)
            data      = np.load(file_path)

            # [CHANGED] accept both old (63) and new (65) samples
            if data.shape == (65,):
                X.append(data)
                y.append(label_idx)

            elif data.shape == (63,):
                # pad old samples with 0.0 for the 2 missing spread features
                data = np.append(data, [0.0, 0.0])
                X.append(data)
                y.append(label_idx)
                skipped += 1

print("🧠 Classes:", class_names)
print("📊 Total samples:", len(X))
print(f"⚠️  Old 63-feature samples padded: {skipped}")

X = np.array(X)
y = np.array(y)

# -----------------------
# SPLIT DATA
# -----------------------
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -----------------------
# [CHANGED] CLASS WEIGHTS
# so U, V, R get more attention during training
# -----------------------
class_weights_array = compute_class_weight(
    class_weight="balanced",
    classes=np.unique(y_train),
    y=y_train
)
class_weight_dict = dict(enumerate(class_weights_array))

print("\n⚖️  Class weights (higher = more attention):")
for idx, name in enumerate(class_names):
    if idx in class_weight_dict:
        w = class_weight_dict[idx]
        marker = " ← boosted" if name in ["U", "V", "R"] else ""
        print(f"   {name}: {w:.3f}{marker}")

# -----------------------
# BUILD MODEL (LANDMARK)
# [CHANGED] input shape 63 → 65
# -----------------------
model = models.Sequential([
    layers.Input(shape=(FEATURE_SIZE,)),

    layers.Dense(256, activation='relu'),
    layers.Dropout(0.3),

    layers.Dense(128, activation='relu'),
    layers.Dropout(0.3),

    layers.Dense(64, activation='relu'),
    layers.Dropout(0.2),

    layers.Dense(len(class_names), activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# -----------------------
# TRAIN MODEL
# [CHANGED] epochs 20 → 50, added class_weight
# -----------------------
print("\n🚀 Starting training...\n")

history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=32,
    class_weight=class_weight_dict
)

# -----------------------
# SAVE MODEL
# -----------------------
model.save(model_save_path)

print("\n✅ Model saved at:", model_save_path)

# -----------------------
# PRINT FINAL ACCURACY
# -----------------------
final_acc     = history.history["accuracy"][-1]
final_val_acc = history.history["val_accuracy"][-1]

print(f"🎯 Train accuracy:      {final_acc*100:.1f}%")
print(f"🎯 Validation accuracy: {final_val_acc*100:.1f}%")