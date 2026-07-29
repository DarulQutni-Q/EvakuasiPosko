import json
import csv
import os
from src.models.warga import Anak, Dewasa, Lansia

class DataManager:
    """
    Class yang menerapkan Single Responsibility Principle (SRP).
    Hanya bertanggung jawab untuk membaca dan menulis data ke storage persisten.
    """
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.warga_file = os.path.join(self.data_dir, "warga.json")
        self.posko_file = os.path.join(self.data_dir, "posko.json")
        self.distribusi_file = os.path.join(self.data_dir, "distribusi_bantuan.csv")
        
        # Buat direktori jika belum ada
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self._inisialisasi_file_awal()

    def _inisialisasi_file_awal(self):
        """Membuat file JSON dan CSV dengan format dasar jika belum ada."""
        if not os.path.exists(self.warga_file):
            with open(self.warga_file, 'w') as f:
                json.dump([], f)
                
        if not os.path.exists(self.posko_file):
            with open(self.posko_file, 'w') as f:
                json.dump([], f)
                
        if not os.path.exists(self.distribusi_file):
            with open(self.distribusi_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["id_distribusi", "tanggal", "posko_id", "jenis_bantuan", "jumlah", "keterangan"])

    def load_warga(self):
        try:
            with open(self.warga_file, 'r') as f:
                data = json.load(f)
            
            warga_list = []
            for item in data:
                # Factory pattern sederhana berdasarkan tipe
                tipe = item.get("tipe")
                warga_obj = None
                
                # Get atribut dengan default value jika tidak ada (backward compatibility)
                jk = item.get("jenis_kelamin", "Tidak Diketahui")
                
                if tipe == "Anak":
                    warga_obj = Anak(item["id"], item["nama"], item["usia"], jk, item["kondisi_kesehatan"], item["tingkat_bahaya_lokasi"])
                elif tipe == "Lansia":
                    warga_obj = Lansia(item["id"], item["nama"], item["usia"], jk, item["kondisi_kesehatan"], item["tingkat_bahaya_lokasi"])
                else: # Default Dewasa
                    warga_obj = Dewasa(item["id"], item["nama"], item["usia"], jk, item["kondisi_kesehatan"], item["tingkat_bahaya_lokasi"])
                
                warga_obj.posko_id = item.get("posko_id")
                warga_list.append(warga_obj)
            return warga_list
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_warga(self, warga_list):
        data = [w.to_dict() for w in warga_list]
        with open(self.warga_file, 'w') as f:
            json.dump(data, f, indent=2)

    def load_posko(self):
        from src.models.posko import Posko
        try:
            with open(self.posko_file, 'r') as f:
                data = json.load(f)
            
            posko_list = []
            for item in data:
                p = Posko(
                    id_posko=item["id"],
                    nama=item["nama"],
                    wilayah=item.get("wilayah", "Tidak Diketahui"),
                    kapasitas_maksimal=item["kapasitas_maksimal"],
                    kapasitas_terisi=item["kapasitas_terisi"],
                    stok_bantuan=item["stok_bantuan"],
                    batas_kritis_kapasitas=item["batas_kritis_kapasitas"],
                    batas_kritis_stok=item["batas_kritis_stok"]
                )
                posko_list.append(p)
            return posko_list
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_posko(self, posko_list):
        data = [p.to_dict() for p in posko_list]
        with open(self.posko_file, 'w') as f:
            json.dump(data, f, indent=2)

    def load_distribusi(self):
        try:
            with open(self.distribusi_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except FileNotFoundError:
            return []

    def add_distribusi(self, id_distribusi, tanggal, posko_id, jenis_bantuan, jumlah, keterangan):
        with open(self.distribusi_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([id_distribusi, tanggal, posko_id, jenis_bantuan, jumlah, keterangan])

    def buat_laporan_txt(self, isi_laporan, filename="laporan_evakuasi.txt"):
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w') as f:
            f.write(isi_laporan)
        return filepath
        
    def buat_laporan_csv(self, data_list, headers, filename):
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data_list)
        return filepath
