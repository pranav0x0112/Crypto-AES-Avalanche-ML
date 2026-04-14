import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor

# Load dataset
df = pd.read_csv("data/avalanche_dataset.csv")

X = df[["bit_flipped"]].values
y = df["avalanche"].values

# -----------------------------
# Train / validation / test split
# -----------------------------
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.25, random_state=42
)

print(f"Train : {len(X_train)} samples")
print(f"Val   : {len(X_val)} samples")
print(f"Test  : {len(X_test)} samples")

# -----------------------------
# Linear Regression
# -----------------------------
lin = LinearRegression()
lin.fit(X_train, y_train)

y_pred_lin = lin.predict(X_test)

print("\n=== Linear Regression ===")
print(f"R²   : {r2_score(y_test, y_pred_lin):.6f}")
print(f"RMSE : {np.sqrt(mean_squared_error(y_test, y_pred_lin)):.6f}")
print(f"MAE  : {mean_absolute_error(y_test, y_pred_lin):.6f}")

# -----------------------------
# Polynomial Regression
# -----------------------------
poly = PolynomialFeatures(degree=2)

X_train_poly = poly.fit_transform(X_train)
X_test_poly  = poly.transform(X_test)

poly_reg = LinearRegression()
poly_reg.fit(X_train_poly, y_train)

y_pred_poly = poly_reg.predict(X_test_poly)

print("\n=== Polynomial Regression ===")
print(f"R²   : {r2_score(y_test, y_pred_poly):.6f}")
print(f"RMSE : {np.sqrt(mean_squared_error(y_test, y_pred_poly)):.6f}")
print(f"MAE  : {mean_absolute_error(y_test, y_pred_poly):.6f}")

# -----------------------------
# Random Forest
# -----------------------------
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

y_pred_rf_test = rf.predict(X_test)

print("\n=== Random Forest ===")
print(f"R²   : {r2_score(y_test, y_pred_rf_test):.6f}")
print(f"RMSE : {np.sqrt(mean_squared_error(y_test, y_pred_rf_test)):.6f}")
print(f"MAE  : {mean_absolute_error(y_test, y_pred_rf_test):.6f}")

# -----------------------------
# Cross-validation
# -----------------------------
scores = cross_val_score(rf, X, y, cv=5, scoring='r2')

print("\nCross-validation R² scores:", scores)
print("Mean R²:", scores.mean())

# -----------------------------
# Plotting
# -----------------------------
bit_range = np.linspace(0, 127, 300).reshape(-1, 1)

lin_line  = lin.predict(bit_range)
poly_line = poly_reg.predict(poly.transform(bit_range))
rf_line   = rf.predict(bit_range)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("AES Avalanche Effect - ML Analysis", fontsize=14)

# Plot 1: model fit
ax1 = axes[0, 0]
ax1.scatter(X_test, y_test, alpha=0.3, s=10, color='steelblue', label='Actual samples')
ax1.plot(bit_range, lin_line,  color='red',    lw=2, label='Linear')
ax1.plot(bit_range, poly_line, color='green',  lw=2, label='Polynomial')
ax1.plot(bit_range, rf_line,   color='orange', lw=2, label='Random Forest')
ax1.axhline(0.5, color='gray', linestyle='--', label='Ideal 0.5')

ax1.set_xlabel('Bit position flipped')
ax1.set_ylabel('Avalanche score')
ax1.set_title('Model fits vs actual data')
ax1.legend()

# Plot 2: avalanche distribution
ax2 = axes[0, 1]
ax2.hist(y, bins=30, color='steelblue', edgecolor='white')
ax2.axvline(0.5, color='red', linestyle='--', label='Ideal 0.5')
ax2.axvline(y.mean(), color='green', linestyle='--', label=f'Mean = {y.mean():.4f}')

ax2.set_title('Distribution of avalanche scores')
ax2.set_xlabel('Avalanche score')
ax2.set_ylabel('Frequency')
ax2.legend()

# Plot 3: average avalanche per bit
ax3 = axes[1, 0]
df_grouped = df.groupby('bit_flipped')['avalanche'].mean()

ax3.bar(df_grouped.index, df_grouped.values, color='steelblue')
ax3.axhline(0.5, color='red', linestyle='--', label='Ideal 0.5')

ax3.set_xlabel('Bit position')
ax3.set_ylabel('Mean avalanche score')
ax3.set_title('Average avalanche per bit position')
ax3.legend()

# Plot 4: residuals
ax4 = axes[1, 1]

residuals_lin  = y_test - y_pred_lin
residuals_poly = y_test - y_pred_poly
residuals_rf   = y_test - y_pred_rf_test

ax4.hist(residuals_lin,  bins=25, alpha=0.5, label='Linear')
ax4.hist(residuals_poly, bins=25, alpha=0.5, label='Polynomial')
ax4.hist(residuals_rf,   bins=25, alpha=0.5, label='Random Forest')

ax4.axvline(0, color='black', linestyle='--')

ax4.set_title('Residuals comparison')
ax4.set_xlabel('Residual error')
ax4.set_ylabel('Count')
ax4.legend()

plt.tight_layout()

# Save result
import os
os.makedirs("results", exist_ok=True)

plt.savefig("results/avalanche_analysis.png", dpi=150)
plt.show()

print("\nPlot saved as results/avalanche_analysis.png")