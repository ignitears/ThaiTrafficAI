import fitz
import json
import os
import re
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

def build_optimal_rag():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    doc = fitz.open(os.path.join(base_dir, "กฏหมายจราจร.pdf"))
    
    rag_chunks = []
    h1, h2, h3 = "", "", ""
    
    # 1. Process narrative section (Pages 1 to 23)
    for i in range(23):
        words = doc[i].get_text("words")
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
        paragraphs = [p.strip() for p in page_text.split("\n") if len(p.strip()) > 20]
        
        current_paragraph = ""
        for p in paragraphs:
            first_word = p.split(" ")[0] if " " in p else p
            
            # Track Thai hierarchical headers
            if re.match(r'^([๐-๙]+|\d+)\.$', first_word):
                h1 = p
                h2, h3 = "", ""
            elif re.match(r'^([๐-๙]+|\d+)\.([๐-๙]+|\d+)$', first_word):
                h2 = p
                h3 = ""
            elif re.match(r'^\(([๐-๙]+|\d+)\)$', first_word):
                h3 = p
                
            is_list_item = re.match(r'^(\(?\d+\)?|\(?[๐-๙]+\)?|\([ก-ฮ]\))\s', p)
            
            if is_list_item:
                if current_paragraph:
                    rag_chunks.append({
                        "type": "narrative",
                        "source": f"Page {i + 1}",
                        "content": current_paragraph.strip()
                    })
                
                context = ""
                is_sub_bullet = re.match(r'^\([ก-ฮ]\)', first_word)
                if is_sub_bullet:
                    if h1: context += f"{h1}\n"
                    if h2: context += f"{h2}\n"
                    if h3: context += f"{h3}\n"
                
                current_paragraph = context + p
            else:
                current_paragraph += " " + p
                
        if current_paragraph:
            rag_chunks.append({
                "type": "narrative",
                "source": f"Page {i + 1}",
                "content": current_paragraph.strip()
            })

    # 2. Process table section (Pages 24 to 52)
    for i in range(23, len(doc)):
        words = doc[i].get_text("words")
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
            
        current_entry = ""
        for line in lines:
            text = fix_thai_pua(line)
            text = re.sub(r'\s+', ' ', text)
            
            if re.match(r'^([๐-๙]+|\d+)\s', text) or text.startswith("ลักษณะ") or text.startswith("หมวด"):
                if current_entry:
                    rag_chunks.append({
                        "type": "fine_table",
                        "source": f"Page {i + 1}",
                        "content": current_entry.strip()
                    })
                current_entry = text
            else:
                current_entry += " " + text
                
        if current_entry:
            rag_chunks.append({
                "type": "fine_table",
                "source": f"Page {i + 1}",
                "content": current_entry.strip()
            })

    out_path = os.path.join(base_dir, "rag_database.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rag_chunks, f, ensure_ascii=False, indent=2)
        
    print(f"Success! Saved {len(rag_chunks)} highly-optimized RAG chunks.")

if __name__ == "__main__":
    build_optimal_rag()