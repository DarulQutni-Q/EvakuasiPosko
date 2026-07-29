from abc import ABC, abstractmethod
from src.utils.exceptions import DataKesehatanTidakValidError

class WargaTerdampak(ABC):
    """
    Superclass WargaTerdampak.
    Menunjukkan abstraksi dan Encapsulation.
    """
    KONDISI_VALID = ["Sehat", "Sakit Ringan", "Sakit Parah"]

    def __init__(self, id_warga: str, nama: str, usia: int, jenis_kelamin: str, kondisi_kesehatan: str, tingkat_bahaya: str):
        self.id_warga = id_warga
        self.nama = nama
        self.usia = usia
        self.jenis_kelamin = jenis_kelamin
        self.tingkat_bahaya = tingkat_bahaya
        
        # Atribut private untuk encapsulation
        self.__kondisi_kesehatan = None
        self.__posko_id = None
        
        # Trigger property setter
        self.kondisi_kesehatan = kondisi_kesehatan

    @property
    def kondisi_kesehatan(self) -> str:
        return self.__kondisi_kesehatan

    @kondisi_kesehatan.setter
    def kondisi_kesehatan(self, value: str):
        if value not in self.KONDISI_VALID:
            raise DataKesehatanTidakValidError(value)
        self.__kondisi_kesehatan = value

    @property
    def posko_id(self):
        return self.__posko_id

    @posko_id.setter
    def posko_id(self, posko_id):
        self.__posko_id = posko_id

    def _hitung_skor_kondisi(self) -> int:
        if self.__kondisi_kesehatan == "Sakit Parah":
            return 30
        elif self.__kondisi_kesehatan == "Sakit Ringan":
            return 15
        return 0
        
    def _hitung_skor_bahaya(self) -> int:
        if self.tingkat_bahaya == "Tinggi":
            return 20
        elif self.tingkat_bahaya == "Sedang":
            return 10
        return 0

    @abstractmethod
    def hitung_prioritas_evakuasi(self) -> int:
        """
        Method abstract yang akan di-override subclass (Polymorphism).
        Semakin tinggi nilai, semakin prioritas.
        """
        pass
    
    def to_dict(self):
        return {
            "id": self.id_warga,
            "nama": self.nama,
            "usia": self.usia,
            "jenis_kelamin": self.jenis_kelamin,
            "tipe": self.__class__.__name__,
            "kondisi_kesehatan": self.kondisi_kesehatan,
            "tingkat_bahaya_lokasi": self.tingkat_bahaya,
            "posko_id": self.posko_id
        }


class Anak(WargaTerdampak):
    """Subclass dari WargaTerdampak"""
    def hitung_prioritas_evakuasi(self) -> int:
        # Anak-anak mendapat base score tinggi (30) + skor kondisi + skor bahaya
        base_score = 30
        return base_score + self._hitung_skor_kondisi() + self._hitung_skor_bahaya()


class Dewasa(WargaTerdampak):
    """Subclass dari WargaTerdampak"""
    def hitung_prioritas_evakuasi(self) -> int:
        # Dewasa mendapat base score rendah (10) + skor kondisi + skor bahaya
        base_score = 10
        return base_score + self._hitung_skor_kondisi() + self._hitung_skor_bahaya()


class Lansia(WargaTerdampak):
    """Subclass dari WargaTerdampak"""
    def hitung_prioritas_evakuasi(self) -> int:
        # Lansia mendapat base score tertinggi (40) + skor kondisi + skor bahaya
        base_score = 40
        return base_score + self._hitung_skor_kondisi() + self._hitung_skor_bahaya()
