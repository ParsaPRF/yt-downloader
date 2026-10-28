# 🎬 دانلودر یوتیوب (نسخهٔ پایتونی)

از لینک‌های `videos.txt` دانلود می‌کند. یک لینک می‌تواند **تک‌ویدیو** یا **پلی‌لیست** باشد.

- **پلی‌لیست** خودکار به **لینک‌های تکی** هر ویدیو شکسته می‌شود و هر ویدیو در یک خط جدا در همان `videos.txt` نوشته می‌شود.
- کیفیت **1080p**، و اگر نبود **بالاترین موجود**، همیشه **همراه صدا**.
- **زیرنویس انگلیسی** (دستی + خودکار) به‌صورت `.srt`.
- هر لینک **موفق** بلافاصله از `videos.txt` حذف می‌شود؛ ناموفق‌ها می‌مانند تا دوباره تلاش شوند.
- مقاوم: ادامهٔ دانلود، تلاش مجدد، کوکی، `deno`/EJS.

---

## 📁 ساختار
```
yt-downloader/
├── yt_download.py      # منطق اصلی
├── download.sh         # wrapper (exec yt_download.py)
├── videos.txt          # لیست لینک‌ها
├── archive.txt         # ضدرِ دانلود مجدد (خودکار)
├── cookies.txt         # کوکی (اختیاری اما برای bot لازم)
├── setup.sh
├── downloads/<عنوان>/<عنوان>.mp4 + .en.srt
└── logs/
```

---

## 🚀 نصب (اوبونتو)
```bash
cd /root && unzip -o yt-downloader.zip && cd yt-downloader
chmod +x setup.sh download.sh
./setup.sh
```

---

## ✍️ لیست
```bash
nano videos.txt
```
هر لینک در یک خط (تک‌ویدیو یا پلی‌لیست). ذخیره: `Ctrl+O` Enter، خروج: `Ctrl+X`.

---

## 🍪 کوکی
برای عبور از پیام «Sign in to confirm you're not a bot» (IP دیتاسنتر):
- با افزونهٔ **Get cookies.txt LOCALLY** از مرورگرِ وارد‌شده کوکی youtube.com را بگیر.
- فایل را در `/root/yt-downloader/cookies.txt` بگذار.

---

## ▶️ اجرا
```bash
cd /root/yt-downloader && ./download.sh
```
یا مستقیم:
```bash
.venv/bin/python yt_download.py
```

### گزینه‌ها
```bash
./download.sh --quality 720          # کیفیت هدف
./download.sh --subs-langs "en.*"    # زبان زیرنویس
./download.sh --no-expand            # پلی‌لیست را به لینک تکی نشکن
./download.sh --no-remove-links      # لینک‌های موفق را حذف نکن
```

### پس‌زمینه با tmux
```bash
tmux new -s ytdl
cd /root/yt-downloader && ./download.sh
# جدا شدن امن: Ctrl+b سپس d   |   برگشت: tmux attach -t ytdl
```

---

## 🔁 رفتار لیست (مهم)
مثال `videos.txt` اولیه:
```
# my list
https://www.youtube.com/playlist?list=PL123
https://youtu.be/singleok
```
بعد از اجرا:
- پلی‌لیست به لینک تکی ویدیوها تبدیل می‌شود.
- هر ویدیو جدا دانلود می‌شود.
- ویدیوهای موفق از لیست حذف می‌شوند.
- فقط **ناموفق‌ها** در لیست می‌مانند.

پس کافی است هر بار دوباره `./download.sh` بزنی؛ فقط باقیمانده‌ها تلاش می‌شوند.

---

## 📊 بررسی
```bash
tail -f /root/yt-downloader/logs/ytdl_*.log
find /root/yt-downloader/downloads -type f
```

---

## ⚠️ رفع اشکال
- **`Sign in to confirm...not a bot`** → `cookies.txt` لازم/منقضی است.
- **`n challenge` / JS runtime** → `./setup.sh` (deno).
- **`ffmpeg not found`** → `sudo apt -y install ffmpeg`.
- **کیفیت 1080 نبود** → بالاترین موجود با صدا انتخاب می‌شود.