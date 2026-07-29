from src.utils.observer import Subject, Observer
from src.utils.exceptions import KapasitasPoskoPenuhError
from src.models.warga import WargaTerdampak

class Posko(Subject):
    def __init__(self, id_posko: str, nama: str, kapasitas_maksimal: int, 
                 stok_bantuan: int, batas_kritis_kapasitas: int, batas_kritis_stok: int, wilayah: str, kapasitas_terisi: int = 0):
        super().__init__()
        self.id_posko = id_posko
        self.nama = nama
        self.wilayah = wilayah
        self.kapasitas_maksimal = kapasitas_maksimal
        self.kapasitas_terisi = kapasitas_terisi
        self.stok_bantuan = stok_bantuan
        self.batas_kritis_kapasitas = batas_kritis_kapasitas
        self.batas_kritis_stok = batas_kritis_stok

    def cek_kondisi_kritis(self):
        """Memeriksa apakah perlu memicu notifikasi ke observer"""
        if self.kapasitas_terisi >= self.batas_kritis_kapasitas:
            self.notify(f"PERINGATAN: Posko {self.nama} ({self.id_posko}) mendekati/mencapai kapasitas maksimal! ({self.kapasitas_terisi}/{self.kapasitas_maksimal})")
            
        if self.stok_bantuan <= self.batas_kritis_stok:
            self.notify(f"PERINGATAN: Stok bantuan di Posko {self.nama} ({self.id_posko}) menipis! (Sisa: {self.stok_bantuan})")

    def tambah_warga(self, warga: WargaTerdampak):
        if self.kapasitas_terisi >= self.kapasitas_maksimal:
            raise KapasitasPoskoPenuhError(self.id_posko)
        
        self.kapasitas_terisi += 1
        warga.posko_id = self.id_posko
        self.cek_kondisi_kritis()

    def kurangi_warga(self, warga: WargaTerdampak):
        if self.kapasitas_terisi > 0 and warga.posko_id == self.id_posko:
            self.kapasitas_terisi -= 1
            warga.posko_id = None
            
    def tambah_bantuan(self, jumlah: int):
        self.stok_bantuan += jumlah
        
    def kurangi_bantuan(self, jumlah: int):
        if self.stok_bantuan >= jumlah:
            self.stok_bantuan -= jumlah
            self.cek_kondisi_kritis()
            return True
        return False

    def to_dict(self):
        return {
            "id": self.id_posko,
            "nama": self.nama,
            "wilayah": self.wilayah,
            "kapasitas_maksimal": self.kapasitas_maksimal,
            "kapasitas_terisi": self.kapasitas_terisi,
            "stok_bantuan": self.stok_bantuan,
            "batas_kritis_kapasitas": self.batas_kritis_kapasitas,
            "batas_kritis_stok": self.batas_kritis_stok
        }

class Relawan(Observer):
    """
    Kelas Observer untuk menerima notifikasi dari Posko.
    """
    def __init__(self, nama: str):
        self.nama = nama
        self.notifikasi_diterima = []

    def update(self, message: str):
        pesan = f"[Notifikasi Relawan {self.nama}] {message}"
        self.notifikasi_diterima.append(pesan)
        print(pesan) # Print untuk keperluan CLI/Demonstrasi
