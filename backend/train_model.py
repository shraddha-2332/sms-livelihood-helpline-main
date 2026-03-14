import os
import sys
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

print("🤖 Intent Classifier Training Script")
print("=" * 60)

# Ensure directories exist
os.makedirs('model', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Dataset path
csv_path = 'data/sample_dataset.csv'

# Check if dataset exists
if not os.path.exists(csv_path):
    print(f"❌ Dataset not found at {csv_path}")
    print("Creating sample dataset...")
    
    # Create sample dataset
    sample_data = {
        'text': [
            'I need fertilizer information', 'खाद की जानकारी चाहिए', 'Best fertilizer for wheat',
            'I need a loan', 'ऋण कैसे मिलेगा', 'Loan for farmers',
            'What is wheat price', 'गेहूं की कीमत', 'Market price of rice',
            'I need a job', 'नौकरी चाहिए', 'Employment opportunities',
            'Training programs', 'प्रशिक्षण कार्यक्रम', 'Skill development courses',
            'Subsidy information', 'सब्सिडी की जानकारी', 'Government subsidy',
            'Crop disease problem', 'फसल में बीमारी', 'Plant disease treatment',
            'Farmer scheme', 'किसान योजना', 'Agricultural scheme',
            'Help needed', 'मदद चाहिए', 'I have a question',
        ],
        'intent': [
            'faq_fertilizer', 'faq_fertilizer', 'faq_fertilizer',
            'faq_loan', 'faq_loan', 'faq_loan',
            'market_price', 'market_price', 'market_price',
            'job_search', 'job_search', 'job_search',
            'training', 'training', 'training',
            'faq_subsidy', 'faq_subsidy', 'faq_subsidy',
            'agriculture_help', 'agriculture_help', 'agriculture_help',
            'faq_scheme', 'faq_scheme', 'faq_scheme',
            'unknown', 'unknown', 'unknown'
        ],
        'language': [
            'en', 'hi', 'en',
            'en', 'hi', 'en',
            'en', 'hi', 'en',
            'en', 'hi', 'en',
            'en', 'hi', 'en',
            'en', 'hi', 'en',
            'en', 'hi', 'en',
            'en', 'hi', 'en',
            'en', 'hi', 'en'
        ]
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv(csv_path, index=False)
    print(f"✅ Created sample dataset at {csv_path}")
else:
    print(f"✅ Found dataset at {csv_path}")

# Load dataset
print("\n📊 Loading dataset...")
df = pd.read_csv(csv_path)

print(f"   Total samples: {len(df)}")
print(f"   Intents: {df['intent'].nunique()}")
print(f"\n   Intent distribution:")
print(df['intent'].value_counts())

# Check required columns
required_columns = {'text', 'intent'}
if not required_columns.issubset(df.columns):
    print(f"❌ Dataset must contain columns: {required_columns}")
    print(f"   Found: {list(df.columns)}")
    sys.exit(1)

# Prepare data
print("\n🔧 Preparing data...")
X = df['text'].fillna('')
y = df['intent'].fillna('unknown')

# Check for empty data
if len(X) == 0 or len(y) == 0:
    print("❌ Dataset is empty!")
    sys.exit(1)

# Split data
# Use stratified split if we have enough samples per class, otherwise use regular split
try:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
except ValueError:
    # If stratified split fails (not enough samples per class), use regular split
    print("⚠️  Warning: Not enough samples for stratified split. Using regular split.")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

print(f"   Training samples: {len(X_train)}")
print(f"   Test samples: {len(X_test)}")

# Create and train model
print("\n🎯 Training model...")
clf = make_pipeline(
    TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=10000,
        min_df=1
    ),
    LogisticRegression(
        max_iter=1000,
        random_state=42
    )
)

clf.fit(X_train, y_train)
print("✅ Model trained successfully")

# Evaluate model
print("\n📈 Evaluating model...")
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"   Accuracy: {accuracy:.2%}")
print("\n   Classification Report:")
print(classification_report(y_test, y_pred))

# Save model
model_path = 'model/intent_clf.joblib'
joblib.dump(clf, model_path)
print(f"\n💾 Model saved to: {model_path}")

# Test model with sample inputs
print("\n🧪 Testing model with sample inputs:")
test_inputs = [
    "I need loan information",
    "खाद की जानकारी",
    "What is the price of wheat",
    "I need a job",
    "Help with training"
]

for text in test_inputs:
    intent = clf.predict([text])[0]
    proba = clf.predict_proba([text])
    confidence = max(proba[0])
    print(f"   '{text}' → {intent} ({confidence:.2%})")

print("\n" + "=" * 60)
print("✅ Training complete!")
print("\nNext steps:")
print("1. Review the model performance above")
print("2. Add more training data to data/sample_dataset.csv")
print("3. Run this script again to retrain")
print("4. Start the application with: docker-compose up")