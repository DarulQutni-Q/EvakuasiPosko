import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import font as tkfont
from src.services.evakuasi_system import EvakuasiSystem
from src.utils.exceptions import DataKesehatanTidakValidError, KapasitasPoskoPenuhError
from src.models.posko import Relawan

class EvakuasiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Manajemen Evakuasi Bencana")
        self.geometry("1000x700")
        
        # --- Besarkan Font +5 ---
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=default_font.cget("size") + 5)
        
        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(size=text_font.cget("size") + 5)
        
        heading_font = tkfont.nametofont("TkHeadingFont")
        heading_font.configure(size=heading_font.cget("size") + 5)
        
        # Konfigurasi gaya Treeview
        style = ttk.Style()
        style.configure("Treeview", font=default_font, rowheight=30)
        style.configure("Treeview.Heading", font=heading_font, font_weight="bold")

        self.system = EvakuasiSystem()
        
        # Mendaftarkan GUI sebagai relawan observer untuk menerima pesan di message box
        class GuiRelawan(Relawan):
            def __init__(self, root):
                super().__init__("Sistem GUI")
                self.root = root
                
            def update(self, message):
                super().update(message)
                messagebox.showwarning("Peringatan Posko!", message, parent=self.root)
                
        self.gui_relawan = GuiRelawan(self)
        self.system.register_relawan(self.gui_relawan)

        self.create_widgets()

    def create_widgets(self):
        # Notebook untuk tab
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Tab Warga
        self.tab_warga = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_warga, text="Kelola Warga")
        self.setup_tab_warga()

        # Tab Posko (Pengelolaan Posko Baru)
        self.tab_kelola_posko = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_kelola_posko, text="Kelola Posko")
        self.setup_tab_kelola_posko()

        # Tab Posko & Evakuasi
        self.tab_posko = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_posko, text="Proses Evakuasi")
        self.setup_tab_posko()
        
        # Tab Laporan
        self.tab_laporan = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_laporan, text="Laporan")
        self.setup_tab_laporan()

    def setup_tab_warga(self):
        # Frame Input
        input_frame = ttk.LabelFrame(self.tab_warga, text="Tambah / Edit Warga")
        input_frame.pack(fill='x', padx=10, pady=10)

        # Fields
        ttk.Label(input_frame, text="Nama:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.ent_nama = ttk.Entry(input_frame)
        self.ent_nama.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Usia:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.ent_usia = ttk.Entry(input_frame)
        self.ent_usia.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Gender:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.cb_gender = ttk.Combobox(input_frame, values=["Laki-laki", "Perempuan"], state="readonly")
        self.cb_gender.grid(row=1, column=1, padx=5, pady=5)
        self.cb_gender.current(0)

        ttk.Label(input_frame, text="Tipe:").grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.cb_tipe = ttk.Combobox(input_frame, values=["Anak", "Dewasa", "Lansia"], state="readonly")
        self.cb_tipe.grid(row=1, column=3, padx=5, pady=5)
        self.cb_tipe.current(1)

        ttk.Label(input_frame, text="Kondisi:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.cb_kondisi = ttk.Combobox(input_frame, values=["Sehat", "Sakit Ringan", "Sakit Parah", "SalahKondisi(Testing Exception)"], state="readonly")
        self.cb_kondisi.grid(row=2, column=1, padx=5, pady=5)
        self.cb_kondisi.current(0)

        ttk.Label(input_frame, text="Bahaya Lokasi:").grid(row=2, column=2, padx=5, pady=5, sticky='e')
        self.cb_bahaya = ttk.Combobox(input_frame, values=["Rendah", "Sedang", "Tinggi"], state="readonly")
        self.cb_bahaya.grid(row=2, column=3, padx=5, pady=5)
        self.cb_bahaya.current(1)

        btn_tambah = ttk.Button(input_frame, text="Simpan / Update Warga", command=self.simpan_warga)
        btn_tambah.grid(row=3, column=0, columnspan=4, pady=10)

        # Untuk menyimpan state saat edit
        self.editing_warga_id = None

        # Frame Tabel
        table_frame = ttk.Frame(self.tab_warga)
        table_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        columns = ('id', 'nama', 'gender', 'tipe', 'usia', 'kondisi', 'prioritas', 'posko')
        self.tree_warga = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree_warga.heading(col, text=col.capitalize())
            self.tree_warga.column(col, width=110)
            
        self.tree_warga.pack(expand=True, fill='both', side='left')
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_warga.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree_warga.configure(yscrollcommand=scrollbar.set)
        
        # Frame Action Buttons (Edit/Hapus)
        action_frame = ttk.Frame(self.tab_warga)
        action_frame.pack(fill='x', padx=10, pady=5)
        
        btn_edit = ttk.Button(action_frame, text="Edit Terpilih", command=self.load_warga_for_edit)
        btn_edit.pack(side='left', padx=5)
        
        btn_hapus = ttk.Button(action_frame, text="Hapus Terpilih", command=self.hapus_warga_terpilih)
        btn_hapus.pack(side='left', padx=5)
        
        btn_batal = ttk.Button(action_frame, text="Batal Edit", command=self.batal_edit_warga)
        btn_batal.pack(side='left', padx=5)
        
        self.refresh_table_warga()

    def setup_tab_kelola_posko(self):
        input_frame = ttk.LabelFrame(self.tab_kelola_posko, text="Tambah / Edit Posko")
        input_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(input_frame, text="Nama Posko:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.ent_posko_nama = ttk.Entry(input_frame)
        self.ent_posko_nama.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Wilayah:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.ent_posko_wilayah = ttk.Entry(input_frame)
        self.ent_posko_wilayah.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Kapasitas Maksimal:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.ent_posko_kapasitas = ttk.Entry(input_frame)
        self.ent_posko_kapasitas.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Stok Awal Bantuan:").grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.ent_posko_stok = ttk.Entry(input_frame)
        self.ent_posko_stok.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Batas Kritis Kapasitas:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.ent_posko_kritis_kapasitas = ttk.Entry(input_frame)
        self.ent_posko_kritis_kapasitas.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Batas Kritis Stok:").grid(row=2, column=2, padx=5, pady=5, sticky='e')
        self.ent_posko_kritis_stok = ttk.Entry(input_frame)
        self.ent_posko_kritis_stok.grid(row=2, column=3, padx=5, pady=5)

        btn_tambah_posko = ttk.Button(input_frame, text="Simpan / Update Posko", command=self.simpan_posko)
        btn_tambah_posko.grid(row=3, column=0, columnspan=4, pady=10)
        
        # State untuk edit
        self.editing_posko_id = None
        
        info_frame = ttk.LabelFrame(self.tab_kelola_posko, text="Daftar Posko Terdaftar")
        info_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        posko_cols = ('id', 'nama', 'wilayah', 'kapasitas', 'stok_bantuan')
        self.tree_kelola_posko = ttk.Treeview(info_frame, columns=posko_cols, show='headings')
        for col in posko_cols:
            self.tree_kelola_posko.heading(col, text=col.capitalize())
        self.tree_kelola_posko.pack(fill='both', expand=True, padx=5, pady=5)

        posko_action_frame = ttk.Frame(self.tab_kelola_posko)
        posko_action_frame.pack(fill='x', padx=10, pady=5)
        
        btn_edit_posko = ttk.Button(posko_action_frame, text="Edit Terpilih", command=self.load_posko_for_edit)
        btn_edit_posko.pack(side='left', padx=5)
        
        btn_hapus_posko = ttk.Button(posko_action_frame, text="Hapus Terpilih", command=self.hapus_posko_terpilih)
        btn_hapus_posko.pack(side='left', padx=5)
        
        btn_batal_posko = ttk.Button(posko_action_frame, text="Batal Edit", command=self.batal_edit_posko)
        btn_batal_posko.pack(side='left', padx=5)

    def setup_tab_posko(self):
        # Frame Tabel Prioritas
        prioritas_frame = ttk.LabelFrame(self.tab_posko, text="Antrean Prioritas (Belum Dievakuasi)")
        prioritas_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        cols = ('id', 'nama', 'prioritas', 'kondisi', 'tipe')
        self.tree_prioritas = ttk.Treeview(prioritas_frame, columns=cols, show='headings', height=5)
        for col in cols:
            self.tree_prioritas.heading(col, text=col.capitalize())
        self.tree_prioritas.pack(fill='both', expand=True, padx=5, pady=5)

        # Frame Evakuasi
        evak_frame = ttk.LabelFrame(self.tab_posko, text="Proses Evakuasi")
        evak_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(evak_frame, text="Pilih Posko Tujuan:").grid(row=0, column=0, padx=5, pady=5)
        self.cb_pilih_posko = ttk.Combobox(evak_frame, state="readonly", width=40)
        self.cb_pilih_posko.grid(row=0, column=1, padx=5, pady=5)
        
        btn_evakuasi = ttk.Button(evak_frame, text="Evakuasi Warga Terpilih", command=self.proses_evakuasi)
        btn_evakuasi.grid(row=0, column=2, padx=10, pady=5)

        # Frame Distribusi Bantuan
        dist_frame = ttk.LabelFrame(self.tab_posko, text="Distribusi Bantuan ke Posko")
        dist_frame.pack(fill='x', padx=10, pady=5)
        
        btn_distribusi = ttk.Button(dist_frame, text="Kirim Bantuan ke Posko Terpilih", command=self.proses_distribusi)
        btn_distribusi.pack(pady=10)

        # Frame Info Posko
        info_frame = ttk.LabelFrame(self.tab_posko, text="Status Posko")
        info_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        posko_cols = ('id', 'nama', 'wilayah', 'kapasitas', 'stok_bantuan')
        self.tree_posko = ttk.Treeview(info_frame, columns=posko_cols, show='headings')
        for col in posko_cols:
            self.tree_posko.heading(col, text=col.capitalize())
        self.tree_posko.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.refresh_tab_posko()

    def setup_tab_laporan(self):
        frame = ttk.Frame(self.tab_laporan)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.txt_laporan = tk.Text(frame, wrap='word', state=tk.DISABLED)
        self.txt_laporan.pack(fill='both', expand=True, side='left')
        
        scroll = ttk.Scrollbar(frame, orient='vertical', command=self.txt_laporan.yview)
        scroll.pack(side='right', fill='y')
        self.txt_laporan.configure(yscrollcommand=scroll.set)
        
        btn_frame = ttk.Frame(self.tab_laporan)
        btn_frame.pack(pady=10)
        
        btn_export_txt = ttk.Button(btn_frame, text="Ekspor ke TXT", command=self.export_txt)
        btn_export_txt.pack(side='left', padx=5)
        
        btn_export_csv = ttk.Button(btn_frame, text="Ekspor ke CSV", command=self.export_csv)
        btn_export_csv.pack(side='left', padx=5)
        
        # Bind event ketika tab laporan dibuka
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
    def on_tab_changed(self, event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        if tab_text == "Laporan":
            self.refresh_preview_laporan()

    def refresh_preview_laporan(self):
        try:
            laporan, _, _, _, _ = self.system.get_preview_laporan()
            self.txt_laporan.config(state=tk.NORMAL)
            self.txt_laporan.delete(1.0, tk.END)
            self.txt_laporan.insert(tk.END, laporan)
            self.txt_laporan.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat preview: {e}")

    # --- Actions ---
    def simpan_warga(self):
        nama = self.ent_nama.get()
        usia = self.ent_usia.get()
        gender = self.cb_gender.get()
        tipe = self.cb_tipe.get()
        kondisi = self.cb_kondisi.get()
        bahaya = self.cb_bahaya.get()

        if not nama or not usia:
            messagebox.showwarning("Input Error", "Mohon isi Nama dan Usia.")
            return

        try:
            usia = int(usia)
            if self.editing_warga_id:
                # Update
                self.system.update_warga(self.editing_warga_id, nama, usia, gender, tipe, kondisi, bahaya)
                messagebox.showinfo("Sukses", "Data Warga berhasil diperbarui.")
                self.batal_edit_warga()
            else:
                # Simpan Baru
                self.system.tambah_warga_baru(nama, usia, gender, tipe, kondisi, bahaya)
                messagebox.showinfo("Sukses", "Warga berhasil ditambahkan.")
                
            self.refresh_table_warga()
            self.refresh_tab_posko()
            
            # Clear inputs
            self.ent_nama.delete(0, tk.END)
            self.ent_usia.delete(0, tk.END)
        except ValueError as e:
            if isinstance(e, DataKesehatanTidakValidError):
                messagebox.showerror("Exception Tertangkap", str(e))
            else:
                messagebox.showerror("Error", str(e))

    def load_warga_for_edit(self):
        selected = self.tree_warga.selection()
        if not selected:
            messagebox.showwarning("Pilih Warga", "Silakan pilih warga dari tabel untuk diedit.")
            return
            
        warga_id = self.tree_warga.item(selected[0])['values'][0]
        warga = next((w for w in self.system.daftar_warga if str(w.id_warga) == str(warga_id)), None)
        
        if warga:
            self.editing_warga_id = warga_id
            self.ent_nama.delete(0, tk.END)
            self.ent_nama.insert(0, warga.nama)
            
            self.ent_usia.delete(0, tk.END)
            self.ent_usia.insert(0, str(warga.usia))
            
            self.cb_gender.set(getattr(warga, 'jenis_kelamin', 'Laki-laki'))
            self.cb_tipe.set(warga.__class__.__name__)
            self.cb_kondisi.set(warga.kondisi_kesehatan)
            self.cb_bahaya.set(warga.tingkat_bahaya)
            
    def hapus_warga_terpilih(self):
        selected = self.tree_warga.selection()
        if not selected:
            messagebox.showwarning("Pilih Warga", "Silakan pilih warga dari tabel untuk dihapus.")
            return
            
        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus warga ini?"):
            warga_id = self.tree_warga.item(selected[0])['values'][0]
            try:
                self.system.hapus_warga(warga_id)
                self.refresh_table_warga()
                self.refresh_tab_posko()
                self.batal_edit_warga() # Reset state
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_warga(self):
        try:
            filepath_csv = self.system.ekspor_data_warga_csv()
            messagebox.showinfo("Laporan Diekspor", f"Data Warga berhasil diekspor ke CSV:\n{filepath_csv}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekspor data warga: {e}")
                
    def batal_edit_warga(self):
        self.editing_warga_id = None
        self.ent_nama.delete(0, tk.END)
        self.ent_usia.delete(0, tk.END)
        self.cb_gender.current(0)
        self.cb_tipe.current(1)
        self.cb_kondisi.current(0)
        self.cb_bahaya.current(1)
                
    def simpan_posko(self):
        nama = self.ent_posko_nama.get()
        wilayah = self.ent_posko_wilayah.get()
        kapasitas = self.ent_posko_kapasitas.get()
        stok = self.ent_posko_stok.get()
        kritis_kapasitas = self.ent_posko_kritis_kapasitas.get()
        kritis_stok = self.ent_posko_kritis_stok.get()
        
        if not all([nama, wilayah, kapasitas, stok, kritis_kapasitas, kritis_stok]):
            messagebox.showwarning("Input Error", "Mohon isi semua field posko.")
            return
            
        try:
            if self.editing_posko_id:
                self.system.update_posko(self.editing_posko_id, nama, wilayah, int(kapasitas), int(stok), int(kritis_kapasitas), int(kritis_stok))
                messagebox.showinfo("Sukses", "Data Posko berhasil diperbarui.")
                self.batal_edit_posko()
            else:
                self.system.tambah_posko_baru(nama, wilayah, int(kapasitas), int(stok), int(kritis_kapasitas), int(kritis_stok))
                messagebox.showinfo("Sukses", "Posko berhasil ditambahkan.")
            
            # Clear inputs
            self.ent_posko_nama.delete(0, tk.END)
            self.ent_posko_wilayah.delete(0, tk.END)
            self.ent_posko_kapasitas.delete(0, tk.END)
            self.ent_posko_stok.delete(0, tk.END)
            self.ent_posko_kritis_kapasitas.delete(0, tk.END)
            self.ent_posko_kritis_stok.delete(0, tk.END)
            
            self.refresh_tab_posko()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def load_posko_for_edit(self):
        selected = self.tree_kelola_posko.selection()
        if not selected:
            messagebox.showwarning("Pilih Posko", "Silakan pilih posko dari tabel untuk diedit.")
            return
            
        posko_id = self.tree_kelola_posko.item(selected[0])['values'][0]
        posko = self.system.get_posko_by_id(posko_id)
        
        if posko:
            self.editing_posko_id = posko_id
            
            self.ent_posko_nama.delete(0, tk.END)
            self.ent_posko_nama.insert(0, posko.nama)
            
            self.ent_posko_wilayah.delete(0, tk.END)
            self.ent_posko_wilayah.insert(0, posko.wilayah)
            
            self.ent_posko_kapasitas.delete(0, tk.END)
            self.ent_posko_kapasitas.insert(0, str(posko.kapasitas_maksimal))
            
            self.ent_posko_stok.delete(0, tk.END)
            self.ent_posko_stok.insert(0, str(posko.stok_bantuan))
            
            self.ent_posko_kritis_kapasitas.delete(0, tk.END)
            self.ent_posko_kritis_kapasitas.insert(0, str(posko.batas_kritis_kapasitas))
            
            self.ent_posko_kritis_stok.delete(0, tk.END)
            self.ent_posko_kritis_stok.insert(0, str(posko.batas_kritis_stok))

    def hapus_posko_terpilih(self):
        selected = self.tree_kelola_posko.selection()
        if not selected:
            messagebox.showwarning("Pilih Posko", "Silakan pilih posko dari tabel untuk dihapus.")
            return
            
        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus posko ini?"):
            posko_id = self.tree_kelola_posko.item(selected[0])['values'][0]
            try:
                self.system.hapus_posko(posko_id)
                self.refresh_tab_posko()
                self.batal_edit_posko()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def batal_edit_posko(self):
        self.editing_posko_id = None
        self.ent_posko_nama.delete(0, tk.END)
        self.ent_posko_wilayah.delete(0, tk.END)
        self.ent_posko_kapasitas.delete(0, tk.END)
        self.ent_posko_stok.delete(0, tk.END)
        self.ent_posko_kritis_kapasitas.delete(0, tk.END)
        self.ent_posko_kritis_stok.delete(0, tk.END)

    def proses_evakuasi(self):
        selected = self.tree_prioritas.selection()
        if not selected:
            messagebox.showwarning("Pilih Warga", "Silakan pilih warga dari tabel prioritas.")
            return
            
        posko_str = self.cb_pilih_posko.get()
        if not posko_str:
            messagebox.showwarning("Pilih Posko", "Silakan pilih posko tujuan.")
            return
            
        warga_id = self.tree_prioritas.item(selected[0])['values'][0]
        posko_id = posko_str.split(" - ")[0]

        try:
            self.system.evakuasi_warga(warga_id, posko_id)
            messagebox.showinfo("Sukses", f"Warga dievakuasi ke {posko_str}")
            self.refresh_table_warga()
            self.refresh_tab_posko()
        except KapasitasPoskoPenuhError as e:
            messagebox.showerror("Exception Tertangkap", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def proses_distribusi(self):
        posko_str = self.cb_pilih_posko.get()
        if not posko_str:
            messagebox.showwarning("Pilih Posko", "Silakan pilih posko tujuan distribusi dari dropdown.")
            return
            
        posko_id = posko_str.split(" - ")[0]
        posko = self.system.get_posko_by_id(posko_id)
        
        jenis_bantuan = simpledialog.askstring("Distribusi Bantuan", "Jenis Bantuan (contoh: Makanan, Obat, Pakaian):")
        if not jenis_bantuan: return
        
        jumlah_str = simpledialog.askstring("Distribusi Bantuan", f"Jumlah {jenis_bantuan} yang dikirimkan:")
        if not jumlah_str: return
        
        try:
            jumlah = int(jumlah_str)
            if jumlah <= 0:
                raise ValueError("Jumlah bantuan harus lebih besar dari 0.")
                
            keterangan = simpledialog.askstring("Distribusi Bantuan", "Keterangan/Catatan tambahan:") or "-"
            
            self.system.distribusikan_bantuan(posko_id, jenis_bantuan, jumlah, keterangan)
            messagebox.showinfo("Sukses", f"Berhasil mendistribusikan {jumlah} {jenis_bantuan} ke {posko.nama}.")
            self.refresh_tab_posko()
        except ValueError as e:
            # Tampilkan pesan error custom jika ada dari kita (<= 0), atau default jika bukan angka
            error_msg = str(e) if str(e) == "Jumlah bantuan harus lebih besar dari 0." else "Jumlah harus berupa angka bulat."
            messagebox.showerror("Error", error_msg)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_txt(self):
        try:
            filepath_txt = self.system.ekspor_laporan_txt()
            messagebox.showinfo("Laporan Diekspor", f"Laporan TXT tersimpan di:\n{filepath_txt}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekspor laporan TXT: {e}")

    def export_csv(self):
        try:
            filepath_csv = self.system.ekspor_laporan_csv()
            messagebox.showinfo("Laporan Diekspor", f"Laporan CSV tersimpan di:\n{filepath_csv}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekspor laporan CSV: {e}")

    # --- Refreshes ---
    def refresh_table_warga(self):
        for i in self.tree_warga.get_children():
            self.tree_warga.delete(i)
            
        for w in self.system.daftar_warga:
            self.tree_warga.insert('', 'end', values=(
                w.id_warga, w.nama, getattr(w, 'jenis_kelamin', '-'), w.__class__.__name__, w.usia, 
                w.kondisi_kesehatan, w.hitung_prioritas_evakuasi(), w.posko_id or "Belum"
            ))

    def refresh_tab_posko(self):
        # Refresh Prioritas
        for i in self.tree_prioritas.get_children():
            self.tree_prioritas.delete(i)
        
        prioritas = self.system.dapatkan_daftar_prioritas()
        for w in prioritas:
            self.tree_prioritas.insert('', 'end', values=(
                w.id_warga, w.nama, w.hitung_prioritas_evakuasi(), w.kondisi_kesehatan, w.__class__.__name__
            ))
            
        # Refresh Status Posko (Di tab evakuasi dan tab kelola)
        for i in self.tree_posko.get_children():
            self.tree_posko.delete(i)
        for i in self.tree_kelola_posko.get_children():
            self.tree_kelola_posko.delete(i)
            
        posko_list = []
        for p in self.system.daftar_posko:
            posko_list.append(f"{p.id_posko} - {p.nama} ({p.wilayah})")
            
            data_row = (p.id_posko, p.nama, p.wilayah, f"{p.kapasitas_terisi}/{p.kapasitas_maksimal}", p.stok_bantuan)
            self.tree_posko.insert('', 'end', values=data_row)
            self.tree_kelola_posko.insert('', 'end', values=data_row)
            
        # Sync Combobox
        self.cb_pilih_posko['values'] = posko_list
        if posko_list:
            self.cb_pilih_posko.current(0)
        else:
            self.cb_pilih_posko.set('')

if __name__ == "__main__":
    app = EvakuasiApp()
    app.mainloop()
                                                                                                                                                                                   