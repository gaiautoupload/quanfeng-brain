import pdfplumber
import os

pdf_path = r"D:\nanodemo\全鋒\國泰金控 20260424 (162大車補貼參數調整).pdf"
output_path = r"C:\Users\III-AIPC-02\.nanobot_2\workspace\quanfeng_brain\data\pdf_text.txt"

os.makedirs(os.path.dirname(output_path), exist_ok=True)

with pdfplumber.open(pdf_path) as pdf:
    full_text = ""
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text:
            full_text += f"\n--- Page {i+1} ---\n{text}\n"

with open(output_path, "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"Extracted {len(full_text)} characters to {output_path}")
print("First 500 chars:")
print(full_text[:500])
