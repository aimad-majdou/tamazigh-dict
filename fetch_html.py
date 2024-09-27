from colorama import Fore
import requests
from bs4 import BeautifulSoup

# Initialize a list to store failed session retrievals
failed_sessions = []

# Function to fetch HTML and return the result div inside titreamz
def fetch_html(session_id):
    url = f"https://tal.ircam.ma/dglai/search/indexs?session={session_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        html = response.text
        
        # Check for any PHP errors in the content
        if "A PHP Error was encountered" in html or "Fatal error" in html:
            print(Fore.RED + f"PHP error found in session {session_id}. Logging as a failed session.")
            failed_sessions.append(f"Content Error: Session ID: {session_id} - PHP error encountered.")
            return None
        
        soup = BeautifulSoup(html, 'html.parser')

        # Find the div with class 'titreamz'
        titreamz_div = soup.find('section', class_='ddoc_funfact_detail_haut')
        if titreamz_div:
            # Find the div with class 'result' inside titreamz
            result_div = titreamz_div.find('div', class_='result')
            if result_div:
                return result_div
            else:
                # Log failure if result_div is not found
                print(Fore.RED + f"No 'div.result' found inside 'div.titreamz' for session_id {session_id}")
                failed_sessions.append(f"Content Error: Session ID: {session_id} - No 'div.result' found inside 'div.titreamz'")
        else:
            # Log failure if titreamz_div is not found
            print(Fore.RED + f"No 'div.titreamz' found for session_id {session_id}")
            failed_sessions.append(f"Content Error: Session ID: {session_id} - No 'div.titreamz' found")
    else:
        # Log failure if HTML cannot be retrieved
        print(Fore.RED + f"HTTP Error: Failed to retrieve HTML from {session_id}. Status code: {response.status_code}")
        failed_sessions.append(f"HTTP Error: Session ID: {session_id} - Status code: {response.status_code}")

    return None  # Return None if any of the steps fail
