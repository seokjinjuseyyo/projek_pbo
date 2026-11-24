# SOLID MEDIKA HUSADA

Dokumen ini menjelaskan penerapan SOLID pada aplikasi Flask utama di folder `clinic/`. Folder prototype `back/` tidak dipakai sebagai dasar refactor.

## RUANG LINGKUP AUDIT

- `app.py`: entry point sudah kecil dan hanya membuat serta menjalankan aplikasi; tidak perlu diubah.
- `clinic/__init__.py`: application factory, extension Flask, compatibility schema existing, dan startup data diperiksa. Pembuatan index SIP dibuat idempoten agar factory aman dipanggil berulang.
- `clinic/models.py`: model dan relasi SQLAlchemy diperiksa. Relasi `User`–`Doctor` dan `User`–`Patient` tetap memakai foreign key; tidak dipaksa menjadi inheritance. File tidak diubah.
- `clinic/services.py`: seluruh service appointment, workflow, farmasi, billing, pasien, notifikasi, rujukan, stok, dan pembelian diperiksa.
- `clinic/routes.py`: route klinik aktif diperiksa. Business logic rujukan serta pembelian pemasok yang panjang dipindahkan secara minimal ke service.
- `seed.py`: seed idempoten diperiksa; hanya cara memanggil object `billing_service` yang disesuaikan. Seed tidak dijalankan pada database existing.
- `clinic/clock.py` dan test aplikasi utama diperiksa sebagai dependency yang benar-benar dipakai.
- Folder `back/`, `front/`, dan file prototype/legacy tidak dijadikan sumber implementasi utama.

## SOLID AUDIT BEFORE REFACTOR

### S — Single Responsibility Principle

- Sudah ada: `AppointmentService`, `WorkflowService`, `PharmacyService`, `BillingService`, dan `NotificationService` sudah dipisahkan menurut bagian pekerjaan klinik.
- Masalah: `WorkflowService.nurse()` dan `WorkflowService.examine()` masih melakukan validasi semua input sekaligus mengatur perubahan alur dan membuat model. Alur rujukan serta pembelian pemasok juga masih ditulis panjang di route.

### O — Open/Closed Principle

- Sudah ada: pembayaran sudah memiliki `PaymentProcessor`, `GeneralPayment`, dan `BPJSPayment`.
- Masalah: `BillingService` masih memilih `GeneralPayment()` atau `BPJSPayment()` secara langsung di dua method. Penambahan strategi penanggung baru mengharuskan perubahan pada service inti.

### L — Liskov Substitution Principle

- Sudah ada: `GeneralPayment` dan `BPJSPayment` memiliki method `amounts(total)` dengan bentuk hasil yang sama.
- Masalah: kontrak hasil dan pemilihan implementasi belum diuji secara khusus melalui tipe induk `PaymentProcessor`.

### I — Interface Segregation Principle

- Sudah ada: `PaymentProcessor` adalah kontrak kecil yang hanya meminta method `amounts()`.
- Masalah: belum ada kontrak kecil untuk komponen yang bertugas memilih processor. `BillingService` mengambil alih pemilihan concrete class.

### D — Dependency Inversion Principle

- Sudah ada: perhitungan tagihan memanggil nama method umum `amounts()`.
- Masalah: `BillingService.invoice()` dan `BillingService.pay()` masih bergantung langsung pada `GeneralPayment` dan `BPJSPayment`, bukan pada resolver/abstraksi yang dapat diinjeksi.

## S — Single Responsibility Principle

### Apa artinya?

Satu class sebaiknya fokus mengurus satu jenis pekerjaan.

### Implementasi di Medika Husada

File: `clinic/validators.py`

Class dan method:

- `NursingAssessmentValidator.validate()` memvalidasi tanda vital dan input pemeriksaan awal.
- `DoctorExaminationValidator.validate()` memvalidasi data pemeriksaan dokter.
- `PrescriptionValidator.validate()` memvalidasi item resep, obat, jumlah, dan aturan pakai.

File: `clinic/services.py`

Class dan method:

- `WorkflowService.nurse()` mengatur alur pemeriksaan Perawat.
- `WorkflowService.examine()` mengatur alur pemeriksaan Dokter.
- `ReferralService` mengatur lifecycle pengajuan, penerbitan, penolakan, arsip, dan tanda tangan rujukan.
- `InventoryService.save_medicine()` mengatur data obat dan perubahan stok manual.
- `SupplierPurchaseService` mengatur pengajuan dan keputusan pembelian pemasok.
- `NotificationService` tetap fokus membuat notifikasi. Tidak dibuat interface tambahan karena saat ini hanya ada satu cara menyimpan notifikasi.

File: `clinic/routes.py`

Route rujukan, obat, dan pembelian pemasok sekarang hanya mengambil object/input, memanggil service, lalu memakai helper `mutate()` untuk commit, flash, dan redirect.

### Kenapa termasuk SRP?

Validator tidak mengubah status kunjungan. `WorkflowService` tidak lagi berisi detail rentang setiap tanda vital atau detail validasi setiap item resep. Route juga tidak lagi menjalankan seluruh aturan bisnis rujukan dan pembelian pemasok.

### Sebelum refactor

`WorkflowService.nurse()` dan `examine()` mengurus validasi sekaligus alur. Beberapa route mengubah banyak model dan stok secara langsung.

### Setelah refactor

Validator mengurus validasi, service mengatur workflow, dan route mengurus HTTP. Pemisahan hanya dibuat pada bagian yang memang memiliki pekerjaan berbeda.

---

## O — Open/Closed Principle

### Apa artinya?

Kalau kita mau menambah jenis baru, sebisa mungkin tidak perlu merusak kode lama.

### Implementasi di Medika Husada

File: `clinic/payments.py`

Class dan method:

- `PaymentProcessorRegistry.register(coverage_type, processor_type)` mendaftarkan strategi.
- `PaymentProcessorRegistry.resolve(appointment)` memilih strategi.
- `create_default_payment_resolver()` mendaftarkan `general` dan `bpjs` sebagai konfigurasi bawaan.

File: `tests/test_solid.py`

Method:

- `test_payment_registry_is_open_for_an_additional_strategy()` menambahkan contoh `CorporatePayment` melalui registry tanpa mengubah `BillingService`.

### Kenapa termasuk OCP?

Strategi penanggung baru dapat dibuat sebagai turunan `PaymentProcessor`, lalu didaftarkan ke registry. Perhitungan invoice dan pembayaran di `BillingService` tidak perlu diberi kondisi baru untuk concrete class tersebut.

Tunai, Transfer, QRIS, dan Debit tetap berupa metode transaksi. Keempatnya sengaja tidak dibuat menjadi class karena berbeda dari pihak yang menanggung tagihan.

### Sebelum refactor

`BillingService` mempunyai kondisi langsung: BPJS membuat `BPJSPayment()`, selain itu membuat `GeneralPayment()`. Kondisi itu ditulis di `invoice()` dan `pay()`.

### Setelah refactor

Pemilihan processor berada pada registry/resolver. `BillingService` hanya meminta resolver memberikan sebuah `PaymentProcessor`.

---

## L — Liskov Substitution Principle

### Apa artinya?

Class anak harus tetap bisa dipakai sebagai pengganti class induknya.

### Implementasi di Medika Husada

File: `clinic/interfaces.py`

Class dan method:

- `PaymentProcessor.amounts(total)` mendefinisikan kontrak yang sama untuk semua strategi.

File: `clinic/payments.py`

Class dan method:

- `GeneralPayment.amounts(total)` mengembalikan `(0, total)`.
- `BPJSPayment.amounts(total)` mengembalikan `(total, 0)`.

File: `tests/test_solid.py`

Method:

- `test_payment_processors_follow_the_same_contract()` menjalankan pengujian yang sama terhadap kedua class melalui kontrak `PaymentProcessor`.

### Kenapa termasuk LSP?

Kedua class menerima parameter `total` yang sama dan selalu mengembalikan tuple `(coverage, payable)`. Keduanya memakai validasi total yang sama. Nilai `coverage + payable` tetap sama dengan total. Pemanggil tidak perlu mengetahui apakah object konkret adalah General atau BPJS.

### Sebelum refactor

Signature kedua class sudah sama, tetapi contract hasil hanya tersirat dan belum punya regression test khusus.

### Setelah refactor

Contract ditulis jelas pada `PaymentProcessor`, validasi total dipakai bersama, dan substitusi kedua implementasi diuji.

---

## I — Interface Segregation Principle

### Apa artinya?

Jangan paksa class memiliki fungsi yang tidak dibutuhkannya.

### Implementasi di Medika Husada

File: `clinic/interfaces.py`

Class dan method:

- `PaymentProcessor` hanya meminta `amounts()`.
- `PaymentProcessorResolver` hanya meminta `resolve()`.

File: `tests/test_solid.py`

Method:

- `test_payment_interfaces_remain_small_and_specific()` memastikan masing-masing interface tetap mempunyai satu abstract method.

### Kenapa termasuk ISP?

Strategi pembayaran tidak dipaksa mengetahui cara memilih strategi. Resolver juga tidak dipaksa membuat invoice atau menyimpan pembayaran. Tidak ada interface besar seperti `ClinicService` yang memuat semua pekerjaan klinik.

### Sebelum refactor

`PaymentProcessor` sudah kecil, tetapi pekerjaan pemilihan concrete class masih berada di `BillingService`.

### Setelah refactor

Kontrak perhitungan dan kontrak pemilihan dipisah menjadi dua interface kecil sesuai kebutuhan pemakainya.

---

## D — Dependency Inversion Principle

### Apa artinya?

Bagian penting program jangan terlalu bergantung pada satu implementasi konkret.

### Implementasi di Medika Husada

File: `clinic/services.py`

Class dan method:

- `BillingService.__init__(processor_resolver)` menerima dependency bertipe `PaymentProcessorResolver`.
- `BillingService._amounts(appointment, total)` meminta resolver dan hanya memanggil kontrak `amounts()`.
- `billing_service` adalah object yang dirangkai dengan resolver bawaan di bagian komposisi aplikasi.

File: `clinic/interfaces.py`

Class:

- `PaymentProcessorResolver` adalah abstraksi yang menjadi dependency `BillingService`.

File: `tests/test_solid.py`

Method:

- `test_billing_service_depends_on_payment_resolver_contract()` menyuntikkan `StubResolver` ke `BillingService` tanpa memakai registry produksi.

### Kenapa termasuk DIP?

`BillingService` tidak lagi membuat `GeneralPayment` atau `BPJSPayment`. Service tingkat tinggi menerima resolver melalui constructor dan bekerja lewat kontrak.

### Sebelum refactor

`BillingService` terikat langsung pada dua concrete class dan memilihnya sendiri.

### Setelah refactor

Concrete class dirangkai di luar `BillingService`. Test dapat memberikan resolver pengganti tanpa mengubah source billing.

## SOLID AUDIT AFTER REFACTOR

### S

- Implementasi: validasi klinis dipisahkan; workflow rujukan, inventori, dan pembelian pemasok dipindahkan dari route.
- File: `clinic/validators.py`, `clinic/services.py`, `clinic/routes.py`.
- Class/method: tiga validator, `WorkflowService.nurse()`, `WorkflowService.examine()`, `ReferralService`, `InventoryService`, `SupplierPurchaseService`.
- Alasan: masing-masing bagian mempunyai satu fokus yang jelas.
- Perubahan: ekstraksi logic saja; status, URL, flash, redirect, dan urutan workflow tetap.

### O

- Implementasi: registry processor pembayaran.
- File: `clinic/payments.py`.
- Class/method: `PaymentProcessorRegistry.register()` dan `resolve()`.
- Alasan: strategi dapat ditambahkan melalui registrasi.
- Perubahan: kondisi concrete class di `BillingService` dihapus.

### L

- Implementasi: General dan BPJS mengikuti contract hasil yang sama.
- File: `clinic/interfaces.py`, `clinic/payments.py`, `tests/test_solid.py`.
- Class/method: `PaymentProcessor.amounts()`, `GeneralPayment.amounts()`, `BPJSPayment.amounts()`.
- Alasan: kedua object dapat menggantikan tipe induk dan melewati pengujian yang sama.
- Perubahan: contract dipertegas dan diuji; hasil bisnis tetap sama.

### I

- Implementasi: dua interface pembayaran yang kecil.
- File: `clinic/interfaces.py`.
- Class/method: `PaymentProcessor.amounts()` dan `PaymentProcessorResolver.resolve()`.
- Alasan: processor hanya menghitung, resolver hanya memilih.
- Perubahan: tidak dibuat interface untuk setiap service yang hanya mempunyai satu implementasi.

### D

- Implementasi: constructor injection pada `BillingService`.
- File: `clinic/services.py` dan `clinic/interfaces.py`.
- Class/method: `BillingService.__init__()` dan `_amounts()`.
- Alasan: billing bergantung pada abstraksi resolver.
- Perubahan: pembuatan General/BPJS dipindahkan ke composition melalui `create_default_payment_resolver()`.

## PEMETAAN PER ROLE

### Admin / Komang

Verifikasi appointment:

`POST /appointments/<id>/verify` → `AppointmentService.verify()` → update status appointment → membuat/memperbarui `Visit` dan nomor antrean.

Ini mengikuti SRP karena route menangani HTTP, sedangkan aturan verifikasi berada di service. Pada rujukan dan pembelian pemasok, route juga memanggil `ReferralService` atau `SupplierPurchaseService`.

### Perawat / Gea

Pemeriksaan awal:

`POST /visits/<id>/nursing` → `WorkflowService.nurse()` → `NursingAssessmentValidator.validate()` → `WorkflowService.transition()`.

Ini adalah SRP: validator memeriksa angka, sedangkan workflow menyimpan assessment dan memindahkan status.

### Dokter Fakih

Pemeriksaan dan resep:

`POST /visits/<id>/examination` → `WorkflowService.examine()` → `DoctorExaminationValidator` + `PrescriptionValidator` → status Farmasi atau Pembayaran.

Dokter Fakih juga dapat membuat permintaan rujukan melalui `ReferralService.request()`. Route memastikan Dokter hanya membuka visit miliknya.

### Dokter Alia

Dokter Alia memakai alur class yang sama dengan Dokter Fakih. Object dokter dan visit berbeda, tetapi contract workflow tetap sama. Tidak dibuat class khusus Alia karena aturan pekerjaannya sama dan class tambahan tidak memberi manfaat.

### Apoteker / Bintang

Proses resep:

`POST /visits/<id>/pharmacy/<action>` → `PharmacyService.process()` → `WorkflowService.transition()` → `Medicine.change_stock()` saat obat siap.

SRP terlihat karena route tidak mengurangi stok sendiri. Pengajuan pembelian pemasok ditangani `SupplierPurchaseService`.

### Kasir / Fatur

Pembayaran:

`POST /visits/<id>/pay` → `billing_service.pay()` → `PaymentProcessorResolver.resolve()` → `PaymentProcessor.amounts()`.

Di sini OCP, LSP, ISP, dan DIP dipakai secara nyata. General/BPJS dapat saling menggantikan sebagai processor. Tunai/Transfer/QRIS/Debit tetap menjadi cara transaksi dan tidak dicampur dengan penanggung tagihan.

### Pasien

Booking:

`POST /appointments/new` → `AppointmentService.book()` → validasi slot/BPJS → notifikasi.

Ini mengikuti SRP karena route tidak mengatur slot atau status. Ketika invoice dibuat, pilihan General/BPJS memengaruhi `coverage` dan `payable`, tetapi Pasien tidak perlu mengetahui concrete processor.

## VALIDASI REGRESSION

### Sebelum refactor

- Suite aplikasi utama: `1 passed, 1 failed, 20 errors`.
- Penyebab utama setup error: `create_app()` menempelkan index `uq_user_sip` berulang kali pada metadata saat fixture membuat aplikasi baru.
- Test workflow lama juga memakai akun `admin` dan pembayaran oleh Admin, sedangkan seed/route aktif memakai Komang dan Kasir/Fatur.
- Suite gabungan juga sudah mempunyai kegagalan prototype FastAPI karena request Tunai tidak mengirim `cash_received`.

### Setelah refactor

- `python -m pytest -q tests`: **28 passed**.
- Cakupan: landing, login/logout enam role, halaman role, booking, verifikasi, antrean, nursing, dokter, resep, farmasi, stok atomik, rujukan, invoice, General, BPJS, pembayaran Fatur, receipt, registrasi, authorization, dan restart database test.
- `python scripts/browser_login_check.py`: **lulus** untuk Admin, Dokter, Perawat, Apoteker, Pasien, dan Kasir pada lebar 1366, 768, dan 375 px; login/logout kembali ke landing; tanpa error JavaScript.
- `python -m pytest -q`: **32 passed, 1 failed**. Satu kegagalan tetap berada di prototype `back/tests/test_api.py`, bukan aplikasi utama, dengan penyebab baseline yang sama: payload Tunai tidak mengirim `cash_received`.

### Keamanan database dan UI

- Semua test workflow memakai database sementara.
- `instance/medika.db` tidak dihapus, tidak di-reset, tidak di-seed ulang, dan timestamp-nya tetap `28 Oktober 2026 21:58:26`.
- Tidak ada migration atau perubahan schema.
- Tidak ada file HTML, CSS, JavaScript frontend, gambar, atau template yang diubah.
- URL frontend dan urutan status Pasien → Admin → Perawat → Dokter → Apoteker → Kasir → Selesai tetap sama.

# FILE YANG DIBUKA SAAT PRESENTASI

## S — SRP

File: `clinic/validators.py` dan `clinic/services.py`

Class: `NursingAssessmentValidator`, `DoctorExaminationValidator`, `PrescriptionValidator`, `WorkflowService`

Method: `validate()`, `nurse()`, `examine()`

Kenapa: validasi dan pengaturan workflow tidak lagi dicampur dalam satu method panjang.

## O — OCP

File: `clinic/payments.py`

Class: `PaymentProcessorRegistry`

Method: `register()` dan `resolve()`

Kenapa: strategi baru didaftarkan tanpa mengubah `BillingService`.

## L — LSP

File: `clinic/interfaces.py` dan `clinic/payments.py`

Class: `PaymentProcessor`, `GeneralPayment`, `BPJSPayment`

Method: `amounts(total)`

Kenapa: dua class anak menerima input dan menghasilkan bentuk output yang sama.

## I — ISP

File: `clinic/interfaces.py`

Class: `PaymentProcessor`, `PaymentProcessorResolver`

Method: `amounts()` dan `resolve()`

Kenapa: setiap interface hanya mempunyai satu fungsi yang benar-benar diperlukan.

## D — DIP

File: `clinic/services.py`

Class: `BillingService`

Method: `__init__()` dan `_amounts()`

Kenapa: `BillingService` menerima `PaymentProcessorResolver`, bukan membuat concrete processor sendiri.

# CHEAT SHEET

Dosen: “Mana SRP?”

Jawaban: “Buka `clinic/validators.py` dan `WorkflowService` di `clinic/services.py`. Validator hanya memeriksa input, sedangkan workflow hanya mengatur proses dan status. Logic rujukan dan pembelian pemasok juga sudah keluar dari route.”

Dosen: “Mana OCP?”

Jawaban: “Buka `PaymentProcessorRegistry.register()` di `clinic/payments.py`. Strategi baru bisa didaftarkan tanpa mengubah `BillingService`. Buktinya ada contoh `CorporatePayment` di `tests/test_solid.py`.”

Dosen: “Mana LSP?”

Jawaban: “`GeneralPayment` dan `BPJSPayment` sama-sama dapat dipakai sebagai `PaymentProcessor`. Keduanya menerima `total` dan mengembalikan `(coverage, payable)` dengan jumlah tetap sama dengan total.”

Dosen: “Mana ISP?”

Jawaban: “Buka `clinic/interfaces.py`. `PaymentProcessor` hanya punya `amounts()`, dan `PaymentProcessorResolver` hanya punya `resolve()`. Tidak ada interface besar yang memaksa class mengurus seluruh klinik.”

Dosen: “Mana DIP?”

Jawaban: “Buka constructor `BillingService`. Billing menerima abstraction `PaymentProcessorResolver`. Pemilihan General atau BPJS dilakukan resolver di luar BillingService.”
