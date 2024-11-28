document.addEventListener("DOMContentLoaded", () => {
    const searchButton = document.querySelector("button");
    const movieSearch = document.getElementById("movieSearch");
    const recommendationDiv = document.getElementById("recommendation");

    searchButton.addEventListener("click", async () => {
        const prompt = movieSearch.value.trim(); // Get the input value

        // Ensure the user has entered a prompt
        if (!prompt) {
            alert("Please enter a plot or prompt!");
            return;
        }

        try {
            // Send the prompt to the backend
            const response = await fetch("/search", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ prompt }),
            });

            // Handle errors if any
            if (!response.ok) {
                throw new Error(`Failed to fetch results: ${response.statusText}`);
            }

            // Parse and display the results
            const results = await response.json();
            
            if (results.error) {
                recommendationDiv.innerHTML = `<p>Error: ${results.error}. Please try again later.</p>`;
                return;
            }

            // Ensure results is an array before calling .map()
            if (Array.isArray(results) && results.length > 0) {
                recommendationDiv.innerHTML = results.map(result => `
                    <div class="movie-item">
                        <h3>${result.title}</h3>
                        <p><strong>Synopsis:</strong> ${result.synopsis}</p>
                        <p><strong>Language:</strong> ${result.language}</p>
                        <p><strong>Year:</strong> ${result.year}</p>
                    </div>
                `).join(""); // Dynamically update the DOM with results
            } else {
                recommendationDiv.innerHTML = `<p>No results found or error occurred. Please try again later.</p>`;
            }
        } catch (error) {
            console.error(error);
            recommendationDiv.innerHTML = `<p>An error occurred: ${error.message}. Please try again later.</p>`;
        }
    });
});
