# BEDAH 4 PILAR OOP MEDIKA HUSADA PER ROLE

Dokumen ini membahas OOP berdasarkan pekerjaan setiap role.

Semua klaim diambil dari source project Medika Husada.

Tidak ada class, method, atau alur yang dibuat hanya untuk melengkapi dokumentasi.

> **Tanggal audit:** 28 Oktober 2026
>
> **Catatan:** nomor baris mengikuti source pada saat audit. Nomor dapat bergeser jika source diubah nanti.

## Kamus Mini

| Istilah | Arti sederhana |
|---|---|
| Class | Cetakan. |
| Object | Hasil nyata dari cetakan. |
| Attribute | Data milik object. |
| Method | Fungsi yang dimiliki class. |
| Service | Bagian program yang mengurus satu kelompok pekerjaan. |
| Route | Pintu yang menerima aksi dari halaman. |
| Abstraksi | Memakai fungsi penting tanpa melihat proses rumitnya. |
| Enkapsulasi | Menjaga data agar tidak diubah sembarangan. |
| Inheritance | Class anak menerima aturan dari class induk. |
| Polymorphism | Method sama dapat memberi hasil berbeda. |

## Source yang Diaudit

Source utama:

- `app.py`
- `seed.py`
- `clinic/__init__.py`
- `clinic/models.py`
- `clinic/services.py`
- `clinic/routes.py`

Source pembanding:

- `begitulah.py`
- `back/app/models.py`
- `back/app/services.py`
- `back/app/schemas.py`
- `back/app/database.py`
- `back/app/main.py`

`app.py` menjalankan package `clinic`.

Karena itu, bukti utama dokumen ini berasal dari folder `clinic`.

`begitulah.py` tidak diimpor oleh aplikasi utama.

File tersebut tidak dipakai sebagai bukti utama aplikasi yang berjalan.

---

## 1. ADMIN — KOMANG

Komang dibuat sebagai object `User` dengan `Role.ADMIN`.

**Bukti akun:** `seed.py`, baris 9.

### Fitur yang Dilakukan Admin

Fitur Admin yang benar-benar terlihat pada source:

- mendaftarkan dan mencari pasien;
- memverifikasi atau menolak appointment;
- memanggil, melewati, atau mengembalikan antrean;
- mengelola dokter dan jadwal;
- mengelola akun staf;
- memproses pengajuan rujukan;
- melihat struk dan laporan pembayaran;
- menyetujui pembelian pemasok.

Catatan penting:

- Admin memverifikasi **appointment**, bukan memverifikasi akun pasien.
- Admin dapat melihat laporan pembayaran.
- Konfirmasi pembayaran pasien dilakukan oleh role Kasir.

### Pilar OOP yang Digunakan Admin

#### Pilar: Abstraksi

**Nama Pilar:**

Abstraksi.

**Dipakai di Fitur:**

Verifikasi appointment.

**File:**

- `clinic/routes.py`
- `clinic/services.py`

**Class:**

`AppointmentService`

**Method:**

`verify()`

**Baris:**

- Route: `clinic/routes.py`, baris 235–241.
- Service: `clinic/services.py`, baris 143–155.

**Alur:**

1. Komang membuka daftar appointment.
2. Komang memilih aksi verifikasi.
3. Route `appointment_action()` menerima request.
4. Route memanggil `AppointmentService.verify()`.
5. Service memeriksa status appointment.
6. Service membuat atau memperbarui `Visit`.
7. Service memberi nomor antrean.
8. Pasien menerima notifikasi.

**Kenapa termasuk pilar ini?**

Route tidak menulis semua proses verifikasi.

Route cukup memanggil satu method service.

Detail antrean, status, dan notifikasi disembunyikan di dalam service.

**Gampangnya:**

Komang cukup menekan tombol verifikasi.

Komang tidak perlu tahu query database yang berjalan.

**Kalau konsep ini tidak dipakai:**

Logika verifikasi akan menumpuk di route.

Kode menjadi panjang dan sulit dirawat.

---

#### Pilar: Enkapsulasi

**Nama Pilar:**

Enkapsulasi aturan perubahan status.

**Dipakai di Fitur:**

- verifikasi appointment;
- perubahan antrean; dan
- pengelolaan akun staf.

**File:**

- `clinic/services.py`
- `clinic/routes.py`
- `clinic/models.py`

**Class:**

- `AppointmentService`
- `User`

**Method:**

- `claim_edit()`
- `verify()`
- `User.set_password()`

**Baris:**

- `AppointmentService.claim_edit()`: `clinic/services.py`, baris 80–91.
- `AppointmentService.verify()`: `clinic/services.py`, baris 143–155.
- Aksi antrean: `clinic/routes.py`, baris 448–459.
- Pengelolaan akun: `clinic/routes.py`, baris 666–684.
- Password `User`: `clinic/models.py`, baris 65–86.

**Alur:**

1. Admin memilih aksi.
2. Route memeriksa apakah role Admin boleh melakukan aksi itu.
3. Method memeriksa status lama.
4. Perubahan ditolak jika status tidak sesuai.
5. Jika valid, data diperbarui.
6. Perubahan disimpan melalui transaksi `mutate()`.
7. Jika terjadi error, transaksi dibatalkan.

**Kenapa termasuk pilar ini?**

Admin tidak mengubah status database langsung dari halaman.

Perubahan melewati method dan aturan tertentu.

Data menjadi lebih terkontrol.

**Gampangnya:**

Status punya pintu masuk.

Tidak semua perubahan boleh lewat.

**Kalau konsep ini tidak dipakai:**

Appointment dapat berpindah ke status yang salah.

Antrean juga dapat diubah dengan aksi yang tidak valid.

### Pilar yang Tidak Ditemukan Langsung pada Admin

- **Inheritance:** tidak ditemukan penggunaan domain langsung pada pekerjaan Admin.
- **Polymorphism:** Admin melihat laporan pembayaran, tetapi pemanggilan strategi pembayaran dilakukan pada alur Kasir.

---

## 2. PERAWAT — GEA

Gea dibuat sebagai object `User` dengan `Role.NURSE`.

**Bukti akun:** `seed.py`, baris 10.

### Fitur yang Dilakukan Perawat

Fitur Perawat yang benar-benar ada:

- melihat pasien yang menunggu pemeriksaan awal;
- mengisi tekanan darah;
- mengisi suhu;
- mengisi berat dan tinggi badan;
- mengisi nadi, napas, saturasi, dan skala nyeri;
- menulis keluhan serta catatan;
- mengirim pasien ke antrean dokter.

Source memakai nama `NursingAssessment`.

Tidak ada class khusus bernama `Triage`.

### Pilar OOP yang Digunakan Perawat

#### Pilar: Abstraksi

**Nama Pilar:**

Abstraksi.

**Dipakai di Fitur:**

Pemeriksaan awal pasien.

**File:**

- `clinic/routes.py`
- `clinic/services.py`

**Class:**

`WorkflowService`

**Method:**

`nurse()`

**Baris:**

- Route: `clinic/routes.py`, baris 374–378.
- Service: `clinic/services.py`, baris 168–179.

**Alur:**

1. Gea memilih pasien dari antrean pemeriksaan awal.
2. Gea mengisi tekanan darah, suhu, nadi, dan data lain.
3. Gea menekan simpan.
4. Route `nursing()` menerima data.
5. Route memanggil `WorkflowService.nurse()`.
6. Service memvalidasi semua angka.
7. Service membuat object `NursingAssessment`.
8. Status `Visit` berubah menjadi `WAITING_DOCTOR`.

**Kenapa termasuk pilar ini?**

Route tidak perlu tahu semua validasi pemeriksaan.

Route cukup menyerahkan pekerjaan kepada service.

**Gampangnya:**

Gea hanya mengisi form.

Service mengurus validasi dan penyimpanan.

**Kalau konsep ini tidak dipakai:**

Validasi tanda vital harus ditulis di route.

Route menjadi panjang dan sulit dibaca.

---

#### Pilar: Enkapsulasi

**Nama Pilar:**

Enkapsulasi aturan pemeriksaan dan status.

**Dipakai di Fitur:**

- validasi vital sign;
- penyimpanan catatan perawat; dan
- pengiriman pasien ke dokter.

**File:**

- `clinic/services.py`
- `clinic/models.py`

**Class:**

- `WorkflowService`
- `NursingAssessment`
- `Visit`

**Method:**

- `nurse()`
- `transition()`

**Baris:**

- `WorkflowService.transition()`: `clinic/services.py`, baris 160–165.
- `WorkflowService.nurse()`: `clinic/services.py`, baris 168–179.
- `NursingAssessment`: `clinic/models.py`, baris 172–188.
- `Visit.status`: `clinic/models.py`, baris 154–169.

**Alur:**

1. Data vital sign masuk ke `WorkflowService.nurse()`.
2. Setiap angka diperiksa batas minimumnya dan maksimumnya.
3. Keluhan wajib diisi.
4. `transition()` memeriksa status kunjungan saat ini.
5. Hanya kunjungan `WAITING_NURSE` yang boleh lanjut.
6. `NursingAssessment` dibuat.
7. Appointment ditandai sudah hadir.

**Kenapa termasuk pilar ini?**

Nilai pemeriksaan dan perubahan status tidak dilakukan sembarangan.

Semua harus melewati aturan di service.

**Gampangnya:**

Service menjadi penjaga pintu.

Data yang tidak masuk akal akan ditolak.

**Kalau konsep ini tidak dipakai:**

Suhu atau tekanan darah yang tidak masuk akal bisa tersimpan.

Pasien juga bisa masuk ke antrean dokter tanpa pemeriksaan awal yang valid.

### Pilar yang Tidak Ditemukan Langsung pada Perawat

- **Inheritance:** tidak ada class `Nurse(User)` pada source.
- **Polymorphism:** tidak ditemukan method Perawat yang sama dengan beberapa perilaku berbeda.

---

## 3. DOKTER

### Dokter Umum — dr. Muhammad Fakih Nabal

Fakih dibuat sebagai object `User` dengan `Role.DOCTOR`.

Fakih juga mempunyai record `Doctor` dengan spesialisasi `Dokter Umum`.

**Bukti:**

- akun: `seed.py`, baris 15;
- record dokter dan spesialisasi: `seed.py`, baris 30–34.

### Dokter Kandungan — dr. Alia Fransiska Dewi Arum Trilestari

Alia dibuat sebagai object `User` dengan `Role.DOCTOR`.

Alia juga mempunyai record `Doctor` dengan spesialisasi `Obstetri dan Ginekologi`.

**Bukti:**

- akun: `seed.py`, baris 16;
- record dokter dan spesialisasi: `seed.py`, baris 30–34.

### Bagaimana Source Sebenarnya?

Fakih dan Alia memakai struktur class yang sama:

- class `User` untuk nama, email, password, role, SIP, dan status akun;
- class `Doctor` untuk spesialisasi, tarif, dan jadwal.

Hubungannya adalah one-to-one melalui `Doctor.user_id`.

**Bukti:**

- relasi `User.doctor`: `clinic/models.py`, baris 65–76;
- class `Doctor`: `clinic/models.py`, baris 109–114.

`Doctor` tidak mewarisi `User`.

Source tidak mempunyai `class Doctor(User)`.

### Fitur yang Dilakukan Dokter

- melihat pasien dan hasil pemeriksaan perawat;
- memulai pemeriksaan;
- menulis anamnesis;
- menulis pemeriksaan fisik;
- menulis diagnosis;
- menulis tindakan dan biaya tindakan;
- membuat resep;
- mengajukan rujukan;
- menandatangani surat rujukan.

### Pilar OOP yang Digunakan Dokter

#### Pilar: Abstraksi

**Nama Pilar:**

Abstraksi.

**Dipakai di Fitur:**

Pemeriksaan dokter dan pembuatan resep.

**File:**

- `clinic/routes.py`
- `clinic/services.py`

**Class:**

`WorkflowService`

**Method:**

`examine()`

**Baris:**

- Route pemeriksaan: `clinic/routes.py`, baris 381–398.
- Service pemeriksaan: `clinic/services.py`, baris 181–200.

**Alur:**

1. Dokter memilih pasien.
2. Dokter memulai pemeriksaan.
3. Status berubah menjadi `WITH_DOCTOR`.
4. Dokter mengisi diagnosis, tindakan, dan resep.
5. Route mengumpulkan data item obat.
6. Route memanggil `WorkflowService.examine()`.
7. Service membuat `DoctorExamination`.
8. Jika ada obat, service membuat `Prescription`.
9. Status bergerak ke farmasi atau pembayaran.

**Kenapa termasuk pilar ini?**

Dokter dan route tidak perlu menulis query penyimpanan satu per satu.

Satu method service mengurus pemeriksaan dan resep.

**Gampangnya:**

Dokter menekan simpan.

Service mengurus object dan status di belakangnya.

**Kalau konsep ini tidak dipakai:**

Logika pemeriksaan, resep, dan status akan tersebar di route.

Risiko ada langkah yang tertinggal menjadi lebih besar.

---

#### Pilar: Enkapsulasi

**Nama Pilar:**

Enkapsulasi aturan pemeriksaan dan workflow.

**Dipakai di Fitur:**

- validasi diagnosis;
- validasi obat resep;
- penyimpanan pemeriksaan; dan
- perubahan status kunjungan.

**File:**

- `clinic/services.py`
- `clinic/models.py`

**Class:**

- `WorkflowService`
- `DoctorExamination`
- `Prescription`

**Method:**

- `examine()`
- `transition()`

**Baris:**

- `WorkflowService.transition()`: `clinic/services.py`, baris 160–165.
- `WorkflowService.examine()`: `clinic/services.py`, baris 181–200.
- `DoctorExamination`: `clinic/models.py`, baris 191–205.
- `Prescription`: `clinic/models.py`, baris 291–310.

**Alur:**

1. Service memeriksa anamnesis, pemeriksaan fisik, dan diagnosis.
2. Service memeriksa ID obat.
3. Obat duplikat ditolak.
4. Jumlah obat harus valid.
5. Status kunjungan diperiksa sebelum dipindahkan.
6. Pemeriksaan dan resep baru disimpan setelah valid.

**Kenapa termasuk pilar ini?**

Data pemeriksaan tidak langsung ditulis bebas dari halaman.

Perubahan melewati aturan di `WorkflowService`.

**Gampangnya:**

Diagnosis dan resep masuk lewat satu pintu yang diperiksa.

**Kalau konsep ini tidak dipakai:**

Resep bisa mempunyai obat duplikat atau jumlah tidak valid.

Status kunjungan juga bisa melompat ke tahap yang salah.

### Pilar yang Tidak Ditemukan Langsung pada Dokter

- **Inheritance domain:** `Doctor` tidak mewarisi `User`; keduanya memakai relasi.
- **Polymorphism:** tidak ditemukan method Dokter yang sama dengan perilaku berbeda untuk Fakih dan Alia. Keduanya memakai alur `WorkflowService.examine()` yang sama.

---

## 4. APOTEKER — BINTANG

Bintang dibuat sebagai object `User` dengan `Role.PHARMACIST`.

**Bukti akun:** `seed.py`, baris 11.

### Fitur yang Dilakukan Apoteker

- menerima resep;
- membuka detail resep;
- memulai proses penyiapan obat;
- melaporkan stok kurang;
- memeriksa obat kedaluwarsa;
- mengurangi stok;
- menandai obat siap;
- menyerahkan obat;
- mengajukan pembelian stok kepada pemasok.

Catatan jujur:

Source memakai istilah “menyiapkan obat”.

Tidak ada class atau method khusus bernama `racik_obat()`.

### Pilar OOP yang Digunakan Apoteker

#### Pilar: Abstraksi

**Nama Pilar:**

Abstraksi.

**Dipakai di Fitur:**

Proses resep dari mulai disiapkan sampai diserahkan.

**File:**

- `clinic/routes.py`
- `clinic/services.py`

**Class:**

`PharmacyService`

**Method:**

`process()`

**Baris:**

- Route: `clinic/routes.py`, baris 401–405.
- Service: `clinic/services.py`, baris 203–228.

**Alur:**

1. Resep masuk ke antrean farmasi.
2. Bintang membuka resep.
3. Bintang memilih aksi mulai proses.
4. Route memanggil `PharmacyService.process()`.
5. Service mengubah status resep menjadi diproses.
6. Saat obat siap, service memeriksa kedaluwarsa dan stok.
7. Saat obat diserahkan, service membuat invoice.

**Kenapa termasuk pilar ini?**

Route hanya meneruskan aksi.

Detail seluruh proses farmasi disimpan dalam satu service.

**Gampangnya:**

Bintang memilih aksi.

Service mengurus langkah teknis di belakangnya.

**Kalau konsep ini tidak dipakai:**

Aturan farmasi akan tersebar di banyak route.

Setiap aksi dapat mempunyai aturan yang tidak konsisten.

---

#### Pilar: Enkapsulasi

**Nama Pilar:**

Enkapsulasi stok obat.

**Dipakai di Fitur:**

- pengecekan stok;
- pengurangan stok; dan
- pencatatan penyerahan obat.

**File:**

- `clinic/models.py`
- `clinic/services.py`

**Class:**

- `Medicine`
- `StockMovement`
- `PharmacyService`

**Method:**

- `Medicine.change_stock()`
- `PharmacyService.process()`

**Baris:**

- `Medicine`: `clinic/models.py`, baris 208–231.
- `StockMovement`: `clinic/models.py`, baris 234–242.
- Pemakaian saat obat siap: `clinic/services.py`, baris 218–223.

**Alur:**

1. Resep berisi daftar obat dan jumlah.
2. Bintang menandai obat siap.
3. `PharmacyService` memeriksa tanggal kedaluwarsa.
4. Service memanggil `Medicine.change_stock()`.
5. Method menolak perubahan jika stok tidak cukup.
6. Jika valid, stok dikurangi.
7. `StockMovement` mencatat jumlah, alasan, aktor, dan kunjungan.
8. Status resep berubah menjadi `READY`.
9. Pasien menerima notifikasi dari perpindahan status.

**Kenapa termasuk pilar ini?**

Stok tidak dikurangi langsung dari halaman.

Perubahan harus lewat method yang mempunyai validasi.

**Gampangnya:**

Stok seperti lemari obat yang dikunci.

`change_stock()` adalah pintu resminya.

**Kalau konsep ini tidak dipakai:**

Stok dapat menjadi minus.

Riwayat perubahan juga dapat hilang.

### Pilar yang Tidak Ditemukan Langsung pada Apoteker

- **Inheritance:** tidak ada class `Pharmacist(User)` pada source.
- **Polymorphism:** aksi farmasi masih dipilih dengan nilai `action` dan percabangan di `process()`, bukan object polymorphic terpisah.

---

## 5. KASIR — FATUR

Fatur dibuat sebagai object `User` dengan `Role.CASHIER`.

**Bukti akun:** `seed.py`, baris 12.

### Fitur yang Dilakukan Kasir

- melihat kunjungan yang menunggu pembayaran;
- membuka invoice;
- memilih metode pembayaran;
- memasukkan uang diterima untuk pembayaran tunai;
- melihat kembalian;
- mengonfirmasi pembayaran;
- membuka struk.

Metode yang diterima source:

- BPJS;
- Tunai;
- Transfer;
- QRIS; dan
- Debit.

Catatan penting:

Metode tersebut belum mempunyai class masing-masing.

Tidak ada method `process_payment()` pada source.

### Pilar OOP yang Digunakan Kasir

#### Pilar: Abstraksi

**Nama Pilar:**

Abstraksi.

**Dipakai di Fitur:**

Konfirmasi pembayaran dan pembuatan invoice.

**File:**

- `clinic/routes.py`
- `clinic/services.py`

**Class:**

`BillingService`

**Method:**

- `invoice()`
- `pay()`

**Baris:**

- Route Kasir: `clinic/routes.py`, baris 408–422.
- `BillingService`: `clinic/services.py`, baris 251–294.

**Alur:**

1. Fatur membuka daftar pembayaran.
2. Fatur memilih invoice pasien.
3. Fatur memilih metode pembayaran.
4. Route `pay()` menerima form.
5. Route memanggil `BillingService.pay()`.
6. Service memeriksa tagihan dan metode.
7. Service membuat object `Payment`.
8. Route menampilkan struk.

**Kenapa termasuk pilar ini?**

Route tidak menghitung semua tagihan sendiri.

Detail pembayaran diserahkan kepada `BillingService`.

**Gampangnya:**

Kasir mengisi form.

Service mengurus hitungan dan status.

**Kalau konsep ini tidak dipakai:**

Logika pembayaran akan menumpuk di route.

Kesalahan hitung menjadi lebih sulit dicari.

---

#### Pilar: Enkapsulasi

**Nama Pilar:**

Enkapsulasi aturan pembayaran.

**Dipakai di Fitur:**

- validasi metode;
- validasi uang tunai;
- perubahan status invoice; dan
- penyelesaian visit.

**File:**

- `clinic/services.py`
- `clinic/models.py`

**Class:**

- `BillingService`
- `Invoice`
- `Payment`
- `WorkflowService`

**Method:**

- `BillingService.pay()`
- `WorkflowService.transition()`

**Baris:**

- `BillingService.pay()`: `clinic/services.py`, baris 270–294.
- `WorkflowService.transition()`: `clinic/services.py`, baris 160–165.
- `Invoice`: `clinic/models.py`, baris 314–324.
- `Payment`: `clinic/models.py`, baris 336–343.

**Alur:**

1. Service memastikan invoice tersedia.
2. Service memeriksa diskon.
3. Service memeriksa metode pembayaran.
4. Jika Tunai, uang diterima harus valid dan cukup.
5. Service menghitung kembalian.
6. Status visit dipindahkan ke `COMPLETED`.
7. Status invoice menjadi lunas atau ditanggung BPJS.
8. Object `Payment` dibuat.

**Kenapa termasuk pilar ini?**

Kasir tidak langsung mengubah status invoice dan visit.

Semua perubahan penting melewati aturan service.

**Gampangnya:**

Pembayaran punya satu pintu resmi.

Pintu itu memeriksa semua aturan sebelum menutup kunjungan.

**Kalau konsep ini tidak dipakai:**

Invoice dapat ditandai lunas walaupun uang tunai kurang.

Visit juga dapat selesai tanpa payment yang valid.

---

#### Pilar: Pewarisan / Inheritance

**Nama Pilar:**

Inheritance strategi pembayaran.

**Dipakai di Fitur:**

Perhitungan tagihan General dan BPJS.

**File:**

`clinic/services.py`

**Class:**

- Induk: `PaymentProcessor`
- Anak: `GeneralPayment`
- Anak: `BPJSPayment`

**Method:**

`amounts()`

**Baris:**

`clinic/services.py`, baris 231–248.

**Alur:**

1. `PaymentProcessor` menentukan bahwa strategi harus punya `amounts()`.
2. `GeneralPayment` mewarisi `PaymentProcessor`.
3. `BPJSPayment` juga mewarisi `PaymentProcessor`.
4. Kedua class anak menulis cara hitungnya sendiri.

**Kenapa termasuk pilar ini?**

Nama class induk ditulis di dalam kurung:

```python
class GeneralPayment(PaymentProcessor):
class BPJSPayment(PaymentProcessor):
```

Itu adalah bentuk inheritance yang nyata pada source.

**Gampangnya:**

`PaymentProcessor` adalah induk.

General dan BPJS adalah anak.

**Kalau konsep ini tidak dipakai:**

Aturan dasar pembayaran harus ditulis dengan cara berbeda-beda.

Tidak ada kontrak method yang sama.

---

#### Pilar: Polimorfisme / Polymorphism

**Nama Pilar:**

Polymorphism pada `amounts()`.

**Dipakai di Fitur:**

Pembagian biaya antara pasien dan BPJS.

**File:**

`clinic/services.py`

**Class:**

- `GeneralPayment`
- `BPJSPayment`
- `BillingService`

**Method:**

- `amounts()`
- `invoice()`
- `pay()`

**Baris:**

- Hasil General dan BPJS: `clinic/services.py`, baris 241–248.
- Pemilihan processor: `clinic/services.py`, baris 251–265.
- Pemakaian saat bayar: `clinic/services.py`, baris 270–294.

**Alur:**

1. Sistem memeriksa apakah appointment memakai BPJS.
2. Sistem memilih `BPJSPayment()` atau `GeneralPayment()`.
3. Object disimpan pada variabel `processor`.
4. Sistem memanggil `processor.amounts(total)`.
5. General menghasilkan tanggungan Rp0 dan pasien membayar total.
6. BPJS menghasilkan tanggungan penuh dan pasien membayar Rp0.

**Kenapa termasuk pilar ini?**

Nama method yang dipanggil sama.

Hasilnya berbeda sesuai object yang menjalankan.

**Gampangnya:**

Perintahnya sama: “hitung pembayaran”.

Jawabannya berbeda untuk General dan BPJS.

**Kalau konsep ini tidak dipakai:**

Percabangan perhitungan dapat semakin panjang.

Setiap strategi harus ditangani langsung oleh `BillingService`.

### Batas Polymorphism Pembayaran

Tunai, Transfer, QRIS, dan Debit masih berupa teks.

Tunai mempunyai percabangan khusus untuk menghitung kembalian.

**Bukti:** `clinic/services.py`, baris 274–287.

Jadi jangan mengatakan ada:

- `CashPayment.process_payment()`;
- `TransferPayment.process_payment()`; atau
- `QRISPayment.process_payment()`.

Class dan method tersebut tidak ada.

---

## 6. PASIEN

Contoh object pasien pada seed:

- Budi Santoso;
- Ratna Permata; dan
- Siti Aminah.

**Bukti akun:** `seed.py`, baris 17–19.

### Fitur yang Dilakukan Pasien

- mendaftar akun;
- melengkapi profil;
- membuat appointment;
- mengubah atau membatalkan appointment;
- melihat antrean;
- melihat rekam medis miliknya;
- melihat resep;
- melihat invoice dan struk.

Catatan rujukan:

Pasien adalah pihak yang dirujuk.

Namun pengajuan rujukan dilakukan Dokter dan penerbitannya dilakukan Admin.

Tidak ada route Pasien untuk menerbitkan rujukan sendiri.

### Pilar OOP yang Digunakan Pasien

#### Pilar: Abstraksi

**Nama Pilar:**

Abstraksi.

**Dipakai di Fitur:**

Booking appointment.

**File:**

- `clinic/routes.py`
- `clinic/services.py`

**Class:**

`AppointmentService`

**Method:**

`book()`

**Baris:**

- Route booking: `clinic/routes.py`, baris 192–199.
- `AppointmentService.book()`: `clinic/services.py`, baris 111–134.

**Alur:**

1. Pasien memilih dokter dan tanggal.
2. Pasien memilih jam yang tersedia.
3. Pasien mengisi keluhan.
4. Route menerima form.
5. Route memanggil `AppointmentService.book()`.
6. Service memeriksa jadwal dan slot.
7. Jika memilih BPJS, service memeriksa BPJS aktif.
8. Object `Appointment` dibuat.
9. Pasien mendapat notifikasi.

**Kenapa termasuk pilar ini?**

Pasien hanya mengisi form booking.

Pasien tidak perlu mengetahui query jadwal dan database.

**Gampangnya:**

Pasien klik booking.

Service mengurus pemeriksaan slot di belakangnya.

**Kalau konsep ini tidak dipakai:**

Halaman booking harus mengurus seluruh query dan validasi sendiri.

Kode halaman menjadi rumit.

---

#### Pilar: Enkapsulasi

**Nama Pilar:**

Enkapsulasi hak akses data pasien.

**Dipakai di Fitur:**

- melihat rekam medis;
- melihat appointment;
- melihat resep; dan
- melihat struk milik sendiri.

**File:**

`clinic/routes.py`

**Class:**

- `Patient`
- `Appointment`
- `Visit`

**Method:**

- `visit_access()`
- `appointment_access()`
- `scoped_visits()`

**Baris:**

`clinic/routes.py`, baris 44–70.

**Alur:**

1. Pasien membuka data kunjungan.
2. Route mengambil `current_user`.
3. `visit_access()` membandingkan pemilik visit dengan user yang login.
4. Jika bukan miliknya, sistem mengembalikan error 403.
5. Jika miliknya, data boleh ditampilkan.
6. `scoped_visits()` juga menyaring daftar visit berdasarkan pasien tersebut.

**Kenapa termasuk pilar ini?**

Data medis tidak dibuka bebas.

Aksesnya dijaga melalui function tertentu.

Ini adalah enkapsulasi pada batas akses aplikasi.

**Gampangnya:**

Rekam medis seperti lemari pribadi.

Pasien hanya mendapat kunci untuk lemari miliknya.

**Kalau konsep ini tidak dipakai:**

Pasien dapat melihat data pasien lain.

Ini berbahaya untuk privasi medis.

---

#### Pilar: Polimorfisme / Polymorphism

**Nama Pilar:**

Polymorphism hasil tagihan General dan BPJS.

**Dipakai di Fitur:**

Hasil invoice yang diterima pasien.

**File:**

`clinic/services.py`

**Class:**

- `GeneralPayment`
- `BPJSPayment`
- `BillingService`

**Method:**

`amounts()`

**Baris:**

`clinic/services.py`, baris 241–265.

**Alur:**

1. Appointment menyimpan apakah pasien memakai BPJS.
2. `BillingService` memilih processor.
3. Processor menjalankan `amounts(total)`.
4. Pasien General mendapat nilai payable penuh.
5. Pasien BPJS mendapat nilai payable Rp0.

**Kenapa termasuk pilar ini?**

Method yang sama menghasilkan tagihan berbeda sesuai object pembayaran.

Pasien menerima hasil dari polymorphism tersebut.

**Gampangnya:**

Tagihan dihitung dengan perintah yang sama.

Hasil pasien General dan BPJS berbeda.

**Kalau konsep ini tidak dipakai:**

Rumus General dan BPJS harus ditangani dengan percabangan langsung di banyak tempat.

### Pilar yang Tidak Ditemukan Langsung pada Pasien

- **Inheritance domain:** `Patient` tidak mewarisi `User`; keduanya memakai relasi `user_id`.
- Inheritance strategi pembayaran memengaruhi tagihan pasien, tetapi tidak dijalankan langsung oleh aksi Pasien.

---

# TABEL RINGKAS PER ROLE

| Role | Pilar | Fitur | File | Class/Method | Penjelasan |
|---|---|---|---|---|---|
| Admin | Abstraksi | Verifikasi appointment | `clinic/services.py` | `AppointmentService.verify()` | Route cukup memanggil service. |
| Admin | Enkapsulasi | Status appointment dan antrean | `clinic/services.py`, `clinic/routes.py` | `claim_edit()`, `verify()`, `queue_action()` | Perubahan status diperiksa lebih dulu. |
| Perawat | Abstraksi | Pemeriksaan awal | `clinic/services.py` | `WorkflowService.nurse()` | Service mengurus validasi dan penyimpanan. |
| Perawat | Enkapsulasi | Vital sign dan status visit | `clinic/services.py` | `nurse()`, `transition()` | Nilai dan perpindahan status dijaga. |
| Dokter | Abstraksi | Pemeriksaan dan resep | `clinic/services.py` | `WorkflowService.examine()` | Satu service mengurus pemeriksaan dan resep. |
| Dokter | Enkapsulasi | Diagnosis, resep, status | `clinic/services.py` | `examine()`, `transition()` | Data harus valid sebelum disimpan. |
| Apoteker | Abstraksi | Proses resep | `clinic/services.py` | `PharmacyService.process()` | Route hanya meneruskan aksi. |
| Apoteker | Enkapsulasi | Pengurangan stok | `clinic/models.py` | `Medicine.change_stock()` | Stok dijaga dan perubahan dicatat. |
| Kasir | Abstraksi | Invoice dan pembayaran | `clinic/services.py` | `BillingService.invoice()`, `pay()` | Detail pembayaran disembunyikan di service. |
| Kasir | Enkapsulasi | Validasi dan status pembayaran | `clinic/services.py` | `BillingService.pay()` | Pembayaran melewati aturan yang sama. |
| Kasir | Inheritance | Strategi General/BPJS | `clinic/services.py` | `GeneralPayment`, `BPJSPayment` | Keduanya mewarisi `PaymentProcessor`. |
| Kasir | Polymorphism | Pembagian biaya | `clinic/services.py` | `amounts()` | Method sama memberi hasil berbeda. |
| Pasien | Abstraksi | Booking | `clinic/services.py` | `AppointmentService.book()` | Pasien tidak perlu tahu query jadwal. |
| Pasien | Enkapsulasi | Data medis milik sendiri | `clinic/routes.py` | `visit_access()`, `scoped_visits()` | Akses disaring berdasarkan pemilik. |
| Pasien | Polymorphism | Hasil tagihan | `clinic/services.py` | `amounts()` | General dan BPJS menghasilkan payable berbeda. |

---

# MATRIX ROLE VS PILAR

| Role | Abstraksi | Enkapsulasi | Pewarisan | Polimorfisme |
|---|---|---|---|---|
| Admin | Ya — service appointment | Ya — status dan akses | Tidak ditemukan implementasi langsung | Tidak ditemukan implementasi langsung |
| Perawat | Ya — `WorkflowService.nurse()` | Ya — vital sign dan status | Tidak ditemukan implementasi langsung | Tidak ditemukan implementasi langsung |
| Dokter | Ya — `WorkflowService.examine()` | Ya — pemeriksaan, resep, status | Tidak ditemukan inheritance domain langsung | Tidak ditemukan implementasi langsung |
| Apoteker | Ya — `PharmacyService.process()` | Ya — `Medicine.change_stock()` | Tidak ditemukan implementasi langsung | Tidak ditemukan implementasi langsung |
| Kasir | Ya — `BillingService` | Ya — aturan pembayaran | Ya — processor General/BPJS | Ya — `amounts()` |
| Pasien | Ya — booking | Ya — akses data sendiri | Tidak ditemukan implementasi langsung | Ya — hasil tagihan General/BPJS |

Catatan:

`User(UserMixin, db.Model)` dan model yang mewarisi `db.Model` adalah inheritance dari framework.

Matrix di atas fokus pada inheritance domain yang terlihat dalam fitur role.

---

# ALUR OOP DARI PASIEN SAMPAI SELESAI

```text
Pasien booking
      ↓
Admin verifikasi
      ↓
Perawat screening
      ↓
Dokter memeriksa
      ↓
Apoteker menyiapkan obat
      ↓
Kasir memproses pembayaran
      ↓
Selesai
```

## 1. Pasien Booking

**Role:** Pasien

**Fitur:** Membuat appointment.

**Class:** `Patient`, `Doctor`, `Appointment`

**Service/Method:** `AppointmentService.book()`

**File:** `clinic/services.py`, baris 111–134.

**Pilar OOP:** Abstraksi + Enkapsulasi aturan booking.

**Kenapa:**

Pasien cukup mengisi form.

Service memeriksa jadwal, slot, dan BPJS.

## 2. Admin Verifikasi

**Role:** Admin

**Fitur:** Memverifikasi appointment dan membuat antrean.

**Class:** `Appointment`, `Visit`, `QueueCounter`

**Service/Method:** `AppointmentService.verify()`

**File:** `clinic/services.py`, baris 143–155.

**Pilar OOP:** Abstraksi + Enkapsulasi status.

**Kenapa:**

Admin cukup memilih verifikasi.

Service mengatur status dan nomor antrean dengan aturan tertentu.

## 3. Perawat Screening

**Role:** Perawat

**Fitur:** Pemeriksaan awal dan vital sign.

**Class:** `NursingAssessment`, `Visit`

**Service/Method:** `WorkflowService.nurse()`

**File:** `clinic/services.py`, baris 168–179.

**Pilar OOP:** Abstraksi + Enkapsulasi.

**Kenapa:**

Service memvalidasi angka dan memindahkan status ke antrean dokter.

## 4. Dokter Memeriksa

**Role:** Dokter

**Fitur:** Diagnosis, tindakan, dan resep.

**Class:** `DoctorExamination`, `Prescription`, `PrescriptionItem`

**Service/Method:** `WorkflowService.examine()`

**File:** `clinic/services.py`, baris 181–200.

**Pilar OOP:** Abstraksi + Enkapsulasi.

**Kenapa:**

Service memeriksa data lalu membuat object pemeriksaan dan resep.

## 5. Apoteker Menyiapkan Obat

**Role:** Apoteker

**Fitur:** Proses resep dan stok.

**Class:** `Prescription`, `Medicine`, `StockMovement`

**Service/Method:** `PharmacyService.process()`, `Medicine.change_stock()`

**File:**

- `clinic/services.py`, baris 203–228;
- `clinic/models.py`, baris 208–242.

**Pilar OOP:** Abstraksi + Enkapsulasi.

**Kenapa:**

Service mengatur alur resep.

Method Medicine menjaga perubahan stok.

## 6. Kasir Memproses Pembayaran

**Role:** Kasir

**Fitur:** Invoice, pembayaran, dan struk.

**Class:** `Invoice`, `Payment`, `PaymentProcessor`, `GeneralPayment`, `BPJSPayment`

**Service/Method:** `BillingService.invoice()`, `BillingService.pay()`, `amounts()`

**File:** `clinic/services.py`, baris 231–294.

**Pilar OOP:** Abstraksi + Enkapsulasi + Inheritance + Polymorphism.

**Kenapa:**

BillingService menyederhanakan proses pembayaran.

General dan BPJS mewarisi induk yang sama dan memberi hasil `amounts()` yang berbeda.

## 7. Selesai

**Role:** Sistem setelah Kasir.

**Fitur:** Menyelesaikan visit dan appointment.

**Class:** `Visit`, `Appointment`, `Invoice`, `Payment`

**Service/Method:** `WorkflowService.transition()`, `BillingService.pay()`

**File:** `clinic/services.py`, baris 270–294.

**Pilar OOP:** Enkapsulasi workflow.

**Kenapa:**

Visit hanya menjadi `COMPLETED` setelah pembayaran valid.

---

# FILE PRESENTASI PER ROLE

## ADMIN

**Buka:**

- `clinic/routes.py`, baris 235–241;
- `clinic/services.py`, baris 143–155.

**Tunjukkan:**

`appointment_action()` memanggil `AppointmentService.verify()`.

**Kalimat presentasi:**

> “Admin memakai abstraksi karena route cukup memanggil service. Enkapsulasinya terlihat saat status diverifikasi sebelum diubah.”

## PERAWAT

**Buka:**

- `clinic/routes.py`, baris 374–378;
- `clinic/services.py`, baris 160–179.

**Tunjukkan:**

`WorkflowService.nurse()` dan `transition()`.

**Kalimat presentasi:**

> “Perawat mengisi form. Service memvalidasi vital sign dan memindahkan pasien ke antrean dokter.”

## DOKTER

**Buka:**

- `clinic/routes.py`, baris 381–398;
- `clinic/services.py`, baris 181–200;
- `clinic/models.py`, baris 109–114.

**Tunjukkan:**

`WorkflowService.examine()` serta relasi `Doctor` ke `User`.

**Kalimat presentasi:**

> “Fakih dan Alia memakai class Doctor yang sama. Doctor tidak mewarisi User; keduanya terhubung dengan user_id.”

## APOTEKER

**Buka:**

- `clinic/services.py`, baris 203–228;
- `clinic/models.py`, baris 208–242.

**Tunjukkan:**

`PharmacyService.process()` memanggil `Medicine.change_stock()`.

**Kalimat presentasi:**

> “Apoteker memakai abstraksi pada service farmasi dan enkapsulasi pada perubahan stok.”

## KASIR

**Buka:**

`clinic/services.py`, baris 231–294.

**Tunjukkan:**

- `PaymentProcessor`;
- `GeneralPayment`;
- `BPJSPayment`;
- `processor.amounts(total)`;
- `BillingService.pay()`.

**Kalimat presentasi:**

> “Kasir adalah bagian yang paling lengkap. Di sini ada abstraksi, enkapsulasi, inheritance, dan polymorphism.”

## PASIEN

**Buka:**

- `clinic/services.py`, baris 111–134;
- `clinic/routes.py`, baris 44–70.

**Tunjukkan:**

`AppointmentService.book()`, `visit_access()`, dan `scoped_visits()`.

**Kalimat presentasi:**

> “Pasien memakai abstraksi saat booking dan enkapsulasi akses saat melihat data miliknya sendiri.”

---

# CHEAT SHEET PERTANYAAN PER ROLE

## Admin

**Dosen:** “Di Admin ada OOP apa?”

**Jawaban:**

> “Ada abstraksi dan enkapsulasi. Contohnya saat verifikasi appointment. Route di `clinic/routes.py` memanggil `AppointmentService.verify()` di `clinic/services.py`. Status diperiksa sebelum diubah.”

## Perawat

**Dosen:** “Di Perawat ada OOP apa?”

**Jawaban:**

> “Ada abstraksi dan enkapsulasi. `WorkflowService.nurse()` memvalidasi vital sign, menyimpan NursingAssessment, lalu memindahkan status ke antrean dokter.”

## Dokter

**Dosen:** “Di Dokter ada OOP apa?”

**Jawaban:**

> “Ada abstraksi dan enkapsulasi pada `WorkflowService.examine()`. Service mengurus diagnosis, resep, dan perubahan status. Doctor tidak mewarisi User pada source ini.”

## Apoteker

**Dosen:** “Di Apoteker mana enkapsulasinya?”

**Jawaban:**

> “Ada di `Medicine.change_stock()` pada `clinic/models.py`. Stok tidak dikurangi langsung. Method memeriksa stok dan mencatat perubahannya.”

## Kasir

**Dosen:** “Di Kasir mana inheritance dan polymorphism?”

**Jawaban:**

> “Buka `clinic/services.py`. GeneralPayment dan BPJSPayment mewarisi PaymentProcessor. Keduanya punya `amounts()`, tetapi hasilnya berbeda. Itu inheritance dan polymorphism.”

## Pasien

**Dosen:** “Di Pasien ada OOP apa?”

**Jawaban:**

> “Ada abstraksi saat booking melalui `AppointmentService.book()`. Ada enkapsulasi akses melalui `visit_access()` supaya pasien hanya melihat data miliknya.”

## Pertanyaan Tambahan

**Dosen:** “Apakah setiap role memakai empat pilar?”

**Jawaban:**

> “Tidak. Saya hanya memetakan pilar yang terlihat langsung pada source. Empat pilar paling lengkap terlihat pada alur Kasir.”

**Dosen:** “Apakah Tunai dan QRIS polymorphic?”

**Jawaban:**

> “Belum. Tunai dan QRIS masih berupa teks. Polymorphism yang nyata ada pada GeneralPayment dan BPJSPayment.”

**Dosen:** “Apakah Doctor mewarisi User?”

**Jawaban:**

> “Tidak. Doctor mempunyai user_id dan berelasi dengan User. Inheritance domain yang nyata ada pada strategi pembayaran.”

---

# KESIMPULAN AUDIT

## Pilar yang Ditemukan per Role

- **Admin:** Abstraksi dan Enkapsulasi.
- **Perawat:** Abstraksi dan Enkapsulasi.
- **Dokter:** Abstraksi dan Enkapsulasi.
- **Apoteker:** Abstraksi dan Enkapsulasi.
- **Kasir:** Abstraksi, Enkapsulasi, Inheritance, dan Polymorphism.
- **Pasien:** Abstraksi, Enkapsulasi, dan hasil Polymorphism pembayaran.

## Batas Implementasi yang Harus Disampaikan Jujur

- Role bukan class anak dari `User`.
- `Doctor` dan `Patient` berelasi dengan `User`, bukan mewarisinya.
- Tunai, Transfer, QRIS, dan Debit belum menjadi class payment terpisah.
- Aksi farmasi masih memakai percabangan `action`, bukan polymorphism.
- Tidak ada method `process_payment()`.
- Tidak ada method `racik_obat()`.
- Pasien tidak menerbitkan rujukan sendiri; Dokter mengajukan dan Admin memprosesnya.

## Konfirmasi Perubahan

Dokumen ini hanya mengaudit dan menjelaskan source.

Tidak ada perubahan pada:

- model;
- service;
- route;
- database;
- workflow;
- login/logout;
- UI;
- role; atau
- fitur aplikasi.
