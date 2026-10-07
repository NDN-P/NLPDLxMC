# MCQA — Thai presenter notes

English deck with Thai speaker notes. These are AI-authored presentation assistance. Add authentic names and contributions before submitting. The team must write AI_AUDIT Section 6 unaided.

## Timing

- Slides 1–2: 0–1 minute
- Slides 3–5: 1–4 minutes
- Live demo: 4–7 minutes
- Slides 6–10: 7–10 minutes
- Individual Q&A: next 5 minutes

## Demo

Before presenting, double-click demo.bat, wait for the ready prompt, and leave the terminal open. Use the full default mode. Model and index preparation is required before the session.

1. `How many Iron Ingots do I need for 3 Hoppers?` Show the validated tool trace and the answer, 15 Iron Ingots. The full direct recipe also uses 3 Chests.
2. `How do you breed cows in Minecraft?` Show the retrieved passages and revision citations. Read the actual answer and avoid adding claims it does not support.
3. `How do you breed cows in Bedrock Edition?` Show the explicit unsupported-edition boundary.

Do not claim general accuracy from these selected demo questions. If a local model answer fails, explain the observed limitation and move on. A frozen transcript is available in docs/demo_output.md and the recorded study folders; identify any replay as recorded evidence.

## Slide 1: MCQA

0:00–0:25

โปรเจกต์ของเราชื่อ MCQA เป็นผู้ช่วยตอบคำถาม Minecraft Java ที่ทำงานบนเครื่องทั้งหมดครับ คำถามเกี่ยวกับเกมจะค้นเอกสารและแสดงแหล่งอ้างอิง ส่วนจำนวนวัตถุดิบจะคำนวณจากสูตรทางการ เป้าหมายคือให้ผู้เล่นตรวจสอบคำตอบได้ และลดการเดาตัวเลขของโมเดลครับ

Sources:
- docs/sources.md
- README.md
- AI_AUDIT.md

## Slide 2: Players need facts and exact amounts

0:25–1:00

ปัญหามีทั้งคำตอบในวิกิที่ปนหลายเวอร์ชัน และการคำนวณจำนวนวัตถุดิบครับ เช่น ถ้าต้องการ Hopper สามชิ้น ผู้เล่นต้องรู้จำนวน Iron Ingots ที่ต้องใช้ เราจึงแยกวิธีตอบ คำถามข้อเท็จจริงใช้หลักฐาน ส่วนตัวเลขใช้เครื่องมือคำนวณ และตั้งขอบเขตเป็น Java Edition ระบบนี้ใช้งานโดยไม่เสียค่า API หลังจากเตรียมโมเดลไว้ในเครื่องครับ

Sources:
- docs/sources.md
- README.md
- docs/failure_analysis.md

## Slide 3: Two answer paths, one local system

1:00–2:00

แถวบนคือการเตรียมข้อมูลครับ เราเก็บวิกิพร้อม revision แบ่งข้อความตาม section แล้วสร้าง dense index บน CPU พร้อม BM25 เวลารับคำถาม ระบบตรวจขอบเขตก่อน ถ้าเป็นสูตรและจำนวนที่อ่านได้ชัดเจน จะส่งไปคำนวณตรงทันที คำถามอื่นจะค้นเอกสาร รวมอันดับด้วย RRF และเรียงใหม่ก่อนส่งให้ Qwen ตอบพร้อม citation ถ้าเป็นคำถามซับซ้อน โมเดลยังสามารถเรียกเครื่องมือสูตรได้ผ่าน tool loop ครับ

Sources:
- mcqa.py: chunks, Retriever, crafting_intent, answer, _agent_answer
- docs/sources.md
- README.md

## Slide 4: Real pages, compact evidence

2:00–2:45

ข้อมูลค้นคืนเป็นบทความจริงจาก Minecraft Wiki ไม่ใช่ชุดถามตอบสังเคราะห์ครับ มี 312 หน้าที่ไม่ซ้ำกันและประมาณแปดแสนหนึ่งหมื่นเจ็ดพันคำ เราเก็บ revision ของแต่ละหน้าไว้ เราเปรียบเทียบ chunk ขนาด 128, 256 และ 512 โทเคน ผล source-page hit เดิมใกล้กัน จึงใช้ 256 เพื่อรักษาบริบทโดยไม่เพิ่มต้นทุนมาก แบ่งตาม section และ paragraph ก่อน ถ้ายาวเกินจึงแบ่งย่อย ไม่มี overlap ข้อจำกัดคือ corpus ยังมีข้อมูลเก่า และ 312 หน้าไม่ได้ครอบคลุมทุกเรื่องในเกมครับ

Sources:
- docs/sources.md
- docs/corpus_inventory.csv
- results/RESULTS.md
- mcqa.py: chunks
- README.md

## Slide 5: Small models keep the system local

2:45–4:00; then switch to the live demo until 7:00

เราใช้ BGE-small ทำ embedding บน CPU ครับ BM25 ช่วยเรื่องชื่อ item ที่ตรงคำ ส่วน dense retrieval ช่วยจับความหมาย RRF รวมอันดับโดยไม่ต้องทำให้คะแนนสองระบบอยู่ในสเกลเดียวกัน จากนั้น cross-encoder จะอ่านคำถามกับ passage คู่กันแล้วเลือกห้าอันดับแรก ส่วน Qwen 4B ทำหน้าที่ตอบและวางแผนเรียกเครื่องมือ โมเดลทั้งหมดมีอยู่ในเครื่อง แต่เราไม่สรุปว่าการเพิ่ม reranker จะทำให้ดีกว่าเสมอ ต้องดูผล ablation ต่อไปครับ

Sources:
- docs/sources.md
- mcqa.py: embedder, reranker, Retriever, chat
- results/verified/test/summary.json

## Slide 6: Retrieved evidence improves factual answers

7:00–7:35

เริ่มจากผลทดลองชุดแรก ซึ่งมีคำถามข้อเท็จจริง 34 ข้อครับ ถ้าให้โมเดลตอบโดยไม่ค้นเอกสาร จะตอบถูก 9 ข้อ เมื่อใช้ dense retrieval เพิ่มเป็น 27 ข้อ ส่วน hybrid ที่มี reranker ได้ 26 ข้อ ผลนี้สนับสนุนว่าการค้นเอกสารช่วยได้ แต่ยังไม่เห็นข้อได้เปรียบชัดเจนของ reranker คะแนนเหล่านี้มาจากการทดลองรุ่นเดิมที่เก็บไว้ และใช้โมเดลเป็นผู้ประเมินครับ

Sources:
- results/verified/test/summary.json
- results/verified/test/RESULTS.md
- results/verified/test/config.json
- data/java_benchmark.jsonl

## Slide 7: The recipe tool improves quantity answers

7:35–8:10

สำหรับการคำนวณวัตถุดิบ เราเปรียบเทียบคำถาม 40 ข้อ โดยเปิดและปิดเครื่องมือ เมื่อไม่มีเครื่องมือ ตอบจำนวนถูกเพียง 1 ข้อ แต่เมื่อใช้เครื่องมือ ถูก 37 ข้อ เครื่องมืออ่านสูตรทางการแล้วคำนวณจำนวนรอบการคราฟต์ให้ ส่วนสามข้อที่ผิดไม่ได้เรียกเครื่องมือเลย จุดที่ยังติดจึงเป็นการส่งคำถามไปใช้เครื่องมือ ผลนี้วัดจำนวนวัตถุดิบโดยตรง ยังไม่ครอบคลุมการวางแผนจากของทั้งหมดในคลังครับ

Sources:
- results/verified/tool_final/summary.json
- results/verified/tool_final/RESULTS.md
- results/verified/tool_final/answers.jsonl
- docs/sources.md

## Slide 8: Current quality needs two kinds of checks

8:10–8:45

ผลของระบบปัจจุบันใช้ชุดทดสอบใหม่ที่มีข้อเท็จจริง 8 ข้อครับ Dense ตอบถูก 6 ข้อ และได้ BERTScore จุดหกห้าสี่ ส่วน reranker ถูก 7 ข้อ แต่ได้ BERTScore จุดหกศูนย์ศูนย์ คะแนนสองแบบวัดคนละเรื่อง การตัดสินความถูกต้องเทียบกับข้อมูลอ้างอิง ส่วน BERTScore วัดความคล้ายของข้อความ จึงอาจให้ลำดับต่างกันได้ ชุดนี้ยังเล็ก และยังไม่มีการตรวจโดยคนอย่างอิสระครับ

Sources:
- results/improvement_review/summary.json
- results/improvement_review/RESULTS.md
- results/improvement_review/after_config.json
- results/improvement_review/paired_stats.json

## Slide 9: Correct numbers can still hide wrong claims

8:45–9:20

ระบบยังมีข้อจำกัดสามเรื่องครับ หนึ่ง การกรองข้อความของเวอร์ชันอื่นอาจตัดข้อมูล Java ที่ใช้ได้ออกไปด้วย สอง คำถามหลายส่วนอาจได้ตัวเลขจากเครื่องมือถูก แต่คำอธิบายที่โมเดลเติมยังไม่มีหลักฐานรองรับ และสาม เราใช้โมเดลเดียวกันตอบและประเมิน จึงมีโอกาสประเมินผิดหรือเข้าข้างคำตอบของตัวเอง เราเก็บคำตอบดิบและแหล่งอ้างอิงไว้ เพื่อให้ย้อนตรวจข้อผิดพลาดเหล่านี้ได้ครับ

Sources:
- results/improvement_review/analysis_notes.md
- docs/failure_analysis.md
- results/improvement_review/after_answers.jsonl
- results/improvement_review/human_check.csv

## Slide 10: AI audit: decisions and an error we caught

9:20–10:00; then individual Q&A

ใน AI Audit เราระบุอย่างตรงไปตรงมาว่า AI เป็นผู้เลือกสามแนวทางนี้ ได้แก่ chunk ขนาด 256 โทเคน โมเดล BGE ที่ทำงานบน CPU และการคำนวณสูตรทางการแบบตรง โดยเก็บ tool loop สำหรับคำถามที่ซับซ้อน ตัวอย่างข้อผิดพลาดที่พบคือ ตัวให้คะแนนเดิมหยิบเลขตัวแรกจากคำตอบ แม้คำตอบนั้นจะปฏิเสธและแค่ทวนจำนวนในคำถาม จึงถูกแก้ให้ตรวจจำนวนวัตถุดิบที่ถาม และไม่ให้คะแนนคำปฏิเสธครับ

Sources:
- AI_AUDIT.md: Decision Journal and Error Catch Log
- docs/codex_prompt_history.md
- codextodo.md
- docs/codex_review.md
- test_eval.py
