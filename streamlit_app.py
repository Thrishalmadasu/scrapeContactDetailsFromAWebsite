import streamlit as st
import re
import requests
import csv
from bs4 import BeautifulSoup
from io import StringIO

# Updated regex patterns
phone_patterns = [
    re.compile(r'\+91[-\s]?\(?[0-9]{3,5}\)?[-\s]?[0-9]{3,4}[-\s]?[0-9]{3,4}(/[-\s]?[0-9]{1,4})?'),
    re.compile(r'\+91[-\s]?[0-9]{10}'),
    re.compile(r'\b[6-9][0-9]{9}\b'),
    re.compile(r'\b[0-9]{3}[-\s]?[0-9]{3}[-\s]?[0-9]{4}\b'),
    re.compile(r'\b[0-9]{4}[-\s]?[0-9]{3}[-\s]?[0-9]{4}\b'),
    re.compile(r'\b[0-9]{4}[-\s]?[0-9]{2}[-\s]?[0-9]{2}[-\s]?[0-9]{2}\b'),
    re.compile(r'\b[0-9]{5}[-\s]?[0-9]{6}\b')
]

email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')


# Function to extract phone numbers and emails from HTML content
def extract_contact_info(url):
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful
        html = response.text

        # Parse the HTML
        soup = BeautifulSoup(html, 'html.parser')

        # Get the entire text of the page
        text = soup.get_text(separator=' ', strip=True)

        # Find phone numbers and emails
        phone_numbers = set()
        emails = set()

        for pattern in phone_patterns:
            matches = pattern.findall(text)
            phone_numbers.update(matches)

        emails.update(email_pattern.findall(text))

        return {
            'url': url,
            'phone_numbers': list(phone_numbers),
            'emails': list(emails)
        }
    except requests.RequestException as e:
        st.error(f"Error fetching {url}: {e}")
        return {
            'url': url,
            'phone_numbers': [],
            'emails': []
        }


# Streamlit app
def main():
    st.title("Contact Info Scraper")
    st.write("Enter the list of website URLs (one per line) to extract contact details.")

    urls_input = st.text_area("Website URLs", height=200)

    if st.button("Get Contact Info"):
        urls = urls_input.split('\n')
        contact_info_list = [extract_contact_info(url) for url in urls]

        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Website", "Phone Numbers", "Emails"])

        for info in contact_info_list:
            writer.writerow([info['url'], ", ".join(info['phone_numbers']), ", ".join(info['emails'])])

        st.download_button(
            label="Download Contact Info CSV",
            data=output.getvalue(),
            file_name='contact_info.csv',
            mime='text/csv'
        )


if __name__ == "__main__":
    main()