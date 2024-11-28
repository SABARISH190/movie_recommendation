import pandas as pd
import ast

# Load the CSV file
data = pd.read_csv("database_with_embeddings.csv")

# Function to safely evaluate the vector and check its dimension
def check_vector_dimensions(value, index):
    try:
        # Convert the string representation of the vector into a list
        vector = ast.literal_eval(value)
        vector_length = len(vector)
        
        # Print the vector length and the index for tracking
        print(f"Row {index}: Vector length = {vector_length}")
        
        # Store the length of vectors for further analysis
        return vector_length
    except Exception as e:
        print(f"Error parsing vector at row {index}: {e}")
        return None

# Apply the check to the 'vector' column and capture the vector lengths
vector_lengths = data['vector'].apply(check_vector_dimensions, index=data.index)

# Display unique dimensions in the dataset
unique_lengths = vector_lengths.dropna().unique()
print("\nUnique vector dimensions in the dataset:", unique_lengths)

# If you want to see how many rows correspond to each dimension
print("\nCount of each vector dimension:")
print(vector_lengths.value_counts())
