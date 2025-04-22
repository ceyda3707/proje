import requests
import sqlite3
import os


# API'den veri çeken sınıf
class APIClient:
    def __init__(self):
        self.base_url = "https://www.themealdb.com/api/json/v1/1/search.php?f={}"
    
    def tum_tarifleri_getir(self):
        tum_tarifler = []
        for harf in "abcdefghijklmnopqrstuvwxyz":
            url = self.base_url.format(harf)
            response = requests.get(url)
            data = response.json()
            if data['meals']:
                tum_tarifler.extend(data['meals'])
        return tum_tarifler

# Veritabanı işlemleri için sınıf
class Veritabani:
    def __init__(self, dosya_adi="tarifler.db"):
        self.dizin = os.path.dirname(os.path.abspath(__file__))
        self.vt_yol = os.path.join(self.dizin, dosya_adi)
        self.conn = None
        self.cursor = None
        self.baglanti_kontrol()  # <--- buraya taşıdık

    def baglanti_kontrol(self):
        try:
            self.conn = sqlite3.connect(self.vt_yol)
            self.cursor = self.conn.cursor()
            self.tablo_olustur()  # <--- buraya taşıdık
        except sqlite3.Error as e:
            print("Veritabanı bağlantısı sağlanamadı:", e)
            
       

    def tablo_olustur(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS yemek_tarifleri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT,
            kategori TEXT,
            bolge TEXT,
            tarif TEXT,
            resim_url TEXT
        )
        """)
        self.conn.commit()

    def veri_ekle(self, isim, kategori, bolge, tarif, resim):
        self.cursor.execute("""
        INSERT INTO yemek_tarifleri (isim, kategori, bolge, tarif, resim_url)
        VALUES (?, ?, ?, ?, ?)
        """, (isim, kategori, bolge, tarif, resim))
        self.conn.commit()

    def kapat(self):
        self.conn.close()

# Ana servis sınıfı
class YemekServisi:
    def __init__(self):
        self.api = APIClient()
        self.db = Veritabani()

    def baslat(self):
        tarifler = self.api.tum_tarifleri_getir()
        for meal in tarifler:
            isim = meal.get("strMeal", "")
            kategori = meal.get("strCategory", "")
            bolge = meal.get("strArea", "")
            tarif = meal.get("strInstructions", "")
            resim = meal.get("strMealThumb", "")
            self.db.veri_ekle(isim, kategori, bolge, tarif, resim)
        print("Tüm tarifler başarıyla kaydedildi.")
        self.db.kapat()

# Çalıştırma
if __name__ == "__main__":
    servis = YemekServisi()
    servis.baslat()
