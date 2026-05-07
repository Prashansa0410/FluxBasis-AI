import pandas as pd
import xgboost as xgb
import pickle
import json
import os

def load_model(model_path):
    with open(model_path, 'rb') as file:
        model = pickle.load(file)
    return model

def predict_flaky_tests(model, input_csv, output_dir):
    # Load input data
    data = pd.read_csv(input_csv)

    predictions = model.predict(data)

    predictions_df = pd.DataFrame(predictions, columns=["prediction"])

    predictions_df.to_csv("reports/predictions.csv", index=False)

    print("Predictions saved successfully!")
    
    # Ensure 'test_name' column exists
    if 'test_name' not in data.columns:
        raise ValueError("Input CSV must contain a 'test_name' column.")
    
    # Prepare features for prediction
    features = data.drop(columns=['test_name'])
    
    # Predict probabilities
    probabilities = model.predict_proba(features)[:, 1]
    
    # Generate predictions
    predicted_labels = (probabilities > 0.7).astype(int)
    
    # Create output DataFrame
    output = pd.DataFrame({
        'test_name': data['test_name'],
        'flaky_probability': probabilities,
        'predicted_label': predicted_labels
    })
    
    # Save report as JSON
    json_path = os.path.join(output_dir, 'flaky_tests_report.json')
    output.to_json(json_path, orient='records', lines=True)
    
    # Save report as CSV
    csv_path = os.path.join(output_dir, 'flaky_tests_report.csv')
    output.to_csv(csv_path, index=False)
    
    print(f"Reports saved to {json_path} and {csv_path}")

if __name__ == "__main__":
    model_path = 'model/flaky_model.pkl'
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    input_csv = os.path.join(BASE_DIR, "data", "sample_test_results.csv")
    
    # Ensure output directory exists
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    
    # Load model
    model = load_model(model_path)
    
    # Predict flaky tests
    predict_flaky_tests(model, input_csv, output_dir)