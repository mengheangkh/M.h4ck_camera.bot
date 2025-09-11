# 📸 M.h4ck Camera – Tracking Telegram Bot  

Bot នេះបង្កើតឡើងសម្រាប់ **តាមដានអ្នកចូល Link** ដោយប្រើ **Telegram Bot + Flask Server**។  
វាអាចប្រមូលព័ត៌មានពីអ្នកចូល link (Device info, Location, Camera) ហើយផ្ញើត្រឡប់ទៅ Telegram។  

---

## 📌 មូលដ្ឋានសំខាន់ៗ  

### 🔹 Telegram Bot *(python-telegram-bot)*  
- អ្នកប្រើត្រូវចាប់ផ្ដើមដោយបញ្ជា `/start`  
- បញ្ចូល **Password** (`BOT_PASSWORD`) មុននឹងអាចប្រើបាន  
- បន្ទាប់ពី authenticated អ្នកប្រើអាច **បង្កើត Tracking Link** ដោយផ្តល់ URL គោលដៅ  
- Bot បង្កើត **Public Link** តាម `ngrok` ហើយផ្ញើត្រឡប់ទៅអ្នកប្រើ  

---

### 🔹 Flask Web Server  
ពេលមានអ្នកចុច Link → Flask បង្ហាញទំព័រ HTML (JavaScript) ដែលប្រមូលព័ត៌មាន៖  
- 📱 Device info *(User-Agent, OS, Screen, Language, Memory, CPU)*  
- 📍 Location *(GPS)*  
- 🔋 Battery status  
- 📸 Camera access *(ថតរូបច្រើនសន្លឹក)*  
- 🌐 IP Address  

🔁 ព័ត៌មានទាំងអស់ត្រូវបាន **POST** ត្រឡប់ទៅ server  

---

### 🔹 Processing Data  
- រូបថតត្រូវបានបន្ថែម **Watermark** → `t.me/mengheang25`  
- Tracking data ត្រូវបានរក្សាទុកក្នុង memory (`tracking_data`)  
- រក្សាទុកជា file local ក្នុង folder → `captured_images/`  

---

### 🔹 Telegram Notification  
- ពេលមានអ្នកចូល Link → Bot ផ្ញើការជូនដំណឹងទៅ Telegram អ្នកបង្កើត Link  
- ជូនដំណឹងរួមមាន៖  
  - 🌐 IP Address  
  - 📱 Device Info  
  - 📍 Location + Google Maps link  
  - 📸 Camera Images *(ជាមួយ watermark)*  
- ផ្ញើប៊ូតុង **“បង្កើតតំណភ្ជាប់ថ្មីទៀត”**  

---

### 🔹 Thread Management  
- Flask Server រត់ក្នុង **Thread ដាច់ដោយឡែក**  
- Telegram Bot រត់ជាមួយ **Polling (ទទួលសារ 24/7)**  

---

## ✅ សរុប  
នេះគឺជា **Tracking Bot** ដែលអាច៖  
- បង្កើតតំណភ្ជាប់  
- ប្រមូលព័ត៌មានពីអ្នកចូល  
- ថតរូបពី Camera  
- ផ្ញើ Notification ទៅ Telegram Bot M.h4ck Camera

