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



sub=[{"id":1,"Weight":"1 g","Price":20,"Discount":5,"SalePrice":19,"Unit":0,"Quantity":0,"Stock":"Out of Stock","Status":"Active"},{"id":2,"Weight":"2 g","Price":30,"Discount":5,"SalePrice":29,"Unit":0,"Quantity":5,"Stock":"Out of Stock","Status":"Active"}]    
# z={"id":1,"Weight":"1 g","Price":20,"Discount":5,"SalePrice":19,"Unit":0,"Quantity":5,"Stock":"In Stock","Status":"Active"}
# a=0
cartquantity=1
id=1
for i in sub:
    if i['id'] == id :
        i.update({ "Quantity" : i["Quantity"] - cartquantity})
        print( sub)
        