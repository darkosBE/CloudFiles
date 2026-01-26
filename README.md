---
s
# ☁️ CloudFiles.lol  
### *A stunning, self-hosted cloud storage — built for beauty and simplicity.*


---

## ✨ Features

- **🔐 Secure Login** – Username: `changeme` / Password: `CHANGEME`
- **📱 Fully Responsive** – Looks gorgeous on mobile, tablet, and desktop
- **📁 File Management** – Upload, download, create, edit, delete
- **✏️ Built-in Text Editor** – Edit `.txt`, `.py`, `.md`, `.json`, and more
- **📊 Live System Dashboard** – Monitor CPU, RAM, disk, and server specs
- **🕒 File Timestamps** – See when files were last modified
- **🚫 No Database Needed** – Uses only the file system
- **🎨 Ultra-Modern UI** – Glassmorphism, animated gradients, smooth animations

---

## 🚀 Quick Start

### 1. Clone or Create the Project
```bash
# If you're in GitHub Codespaces, just create a new file called `app.py`
# Otherwise, clone your repo or create a folder
mkdir cloudfiles && cd cloudfiles
```

### 2. Install Dependencies
```bash
pip install flask psutil
```

> 💡 **Note**:  
> - `flask` → Web framework  
> - `psutil` → System monitoring (CPU/RAM/Disk)

### 3. Save the Code
Save the [ `app.py`](#).

### 4. Run the Server
```bash
python app.py
```

### 5. Access Your Cloud
Open your browser and go to:  
👉 **http://localhost:PORT**

Or if you're using **GitHub Codespaces**:  
1. Run the app  
2. Click the **"Ports"** tab in the bottom panel  
3. Make port `your given port ex: 8080` **Public**  
4. Click **"Open in Browser"**

---

## 🔐 Login Credentials

| Field    | Value     |
|----------|-----------|
| Username | `changeme` |
| Password | `CHANGEME`   |

> ⚠️ **For personal use only** – this is not hardened for public internet exposure.

---

## 📁 File Storage

All your files are stored in:  
```
your-project-folder/
└── cloudfiles_storage/   ← Your private cloud!
```

This folder is created automatically on first run.

---

## 🖥️ System Requirements

- **Python 3.7+** (tested on 3.12.12)
- ~50 MB disk space
- Any OS (Windows, macOS, Linux, GitHub Codespaces)

---

## 🌐 Deployment Tips

### GitHub Codespaces ✅
- Works out of the box
- Expose port `8080`
- No extra config needed

### VPS / Cloud Server
```bash
# Run in background (using nohup)
nohup python app.py > cloudfiles.log 2>&1 &

# Access via your server IP:
# http://YOUR_SERVER_IP:PORT
```

> 🔒 **Security Note**:  
> For public servers, consider:
> - Adding HTTPS (via Nginx + Let's Encrypt)
> - Changing default credentials
> - Restricting by IP

---

## 🎨 UI Highlights

- **Glassmorphism design** with backdrop blur
- **Animated gradient logo** 🌈
- **Smooth hover & tap animations**
- **Floating Action Button (FAB)** for quick actions
- **Live system metrics** with animated progress bars
- **Dark theme optimized** for low eye strain

---

## 📜 License

This project is **free for personal use**.  
Made with ❤️ for **Syzdark**.

---

> **CloudFiles.lol** — Your files, your server, your rules.  
> *No tracking. No ads. Just beauty.*

---

💾 **All data stays on your machine.**  
🌐 **Access from anywhere.**  
✨ **Enjoy your private cloud!**

--- 
