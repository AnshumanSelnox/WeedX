# from selenium import webdriver
# import time
# from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
# # options = Options()
# # options.add_argument("start-maximized")
# # driver=webdriver.Chrome(options=options)
# driver = webdriver.Chrome(ChromeDriverManager().install())
# # profile = webdriver.FirefoxProfile('./geckodriver')
# # from selenium.webdriver.firefox.options import Options as FirefoxOptions

# # options = FirefoxOptions()
# # options.add_argument("--headless")
# # driver = webdriver.Firefox()
# # driver=webdriver.Firefox()
# driver.get("https://www.weedx.io/")

# time.sleep(50)

# # rows = driver.find_elements('//table[@id='tweets_table']//tr//td')

# # for row in rows:
# #     print(row.text)

# elems = driver.find_elements(By.TAG_NAME, "h1")
# elems1 = driver.find_elements(By.TAG_NAME, "h2")
# elems2 = driver.find_elements(By.TAG_NAME, "h3")
# # elems3 = driver.find_elements(By.TAG_NAME, "div")

# for i in elems:
#     print("h1 =",i.text)
# for i in elems1:
#     print("h2 =",i.text)
# for i in elems2:
#     print("h3 =",i.text)
# # for i in elems3:
# #     print("div =",i.text)


# print("Count h1 =",len(elems))
# print("Count h2 =",len(elems1))
# print("Count h3 =",len(elems2))
# # print("Count div =",len(elems3))    

# driver.quit()

# Practice question
# a=[1,5,6,7,9] #remove element from list
# for i in a:
#     if i==6:
#         a.remove(6)
#     print(a)

# lst=[2,4,4,4,3,8,5,5] #remove duplicate items from list
# a=[]
# for i in lst:
#     if i not in a:
#             a.append(i)
# print(a)

# a=[1,2,3] #whats gone be output of this
# d={a:20}
# print(d)

# x=[1,2,3] #call by reference
# y=x
# y.append(4)
# print(x)


# s={1,2,3,4}
# s.discard(1)
# print(s)

# a=[1,2,3,5,"aaa",{"a":"as","s":"df"}]   #remove duplicate item from 2 array
# b=[1,2,5,4,{"a":"as","s":"df"}]
# c=[]
# for i in a:
#     for j in b:
#         if i not in c:
#             c.append(i)
#         elif j not in c:
#             c.append(j)
# print(c)

# a=[1,5,9,13,{"a":15}] #Biggest element in list
# print(max(a))


# j=[{"a":15},{"a":200},{"a":30}] #Highest value in json and dict 
# for i in j:
#     for k in j:
#         if i["a"] >20:
#             print(i["a"])



# [{"id":728,"username":"qwertyyu","StoreName":"selnox","ProductName":"Big Bad Sour Bears - Indica","Cart_Quantity":2,"Price":{"id":1,"Weight":"1 G","Price":12212,"Discount":2,"SalePrice":11967.76,"Unit":"","Quantity":1,"Stock":"","Status":"Active"},"TotalPrice":23936,"created_by":36,"Product_id":1,"Store_id":15,"Image_id":113}]

# a=[{"id": 14,"Xml": ["https://www.weedx.io/weed-dispensaries/in/united-states/texas/el-paso","https://www.weedx.io/weed-dispensaries/in/united-states/new-york/","https://www.weedx.io/weed-dispensaries/in/united-states/district-of-columbia/washington",]}]
# j="https://www.weedx.io/weed-dispensaries/in/united-states/texas/el-pas"
# for i in a:
#     if j not in i["Xml"]:
#             a[0]["Xml"].append(j)
# print(a)

# sub=[{"id":1,"Weight":"1 g","Price":20,"Discount":5,"SalePrice":19,"Unit":0,"Quantity":7,"Stock":"Out of Stock","Status":"Active"},{"id":2,"Weight":"2 g","Price":30,"Discount":5,"SalePrice":29,"Unit":0,"Quantity":5,"Stock":"Out of Stock","Status":"Active"}]    
# z={"id":1,"Weight":"1 g","Price":20,"Discount":5,"SalePrice":19,"Unit":0,"Quantity":5,"Stock":"In Stock","Status":"Active"}
# # a=0
# cartquantity=1
# id=1
# # for i in sub:
# #         if i["id"]==id:
# #             # sub[a]= z
# #             # print(i["Quantity"]-cartquantity)
# #         # a=+1
# for i in sub:
#     # for k, v in i.items():
#     #     if k['id']==id:
#     #         sub[k] = ''
#     if i["id"]==id:
#         a=i["Quantity"]-cartquantity
#         sub.Quantity.update(a)
        
# print("AAAAAAAAAAAAAAAAAAA",sub)



# sub=[{"id":1,"Weight":"1 g","Price":20,"Discount":5,"SalePrice":19,"Unit":0,"Quantity":0,"Stock":"Out of Stock","Status":"Active"},{"id":2,"Weight":"2 g","Price":30,"Discount":5,"SalePrice":29,"Unit":0,"Quantity":5,"Stock":"Out of Stock","Status":"Active"}]    
# # z={"id":1,"Weight":"1 g","Price":20,"Discount":5,"SalePrice":19,"Unit":0,"Quantity":5,"Stock":"In Stock","Status":"Active"}
# # a=0
# cartquantity=1
# id=1
# for i in sub:
#     if i['id'] == id :
#         i.update({ "Quantity" : i["Quantity"] - cartquantity})
#         print( sub)
        
# l=[]    
# a=[{"DiscountType": "Amount off Products", "ProLocationOnly": False, "AllCustomer": True, "DiscountCode": "x8ss9k3451121a", "AutomaticDiscount": None, "EndDate": None, "EndTime": None, "LimitNumberOfTime": None, "LimitToOneUsePerCustomer": True, "MinimumPurchaseAmount": None, "MinimumQuantityofItem":None, "NoMinimumRequirements": True, "PercentageAmount": "222", "SpecificCustomer": None, "Specific_customer_segments": None, "StartDate": "2023-12-08", "StartTime": "00:00", "ValueAmount": None, "category":[], "product": [46, 47, 48, 49], "CombinationProduct": False, "CombinationDiscount": False, "CustomerBuys": None, "CustomerSpends": None, "CustomerGets": None, "Free": False, "status": "Active"},
# {"DiscountType": "Amount off Products", "ProLocationOnly": False, "AllCustomer": True, "DiscountCode": "x8ss9k3451121aaa", "AutomaticDiscount": None, "EndDate": None, "EndTime": None, "LimitNumberOfTime": None, "LimitToOneUsePerCustomer": True, "MinimumPurchaseAmount": None, "MinimumQuantityofItem":None, "NoMinimumRequirements": True, "PercentageAmount": "222", "SpecificCustomer": None, "Specific_customer_segments": None, "StartDate": "2023-12-08", "StartTime": "00:00", "ValueAmount": None, "category":[], "product": [46, 47, 48, 49], "CombinationProduct": False, "CombinationDiscount": False, "CustomerBuys": None, "CustomerSpends": None, "CustomerGets": None, "Free": False, "status": "Active"}]
# for i in a:
#     z=list(i)
#     if i["DiscountCode"]=="x8ss9k3451121a":
#         z.remove("DiscountCode")
#         # l.append(z)
# print(z)
# l=a.keys()
# l.remove("DiscountCode")
# print(l)
# print("AAA",a)

# for i in range(len(a)):
#     if a[i]['DiscountCode'] == "x8ss9k3451121aaa":
#         del a[i]
# print(a)
# a=[{"id": 1, "Weight": "", "Price": 40, "Discount": 8, "SalePrice": 36.8, "Unit": 1, "Quantity": -3, "Stock": "Out of Stock", "Status": "Active"}]

# [{"Product_Id": 46, "Price_Id": 2}, {"Product_Id": 47, "Price_Id": 1}, {"Product_Id": 49, "Price_Id": 1}, {"Product_Id": 50, "Price_Id": 1}, {"Product_Id": 50, "Price_Id": 2}, {"Product_Id": 50, "Price_Id": 3}, {"Product_Id": 50, "Price_Id": 4}, {"Product_Id": 51, "Price_Id": 1}]


# a={"s":123}
# b={"d":456}
# a.update(b)
# print(a)


# [
#     {
#         "Product_Name": "Sour Jack 3.5g Sativa",
#         "Prices": [
#             {
#                 "Price": [
#                     {
#                         "id": 1,
#                         "Weight": "",
#                         "Price": 40,
#                         "Discount": 8,
#                         "SalePrice": 36.8,
#                         "Unit": 1,
#                         "Quantity": 3,
#                         "Stock": "Out of Stock",
#                         "Status": "Active",
#                         "CostOfGoods":10,
#                     }
#                 ],
#                 "id": 1
#             }
#         ],

#     },
#     {
#         "Product_Name": "Bolo Runtz",
#         "Prices": [
#             {
#                 "Price": [
#                     {
#                         "id": 1,
#                         "Weight": "1 g",
#                         "Price": 65,
#                         "Discount": 0,
#                         "SalePrice": 65,
#                         "Unit": "",
#                         "Quantity": 4,
#                         "Stock": "IN Stock",
#                         "Status": "Active",
#                         "CostOfGoods":20,
                        
#                     },
#                     {
#                         "id": 2,
#                         "Weight": "1/8 oz",
#                         "Price": 130,
#                         "Discount": 0,
#                         "SalePrice": 130,
#                         "Unit": "",
#                         "Quantity": 1,
#                         "Stock": "IN Stock",
#                         "Status": "Active",
#                         "CostOfGoods":50
#                     },
#                     {
#                         "id": 3,
#                         "Weight": "1/4 oz",
#                         "Price": 195,
#                         "Discount": 0,
#                         "SalePrice": 195,
#                         "Unit": "",
#                         "Quantity": 1,
#                         "Stock": "IN Stock",
#                         "Status": "Active",
#                         "CostOfGoods":100
#                     },
#                     {
#                         "id": 4,
#                         "Weight": "1/2 oz",
#                         "Price": 260,
#                         "Discount": 0,
#                         "SalePrice": 260,
#                         "Unit": "",
#                         "Quantity": 1,
#                         "Stock": "IN Stock",
#                         "Status": "Active",
#                         "CostOfGoods":100
#                     },
#                     {
#                         "id": 5,
#                         "Weight": "1 oz",
#                         "Price": 325,
#                         "Discount": 0,
#                         "SalePrice": 325,
#                         "Unit": "",
#                         "Quantity": 1,
#                         "Stock": "IN Stock",
#                         "Status": "Active",
#                         "CostOfGoods":100
#                     },
#                     {
#                         "id": 6,
#                         "Weight": "Pre-Roll 0.5g",
#                         "Price": 10,
#                         "Discount": 0,
#                         "SalePrice": 10,
#                         "Unit": "",
#                         "Quantity": 50,
#                         "Stock": "IN Stock",
#                         "Status": "Active",
#                         "CostOfGoods":5
#                     }
#                 ],
#                 "id": 12
#             }
#         ],
        
#     },
#     {
#         "Product_Name": "Pink Pez",
        
#         "Prices": [
#             {
#                 "Price": [
#                     {
#                         "id": 1,
#                         "Weight": "1 g",
#                         "Price": 70,
#                         "Discount": 0,
#                         "SalePrice": 70,
#                         "Unit": 1,
#                         "Quantity": 0,
#                         "Stock": "Out of Stock",
#                         "Status": "Active",
#                         "CostOfGoods":30,
#                     },
#                     {
#                         "id": 2,
#                         "Weight": "",
#                         "Price": 140,
#                         "Discount": 0,
#                         "SalePrice": 140,
#                         "Unit": 2,
#                         "Quantity": 0,
#                         "Stock": "Out of Stock",
#                         "Status": "Active",
#                         "CostOfGoods":50,
#                     },
                    
#                 ],
#                 "id": 13
#             }
#         ],
        
#     }
# ]

# import 

# a=["FLOWER","FLOWER","FLOWER","FLOWER","FLOWER","EDIBLES","FLOWER","FLOWER","CONCENTRATES","VAPE PENS"]
# # for i in range(0, len(a)):    
# #     for j in range(i+1, len(a)):    
# #         if(a[i] == a[j]):    
# #             print(a[j]);   

# l={i:a.count(i) for i in a}
# print(l)

# import requests,json
# import pandas as pd

# class BearerAuth(requests.auth.AuthBase):
#     def __init__(self, token):
#         self.token = token
#     def __call__(self, r):
#         r.headers["authorization"] = "Bearer " + self.token
#         return r
# data={"City":"","Country":"United States","State":"New York"}
# auth=input("auth")
# api="https://api.cannabaze.com/VendorPanel/Get-Product/"
# x=requests.get(api,auth=BearerAuth(str(auth)))
# print((json.loads(x.text)))
# objects = [
#     { "name": 'Object 1', "values": { "value1": 10, "value2": 20, "value3": 30 } },
#     { "name": 'Object 2', "values": { "value1": 40, "value2": 50, "value3": 60 } },
#     { "name": 'Object 3', "values": { "value1": 70, "value2": 80, "value3": 90 } },
#     { "name": 'Object 4', "values": { "value1": 100, "value2": 110, "value3": 120 } }
#   ]
# a=[]
# a=[{ "name": 'Object 1',"value1": 10,"value2": 20 }]
# for i in objects:
#     i.update(i.get("values"))
#     i.pop("values")
#     a.append(i)
# print(a)
# # for i in objects:
# df = pd.DataFrame(a) #.to_excel("Dispensaries.xlsx")
# # df=df.drop(['category_id','StoreDelivery'],axis=1)
# df=df.to_excel("Dispensaries.xlsx")

# class CropRatio:
#     def __init__(self):
#         self.crop_counts = {}

#     def add(self, crop, count):
#         if crop in self.crop_counts:
#             self.crop_counts[crop] += count
#         else:
#             self.crop_counts[crop] = count

#     def proportion(self, crop):
#         total_count = sum(self.crop_counts.values())
#         if total_count == 0:
#             return 0
#         if crop in self.crop_counts:
#             return self.crop_counts[crop] / total_count
#         else:
#             return 0
# crop_ratio=CropRatio()
# crop_ratio.add("wheat",4)
# crop_ratio.add("wheat",5)
# crop_ratio.add("Rice",1)

# print(crop_ratio.proportion("wheat")) #Return 0.9
# print(crop_ratio.proportion("Rice")) #Return 0.1
# print(crop_ratio.proportion("Corn")) #Return 0

# class CropRatio:
#     def __init__(self):
#         pass #Write logic

# crop_ratio=CropRatio()
# crop_ratio.add("wheat",4)
# crop_ratio.add("wheat",5)
# crop_ratio.add("Rice",1)

# print(crop_ratio.proportion("wheat")) #Return 0.9
# print(crop_ratio.proportion("Rice")) #Return 0.1
# print(crop_ratio.proportion("Corn")) #Return 0


# import requests
# import json
# import pandas as pd

# class BearerAuth(requests.auth.AuthBase):
#     def __init__(self, token):
#         self.token = token

#     def __call__(self, r):
#         r.headers["authorization"] = "Bearer " + self.token
#         return r

# try:
#     auth = input("Enter auth token: ")
#     api = "https://api.cannabaze.com/VendorPanel/Get-Product/"
    
#     response = requests.get(api, auth=BearerAuth(str(auth)))

#     # Check if the request was successful (status code 200)
#     response.raise_for_status()

#     data = json.loads(response.text)

#     # Create DataFrame
#     df = pd.DataFrame(data)

#     # Drop unnecessary columns
#     df = df.drop(['category_id', 'StoreDelivery'], axis=1)

#     # Provide a file path for the Excel file
#     excel_file_path = "path/to/Dispensaries.xlsx"

#     # Save DataFrame to Excel
#     df.to_excel(excel_file_path, index=False)
    
#     print(f"Data has been successfully saved to {excel_file_path}")

# except requests.exceptions.RequestException as e:
#     print(f"Error making the request: {e}")
# except Exception as e:
#     print(f"An unexpected error occurred: {e}")



# import base64
# import requests


# def get_as_base64(url):

    # return base64.b64encode(requests.get(url).content)


# url=["https://selnoxmedia.s3.amazonaws.com/media/product_images/2159d3_42ff23afb9a04ba88c4d1dcd09c66c6amv21.webp?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAS4WSA6KJNP6NPPES%2F20240104%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20240104T071929Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=4ac6269f37358ef4209b30f9ba1c48fbbd11774dfa7406e67ab7637a01aa0f7b"]

# get_as_base64(url)




# class Node:  
#     def __init__(self, value):  
#         self.value = value  
#         self.next = None  

# def insertAfterNode(self, previous_node, value):  
#     if previous_node is None:  
#         print("There is no previous node. Make a new head.")  
#         return  

#     insertion_node = Node(value)  
#     insertion_node.next = previous_node.next  
#     previous_node.next = insertion_node  
    
# insertAfterNode(self=1,previous_node=5,value=10)


# import requests

# def download_file(url, destination):
#     response = requests.get(url)
#     with open(destination, 'wb') as file:
#         file.write(response.content)

# # Replace 'your_link_here' with the actual link you want to download
# link_url = 'https://unsplash.com/photos/a-jellyfish-floating-in-the-water-at-night-6PGkhhCx6-Y'

# # Replace 'output_file.postman_form' with the desired file name for your Postman form file
# output_file = 'output_file.postman_form'

# download_file(link_url, output_file)

# print(f'The file has been downloaded and saved as {output_file}')
# import requests
# from PIL import Image
# from io import BytesIO

# def link_to_image(link, output_path):
#     try:
#         # Send a GET request to the URL
#         response = requests.get(link)
#         response.raise_for_status()  # Raise an exception for bad requests

#         # Open the image using Pillow
#         image = Image.open(BytesIO(response.content))

#         # Save the image to the specified output path
#         image.save(output_path)

#         print(f"Image saved successfully at {output_path}")

#     except Exception as e:
#         print(f"Error: {e}")

# # Example usage:
# url = "https://plus.unsplash.com/premium_photo-1684993466316-81ae0b6c96ae?q=80&w=1744&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
# output_file = "output_image.jpg"

# link_to_image(url, output_file)


# Set = set([1, 2, 'Geeks', 4, 'For', 6, 'Geeks'])
# # print("\nSet with the use of Mixed Values")
# # print(Set)
 
# # Accessing element using
# # for loop
# print("\nElements of set: ")
# for i in Set:
#     print(i, end =" ")
# # print()
# list1=[1,2,3]
# for j in list1:
#     print(j,end="")

# # # Checking the element
# # # using in keyword
# # print("Geeks" in Set)




# Same as {"a", "b","c"}
# normal_set = set(["a", "b","c"])
 
# print("Normal Set")
# print(normal_set)
 
# # A frozen set
# frozen_set = frozenset(["e", "f", "g"])
# # frozen_set.add("h")
 
# print("\nFrozen Set")
# print(frozen_set)


# Dict = {'Name': 'Geeks', 1: [1, 2, 3, 4]}
# print(Dict[1])
# # # print(Dict)

# import numpy as np

# a = np.array([[1,2,3,4],[4,55,1,2],
# 			[8,3,20,19],[11,2,22,21]])
# s = np.array([[1,2,3,4],[4,55,1,2],
# 			[8,3,20,19],[11,2,22,21]])
# d=s*a
# print(d)
# m = np.reshape(a,(4, 4))
# print(m)

# Accessing element
# print("\nAccessing Elements")
# print(a[1])
# print(a[2][0])

# # Adding Element
# m = np.append(m,[[1, 15,13,11]],0)
# print("\nAdding Element")
# print(m)

# # Deleting Element
# m = np.delete(m,[1],0)
# print("\nDeleting Element")
# print(m)

# A simple Python program to introduce a linked list

# Node class
# class Node:

# 	# Function to initialise the node object
# 	def __init__(self, data):
# 		self.data = data # Assign data
# 		self.next = None # Initialize next as null
  


# # Linked List class contains a Node object
# class LinkedList:

# 	# Function to initialize head
# 	def __init__(self):
# 		self.head = None
        


# # Code execution starts here
# if __name__=='__main__':

# 	# Start with the empty list
# 	llist = LinkedList()

# 	llist.head = Node(1)
# 	second = Node(2)
# 	third = Node(3)
    

# 	llist.head.next = second; # Link first node with second
# 	second.next = third; # Link second node with the third node

import mysql

mydb = mysql.connector.connect(
  host="localhost",
  user="Anshuman",
  password="password"
)

print(mydb) 