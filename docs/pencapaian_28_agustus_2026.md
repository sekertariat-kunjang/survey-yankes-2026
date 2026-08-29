# Dokumentasi Pencapaian Pengembangan Aplikasi CeKReK
**Tanggal:** 28 Agustus 2026  
**Status Proyek:** Siap Digunakan / Teruji (Beta)

---

## 📋 Latar Belakang & Deskripsi
Aplikasi **CeKReK** (*Cek langsung Kondisi dan buktikan layanan Puskesmas sudah sesuai dengan standaR Kesehatan*) adalah sistem survei kesehatan digital multi-step yang dirancang untuk melakukan evaluasi dan pemantauan standar mutu pelayanan Puskesmas Kabupaten secara *real-time*. Proyek ini dibangun menggunakan kombinasi backend **Python (Flask)**, database **SQLite**, dan frontend yang estetis menggunakan **Tailwind CSS**.

---

## 🚀 Fitur Utama & Pencapaian Hari Ini

### 1. Backend & Manajemen Data (Python & SQLite)
- **Database Relasional:** Membuat file database `survey.db` dengan tabel `responses` yang menampung seluruh jawaban survei, teks penjelasan dinamis, serta metadata pelacakan GPS.
- **Kalkulasi Metrik Mutu (Compliance Index):** 
  - Backend menghitung **Kepatuhan Global** penilai berbasis rata-rata tertimbang: 50% dari jawaban Ya/Tidak, dan 50% dari kelengkapan checklist pelayanan prima.
  - Perhitungan statistik kepatuhan spesifik untuk tiap ruangan layanan (Poli Rawat Jalan, Laboratorium, Farmasi/Apotek, dan Unit Informasi/Keluhan).
- **Ekspor Laporan (Pandas CSV):** Implementasi endpoint `/export` untuk mengunduh seluruh data survei dalam format `.csv` dengan penataan kolom checklist yang mudah dibaca.

### 2. Antarmuka Pengguna Multi-Step yang Estetis (Tailwind CSS)
- **Desain Premium (Glassmorphic UI):** Desain modern menggunakan warna bertema medis (Teal & Emerald), latar belakang gradien halus, efek transparansi kaca, dan tipografi dari *Outfit* & *Inter* Google Fonts.
- **Formulir Alur 5-Langkah:**
  1. **Langkah 1 (Identitas & Lokasi):** Input nama observer, waktu, tanggal, dan pemilihan 37 Puskesmas secara interaktif.
  2. **Langkah 2 (Poli Rawat Jalan):** Evaluasi kenyamanan poli, privasi ruang dokter, checklist 10 pelayanan prima, dan waktu tunggu poli.
  3. **Langkah 3 (Laboratorium):** Kebersihan, ketersediaan kursi tunggu, dan checklist 8 pelayanan prima lab.
  4. **Langkah 4 (Farmasi):** Kebersihan, kursi tunggu, ketersediaan obat, checklist 12 pelayanan prima farmasi, dan waktu tunggu obat jadi/racikan.
  5. **Langkah 5 (Informasi & Keluhan):** Evaluasi loket keluhan, petugas pemberi info, dan checklist 8 tindakan pelayanan prima pengaduan.
- **Input Dinamis & Interaktif:** 
  - Tombol pilihan Ya/Tidak dirancang sebagai kartu khusus yang menyala saat aktif.
  - Kolom teks penjelasan (*textarea*) otomatis slide terbuka dan bersifat wajib (*required*) **hanya** jika penilai memilih opsi "Tidak" atau "Lainnya".
  - Dilengkapi fitur pencarian instan (*real-time filter*) untuk mencari nama Puskesmas pada grid pilihan.

### 3. Validasi Lokasi Berbasis GPS (Geofencing - Opsi B)
- **Deteksi Posisi Real-time:** Memanfaatkan HTML5 Geolocation API untuk meminta koordinat Latitude & Longitude perangkat penilai saat formulir dibuka.
- **Perhitungan Rumus Haversine:** Menghitung jarak lurus (meter/kilometer) secara presisi antara koordinat penilai dengan koordinat 37 lokasi Puskesmas terdaftar di Kabupaten Kediri.
- **Verifikasi Lokasi & Kebijakan Validasi:**
  - **GPS Terverifikasi:** Jika jarak penilai ≤ 300 meter dari Puskesmas, sistem otomatis mencentang nama Puskesmas tersebut di formulir dan mengunci statusnya menjadi hijau (*Verified*).
  - **Fallback Manual:** Jika di luar radius 300m atau GPS tidak aktif/tidak diizinkan, penilai tetap diperbolehkan memilih Puskesmas secara manual (fleksibel). Jarak rill dan koordinat GPS mereka tetap direkam untuk proses transparansi audit data.
  - **Pembaruan Jarak Dinamis:** Jika penilai berada dalam mode manual dan memilih Puskesmas, jarak koordinat GPS mereka akan otomatis diperbarui dan disesuaikan terhadap Puskesmas yang mereka klik.

### 4. Panel Analitik (Dashboard Admin) & Visualisasi Chart.js
- **Kartu Metrik Utama:** Menampilkan Total Responden, Nilai Kepatuhan Global, serta skor kepatuhan per departemen.
- **Dua Grafik Interaktif:**
  - *Chart 1 (Doughnut):* Perbandingan tingkat kepatuhan antar unit pelayanan (Poli, Lab, Farmasi, Keluhan).
  - *Chart 2 (Bar Chart):* Distribusi jumlah laporan/responden yang masuk untuk masing-masing Puskesmas.
- **Tabel Detail & Pencarian:** Tabel daftar survei dengan fitur pencarian nama penilai atau nama Puskesmas.
- **Lencana Status Validasi GPS:** Menampilkan lencana visual di tabel:
  - *Terverifikasi GPS (Jarak dalam meter)* - Hijau
  - *Manual / Luar Radius (Jarak dalam kilometer)* - Oranye
  - *GPS Off / Tidak Aktif* - Abu-abu
- **Modal Popup Detail:** Klik detail baris tabel akan membuka jendela pop-up modern yang menampilkan jawaban lengkap responden, opsi checklist yang dipilih, keterangan detail "Tidak", serta blok metadata koordinat GPS.

---

## 🧪 Hasil Pengujian & Jaminan Kualitas

1. **Automated Unit Tests (`test_app.py`):**
   - Berhasil memvalidasi fungsionalitas server (kembalian status `200` pada `/` dan `/dashboard`).
   - Berhasil menguji simulasi kirim data survei (status `200` pada `/submit`) dengan payload data GPS lengkap.
   - Menguji kebenaran integrasi baris data di SQLite dan memvalidasi keakuratan ekspor file CSV.
   - Hasil pengujian: **`OK` (3/3 Tests Passed)**.

2. **Manual & Browser Subagent Testing:**
   - Formulir survei diuji menggunakan agen browser untuk pengisian berurutan, penanganan validasi input kosong, transisi halaman, kemunculan otomatis notifikasi modal sukses, dan pengalihan ke dashboard.
   - Memvalidasi keakuratan notifikasi visual status GPS dan detail modal di dashboard admin.

---

## 📂 Struktur File Workspace
```text
survey-yankes-2026/
├── app.py                     # Script backend Flask utama & Database logic
├── test_app.py                # File pengujian unit test backend
├── survey.db                  # Database lokal SQLite (dibuat otomatis)
├── survey_responses.csv       # File ekspor data CSV (dibuat otomatis saat ekspor)
├── docs/
│   └── pencapaian_28_agustus_2026.md  # File dokumentasi ini [NEW]
├── static/
│   ├── css/
│   │   └── custom.css         # Styling transisi form, glassmorphism, & lencana
│   └── js/
│      └── survey.js          # Logika navigasi form step, validasi, & rumus GPS Haversine
└── templates/
    ├── base.html              # Layout HTML dasar, fonts, & impor Tailwind
    ├── survey.html            # UI Formulir evaluasi 5-langkah
    └── dashboard.html         # Panel admin, grafik Chart.js, & modal detail
```
