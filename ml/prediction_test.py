import joblib

# Load the saved pipeline 
pipeline = joblib.load("ml/saved_model/model.joblib")

# sepal_length, sepal_width, petal_length, petal_width Iris flower measurements
sample = [[5.9, 2.8, 4.3, 1.3]]

prediction = pipeline.predict(sample)

species = ["setosa", "versicolor", "virginica"]

print(f"Predicted species: {species[prediction[0]]}")