import re

with open("crypto_momentum/ai_predictor.py", "r") as f:
    content = f.read()

content = content.replace(
    "from sklearn.ensemble import GradientBoostingClassifier",
    "from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, VotingClassifier\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.model_selection import TimeSeriesSplit, cross_val_score",
)

init_func = """
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
        rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        lr = LogisticRegression(random_state=42, max_iter=1000)

        self.model = VotingClassifier(
            estimators=[('gb', gb), ('rf', rf), ('lr', lr)],
            voting='soft'
        )
        self.scaler = StandardScaler()
        self.is_trained = False
"""

# Replace __init__
content = re.sub(
    r"    def __init__\(self, df: pd\.DataFrame\):.*?(?=    def prepare_features)",
    init_func,
    content,
    flags=re.DOTALL,
)

train_func = """
    def train_and_predict(self) -> dict:
        \"\"\"
        Trains the model on historical data and predicts the probability
        of a positive return for the current (latest) period.
        \"\"\"
        X, y, feature_cols = self.prepare_features()

        if X is None or len(X) < 30:
            logger.warning("Not enough data to train AI Predictor.")
            return {"confidence": 50.0, "cv_accuracy": 0.0, "feature_importances": {}}

        try:
            # We train on all data except the last row
            X_train = X.iloc[:-1]
            y_train = y.iloc[:-1]

            # The last row is our current state we want to predict
            X_latest = X.iloc[[-1]]

            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_latest_scaled = self.scaler.transform(X_latest)

            # Cross validation
            tscv = TimeSeriesSplit(n_splits=5)
            cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=tscv, scoring='accuracy')
            cv_accuracy = cv_scores.mean() * 100

            # Train model
            self.model.fit(X_train_scaled, y_train)
            self.is_trained = True

            # Predict probability of class 1 (positive return)
            prob = self.model.predict_proba(X_latest_scaled)[0][1]

            # Convert to percentage
            confidence_score = prob * 100

            # Get feature importances from GB and RF models
            feature_importances = {}
            for name, clf in self.model.named_estimators_.items():
                if hasattr(clf, 'feature_importances_'):
                    for i, col in enumerate(feature_cols):
                        feature_importances[col] = feature_importances.get(col, 0) + clf.feature_importances_[i]

            # Average the importances
            num_models_with_fi = sum(1 for clf in self.model.named_estimators_.values() if hasattr(clf, 'feature_importances_'))
            if num_models_with_fi > 0:
                for k in feature_importances:
                    feature_importances[k] /= num_models_with_fi

            # Sort importances
            feature_importances = dict(sorted(feature_importances.items(), key=lambda item: item[1], reverse=True))

            return {
                "confidence": confidence_score,
                "cv_accuracy": cv_accuracy,
                "feature_importances": feature_importances
            }

        except Exception as e:
            logger.error(f"Error in AI Predictor: {e}")
            return {"confidence": 50.0, "cv_accuracy": 0.0, "feature_importances": {}}
"""

# Replace train_and_predict
content = re.sub(
    r"    def train_and_predict\(self\) -> float:.*",
    train_func,
    content,
    flags=re.DOTALL,
)

with open("crypto_momentum/ai_predictor.py", "w") as f:
    f.write(content)
