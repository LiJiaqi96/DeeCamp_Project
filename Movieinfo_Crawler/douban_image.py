from bs4 import BeautifulSoup
import requests
# import json
# import urllib2
# import time

path = "Movie.txt"
f = open(path)
files = f.readlines()
nums = []
for file in files[1:]:
    nums.append(file.split('\t')[0])
print(len(nums))
count = 0
images_url = {}
for num in nums:
    # url = "https://api.douban.com/v2/movie/" + num
    url = "https://movie.douban.com/subject/" + num
    web_data = requests.get(url)
    print(web_data)
    soup = BeautifulSoup(web_data.text,'lxml')
    # data = web_data.json()
    # print(data)
    # if(data.has_key('image')):
    #     images_url.append(data['image'])
    # else:
    #     images_url.append('')
    image = soup.select("#mainpic > a > img")
    print(image)
    if(image == []):
        images_url[num] = None
    else:
        images_url[num] = image[0].get('src')
        print(image[0].get('src'))
    print(count)
    count += 1



# soup = BeautifulSoup(web_data.text,'json')
#
# data_raw = soup.select("body > p")
# print(type(data_raw))