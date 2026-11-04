# Panduan Pengumpulan Capstone Project
## GDG On Widyatama University - Mobile Development Study Jam

Panduan singkat cara mengumpulkan tugas akhir (Capstone Project) aplikasi **LuminaWalls** ke repositori sentral panitia.

---

## 1. Prasyarat Singkat
Sebelum mulai, pastikan:
- [x] Mini Project LuminaWalls di laptop kamu sudah selesai (Sesi 1 - 5).
- [x] Repositori GitHub pribadimu disetel ke **Public** (bukan Private).
- [x] Semua kode lokal sudah kamu push ke branch `main` di GitHub pribadimu.

---

## 2. Langkah Pengumpulan (Hanya 6 Langkah Cepat!)

### Langkah 1: Fork Repositori
1. Buka link ini di browser: 👉 **`https://github.com/gdgocwidyatama/Substitution-MobileDev`**
2. Klik tombol **Fork** di pojok kanan atas, lalu klik **Create fork**.

---

### Langkah 2: Clone ke Laptop
Buka Terminal / Git Bash di laptop kamu, lalu jalankan:
```bash
git clone https://github.com/<username-kamu>/Substitution-MobileDev.git
cd Substitution-MobileDev
```
*(Ganti `<username-kamu>` dengan username GitHub pribadimu)*

---

### Langkah 3: Buat Branch Baru
```bash
git checkout -b submit/nama-kamu
```
*Contoh:*
```bash
git checkout -b submit/dimas-dwi-ariyanto
```

---

### Langkah 4: Tambahkan Submodule Aplikasi Kamu
```bash
git submodule add https://github.com/<username-kamu>/<nama-repo-kamu>.git submissions/nama-kamu
```

*Contoh nyata:*
```bash
git submodule add https://github.com/pavelc4/luminawalls.git submissions/dimas-dwi-ariyanto
```

> [!WARNING]
> - Wajib gunakan URL **HTTPS** (`https://github.com/...`), **JANGAN** pakai SSH (`git@github.com:...`).
> - Jangan ada tanda garis miring (`/`) di akhir path (`submissions/dimas-dwi-ariyanto`, bukan `submissions/dimas-dwi-ariyanto/`).

---

### Langkah 5: Commit dan Push
```bash
git add .
git commit -m "submit capstone <Nama Kamu>"
git push origin submit/nama-kamu
```

*Contoh:*
```bash
git add .
git commit -m "submit capstone Dimas Dwi Ariyanto"
git push origin submit/dimas-dwi-ariyanto
```

---

### Langkah 6: Buka Pull Request (PR)
1. Buka repo hasil fork-mu di browser: `https://github.com/<username-kamu>/Substitution-MobileDev`
2. Klik tombol hijau **Compare & pull request** (atau buka tab **Pull requests** -> **New pull request**).
3. **Judul PR** (Salin format di bawah ini ke kolom judul/title PR):
   ```text
   Submission Capstone - <Nama Lengkap Kamu>
   ```
   *Contoh:*
   ```text
   Submission Capstone - Dimas Dwi Ariyanto
   ```
4. **Isi Deskripsi / Body PR** (Jika kolom deskripsi kosong atau ingin isi ulang, salin template ini):
   ```markdown
   ### Data Peserta & Proyek
   * **Nama Lengkap**: <Nama Lengkap Kamu>
   * **Username GitHub**: @<username-kamu>
   * **URL Repo Pribadi LuminaWalls**: https://github.com/<username-kamu>/luminawalls
   * **Path Submodule di PR ini**: `submissions/<nama-lengkap-kamu>`

   ### Catatan / Pesan Kesan (Opsional)
   (Tulis cerita singkat, tantangan, atau kesan pesan kamu selama mengikuti Study Jam ini)
   ```
   *Contoh pengisian:*
   ```markdown
   ### Data Peserta & Proyek
   * **Nama Lengkap**: Dimas Dwi Ariyanto
   * **Username GitHub**: @pavelc4
   * **URL Repo Pribadi LuminaWalls**: https://github.com/pavelc4/luminawalls
   * **Path Submodule di PR ini**: `submissions/dimas-dwi-ariyanto`

   ### Catatan / Pesan Kesan (Opsional)
   Aplikasi berhasil dibuat dari nol menggunakan Jetpack Compose!
   ```
5. Klik **Create pull request**. Selesai! 🎉

> [!NOTE]
> Kamu **tidak perlu mengedit file `CONTRIBUTORS.md`**. Data dirimu akan dimasukkan ke tabel kontributor secara otomatis oleh GitHub bot saat PR di-merge oleh panitia!

---

## 3. Pertanyaan Sering Ditanyakan (FAQ)

### Tanya: "Setelah buka PR, saya ada update perbaikan kode di repo LuminaWalls. Harus bikin PR baru?"
**Jawab:** Tidak perlu! Cukup buka Terminal di folder `Substitution-MobileDev`, lalu jalankan:
```bash
cd submissions/nama-kamu
git pull origin main
cd ../..
git commit -am "update: revisi kode aplikasi"
git push origin submit/nama-kamu
```
PR kamu di GitHub akan otomatis ter-update sendiri.

### Tanya: "Muncul error 'destination path already exists in index'?"
**Jawab:** Hapus cache Git folder tersebut dengan perintah:
```bash
git rm --cached submissions/nama-kamu
```
Lalu ulangi Langkah 4 dengan benar.
