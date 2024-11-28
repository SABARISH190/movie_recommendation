from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import ast

# Initialize FastAPI app
app = FastAPI()

# Graceful shutdown handling (to prevent async cancel errors)
@app.on_event("startup")
async def startup_event():
    print("Application startup complete.")

@app.on_event("shutdown")
async def shutdown_event():
    print("Application shutdown complete.")

# Load the sentence transformer model ("paraphrase-mpnet-base-v2")
model = SentenceTransformer('paraphrase-mpnet-base-v2')

# Load the dataset
data = pd.read_csv(r"C:\Users\123\Desktop\project\database_with_embeddings.csv")

# Safely parse the 'vector' column (handling NaN values and dimension mismatch)
def safe_literal_eval(value):
    try:
        if pd.isna(value):
            return np.zeros(384)  # Use a zero-vector if NaN
        vector = np.array(ast.literal_eval(value))
        if vector.shape[0] != 384:  # Check if the vector has the correct dimension
            print(f"Warning: Vector dimension mismatch. Found {vector.shape[0]} instead of 384.")
            # Resize or pad the vector to have 384 dimensions (e.g., zero-padding)
            if vector.shape[0] == 768:  # If the vector is 768-dimensional
                return vector[:384]  # Truncate to 384 if it's 768-dimensional
            else:
                return np.zeros(384)  # Default to a zero-vector for mismatched dimensions
        return vector
    except Exception as e:
        print(f"Error parsing vector: {e}")
        return np.zeros(384)  # Use a zero-vector in case of any parsing error

# Apply safe_literal_eval to parse the vectors
embeddings = np.vstack(data['vector'].apply(safe_literal_eval).to_numpy())

# Initialize FAISS index for similarity search
dimension = embeddings.shape[1]  # Should be 384
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Define request schema for receiving user input
class PromptRequest(BaseModel):
    prompt: str

# Set up Jinja2 template engine
templates = Jinja2Templates(directory="templates")

# Serve static files (like CSS and JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route to render the prompt page (user enters a plot or prompt)
@app.get("/", response_class=HTMLResponse)
async def read_prompt_page(request: Request):
    return templates.TemplateResponse("prompt page.html", {"request": request})

# Route to handle the similarity search based on user input
@app.post("/search")
async def search_similar_movies(request: PromptRequest):
    try:
        # Vectorize the user's input using the "paraphrase-mpnet-base-v2" model
        prompt_embedding = model.encode(request.prompt)
        print(f"Input Prompt: {request.prompt}")
        print(f"Generated Prompt Embedding: {prompt_embedding[:5]}...")  # Log first few elements of the embedding

        # Perform similarity search using FAISS
        distances, indices = index.search(np.array([prompt_embedding]), k=3)
        print(f"Distances: {distances}")  # Log the distances returned by FAISS
        print(f"Indices: {indices}")      # Log the indices returned by FAISS

        # Check if FAISS returns empty results
        if distances.size == 0 or indices.size == 0:
            print("Error: FAISS search returned empty distances or indices.")
            return {"error": "No results found for the given prompt."}

        # Collect the results
        results = []
        for idx in indices[0]:
            if idx >= 0:  # Ensure valid index
                movie = data.iloc[idx]
                results.append({
                    "title": movie['title'],
                    "synopsis": movie['synopsis'],
                    "language": movie['language'],
                    "year": movie['year']
                })

        if not results:
            print("No results found after searching.")
        
        return results
    
    except Exception as e:
        # Log the error and return a message to help with debugging
        print(f"Error in /search: {e}")
        return {"error": "An error occurred while processing the request."}

# Route to render the result page (displaying the search results)
@app.get("/results", response_class=HTMLResponse)
async def read_result_page(request: Request):
    return templates.TemplateResponse("result.html", {"request": request})
