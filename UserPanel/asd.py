from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
# options = Options()
# options.add_argument("start-maximized")
# driver=webdriver.Chrome(options=options)
driver = webdriver.Chrome(ChromeDriverManager().install())
# profile = webdriver.FirefoxProfile('./geckodriver')
# from selenium.webdriver.firefox.options import Options as FirefoxOptions

# options = FirefoxOptions()
# options.add_argument("--headless")
# driver = webdriver.Firefox()
# driver=webdriver.Firefox()
driver.get("https://www.weedx.io/")

time.sleep(50)

# rows = driver.find_elements('//table[@id='tweets_table']//tr//td')

# for row in rows:
#     print(row.text)

elems = driver.find_elements(By.TAG_NAME, "h1")
elems1 = driver.find_elements(By.TAG_NAME, "h2")
elems2 = driver.find_elements(By.TAG_NAME, "h3")
# elems3 = driver.find_elements(By.TAG_NAME, "div")

for i in elems:
    print("h1 =",i.text)
for i in elems1:
    print("h2 =",i.text)
for i in elems2:
    print("h3 =",i.text)
# for i in elems3:
#     print("div =",i.text)


print("Count h1 =",len(elems))
print("Count h2 =",len(elems1))
print("Count h3 =",len(elems2))
# print("Count div =",len(elems3))    

driver.quit()


# a=[1,5,6,7,9]
# for i in a:
#     if i==6:
#         a.remove(6)
#     print(a)