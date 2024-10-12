import requests
import uuid

def order( productId: str, productName: str, productPrice: float, action: str):
    mobile="123"
    url = "https://hackrx-ps4.vercel.app/order"
    
    _id = str(uuid.uuid4())

    headers = {
        "team": "unenthusiats",      
        "mobile": mobile,
        "x-team": "unenthusiats" 
    }

    payload = {
        "productId": productId,
        "productName": productName,
        "productPrice": productPrice,
        "action": action,
        "id": _id,
        "mobile": mobile
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


def get_orders():
    mobile="123"
    url = "https://hackrx-ps4.vercel.app/orders"
    
    headers = {
        "team": "unenthusiats",
        "mobile": mobile,
        "x-team": "unenthusiats"
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
    mobile="123"
    url = f"https://hackrx-ps4.vercel.app/order-status?orderId{order_id}&mobile={mobile}"
    
    headers = {
        "team": "unenthusiats",
        "mobile": mobile,
        "x-team": "unenthusiats"
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
