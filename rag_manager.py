import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from brain import CharacterBrain

class RAGManager:
    def __init__(self, model_path: str):
        self.brain = CharacterBrain(model_path)
        self.is_tsundere = False
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "data")
        
        self.index = faiss.read_index(os.path.join(data_dir, "vector_index.faiss"))
        with open(os.path.join(data_dir, "rag_database.json"), "r", encoding="utf-8") as f:
            self.data = json.load(f)
            
        self.embed_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    def retrieve_context(self, query: str, top_k: int = 6) -> str:
        query_vector = self.embed_model.encode([query]).astype("float32")
        distances, indices = self.index.search(query_vector, top_k)
        retrieved_texts = [self.data[idx]["content"] for idx in indices[0] if idx < len(self.data)]
        return "\n---\n".join(retrieved_texts)

    def generate_answer(self, user_query: str, history: list[dict] = None, is_tsundere: bool = False) -> str:
        active_tsundere = is_tsundere or self.is_tsundere
        rag_context = self.retrieve_context(user_query, top_k=6)
        
        if active_tsundere:
            system_instruction = (
                "คุณคือผู้ช่วยกฎหมายจราจรไทยที่มีนิสัย 'สึนเดะเระ' (Tsundere) และใจร้อน\n"
                "หน้าที่: ตอบคำถามจาก [ข้อมูลอ้างอิง] เท่านั้น ห้ามแต่งเติมข้อมูลเองเด็ดขาด\n\n"
                "กฎข้อบังคับ:\n"
                "1. หากถูกถามว่าคุณคือใคร หรือทำอะไรได้บ้าง ให้พิมพ์ [IDENTITY] คำเดียวเท่านั้น!\n"
                "2. หากคำถามไม่มีคำตอบใน [ข้อมูลอ้างอิง] หรือสิ่งนั้นไม่มีระบุในเอกสาร ให้พิมพ์ [NO_INFO] คำเดียวเท่านั้น ห้ามมั่วเด็ดขาด!\n"
                "3. หากคำถามไม่เกี่ยวกับรถ จราจร หรือกฎหมาย ให้พิมพ์ [OFF_TOPIC] คำเดียวเท่านั้น!\n"
                "4. หากมีข้อมูล ให้สรุปเนื้อหาตอบแบบสึนเดะเระ ประชดประชัน ห้ามเกิน 3 ประโยค\n"
                "5. แทนตัวเองว่า 'ฉัน' เสมอ\n"
                "6. ห้ามบอกว่าตัวเองเป็นสึนเดะเระ\n"
                "7.หากเป็นการทักทาย หรือมีข้อมูลในเอกสาร ให้ตอบความรู้ตามนั้น แต่ใช้คำพูดประชดประชัน ปากไม่ตรงกับใจ (เช่น 'เชอะ!', 'ฮึ', 'ฮึ่ม', 'รีบ ๆ ถามคำถามต่อไปได้แล้ว',  'ตาบ้าเอ๊ย!')\n"
            )
            temp = 0.5 # Lowered temperature to prevent creative writing
        else:
            system_instruction = (
                "คุณเป็นผู้ช่วยตอบคำถามกฎหมายจราจรไทย\n"
                "หน้าที่: ตอบคำถามจาก [ข้อมูลอ้างอิง] เท่านั้น ห้ามแต่งเติมข้อมูลเองเด็ดขาด\n\n"
                "กฎข้อบังคับ:\n"
                "1. หากถูกถามว่าคุณคือใคร หรือทำอะไรได้บ้าง ให้พิมพ์ [IDENTITY] คำเดียวเท่านั้น!\n"
                "2. หากคำถามไม่มีคำตอบใน [ข้อมูลอ้างอิง] หรือสิ่งนั้นไม่มีระบุในเอกสาร ให้พิมพ์ [NO_INFO] คำเดียวเท่านั้น ห้ามมั่วเด็ดขาด!\n"
                "3. หากคำถามไม่เกี่ยวกับรถ จราจร หรือกฎหมาย ให้พิมพ์ [OFF_TOPIC] คำเดียวเท่านั้น!\n"
                "4. หากมีข้อมูล ให้สรุปเนื้อหาตอบตรงๆ อย่างเป็นทางการ ห้ามเกิน 3 ประโยค ห้ามแต่งเรื่องขึ้นเองเด็ดขาด\n"
                "5. แทนตัวเองว่า 'ฉัน' เสมอ"
            )
            temp = 0.05 # Near-zero temperature for strict adherence to facts

        history_text = ""
        if history:
            for msg in history[-6:]:
                role = "user" if msg.get("role") == "user" else "assistant"
                content = msg.get("content", "")
                history_text += f"<|start_header_id|>{role}<|end_header_id|>\n\n{content}<|eot_id|>\n"

        prompt = (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            f"{system_instruction}\n\n"
            f"[ข้อมูลอ้างอิงที่จะต้องนำไปตอบ]:\n{rag_context}<|eot_id|>\n"
            f"{history_text}"
            f"<|start_header_id|>user<|end_header_id|>\n\n{user_query}<|eot_id|>\n"
            "<|start_header_id|>assistant<|end_header_id|>\n\n"
        )
        
        reply = self.brain.generate_from_prompt(prompt, temperature=temp)
        
        # Bruteforce cleanup
        reply = reply.replace("ตามข้อมูลอ้างอิง,", "").replace("ตามข้อมูลอ้างอิง", "").replace("จากข้อมูลอ้างอิง", "").strip()
        if reply.startswith(" "): 
            reply = reply.lstrip()
            
        # Intercept trigger words instantly
        if "[IDENTITY]" in reply:
            if active_tsundere: return "เชอะ! ฉันก็เป็นแค่ผู้ช่วยตอบคำถามกฎหมายจราจรไทยเท่านั้นแหละ ไม่ได้อยากจะมาช่วยตอบคำถามนายนักหรอกนะ ตาบ้า!"
            return "ฉันคือผู้ช่วย AI ที่สามารถให้ข้อมูลเกี่ยวกับกฎหมายจราจร การใช้รถ และการใช้ถนนในประเทศไทยค่ะ"
        
        if "[OFF_TOPIC]" in reply:
            if active_tsundere: return "ถามอะไรไร้สาระยะ! ฉันมาตอบเรื่องจราจรนะ ตาบ้า!"
            return "ขออภัยค่ะ ฉันเป็นผู้ช่วยด้านกฎหมายจราจร ไม่สามารถตอบคำถามนี้ได้"
            
        if "[NO_INFO]" in reply:
            if active_tsundere: return "เชอะ! ในเอกสารฉันไม่มีเรื่องนี้หรอกนะ ไปหาเอาเองสิยะ!"
            return "ขออภัยค่ะ ข้อมูลนี้ไม่มีระบุอยู่ในระบบ"
            
        return reply