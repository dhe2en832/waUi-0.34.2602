# 🚀 WACSA-MD2 UI - Setup & Running Guide

## 📋 **Requirements**

### **System Requirements**
- **OS**: Windows 10/11 (recommended), Linux, macOS
- **Python**: 3.8 or higher **(Python 3.14.3 recommended - latest version)**
- **Node.js**: 14.0.0 or higher (for changelog script)
- **RAM**: Minimum 4GB
- **Storage**: 500MB free space

### **Software yang Dibutuhkan**
1. **Python 3.8+** - Download dari [python.org](https://python.org) **(Python 3.14.3 latest recommended)**
2. **Node.js 14+** - Download dari [nodejs.org](https://nodejs.org)
3. **Git** - Download dari [git-scm.com](https://git-scm.com)

---

## 🔧 **Installation Steps**

### **1. Install Python 3.14.3 (Latest)**
```bash
# Download Python 3.14.3 dari https://python.org
# Penting: Centang "Add Python to PATH" saat install

# Verify installation
python --version
# Output: Python 3.14.3
```

### **2. Masuk ke folder project**
```bash
cd wacsaa-md2-ui
```

### **3. Install Python Dependencies**
```bash
# Install Python packages
pip install -r requirements.txt
```

### **4. Install Node.js Dependencies**
```bash
# Install Node.js packages (for changelog script)
npm install
```

### **5. Verify Installation**
```bash
# Check Python version
python --version

# Check Node.js version  
node --version

# Check installed packages
pip list
```

---

## 🎮 **Running the Application**

### **Option 1: Quick Start (Recommended)**
```bash
python run.py
```
Script ini akan:
- Install dependencies otomatis
- Jalankan aplikasi langsung

### **Option 2: Manual Start**
```bash
python main.py
```

### **Option 3: Development Mode**
```bash
npm start
# atau
python main.py
```

---

## 🖥️ **Application Interface**

### **Main Navigation**
- **Dashboard**: Overview status dan statistik
- **WhatsApp**: Kirim pesan, cek status
- **Messages**: Lihat history pesan
- **Settings**: Konfigurasi server

### **WhatsApp Module Features**
- ✅ Status checking (real-time)
- ✅ Send text messages
- ✅ Send media messages (image, video, audio, document)
- ✅ File browser untuk media selection
- ✅ Message type toggle (Text/Media)

---

## 🔗 **Server Configuration**

### **1. Start WACSA-MD2 Server**
Pastikan WACSA-MD2 server sudah running:
```bash
# Di folder wacsa-md2
npm start
# atau
node src/main.js
```

### **2. Connect UI ke Server**
1. Buka WACSA-MD2 UI
2. Masukkan server URL di sidebar (contoh: `http://192.168.100.13:8008`)
3. Klik "Connect"
4. Cek WhatsApp status dengan "Refresh Status"

### **3. API Endpoints yang Digunakan**
- `GET /health` - Server health check
- `GET /log/received-message` - History pesan masuk
- `GET /log/sent-message` - History pesan keluar  
- `GET /log/statistic` - Statistik WhatsApp
- `POST /message/send-text` - Kirim pesan teks
- `POST /message/send-media` - Kirim pesan media

---

## ⚠️ **Important Notes**

### **Read-and-Clear Pattern**
WACSA-MD2 menggunakan "Read-and-Clear" pattern untuk logs:
- Setiap kali `/log/*` endpoint dipanggil, log akan **dihapus**
- Ini mencegah duplicate processing
- Enable backup di `wacsa.ini` jika perlu preserve data

### **Message History**
- Pesan akan hilang setelah dibaca dari logs
- UI menampilkan copy dari pesan yang sudah dibaca
- Refresh messages akan menghapus logs di server

---

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **1. Python Not Found**
```bash
# Error: 'python' is not recognized
# Solution: Use 'py' instead of 'python' (Windows)
py run.py
# atau
python3 run.py
```

#### **2. Module Not Found**
```bash
# Error: ModuleNotFoundError: No module named 'customtkinter'
# Solution: Install dependencies
pip install -r requirements.txt
```

#### **3. Connection Failed**
```bash
# Error: Failed to connect to server
# Solution: 
# 1. Pastikan WACSA-MD2 server running
# 2. Check server URL
# 3. Verify firewall settings
```

#### **4. Empty Logs on Second Request**
```bash
# This is expected behavior (Read-and-Clear pattern)
# Solution: Enable backup in wacsa.ini
[BackupLog]
ReceivedLogBackup=true
SentLogBackup=true
StatisticLogBackup=true
```

### **Debug Mode**
Untuk debugging, tambahkan logging:
```python
# Di main.py, tambahkan:
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📦 **Building Executable**

### **Windows Executable**
```bash
python build.py
```
Executable akan dibuat di `dist/WACSA-MD2-UI.exe`

### **Requirements untuk Build**
- PyInstaller (otomatis di-install)
- Python 3.8+
- Windows (untuk Windows executable)

---

## 📝 **Development**

### **Project Structure**
```
wacsa-md2-ui/
├── main.py              # Main application
├── api_client.py        # API client
├── build.py             # Build script
├── run.py               # Quick start
├── requirements.txt     # Python deps
├── package.json         # Node.js config
└── custom/              # Custom scripts
    └── scripts/
        └── generate-changelog.cjs
```

### **Adding New Features**
1. Edit `main.py` untuk UI changes
2. Edit `api_client.py` untuk API changes
3. Test dengan `python main.py`
4. Generate changelog: `npm run changelog`

### **Code Style**
- Python: PEP 8 guidelines
- Use descriptive variable names
- Add comments for complex logic
- Follow existing code patterns

---

## 🎯 **Quick Test**

### **Test Application Startup**
```bash
# Test 1: Basic startup
python run.py

# Test 2: Check dependencies
pip list | grep customtkinter

# Test 3: Test API client (if server running)
python -c "from api_client import WACSAAPIClient; print('API Client OK')"
```

### **Test WhatsApp Features**
1. Start aplikasi
2. Connect ke WACSA-MD2 server
3. Test kirim pesan teks
4. Test kirim media file
5. Check message history

---

## 📞 **Support**

### **Getting Help**
1. Check troubleshooting section
2. Review WACSA-MD2 documentation
3. Check GitHub issues
4. Contact development team

### **Report Issues**
- Include: OS version, Python version, error messages

---

## 🔄 **Updates & Maintenance**

### **Update Dependencies**
```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Update Node.js packages
npm update
```

### **Generate Changelog**
```bash
npm run changelog
git add custom/docs/changelog/daily/codeChange-$(date +%Y%m%d).md
git commit -m "docs: update changelog"
```

---

**Selamat menggunakan WACSA-MD2 UI! 🚀**
