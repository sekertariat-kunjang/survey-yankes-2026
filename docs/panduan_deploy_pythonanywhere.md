# Panduan Lengkap Deployment CeKReK ke PythonAnywhere

Panduan ini disusun khusus untuk mendeploy aplikasi **CeKReK** (*Cek langsung Kondisi dan buktikan layanan Puskesmas sudah sesuai dengan standaR Kesehatan*) ke hosting **PythonAnywhere** menggunakan domain:  
👉 **`https://cekrek.pythonanywhere.com`**

---

## 📌 Ringkasan Parameter Konfigurasi

| Parameter | Nilai Konfigurasi |
|---|---|
| **Platform** | [PythonAnywhere](https://www.pythonanywhere.com) (Akun: `cekrek`) |
| **Email Terdaftar** | `upt.pkm.kunjang@gmail.com` |
| **URL Aplikasi** | `https://cekrek.pythonanywhere.com` |
| **Repositori GitHub** | `https://github.com/sekertariat-kunjang/survey-yankes-2026.git` |
| **Versi Python** | Python 3.10 (atau Python 3.11) |
| **Virtual Environment** | `/home/cekrek/.virtualenvs/survey-env` |
| **Folder Proyek** | `/home/cekrek/survey-yankes-2026` |
| **WSGI File** | `/var/www/cekrek_pythonanywhere_com_wsgi.py` |

---

## 🚀 Langkah-Langkah Deployment

### Langkah 1: Klon Repositori & Buat Virtualenv (Bash Console)

1. Masuk (*Log In*) ke akun Anda di [PythonAnywhere](https://www.pythonanywhere.com/login/).
2. Buka tab **Consoles** pada menu navigasi atas.
3. Di bawah bagian **Start a new console**, klik **Bash**.
4. Tunggu terminal hitam muncul, kemudian jalankan perintah berikut secara berurutan:

```bash
# 1. Pastikan berada di direktori home
cd ~

# 2. Kloning repositori proyek dari GitHub
git clone https://github.com/sekertariat-kunjang/survey-yankes-2026.git

# 3. Masuk ke folder proyek
cd ~/survey-yankes-2026

# 4. Buat virtual environment bernama 'survey-env' menggunakan Python 3.10
python3.10 -m venv ~/.virtualenvs/survey-env

# 5. Aktifkan virtual environment
source ~/.virtualenvs/survey-env/bin/activate

# 6. Perbarui pip dan instal seluruh dependensi
pip install --upgrade pip
pip install -r requirements.txt
```

> **Tips:** Proses instalasi `pandas` dan dependensinya membutuhkan waktu sekitar 1–2 menit. Tunggu hingga prompt terminal kembali aktif dan menampilkan baris perintah baru.

---

### Langkah 2: Konfigurasi File Lingkungan (.env)

Masih di dalam terminal Bash (folder `~/survey-yankes-2026`):

```bash
# Salin template .env.example menjadi .env
cp .env.example .env

# Buka editor nano untuk mengatur password admin dan kunci rahasia
nano .env
```

Sesuaikan isinya:
```ini
SECRET_KEY=kunci-rahasia-acak-minimal-32-karakter-keamanan-2026
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password_admin_yang_kuat_dan_aman
FLASK_DEBUG=false
```

- Tekan `Ctrl + O` lalu `Enter` untuk menyimpan file.
- Tekan `Ctrl + X` untuk keluar dari nano.

---

### Langkah 3: Buat Web App Baru di Tab "Web"

1. Klik tab **Web** di menu navigasi atas dashboard PythonAnywhere.
2. Klik tombol biru **"Add a new web app"**.
3. Pada dialog domain: domain Anda akan otomatis terisi `cekrek.pythonanywhere.com`. Klik **Next**.
4. Pada pilihan framework: **PILIH "Manual configuration (including virtualenvs)"**  
   *(⚠️ PENTING: JANGAN pilih opsi "Flask" wizard bawaan karena opsi tersebut akan membuat struktur file kosong baru yang menimpa proyek kita).*
5. Pada pilihan versi Python: Pilih **Python 3.10** (sesuai versi venv yang dibuat pada Langkah 1).
6. Klik **Next** hingga selesai.

---

### Langkah 4: Hubungkan Virtual Environment & Direktori Proyek

Setelah halaman konfigurasi Web App terbuka:

1. **Bagian Code:**
   - **Source code:** Isi dengan `/home/cekrek/survey-yankes-2026`
   - **Working directory:** Isi dengan `/home/cekrek/survey-yankes-2026`

2. **Bagian Virtualenv:**
   - Klik teks abu-abu di samping tulisan **Virtualenv:**
   - Masukkan path lengkap: `/home/cekrek/.virtualenvs/survey-env`
   - Klik tanda centang biru (OK). PythonAnywhere akan memvalidasi path tersebut.

---

### Langkah 5: Konfigurasi File WSGI

1. Masih di tab **Web**, cari bagian **Code** -> **WSGI configuration file**.
2. Klik link file berwarna biru: `/var/www/cekrek_pythonanywhere_com_wsgi.py`.
3. Editor file berbasis web akan terbuka.
4. Hapus seluruh isi default file tersebut (*Select All* lalu *Delete*).
5. Salin dan tempel (*Paste*) kode konfigurasi berikut:

```python
import sys
import os

# 1. Tambahkan path folder proyek ke sys.path
project_home = '/home/cekrek/survey-yankes-2026'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 2. Atur working directory
os.chdir(project_home)

# 3. Impor instance Flask app sebagai 'application'
from app import app as application
```

6. Klik tombol hijau **Save** di pojok kanan atas halaman.
7. Klik tombol panah kembali atau klik tab **Web** untuk kembali ke halaman web app.

---

### Langkah 6: Konfigurasi Pemetaan File Statis (Static Files)

Agar file stylesheet CSS kustom (`custom.css`) dan skrip form (`survey.js`) dimuat secara instan oleh server Nginx PythonAnywhere:

1. Pada tab **Web**, gulir ke bagian **Static files:**
2. Klik baris **Enter URL**:
   - Ketik: `/static/`
3. Klik pada kolom **Directory** yang sejajar:
   - Ketik: `/home/cekrek/survey-yankes-2026/static/`
4. Klik tanda centang biru untuk menyimpan.

---

### Langkah 7: Aktifkan "Force HTTPS" (WAJIB untuk GPS)

> [!IMPORTANT]
> **Krusial untuk Fitur GPS Geofencing**:  
> Browser seluler (Google Chrome di Android, Safari di iOS/iPhone, dan Microsoft Edge di PC) **memblokir penuh** sensor HTML5 Geolocation (`navigator.geolocation`) jika situs diakses melalui HTTP biasa tanpa sertifikat SSL/TLS.

1. Masih pada tab **Web**, gulir ke bawah menuju bagian **Security**.
2. Cari toggle **Force HTTPS**.
3. Ubah statusnya menjadi **Enabled / ON**.  
   *(PythonAnywhere otomatis menyediakan sertifikat SSL gratis untuk subdomain `cekrek.pythonanywhere.com`).*

---

### Langkah 8: Reload Web App & Uji Coba

1. Gulir kembali ke bagian paling atas tab **Web**.
2. Klik tombol hijau besar **"Reload cekrek.pythonanywhere.com"**.
3. Buka tab baru di browser Anda dan kunjungi:  
   👉 **`https://cekrek.pythonanywhere.com`**

#### 🧪 Checklist Verifikasi Langsung:
- [ ] **Tampilan Survei:** Halaman survei 5-langkah muncul dengan styling Tailwind teal/emerald yang rapi.
- [ ] **Izin GPS:** Browser meminta dialog *“cekrek.pythonanywhere.com wants to use your location”*. Klik **Allow / Izinkan**.
- [ ] **Deteksi Koordinat:** Kartu GPS menampilkan koordinat Lintang & Bujur perangkat serta jarak ke Puskesmas.
- [ ] **Pengiriman Data:** Lengkapi satu formulir uji coba dan klik Kirim Survei. Pastikan pop-up sukses muncul.
- [ ] **Dashboard Admin:** Akses `https://cekrek.pythonanywhere.com/login`, masukkan username & password yang Anda atur di `.env`. Pastikan grafik Chart.js dan data responden uji coba muncul di tabel.
- [ ] **Ekspor CSV & Backup:** Klik tombol **Ekspor CSV** dan **Backup DB (.db)** di dashboard untuk memastikan file berhasil diunduh.

---

### Langkah 9: Penjadwalan Backup Mingguan (Scheduled Task)

Aplikasi CeKReK dilengkapi skrip otomatis `cron_backup_reminder.py` untuk memantau rutinitas pencadangan database.

1. Buka tab **Tasks** pada navigasi atas PythonAnywhere.
2. Di bagian **Schedule a task**:
   - Atur waktu eksekusi harian, misal: `01:00` UTC (pukul 08:00 WIB).
   - Pada kolom **Command**, masukkan perintah berikut:
     ```bash
     /home/cekrek/.virtualenvs/survey-env/bin/python /home/cekrek/survey-yankes-2026/cron_backup_reminder.py
     ```
3. Klik tombol **Create**.

---

## 🔄 Pembaruan Kode di Masa Depan (Update / Maintenance)

Jika terdapat perbaikan kode, penambahan fitur baru, atau sinkronisasi commit dari GitHub di masa depan:

1. Buka tab **Consoles** -> **Bash** di PythonAnywhere.
2. Jalankan perintah singkat berikut:
   ```bash
   cd ~/survey-yankes-2026
   git pull origin main
   ```
3. Masuk ke tab **Web**, lalu klik **Reload cekrek.pythonanywhere.com**.
4. Aplikasi akan langsung terbarui secara *live* tanpa *downtime* yang berarti.
