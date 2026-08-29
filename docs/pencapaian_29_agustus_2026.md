# Dokumentasi Pencapaian Pengembangan Aplikasi CeKReK
**Tanggal:** 29 Agustus 2026  
**Status Proyek:** Pengembangan & Pembaruan Presisi Fitur GPS (Beta)

---

## 📋 Latar Belakang & Deskripsi Pembaruan
Hari ini kami melakukan serangkaian pengujian operasional rill serta pembaruan fitur geolokasi GPS pada formulir survei **CeKReK** untuk meningkatkan presisi deteksi lokasi penilai (observer) di lapangan.

---

## 🚀 Fitur Utama & Pencapaian Hari Ini

### 1. Akurasi & Presisi Koordinat GPS (37 Puskesmas)
- **Survei Geocoding Berbasis Wilayah (Kediri):** Melakukan pemetaan ulang koordinat Lintang (Latitude) dan Bujur (Longitude) untuk seluruh 37 Puskesmas terdaftar menggunakan batasan wilayah geografis (*bounding box*) Kabupaten Kediri (`-8.20 s.d -7.50` LS dan `111.75 s.d 112.45` BT).
- **Hasil:** Menggantikan titik koordinat perkiraan kasar (dibulatkan 3 desimal sebelumnya) dengan koordinat presisi rill dari peta digital. Hal ini memastikan toleransi geofencing 300 meter dapat berfungsi dengan benar saat pengguna berada di titik lokasi fisik Puskesmas yang sebenarnya.
- **Pembaruan File Pemetaan:** Seluruh koordinat baru telah diintegrasikan langsung pada objek `PUSKESMAS_COORDS` di file [`static/js/survey.js`](file:///c:/Users/star/3D%20Objects/survey-yankes-2026/static/js/survey.js).

### 2. Peningkatan Transparansi Geofencing GPS di UI
- **Tampilan Koordinat Real-time:** Memperbarui fungsi kartu status GPS pada halaman survei agar menampilkan koordinat Latitude dan Longitude yang dibaca oleh browser secara langsung (misal: `GPS Anda: -7.250921, 112.770824`).
- **Tujuan:** Memberikan transparansi penuh kepada pengguna mengenai koordinat yang dilaporkan oleh perangkat mereka. Ini memudahkan diagnosis masalah apabila perangkat mendeteksi lokasi yang melenceng (misalnya di luar radius Puskesmas).

### 3. Diagnosis & Penanganan Limitasi Lokasi Browser (IP-based Geolocation)
- **Identifikasi Masalah:** Menyelidiki kendala deteksi lokasi di mana penilai secara fisik berada di Puskesmas Kunjang tetapi terdeteksi berjarak 66.62 km dari lokasi Puskesmas.
- **Penyebab:** Limitasi perangkat desktop/laptop atau ponsel tanpa modul GPS aktif/presisi tinggi yang mendeteksi lokasi berdasarkan *IP Address*. ISP seluler atau kabel di wilayah Kediri sering mengarahkan rute internet melalui *gateway* regional di **Surabaya** (~66 km dari Kunjang).
- **Validasi Fallback Manual:** Memastikan bahwa apabila terjadi ketidakakuratan deteksi browser ini, fitur **Fallback Manual** (memilih Puskesmas Kunjang secara manual dari daftar) tetap bekerja dengan baik untuk menjamin kelancaran pengisian survei.

---

## 📂 File yang Diperbarui
- [`static/js/survey.js`](file:///c:/Users/star/3D%20Objects/survey-yankes-2026/static/js/survey.js) - Pembaruan peta koordinat presisi 37 Puskesmas dan integrasi visualisasi koordinat GPS di UI.
- [`docs/pencapaian_29_agustus_2026.md`](file:///c:/Users/star/3D%20Objects/survey-yankes-2026/docs/pencapaian_29_agustus_2026.md) - Dokumentasi pencapaian hari ini. [NEW]
