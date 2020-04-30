import requests
from bs4 import BeautifulSoup
import pandas as pd
urls=pd.read_csv("TvUrl.csv")
urls=urls.values.tolist()
imgs_url={"Product_img":[]}
for u in urls:
	url=u[0]
	r=requests.get(str(url))
	soup = BeautifulSoup(r.content,"lxml")
	data = soup.find_all("div",{"class":"_2_AcLJ"})[0]
	imgs_url["Product_img"].append(str(data.get("style")[:-1]))
for i in range(len(imgs_url["Product_img"])):
	imgs_url["Product_img"][i]=imgs_url["Product_img"][i][imgs_url["Product_img"][i].find('url')+4:]
print(imgs_url)
TVurlImgs=pd.DataFrame(imgs_url)
TVurlImgs.to_csv('TVimgsURL.csv')