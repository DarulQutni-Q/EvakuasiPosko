import unittest
import os
import json
from src.models.warga import Anak, Dewasa, Lansia
from src.models.posko import Posko, Relawan
from src.utils.exceptions import DataKesehatanTidakValidError, KapasitasPoskoPenuhError
from src.services.data_manager import DataManager

class TestEvakuasiBencana(unittest.TestCase):

    def setUp(self):
        # File sementara untuk testing file handling
        self.test_dir = "test_data"
        self.data_manager = DataManager(self.test_dir)

    def tearDown(self):
        # Hapus file setelah test
        for f in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, f))
        os.rmdir(self.test_dir)

    # 1. Test Inheritance & Normal Case
    def test_inisialisasi_warga(self):
        anak = Anak("W1", "Andi", 10, "Laki-laki", "Sehat", "Tinggi")
        self.assertEqual(anak.nama, "Andi")
        self.assertEqual(anak.kondisi_kesehatan, "Sehat")

    # 2. Test Polymorphism
    def test_polymorphism_prioritas(self):
        anak = Anak("W1", "Andi", 10, "Laki-laki", "Sehat", "Sedang") # Base 30 + (Sehat:0) + (Sedang:10) = 40
        dewasa = Dewasa("W2", "Budi", 30, "Laki-laki", "Sehat", "Sedang") # Base 10 + (Sehat:0) + (Sedang:10) = 20
        lansia = Lansia("W3", "Cici", 70, "Perempuan", "Sehat", "Sedang") # Base 40 + (Sehat:0) + (Sedang:10) = 50
        
        self.assertEqual(anak.hitung_prioritas_evakuasi(), 40)
        self.assertEqual(dewasa.hitung_prioritas_evakuasi(), 20)
        self.assertEqual(lansia.hitung_prioritas_evakuasi(), 50)
        
        # Polymorphism check: lansia harus lebih prioritas dari dewasa meski kondisi sama
        self.assertTrue(lansia.hitung_prioritas_evakuasi() > dewasa.hitung_prioritas_evakuasi())

    # 3. Test Encapsulation (Validasi Setter)
    def test_encapsulation_kondisi_valid(self):
        dewasa = Dewasa("W2", "Budi", 30, "Laki-laki", "Sehat", "Sedang")
        dewasa.kondisi_kesehatan = "Sakit Ringan" # Harus berhasil
        self.assertEqual(dewasa.kondisi_kesehatan, "Sakit Ringan")

    # 4. Test Custom Exception 1 (DataKesehatanTidakValidError)
    def test_exception_kesehatan_tidak_valid(self):
        dewasa = Dewasa("W2", "Budi", 30, "Laki-laki", "Sehat", "Sedang")
        with self.assertRaises(DataKesehatanTidakValidError):
            dewasa.kondisi_kesehatan = "Pusing Sedikit" # Invalid, harus raise error

    # 5. Test Penambahan Warga ke Posko (Batas Bawah/Normal)
    def test_tambah_warga_posko(self):
        posko = Posko("P1", "Posko A", 10, 100, 9, 20, "Utara")
        anak = Anak("W1", "Andi", 10, "Laki-laki", "Sehat", "Tinggi")
        
        posko.tambah_warga(anak)
        self.assertEqual(posko.kapasitas_terisi, 1)
        self.assertEqual(anak.posko_id, "P1")

    # 6. Test Custom Exception 2 (KapasitasPoskoPenuhError)
    def test_exception_posko_penuh(self):
        posko = Posko("P1", "Posko A", 1, 100, 1, 20, "Utara") # Max kapasitas hanya 1
        w1 = Dewasa("W1", "Budi", 30, "Laki-laki", "Sehat", "Tinggi")
        w2 = Dewasa("W2", "Cici", 30, "Perempuan", "Sehat", "Tinggi")
        
        posko.tambah_warga(w1) # Berhasil
        
        with self.assertRaises(KapasitasPoskoPenuhError):
            posko.tambah_warga(w2) # Kapasitas sudah 1 (maksimal), harus raise error

    # 7. Test Observer Pattern (Notifikasi batas kritis)
    def test_observer_notifikasi_kritis(self):
        posko = Posko("P1", "Posko A", 10, 100, 2, 20, "Utara") # Batas kritis kapasitas di 2
        relawan = Relawan("Relawan 1")
        posko.attach(relawan)
        
        w1 = Dewasa("W1", "Budi", 30, "Laki-laki", "Sehat", "Tinggi")
        w2 = Dewasa("W2", "Cici", 30, "Perempuan", "Sehat", "Tinggi")
        
        posko.tambah_warga(w1) # kapasitas = 1 (belum kritis)
        self.assertEqual(len(relawan.notifikasi_diterima), 0)
        
        posko.tambah_warga(w2) # kapasitas = 2 (mencapai batas kritis)
        self.assertEqual(len(relawan.notifikasi_diterima), 1)
        self.assertIn("mendekati/mencapai kapasitas maksimal", relawan.notifikasi_diterima[0])

    # 8. Test File Handling (JSON Persistence)
    def test_baca_tulis_file(self):
        w1 = Dewasa("W1", "Budi", 30, "Laki-laki", "Sehat", "Tinggi")
        self.data_manager.save_warga([w1])
        
        # Load kembali
        loaded_warga = self.data_manager.load_warga()
        self.assertEqual(len(loaded_warga), 1)
        self.assertEqual(loaded_warga[0].nama, "Budi")
        self.assertIsInstance(loaded_warga[0], Dewasa)

if __name__ == '__main__':
    unittest.main()
