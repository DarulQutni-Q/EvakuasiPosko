from src.services.data_manager import DataManager
from src.models.warga import Anak, Dewasa, Lansia
from src.models.posko import Posko, Relawan
import datetime

class EvakuasiSystem:
    def __init__(self, data_manager: DataManager = None):
        self.data_manager = data_manager or DataManager()
        self.daftar_warga = self.data_manager.load_warga()
        self.daftar_posko = self.data_manager.load_posko()
        self.relawan_terdaftar = []
        
        # Attach relawan default ke setiap posko yang diload
        relawan_default = Relawan("Koordinator Utama")
        self.register_relawan(relawan_default)

    def register_relawan(self, relawan: Relawan):
        self.relawan_terdaftar.append(relawan)
        for posko in self.daftar_posko:
            posko.attach(relawan)

    def tambah_warga_baru(self, nama, usia, jenis_kelamin, tipe, kondisi_kesehatan, tingkat_bahaya):
        # Auto-increment ID Warga
        if not self.daftar_warga:
            id_warga = "W001"
        else:
            # Ambil ID terakhir, hilangkan karakter 'W', tambah 1, lalu format ulang
            last_id = self.daftar_warga[-1].id_warga
            try:
                num = int(last_id.replace("W", ""))
                id_warga = f"W{num+1:03d}"
            except ValueError:
                id_warga = f"W{len(self.daftar_warga)+1:03d}"

        warga = None
        if tipe == "Anak":
            warga = Anak(id_warga, nama, usia, jenis_kelamin, kondisi_kesehatan, tingkat_bahaya)
        elif tipe == "Lansia":
            warga = Lansia(id_warga, nama, usia, jenis_kelamin, kondisi_kesehatan, tingkat_bahaya)
        else:
            warga = Dewasa(id_warga, nama, usia, jenis_kelamin, kondisi_kesehatan, tingkat_bahaya)
            
        self.daftar_warga.append(warga)
        self.data_manager.save_warga(self.daftar_warga)
        return warga

    def update_warga(self, id_warga, nama, usia, jenis_kelamin, tipe, kondisi_kesehatan, tingkat_bahaya):
        id_warga_str = str(id_warga)
        idx = next((i for i, w in enumerate(self.daftar_warga) if str(w.id_warga) == id_warga_str), None)
        if idx is None:
            raise ValueError(f"Warga dengan ID {id_warga_str} tidak ditemukan.")
            
        warga_lama = self.daftar_warga[idx]
        posko_id_lama = warga_lama.posko_id
        
        # Buat instansiasi ulang jika tipe berubah, jika tidak cukup update
        if warga_lama.__class__.__name__ != tipe:
            if tipe == "Anak":
                warga_baru = Anak(id_warga_str, nama, usia, jenis_kelamin, kondisi_kesehatan, tingkat_bahaya)
            elif tipe == "Lansia":
                warga_baru = Lansia(id_warga_str, nama, usia, jenis_kelamin, kondisi_kesehatan, tingkat_bahaya)
            else:
                warga_baru = Dewasa(id_warga_str, nama, usia, jenis_kelamin, kondisi_kesehatan, tingkat_bahaya)
            warga_baru.posko_id = posko_id_lama
            self.daftar_warga[idx] = warga_baru
        else:
            warga_lama.nama = nama
            warga_lama.usia = usia
            warga_lama.jenis_kelamin = jenis_kelamin
            warga_lama.kondisi_kesehatan = kondisi_kesehatan
            warga_lama.tingkat_bahaya = tingkat_bahaya
            
        self.data_manager.save_warga(self.daftar_warga)

    def hapus_warga(self, id_warga):
        # Konversi ke string untuk memastikan perbandingan yang konsisten
        id_warga_str = str(id_warga)
        warga = next((w for w in self.daftar_warga if str(w.id_warga) == id_warga_str), None)
        if not warga:
            raise ValueError(f"Warga dengan ID {id_warga_str} tidak ditemukan.")
            
        if warga.posko_id:
            posko = self.get_posko_by_id(warga.posko_id)
            if posko:
                posko.kurangi_warga(warga)
                self.data_manager.save_posko(self.daftar_posko)
                
        self.daftar_warga.remove(warga)
        self.data_manager.save_warga(self.daftar_warga)

    def tambah_posko_baru(self, nama, wilayah, kapasitas_maksimal, stok_bantuan, batas_kritis_kapasitas, batas_kritis_stok):
        # Auto-increment ID Posko
        if not self.daftar_posko:
            id_posko = "P001"
        else:
            last_id = self.daftar_posko[-1].id_posko
            try:
                num = int(last_id.replace("P", ""))
                id_posko = f"P{num+1:03d}"
            except ValueError:
                id_posko = f"P{len(self.daftar_posko)+1:03d}"
                
        posko = Posko(id_posko, nama, kapasitas_maksimal, stok_bantuan, batas_kritis_kapasitas, batas_kritis_stok, wilayah)
        self.daftar_posko.append(posko)
        
        # Attach relawan yang sudah terdaftar ke posko baru
        for relawan in self.relawan_terdaftar:
            posko.attach(relawan)
            
        self.data_manager.save_posko(self.daftar_posko)
        return posko

    def update_posko(self, id_posko, nama, wilayah, kapasitas_maksimal, stok_bantuan, batas_kritis_kapasitas, batas_kritis_stok):
        posko = self.get_posko_by_id(id_posko)
        if not posko:
            raise ValueError(f"Posko dengan ID {id_posko} tidak ditemukan.")
            
        if kapasitas_maksimal < posko.kapasitas_terisi:
            raise ValueError(f"Kapasitas maksimal tidak boleh lebih kecil dari kapasitas terisi saat ini ({posko.kapasitas_terisi}).")
            
        posko.nama = nama
        posko.wilayah = wilayah
        posko.kapasitas_maksimal = kapasitas_maksimal
        posko.stok_bantuan = stok_bantuan
        posko.batas_kritis_kapasitas = batas_kritis_kapasitas
        posko.batas_kritis_stok = batas_kritis_stok
        
        posko.cek_kondisi_kritis()
        self.data_manager.save_posko(self.daftar_posko)
        
    def hapus_posko(self, id_posko):
        posko = self.get_posko_by_id(id_posko)
        if not posko:
            raise ValueError("Posko tidak ditemukan.")
            
        if posko.kapasitas_terisi > 0:
            raise ValueError("Posko tidak dapat dihapus karena masih ada pengungsi di dalamnya. Pindahkan pengungsi terlebih dahulu.")
            
        self.daftar_posko.remove(posko)
        self.data_manager.save_posko(self.daftar_posko)

    def get_posko_by_id(self, posko_id):
        for p in self.daftar_posko:
            if p.id_posko == posko_id:
                return p
        return None

    def evakuasi_warga(self, warga_id, posko_id):
        warga = next((w for w in self.daftar_warga if w.id_warga == warga_id), None)
        posko = self.get_posko_by_id(posko_id)
        
        if not warga:
            raise ValueError(f"Warga dengan ID {warga_id} tidak ditemukan.")
        if not posko:
            raise ValueError(f"Posko dengan ID {posko_id} tidak ditemukan.")
            
        # Jika warga sudah di posko lain, kurangi dari posko lama
        if warga.posko_id:
            posko_lama = self.get_posko_by_id(warga.posko_id)
            if posko_lama:
                posko_lama.kurangi_warga(warga)

        # Proses menambahkan ke posko baru (bisa raise KapasitasPoskoPenuhError)
        posko.tambah_warga(warga)
        
        # Save perubahan
        self.data_manager.save_warga(self.daftar_warga)
        self.data_manager.save_posko(self.daftar_posko)
        return True

    def distribusikan_bantuan(self, posko_id, jenis_bantuan, jumlah, keterangan):
        posko = self.get_posko_by_id(posko_id)
        if not posko:
            raise ValueError(f"Posko dengan ID {posko_id} tidak ditemukan.")
            
        posko.tambah_bantuan(jumlah)
        
        id_dist = f"D{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        tanggal = datetime.datetime.now().strftime("%Y-%m-%d")
        
        self.data_manager.add_distribusi(id_dist, tanggal, posko_id, jenis_bantuan, jumlah, keterangan)
        self.data_manager.save_posko(self.daftar_posko)

    def kurangi_bantuan_posko(self, posko_id, jumlah):
        posko = self.get_posko_by_id(posko_id)
        if not posko:
            raise ValueError("Posko tidak ditemukan.")
        berhasil = posko.kurangi_bantuan(jumlah)
        if berhasil:
            self.data_manager.save_posko(self.daftar_posko)
        return berhasil

    def dapatkan_daftar_prioritas(self):
        """Mengurutkan warga berdasarkan prioritas evakuasi tertinggi dan belum ada di posko"""
        warga_belum_evakuasi = [w for w in self.daftar_warga if not w.posko_id]
        
        # Urutkan berdasarkan polymorphism method hitung_prioritas_evakuasi()
        # Descending (nilai tertinggi di atas)
        warga_belum_evakuasi.sort(key=lambda w: w.hitung_prioritas_evakuasi(), reverse=True)
        return warga_belum_evakuasi

    def get_preview_laporan(self):
        jumlah_pengungsi = len([w for w in self.daftar_warga if w.posko_id is not None])
        kebutuhan_belum_terpenuhi = len([w for w in self.daftar_warga if w.posko_id is None])
        
        rekap_wilayah = {}
        for p in self.daftar_posko:
            if p.wilayah not in rekap_wilayah:
                rekap_wilayah[p.wilayah] = {"kapasitas_total": 0, "terisi": 0, "posko_count": 0}
            rekap_wilayah[p.wilayah]["kapasitas_total"] += p.kapasitas_maksimal
            rekap_wilayah[p.wilayah]["terisi"] += p.kapasitas_terisi
            rekap_wilayah[p.wilayah]["posko_count"] += 1
            
        riwayat_distribusi = self.data_manager.load_distribusi()
        total_bantuan_didistribusikan = sum(int(d['jumlah']) for d in riwayat_distribusi) if riwayat_distribusi else 0

        laporan = "=== LAPORAN MANAJEMEN EVAKUASI BENCANA ===\n"
        laporan += f"Tanggal Laporan: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        laporan += "1. RINGKASAN UMUM\n"
        laporan += f"   - Total Warga Terdampak: {len(self.daftar_warga)}\n"
        laporan += f"   - Jumlah Pengungsi (Sudah Dievakuasi): {jumlah_pengungsi}\n"
        laporan += f"   - Kebutuhan Belum Terpenuhi (Belum Dievakuasi): {kebutuhan_belum_terpenuhi}\n"
        laporan += f"   - Total Bantuan Didistribusikan: {total_bantuan_didistribusikan} unit\n\n"
        
        laporan += "2. KAPASITAS POSKO PER WILAYAH\n"
        for wilayah, data in rekap_wilayah.items():
            laporan += f"   - Wilayah {wilayah}:\n"
            laporan += f"     Jumlah Posko: {data['posko_count']}\n"
            laporan += f"     Kapasitas Terisi: {data['terisi']} / {data['kapasitas_total']}\n"
        laporan += "\n"
        
        laporan += "3. DETAIL POSKO\n"
        for p in self.daftar_posko:
            laporan += f"   - {p.nama} (ID: {p.id_posko}, Wilayah: {p.wilayah})\n"
            laporan += f"     Kapasitas: {p.kapasitas_terisi}/{p.kapasitas_maksimal}\n"
            laporan += f"     Stok Bantuan: {p.stok_bantuan} unit\n\n"
            
        laporan += "4. DAFTAR PRIORITAS EVAKUASI (Belum Dievakuasi)\n"
        prioritas = self.dapatkan_daftar_prioritas()
        if not prioritas:
            laporan += "   Semua warga telah dievakuasi.\n"
        else:
            for i, w in enumerate(prioritas, 1):
                laporan += f"   {i}. {w.nama} (Usia: {w.usia}, Tipe: {w.__class__.__name__})\n"
                laporan += f"      Kesehatan: {w.kondisi_kesehatan}, Skor Prioritas: {w.hitung_prioritas_evakuasi()}\n"
                
        return laporan, jumlah_pengungsi, kebutuhan_belum_terpenuhi, rekap_wilayah, total_bantuan_didistribusikan

    def ekspor_laporan_txt(self):
        laporan, _, _, _, _ = self.get_preview_laporan()
        return self.data_manager.buat_laporan_txt(laporan)
        
    def ekspor_laporan_csv(self):
        _, jumlah_pengungsi, kebutuhan_belum_terpenuhi, rekap_wilayah, total_bantuan_didistribusikan = self.get_preview_laporan()
        
        headers_csv = ["Kategori", "Nilai"]
        data_csv = [
            ["Total Warga", len(self.daftar_warga)],
            ["Sudah Evakuasi", jumlah_pengungsi],
            ["Belum Evakuasi", kebutuhan_belum_terpenuhi],
            ["Total Posko", len(self.daftar_posko)],
            ["Total Bantuan Didistribusikan", total_bantuan_didistribusikan]
        ]
        for wilayah, data in rekap_wilayah.items():
            data_csv.append([f"Kapasitas Wilayah {wilayah}", f"{data['terisi']}/{data['kapasitas_total']}"])
            
        return self.data_manager.buat_laporan_csv(data_csv, headers_csv, "ringkasan_evakuasi.csv")
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      