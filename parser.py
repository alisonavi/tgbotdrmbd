import requests
from bs4 import BeautifulSoup

def get_random_joke():
    url = "https://www.anekdot.ru/random/story/"
    response = requests.get(url)
    response.raise_for_status()  # Ensure we got a successful response

    soup = BeautifulSoup(response.text, 'html.parser')

    # On anekdot.ru, jokes are often inside a <div class="text"> for stories.
    # Let's find all divs with class "text" and pick the first one.
    joke_div = soup.find('div', class_='text')
    if joke_div:
        # Extract text and strip extra whitespace
        joke_text = joke_div.get_text(strip=True)
        return joke_text
    else:
        return "Не удалось получить шутку."

# Example usage:
joke = get_random_joke()
print(joke)
