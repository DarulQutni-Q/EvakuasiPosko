class KapasitasPoskoPenuhError(Exception):
    """Exception raised ketika posko sudah mencapai kapasitas maksimal."""
    def __init__(self, posko_id, message="Posko sudah mencapai kapasitas maksimal"):
        self.posko_id = posko_id
        self.message = f"{message} (ID: {posko_id})"
        super().__init__(self.message)

class DataKesehatanTidakValidError(ValueError):
    """Exception raised ketika input kondisi kesehatan tidak sesuai standar."""
    def __init__(self, kondisi_input, message="Kondisi kesehatan tidak valid"):
        self.kondisi_input = kondisi_input
        self.message = f"{message}: '{kondisi_input}'. Gunakan: 'Sehat', 'Sakit Ringan', 'Sakit Parah'"
        super().__init__(self.message)
