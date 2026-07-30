import re

with open("crypto_momentum/ai_predictor.py", "r") as f:
    content = f.read()

new_fi_logic = """            feature_importances = {}
            for name, clf in self.model.named_estimators_.items():
                if hasattr(clf, "feature_importances_"):
                    # Vectorized addition of feature importances
                    for i, col in enumerate(feature_cols):
                        feature_importances[col] = (
                            feature_importances.get(col, 0)
                            + clf.feature_importances_[i]
                        )

            # Average the importances
            num_models_with_fi = sum(
                1
                for clf in self.model.named_estimators_.values()
                if hasattr(clf, "feature_importances_")
            )
            if num_models_with_fi > 0:
                feature_importances = {
                    k: v / num_models_with_fi for k, v in feature_importances.items()
                }

            # Keep top 5 features for display
            feature_importances = dict(
                sorted(
                    feature_importances.items(), key=lambda item: item[1], reverse=True
                )[:5]
            )"""

# In the ai_predictor file we can just leave it, since it's only 5-10 features and O(n).
# However, the previous code had `sorted(..., reverse=True)` without `[:5]`. I'll add `[:5]` to avoid returning all features to the UI unnecessarily if there are many.

pattern = r"            feature_importances = \{\}.*?feature_importances = dict\(\n                sorted\(\n                    feature_importances\.items\(\), key=lambda item: item\[1\], reverse=True\n                \)\n            \)"
replaced = re.sub(pattern, new_fi_logic, content, flags=re.DOTALL)

with open("crypto_momentum/ai_predictor.py", "w") as f:
    f.write(replaced)

print("Patched ai_predictor.py feature importances to limit top 5.")
