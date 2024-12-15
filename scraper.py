import requests
from bs4 import BeautifulSoup
import csv

# Step 1: Base URL
base_url = "http://books.toscrape.com/catalogue/category/books_1/"
page_url = "index.html"  # First page

# Step 2: Prepare a list to store the data
books_data = []

# Step 3: Mapping for star ratings (convert textual ratings to numeric)
rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

# Step 4: Function to convert rating to numeric
def convert_rating_to_numeric(rating_class):
    # Extract the rating class (e.g., "star-rating Three")
    rating = rating_class[1] if len(rating_class) > 1 else None
    # Convert rating to numeric using the rating_map
    return rating_map.get(rating, "N/A")  # If the rating is not found, return "N/A"

# Step 5: Loop through all pages
while page_url:
    # Construct the full URL
    url = base_url + page_url

    # Send an HTTP GET request
    response = requests.get(url)

    if response.status_code == 200:
        print(f"Successfully fetched: {url}")
        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract book data
        book_containers = soup.find_all("article", class_="product_pod")

        for book in book_containers:
            # Extract book name
            name_tag = book.find("a", title=True)
            name = name_tag["title"] if name_tag else "N/A"

            # Extract price
            price_tag = book.find("p", class_="price_color")
            price = price_tag.get_text(strip=True) if price_tag else "N/A"

            # Extract rating and convert it to numeric form
            rating_tag = book.find("p", class_="star-rating")
            rating_class = rating_tag["class"] if rating_tag else []
            rating = convert_rating_to_numeric(rating_class)  # Convert rating to numeric form

            # Preprocessing: Handle missing or inconsistent values
            if name == "N/A" or price == "N/A" or rating == "N/A":
                continue  # Skip entries with missing critical data

            # Preprocessing: Ensure price is numeric (remove "£" and convert to float)
            if price != "N/A" and price.startswith("£"):
                price = float(price[1:])  # Remove the "£" sign and convert to float

            # Append the cleaned data to the list
            books_data.append({"Name": name, "Price": price, "Rating": rating})

        # Find the "next" button for pagination
        next_button = soup.find("li", class_="next")
        page_url = next_button.find("a")["href"] if next_button else None
    else:
        print(f"Failed to fetch: {url} (Status code: {response.status_code})")
        break

# Step 6: Save the data to a CSV file
output_file = "books_data.csv"

with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["Name", "Price", "Rating"])
    writer.writeheader()
    writer.writerows(books_data)

print(f"Data saved to {output_file}!")
