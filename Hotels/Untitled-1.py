import csv
import requests 
from bs4 import BeautifulSoup

def Scrap_and_Save(soup, data_file) :
    # Find all stays
    hotels = soup.find_all('div', attrs= {'class':'listing-items__item'})
    for each_hotel in hotels:
        content = each_hotel.find('a', attrs= {'class':'vertical-card'}, recursive=False)
        if content == None : continue

        # Find features
        code = kind = name = price = comment = score = province = city = star = ''
        
        # kind, code
        split_url = content['href'].split('/')
        if len(split_url) == 3 :
            kind = split_url[1]
            code = split_url[2]
        
        content_card = content.find('div', attrs= {'class':'vertical-card__wrapper'}, recursive=False)
        if content_card == None : continue
        
        # score, comment
        content_temp = content_card.find('div', attrs= {'class':'vertical-card__rate'}, recursive=False)
        if content_temp != None : 
            spans = content_temp.find_all('span', recursive=False)
            for each_span in spans:
                if each_span.has_attr('class') and each_span['class'][0] == 'vertical-card__rate-score' :
                    score = each_span.get_text().strip()
                if each_span.has_attr('class') and each_span['class'][0] == 'vertical-card__rate-count' :
                    comment = each_span.get_text().strip()
        # name, star
        content_temp = content_card.find('p', attrs= {'class':'vertical-card__name'}, recursive=False)
        if content_temp != None : 
            spans = content_temp.find_all('span', recursive=False)
            for each_span in spans:
                if each_span.has_attr('class') == False:
                    name = each_span.get_text().strip()
                if each_span.has_attr('class') and each_span['class'][0] == 'vertical-card__star' :
                    star = each_span.get_text().strip()            # content_temp = content.find('span', attrs= {'class':'vertical-card__rate-count'}, recursive=False)
        # province, city
        content_temp = content_card.find('p', attrs= {'class':'vertical-card__feature'}, recursive=False)
        if content_temp != None : 
            temp_city = ''
            temp_city = content_temp.find('span', recursive=False)
            if temp_city != None : temp_city = temp_city.get_text().strip()
            temp_city = temp_city.replace('\n','')
            temp_city = temp_city.split('،')
            if len(temp_city) == 2:
                city = temp_city[1].strip()
                province = temp_city[0].strip()
        # price
        content_temp = content_card.find('div', attrs= {'class':'pricing vertical-card__pricing'}, recursive=False)
        if content_temp != None : 
            content_temp = content_temp.find('div', attrs= {'class':'hotel-pricing'}, recursive=False)
            if content_temp != None:
                content_temp = content_temp.find('p', attrs= {'class':'hotel-pricing__price'}, recursive=False)
                if content_temp != None:
                    temp_price = ''
                    temp_price = content_temp.find('strong', recursive=False)
                    if temp_price != None : temp_price = temp_price.get_text().strip().split('تومان')[0].replace(',','')
                    price = temp_price.strip()
        
        new_row = [code,kind,name,price,comment,score,province,city,star]
        
        with open(data_file, 'a+', newline='', encoding='utf-8') as write_obj:
            # Create a writer object from csv module
            csv_writer = csv.writer(write_obj)
            # Add contents of list as last row in the csv file
            csv_writer.writerow(new_row)

if __name__ == "__main__":
    Data_File_Name = 'Data.csv'
    City_File_Name = 'Cities.txt'
    
    # Write the headers in data csv file
    with open(Data_File_Name, mode='w', newline='', encoding='utf-8') as csv_file:
        handle = csv.writer(csv_file)
        handle.writerow(['code','kind','name','price','comment','score','province', 'city','star'])

    city_list = list()
    # Read city source file
    with open(City_File_Name,'r',encoding='utf-8') as city_file:
        lines = city_file.readlines()
        for each_line in lines:
            city_list.append(each_line.replace('\n',''))

    # Get HTML of all cities
    Jabama_Url = 'https://www.jabama.com/'
    Jabama_Url_WithoutSlash = 'https://www.jabama.com'

    for each_city in city_list :
        # Find all pages (At last Max_page_no pages)
        Max_page_no = 10
        for each_page in range(Max_page_no):
            temp_page = str(each_page + 1)

            print('Scraping', each_city, 'page', temp_page)
            
            temp_Url = f'{Jabama_Url}search?q={each_city}&kind=hotel&page-number={temp_page}'

            # Check if page is found
            response = requests.get(temp_Url)
            if response.status_code != 200:
                break
                
            print (temp_Url)

            soup = BeautifulSoup(response.content, 'html.parser')

            # Jabama return this page instead of 404
            check_empty = soup.find_all('div', attrs= {'class':'listing-empty-state'})
            if len(check_empty) > 0:
                break
            
            Scrap_and_Save(soup, Data_File_Name)
