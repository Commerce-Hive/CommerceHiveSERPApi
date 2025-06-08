import requests
import time

SYNC_API_KEY = "U2ILFPTTo9oXkmVOSqhHJKYuZXD0NMp0dmSpp1PgVcUCSCHGG75YXMNALy9L"  # <-- Put your real API key here

headers = {
    "Authorization": f"Bearer {SYNC_API_KEY}",
    "Content-Type": "application/json"
}

def convert_asin_to_upc(asin):
    submit_url = "https://api.synccentric.com/v1/product_matching_jobs"
    data = {
        "inputs": [
            {"asin": asin}
        ]
    }
    
    print(f"Submitting ASIN to UPC conversion job for ASIN: {asin}")
    response = requests.post(submit_url, headers=headers, json=data)
    
    if response.status_code != 200:
        print(f"Failed to submit job. Status code: {response.status_code}")
        print("Response text:", response.text)
        return None
    
    response_json = response.json()
    job_id = response_json.get("id")
    if not job_id:
        print("No job ID returned in response:", response_json)
        return None
    
    print(f"Job submitted successfully. Job ID: {job_id}")
    
    results_url = f"https://api.synccentric.com/v1/product_matching_jobs/{job_id}"
    
    for attempt in range(10):
        print(f"Polling for results... Attempt {attempt + 1}")
        res = requests.get(results_url, headers=headers)
        if res.status_code != 200:
            print(f"Error polling results: {res.status_code}")
            print("Response text:", res.text)
            time.sleep(5)
            continue
        
        result_json = res.json()
        status = result_json.get("status")
        print(f"Job status: {status}")
        
        if status == "completed" and result_json.get("results"):
            upc = result_json["results"][0].get("upc")
            print(f"UPC found: {upc}")
            return upc
        
        time.sleep(5)
    
    print("Timed out waiting for job results.")
    return None

# Example usage:
asin = "B08N5WRWNW"  # Example ASIN
upc = convert_asin_to_upc(asin)
print("Final converted UPC:", upc)
