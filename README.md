# Lab 11 - Guardrails, HITL, Responsible AI

**Họ và tên:** Nguyễn Đào Nam Hải
**MSSV:** 2A202601037

## Cách chạy

1. Cài đặt thư viện:
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Cài đặt API Key:
```powershell
$env:GOOGLE_API_KEY="your-api-key"
```

3. Chạy từng phần:
```powershell
# Phần 1: Tấn công agent không bảo vệ
python src/main.py --part 1

# Phần 2: Kiểm tra phòng thủ (Defense in Depth)
python src/main.py --part 2

# Phần 3: Chạy toàn bộ pipeline kiểm thử tự động
python src/main.py --part 3

# Phần 4: Mô phỏng Human in the Loop (HITL)
python src/main.py --part 4
```
