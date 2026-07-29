# Sistem Manajemen Evakuasi Bencana dan Pengungsian

Proyek ini dibangun untuk memenuhi kriteria:
1. **Pola Desain Wajib**: Observer Pattern.
2. **Inheritance**: WargaTerdampak (superclass) -> Anak, Dewasa, Lansia (subclass).
3. **Polymorphism**: Overriding `hitung_prioritas_evakuasi()`.
4. **Encapsulation**: Atribut `__kondisi_kesehatan` dan `__posko_id` privat menggunakan setter dengan validasi.
5. **Exception Handling**: `KapasitasPoskoPenuhError` dan `DataKesehatanTidakValidError`.
6. **File Handling**: Penyimpanan persisten warga.json, posko.json, distribusi_bantuan.csv, dan export TXT.
7. **Prinsip SOLID**: Single Responsibility Principle (SRP) diterapkan pada `DataManager`.
8. **GUI**: Menggunakan Tkinter.

## Kebutuhan Sistem
- Python 3.11 atau lebih baru
- `pytest` (Hanya untuk menjalankan unit tests)

## Cara Instalasi
1. Pastikan Anda memiliki Python 3.11+
2. Install pytest (opsional untuk testing):
   ```bash
   pip install -r requirements.txt
   ```

## Cara Menjalankan Aplikasi
Buka terminal dan jalankan:
```bash
python main.py
```

## Skenario Demonstrasi GUI

### 1. Skenario Normal (Berhasil)
1. Buka tab "Kelola Warga".
2. Masukkan ID: `W004`, Nama: `Bagas`, Usia: `12`, Tipe: `Anak`, Kondisi: `Sehat`, Bahaya: `Sedang`.
3. Klik "Simpan Warga". Warga berhasil ditambahkan ke tabel di bawah.
4. Buka tab "Posko & Evakuasi". Bagas akan muncul di "Antrean Prioritas".
5. Pilih Bagas, pilih posko "Posko SDN 1", klik "Evakuasi Warga Terpilih". Kapasitas posko SDN 1 akan bertambah.

### 2. Skenario Kesalahan 1: Custom Exception `DataKesehatanTidakValidError`
1. Buka tab "Kelola Warga".
2. Masukkan input acak untuk warga baru.
3. Pada dropdown **Kondisi**, pilih "SalahKondisi(Testing Exception)".
4. Klik "Simpan Warga".
5. Muncul popup Error yang menangkap Exception: "Kondisi kesehatan tidak valid: 'SalahKondisi(Testing Exception)'. Gunakan: 'Sehat', 'Sakit Ringan', 'Sakit Parah'". Data dibatalkan/tidak disimpan (Validasi Encapsulation bekerja).

### 3. Skenario Kesalahan 2: Custom Exception `KapasitasPoskoPenuhError` (Observer Pattern beraksi)
1. Buka tab "Posko & Evakuasi".
2. Pada data awal, `Posko Balai Desa` (P001) sengaja disetting agar batas kritisnya = 45 dan maksimal = 50. Untuk demo cepat agar penuh, mari edit file `data/posko.json`.
3. Ubah `kapasitas_terisi` P001 menjadi `50` (Penuh). Lalu jalankan ulang aplikasi.
4. Coba evakuasi salah satu warga dari antrean prioritas ke `Posko Balai Desa`.
5. Aplikasi akan menampilkan popup Error Exception: "Posko sudah mencapai kapasitas maksimal (ID: P001)". Proses evakuasi dibatalkan.
6. (Untuk melihat Observer): Coba ubah `kapasitas_terisi` menjadi 49, jalankan aplikasi, evakuasi 1 orang. Observer (Relawan/GUI) akan pop-up peringatan bahwa kapasitas kritis telah tercapai.
