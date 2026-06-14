import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

try:
    from xgboost import XGBClassifier
    xgboost_available = True
except:
    xgboost_available = False


# =========================
# 1. LOAD DATASETS
# =========================

area_df = pd.read_csv("cropped-area.csv")
pesticide_df = pd.read_csv("pesticides-spray.csv")
production_df = pd.read_csv("production-crop.csv")

print("Area Dataset:", area_df.shape)
print("Pesticide Dataset:", pesticide_df.shape)
print("Production Dataset:", production_df.shape)


# =========================
# 2. CLEAN AREA DATA
# =========================

area_df = area_df.dropna()
area_df.columns = ["Crop", "Cropped_Area", "Area_Percent"]

area_df = area_df[area_df["Crop"] != "The Punjab"]

area_df["Crop"] = area_df["Crop"].str.strip()
area_df["Cropped_Area"] = pd.to_numeric(area_df["Cropped_Area"], errors="coerce")
area_df["Area_Percent"] = pd.to_numeric(area_df["Area_Percent"], errors="coerce")

print("\nCleaned Area Data:")
print(area_df.head())


# =========================
# 3. CLEAN PESTICIDE DATA
# =========================

pesticide_df = pesticide_df.replace("-", np.nan)

for col in pesticide_df.columns:
    if col != "Year":
        pesticide_df[col] = pd.to_numeric(pesticide_df[col], errors="coerce")

# Convert wide crop columns into long format
pesticide_long = pesticide_df.melt(
    id_vars=["Year"],
    var_name="Crop",
    value_name="Pesticide_Usage"
)

pesticide_long["Crop"] = pesticide_long["Crop"].replace({
    "Rice and Rice Nursery": "Rice",
    "Vegetables/ Fruits": "Vegetables"
})

pesticide_long["Crop"] = pesticide_long["Crop"].str.strip()

print("\nPesticide Long Format:")
print(pesticide_long.head())


# =========================
# 4. CLEAN PRODUCTION DATA
# =========================

production_df.columns = [
    "Year",
    "Total_Area_Sown",
    "Area_Thousand_Hect",
    "Production_Thousand_Tons",
    "Index_Area_Sown",
    "Index_Production",
    "Share_Area_Sown"
]

for col in production_df.columns:
    if col != "Year":
        production_df[col] = pd.to_numeric(production_df[col], errors="coerce")

production_df = production_df.fillna(production_df.mean(numeric_only=True))

print("\nProduction Data:")
print(production_df.head())


# =========================
# 5. MERGE DATASETS
# =========================

merged_df = pesticide_long.merge(area_df, on="Crop", how="left")
merged_df = merged_df.merge(production_df, on="Year", how="left")

# Fill missing values
merged_df = merged_df.fillna(0)

print("\nMerged Dataset:")
print(merged_df.head())
print("Merged Shape:", merged_df.shape)


# =========================
# 6. FEATURE ENGINEERING
# =========================

merged_df["Pesticide_per_Area"] = merged_df["Pesticide_Usage"] / (merged_df["Cropped_Area"] + 1)

merged_df["Production_per_Area"] = merged_df["Production_Thousand_Tons"] / (
    merged_df["Area_Thousand_Hect"] + 1
)

merged_df["Area_Risk"] = np.where(merged_df["Area_Percent"] < 5, 1, 0)

merged_df["Pesticide_Risk"] = np.where(
    merged_df["Pesticide_Usage"] > merged_df["Pesticide_Usage"].median(),
    1,
    0
)

merged_df["Production_Risk"] = np.where(
    merged_df["Index_Production"] < merged_df["Index_Production"].median(),
    1,
    0
)


# =========================
# 7. CREATE CRISIS TARGET
# =========================

risk_score = (
    merged_df["Area_Risk"] +
    merged_df["Pesticide_Risk"] +
    merged_df["Production_Risk"]
)

merged_df["Crisis_Level"] = np.where(
    risk_score <= 1,
    "Low Risk",
    np.where(risk_score == 2, "Medium Risk", "High Risk")
)

print("\nCrisis Level Counts:")
print(merged_df["Crisis_Level"].value_counts())


# =========================
# 8. ENCODE CATEGORICAL DATA
# =========================

crop_encoder = LabelEncoder()
target_encoder = LabelEncoder()

merged_df["Crop_Encoded"] = crop_encoder.fit_transform(merged_df["Crop"])
merged_df["Target"] = target_encoder.fit_transform(merged_df["Crisis_Level"])


# =========================
# 9. SELECT FEATURES
# =========================

features = [
    "Crop_Encoded",
    "Pesticide_Usage",
    "Cropped_Area",
    "Area_Percent",
    "Total_Area_Sown",
    "Area_Thousand_Hect",
    "Production_Thousand_Tons",
    "Index_Area_Sown",
    "Index_Production",
    "Pesticide_per_Area",
    "Production_per_Area"
]

X = merged_df[features]
y = merged_df["Target"]


# =========================
# 10. TRAIN TEST SPLIT
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)


# =========================
# 11. TRAIN MODELS
# =========================

models = {
    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        max_depth=5,
        random_state=42
    ),
    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )
}

if xgboost_available:
    models["XGBoost"] = XGBClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        random_state=42,
        eval_metric="mlogloss"
    )


best_model = None
best_accuracy = 0
best_model_name = ""

print("\n================ MODEL RESULTS ================")

for name, model in models.items():
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print(f"\n{name} Accuracy: {acc * 100:.2f}%")
    print(classification_report(
        y_test,
        preds,
        target_names=target_encoder.classes_
    ))

    if acc > best_accuracy:
        best_accuracy = acc
        best_model = model
        best_model_name = name


print("\nBest Model:", best_model_name)
print("Best Accuracy:", round(best_accuracy * 100, 2), "%")


# =========================
# 12. SAVE MODEL + DATA
# =========================

joblib.dump(best_model, "agri_crisis_model.pkl")
joblib.dump(crop_encoder, "crop_encoder.pkl")
joblib.dump(target_encoder, "target_encoder.pkl")

merged_df.to_csv("final_agriculture_crisis_dataset.csv", index=False)

print("\nFiles saved:")
print("agri_crisis_model.pkl")
print("crop_encoder.pkl")
print("target_encoder.pkl")
print("final_agriculture_crisis_dataset.csv")


# =========================
# 13. SAMPLE PREDICTION
# =========================

sample = X_test.iloc[[0]]
prediction = best_model.predict(sample)
predicted_class = target_encoder.inverse_transform(prediction)

print("\nSample Prediction:")
print(sample)
print("Predicted Crisis Level:", predicted_class[0])