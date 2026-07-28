import fitz
import json
import os
import unicodedata

def fix_thai_pua(text):
    text = unicodedata.normalize('NFKC', text)
    mapping = {
        '\uf700': 'ฐ', '\uf701': 'ิ', '\uf702': 'ี', '\uf703': 'ึ', 
        '\uf704': 'ื', '\uf705': 'ุ', '\uf706': 'ู', '\uf70a': '่', 
        '\uf70b': '้', '\uf70c': '๊', '\uf70d': '๋', '\uf70e': '์', 
        '\uf710': 'ั', '\uf711': 'ั', '\uf712': '็', 'เลี้ยวว': 'เลี้ยว',
        'ปูาย': 'ป้าย', 'ฝุา': 'ฝ่า', 'ฝุุน': 'ฝุ่น', 
        'ปจจุบัน': 'ปัจจุบัน', 'เปน': 'เป็น', 'ให': 'ให้',
        'ใช': 'ใช้', 'ผู': 'ผู้', 'ได': 'ได้', 'ตอง': 'ต้อง',
        'แก': 'แก่', 'ดวย': 'ด้วย', 'กวา': 'กว่า', 'อยาง': 'อย่าง',
        'ขอ': 'ข้อ', 'สวน': 'ส่วน', 'ไฟฟา': 'ไฟฟ้า',
        'สวาง': 'สว่าง', 'ทาย': 'ท้าย', 'หนา': 'หน้า', 'กลุม': 'กลุ่ม',
        'ตํารวจ': 'ตำรวจ', 'น้ํามัน': 'น้ำมัน', 'สําคัญ': 'สำคัญ'
    }
    for bad, good in mapping.items():
        text = text.replace(bad, good)
    return text

def extract_pdf():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    doc = fitz.open(os.path.join(base_dir, "กฏหมายจราจร.pdf"))
    
    pages_data = []
    for i, page in enumerate(doc):
        words = page.get_text("words")
        words.sort(key=lambda w: (round(w[1] / 12), w[0]))
        
        lines = []
        current_y = None
        current_line = []
        
        for w in words:
            if current_y is None or round(w[1] / 12) == current_y:
                current_line.append(w[4])
                current_y = round(w[1] / 12)
            else:
                lines.append(" ".join(current_line))
                current_line = [w[4]]
                current_y = round(w[1] / 12)
        if current_line:
            lines.append(" ".join(current_line))
        
        page_text = "\n".join([fix_thai_pua(line) for line in lines])
        pages_data.append({"page": i + 1, "content": page_text})
        
    with open(os.path.join(base_dir, "extracted_data.json"), "w", encoding="utf-8") as f:
        json.dump(pages_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    extract_pdf()