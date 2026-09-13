from playwright.sync_api import sync_playwright
import csv
import re

def scrape_laptops():
    with sync_playwright() as p:
        # headless=True agar berjalan di latar belakang (tanpa membuka jendela UI)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Menavigasi ke webscraper.io (Katalog Laptop)...")
        page.goto("https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops")
        
        # WAIT STRATEGY: Tunggu hingga elemen kartu produk (thumbnail) termuat
        page.wait_for_selector(".thumbnail")
        
        products = page.query_selector_all(".thumbnail")
        cleaned_data = []
        
        print(f"Ditemukan {len(products)} produk laptop. Memulai ekstraksi...\n")
        
        for product in products:
            # 1. Ekstraksi Data Dinamis
            title_elem = product.query_selector(".title")
            price_elem = product.query_selector(".price")
            review_elem = product.query_selector(".review-count")
            
            # Ambil teks mentahnya
            raw_title = title_elem.get_attribute("title") if title_elem else None
            raw_price = price_elem.inner_text() if price_elem else None
            raw_review = review_elem.inner_text() if review_elem else None
            
            # 2. Penanganan Missing Value
            if not raw_title or not raw_price or not raw_review:
                continue 
                
            # 3. Data Cleaning
            # a. Trimming (Hapus spasi di awal/akhir)
            clean_title = raw_title.strip()
            
            # b. Konversi tipe data Harga: "$1,199.00" -> 1199.00 (Float)
            clean_price_str = re.sub(r'[^\d.]', '', raw_price)
            clean_price = float(clean_price_str)
            
            # c. Konversi tipe data Ulasan: "14 reviews" -> 14 (Integer)
            clean_review_str = re.sub(r'[^\d]', '', raw_review)
            clean_review = int(clean_review_str) if clean_review_str else 0
            
            # Simpan ke dictionary
            cleaned_data.append({
                "Product_Name": clean_title,
                "Price_USD": clean_price,
                "Total_Reviews": clean_review
            })
            
            # Cetak sampel pertama untuk bukti tugas
            if len(cleaned_data) == 1:
                print("=== CONTOH DATA SEBELUM CLEANING ===")
                print(f"Nama   : {raw_title!r}")
                print(f"Harga  : {raw_price!r}")
                print(f"Ulasan : {raw_review!r}\n")
                
                print("=== CONTOH DATA SESUDAH CLEANING ===")
                print(f"Nama   : {clean_title}")
                print(f"Harga  : {clean_price} (Tipe: {type(clean_price).__name__})")
                print(f"Ulasan : {clean_review} (Tipe: {type(clean_review).__name__})\n")
                
        # 4. Penyimpanan ke CSV
        csv_filename = "cleaned_laptops_data.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Product_Name", "Price_USD", "Total_Reviews"])
            writer.writeheader()
            writer.writerows(cleaned_data)
            
        print(f"Berhasil! Data diekstrak dan disimpan ke {csv_filename}")
        browser.close()

if __name__ == "__main__":
    scrape_laptops()