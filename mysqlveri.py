import mysql.connector
from mysql.connector import Error
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

def download_file_and_save_to_database(url, folder):
    response = requests.get(url)
    if response.status_code == 200:
        # PDF dosyasını indir
        file_name = os.path.basename(url)
        file_path = os.path.join(folder, file_name)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"{file_name} indirildi.")
        
        # PDF dosyasının veritabanına kaydet
        try:
            connection = mysql.connector.connect(host='localhost',
                                                 database='deneme3005',
                                                 user='root',
                                                 password='')
            if connection.is_connected():
                cursor = connection.cursor()
                query = "INSERT INTO pdf_files (file_name, file_path) VALUES (%s, %s)"
                data = (file_name, file_path)
                cursor.execute(query, data)
                connection.commit()
                print(f"{file_name} veritabanına kaydedildi.")
        except Error as e:
            print("Veritabanına bağlanırken bir hata oluştu:", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL bağlantısı kapatıldı.")

    else:
        print(f"{url} indirilemedi.")

def download_pdf_files_and_save_to_database(base_url, folder):
    response = requests.get(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            if href.endswith('.pdf'):
                pdf_url = urljoin(base_url, href)
                download_file_and_save_to_database(pdf_url, folder)
    else:
        print("Sayfa yüklenemedi.")

if __name__ == "__main__":
    base_url = 'https://iso500.org.tr/iso-500-dergiler'
    folder = 'downloaded_pdf_files'

    if not os.path.exists(folder):
        os.makedirs(folder)

    download_pdf_files_and_save_to_database(base_url, folder)
