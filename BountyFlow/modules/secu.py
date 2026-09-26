import requests
 
API_KEY = "api_key_here"
BASE_URL = "https://api.securitytrails.com/v1/domain"
 
def run_securitytrails(domain):
    url = f"{BASE_URL}/{domain}/subdomains"
    headers = {
        "apikey": API_KEY,
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "subdomains" in data:
                subdomains = [f"{sub}.{domain}" for sub in data["subdomains"]]
                return subdomains
            return []
        elif response.status_code == 429:
            print(f"securitytrails rate limit for {domain}")
            return []
        else:
            print(f"securitytrails error {response.status_code} for {domain}")
            return []
            
    except Exception as e:
        print(f"securitytrails error for {domain}: {e}")
        return []