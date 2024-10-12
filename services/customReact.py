
from services.llm import LLMService
from tools.order import order,get_order_status,get_orders
import requests
from services.knowledgeBase import KnowledgeBaseService


class CustomReact():

    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
        self.llmservice=LLMService()
        self.kb=KnowledgeBaseService("knowledgebase")

    def getAction(self,action_query):
        res=self.llmservice.generate_response(messages=[
            {
                "role":"system",
                "content":"""
1
                These are the actions thatb  can be performed

                1. CreateOrder : Creates an order
                2. GetOrders : gets all orders
                3. GetOrderStatus : gets the status of the order


                Based on the user query return which actions do wee need to perform

                Strictly follow the below output format
                Strictly return the the Action name.



                
                """
            },
            {
                "role":"user",
                "content":action_query
            }

           
        ])

        return res


    def perform_action(self,action_query):
        print("performing action",action_query)

        action_method=self.getAction(action_query)

        if action_method=="CreateOrder":
            return self.order()
        elif action_method=="GetOrders":
            return self.getOrders()
        elif action_method=="GetOrderStatus":
            return self.getOrderStatus()
        else:
            print("Invalid action")

       

    def answer(self,action_query):
        print("Answering the query",action_query)
        return self.perform_action(action_query)




    def order(self,query):
        url="https://hackrx-ps4.vercel.app/order"
        print("Ordering the product")

        context_kb_data=self.kb.search_knowledge_base(query)
        headers={
            "team":"unenthusiasts",
            "mobile":"12345",
            "x-team":"unenthusiasts"
        }


        body=self.llmservice.generate_response(messages=[
            {
                        "role":"system",
                "content":f'''
                STRICTLY FOLLOW THE JSON FORMAT
                This is the context KB data
                {context_kb_data}

                you need to build a body json object in the following json format
                 {
                    "id": "string",
                    "mobile": "string",
                    "productId": "string",
                    "productName": "string",
                    "productPrice": 0,
                    "action": "cancel"
                }



                
                
                '''

            }
        ])
        try:
            response=requests.post(url,json=body,header=headers)
            data = response.json()
            return data

    
        except Exception as e:
            print("An error occurred in order :", str(e))


    def getOrders(self):
        print("Getting the orders")
        url="https://hackrx-ps4.vercel.app/orders"
        headers={
            "team":"unenthusiasts",
            "mobile":"12345",
            "x-team":"unenthusiasts"
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

    def getOrderStatus(self,order_id):
        print("Getting the order status")
        #gpt call

        url = f"https://hackrx-ps4.vercel.app/order-status?orderId{order_id}&mobile=12345"
        headers = {
            "team": "unenthusiasts",
            "mobile": "12345",
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


        
        
if __name__ =="main":
        
    obj=CustomReact()
    print(obj.answer("create an order for Wireless Bluetooth Speaker"))



              



