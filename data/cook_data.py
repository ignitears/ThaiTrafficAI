import json
import re
import os

def cook_perfect_database():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, "extracted_data.json")
    output_path = os.path.join(base_dir, "perfect_rag_database.json")
    
    # Read the raw extracted JSON you provided
    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    cooked_chunks = []
    
    # Context trackers for the narrative rules (Pages 1-23)
    h1_context = ""  # Tracks headers like "๒.๑ รถยนต์ต้องมีโคมไฟ..."
    h2_context = ""  # Tracks sub-headers like "(๑) โคมไฟหน้ารถมี ๓ ประเภท คือ"
    
    # Context trackers for the fine tables (Pages 24-52)
    laksana_context = "" # Tracks "ลักษณะ ๑ การใช้รถ"
    mhod_context = ""    # Tracks "หมวด ๑ ลักษณะของรถที่ใช้ในทาง"
    
    current_chunk = None

    for page in raw_data:
        page_num = page["page"]
        lines = page["content"].split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # --- NARRATIVE SECTION (Pages 1-23) ---
            if page_num <= 23:
                # Match main headers like "๒.๑" or "๒.๒"
                if re.match(r'^[๐-๙]+\.[๐-๙]+\s', line):
                    h1_context = line
                    h2_context = ""
                    current_chunk = {"source": f"Page {page_num}", "content": line}
                    cooked_chunks.append(current_chunk)
                    
                # Match sub-headers like "(๑)" or "(๒)"
                elif re.match(r'^\([๐-๙]+\)\s', line):
                    h2_context = line
                    text = f"{h1_context}\n{line}".strip()
                    current_chunk = {"source": f"Page {page_num}", "content": text}
                    cooked_chunks.append(current_chunk)
                    
                # Match bullet points like "(ก)", "(ข)", "(ค)"
                elif re.match(r'^\([ก-ฮ]\)\s', line):
                    text = f"{h1_context}\n{h2_context}\n{line}".strip()
                    current_chunk = {"source": f"Page {page_num}", "content": text}
                    cooked_chunks.append(current_chunk)
                    
                # Append continuing text to the current chunk
                else:
                    if current_chunk:
                        current_chunk["content"] += f" {line}"
                        
            # --- TABLE SECTION (Pages 24-52) ---
            else:
                # Match major table categories
                if line.startswith("ลักษณะ"):
                    laksana_context = line
                    mhod_context = ""
                elif line.startswith("หมวด"):
                    mhod_context = line
                    
                # Match numbered offense rows like "๑ นํารถที่มีสภาพ..."
                elif re.match(r'^[๐-๙]+\s', line) and not line.startswith("ลําดับ"):
                    text = f"{laksana_context}\n{mhod_context}\n{line}".strip()
                    current_chunk = {"source": f"Page {page_num}", "content": text}
                    cooked_chunks.append(current_chunk)
                    
                # Append continuing table text to the current offense
                else:
                    # Ignore repetitive table headers
                    if "ลําดับ ข้อหาหรือฐานความผิด" in line or "ลักษณะ ชนิดหรือประเภท" in line:
                        continue
                    if current_chunk:
                        current_chunk["content"] += f" {line}"

    # Clean up empty or invalid chunks
    final_chunks = [c for c in cooked_chunks if len(c["content"]) > 20]

    # Save the masterfully cooked data
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_chunks, f, ensure_ascii=False, indent=2)
        
    print(f"Chef's kiss! Cooked {len(final_chunks)} perfect RAG chunks.")

if __name__ == "__main__":
    cook_perfect_database()