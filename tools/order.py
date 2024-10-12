import requests
import uuid

def order( productId: str, productName: str, productPrice: float, action: str):
    if not productId or not productName or not productPrice or not action:
        return "Insufficient data. All parameters (productId, productName, productPrice, action) are required."

    mobile="123456"
    url = "https://hackrx-ps4.vercel.app/order"
    
    _id =str(uuid.uuid4())
    # _id ="orderid"+str(uuid.uuid4())

    headers = {
        "team": "unenthusiasts",      
        "mobile": mobile,
        "x-team": "unenthusiasts" 
    }

    payload = {
        "productId": productId,
        "productName": productName,
        "productPrice": productPrice,
        "action": action,
        "id": _id,
        "mobile": mobile
    }

    print("payload", payload)

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed with status code: {response.status}")
            print("Error:", response.text)

    except Exception as e:
        print("An error occurred:", str(e))


def get_orders():
    mobile="123456"
    url = "https://hackrx-ps4.vercel.app/orders"
    
    headers = {
        "team": "unenthusiasts",
        "mobile": mobile,
        "x-team": "unenthusiasts"
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            print("the daata",data)
            return data
        else:
            print(f"Failed with status code: {response.status}")
            print("Error:", response.text)

    except Exception as e:
        print("An error occurred:", str(e))


def get_order_status(order_id: str):
    mobile="123456"
    url = f"https://hackrx-ps4.vercel.app/order-status?orderId{order_id}&mobile={mobile}"
    
    headers = {
        "team": "unenthusiasts",
        "mobile": mobile,
        "x-team": "unenthusiasts"
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed with status code: {response.status}")
            print("Error:", response.text)

    except Exception as e:
        print("An error occurred:", str(e))


def generate_leads():
    mobile="123"
    url = "https://hackrx-ps4.vercel.app/generate-lead"
    headers = {
        "team": "unenthusiasts",
        "mobile": mobile,
        "x-team": "unenthusiasts"
    }
    payload={
        "mobile":mobile
    }
    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed with status code: {response.status}")
            print("Error:", response.text)

    except Exception as e:
        print("An error occurred:", str(e))
        
def eligibility_check():
    mobile="123"
    url = "https://hackrx-ps4.vercel.app/eligibility-check"
    headers = {
        "team": "unenthusiasts",
        "mobile": mobile,
        "x-team": "unenthusiasts"
    }
    payload={
        "mobile":mobile
    }
    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed with status code: {response.status}")
            print("Error:", response.text)

    except Exception as e:
        print("An error occurred:", str(e))


        
def health_check():
    mobile="123"
    url = "https://hackrx-ps4.vercel.app/health-check"
    headers = {
        "team": "unenthusiasts",
        "mobile": mobile,
        "x-team": "unenthusiasts"
    }
    try:
        response = requests.get(url,headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed with status code: {response.status}")
            print("Error:", response.text)

    except Exception as e:
        print("An error occurred:", str(e))