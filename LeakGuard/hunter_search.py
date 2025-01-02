import requests
from .utils import Hunter_API_KEY,save_excel_or_json
def search_hunter(domain=None, file=None, output_file=None,mode=None):
    API_KEY = Hunter_API_KEY
    # wb = Workbook()

    url= f'https://api.hunter.io/v2/domain-search?domain={domain}&api_key={API_KEY}'
    emails = []
    response = requests.get(url)
    data = response.json()

    for email in data['data']['emails']:
        emails.append(str(email['value']))

    save_excel_or_json(results=emails)

