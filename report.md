Nama : Ananda Dihan Naufal
NIM  : 11221055
Matkul : Sistem Terdistribusi


# Bagian Teori — UTS Sistem Terdistribusi (Bab 1–7)
Berdasarkan buku *Distributed Systems: Principles and Paradigms* (2nd ed.) oleh Andrew S. Tanenbaum & Maarten Van Steen (2007).

---

**Diagram sederhana**
```
Publisher  --HTTP-->  Aggregator (FastAPI + asyncio workers) --SQLite-->
                                 |-> /events, /stats
```

## T1 – Karakteristik Sistem Terdistribusi dan Trade-off pada Desain Pub-Sub Log Aggregator

Sistem terdistribusi didefinisikan oleh Tanenbaum dan Van Steen (2007) sebagai sekumpulan komputer independen yang tampak bagi pengguna sebagai satu sistem terpadu. Ciri utama sistem ini mencakup **konkurensi komponen**, **tidak adanya global clock**, dan **kegagalan yang bersifat independen**. Dalam konteks ini, setiap node dapat beroperasi sendiri, tetapi tetap berkoordinasi untuk mencapai tujuan bersama melalui komunikasi pesan. Keuntungan utama sistem terdistribusi adalah peningkatan **scalability**, **resource sharing**, dan **availability**, namun di sisi lain menimbulkan tantangan seperti **latency**, **consistency**, dan **fault tolerance**.

Pada desain Pub/Sub log aggregator, trade-off utama muncul antara **consistency** dan **availability**. Model Pub/Sub menuntut sistem tetap responsif meskipun terjadi gangguan pada salah satu komponen. Desainer sistem harus memutuskan sejauh mana sistem memprioritaskan *availability* (melayani semua permintaan walau data bisa sedikit tertunda) dibanding *strong consistency* (semua node memiliki state identik). Selain itu, terdapat kompromi antara **throughput** dan **ordering**: semakin tinggi kebutuhan ketertiban pesan (total ordering), semakin besar overhead komunikasi yang dibutuhkan. Dengan demikian, desain Pub/Sub aggregator harus menyeimbangkan efisiensi, reliabilitas, dan kesederhanaan arsitektur agar tetap memenuhi tujuan fungsional dalam lingkungan terdistribusi.  
*(Tanenbaum & Van Steen, 2007, Bab 1)*

---

## T2 – Perbandingan Arsitektur Client–Server dan Publish–Subscribe

Menurut Tanenbaum dan Van Steen (2007), arsitektur **client–server** beroperasi melalui hubungan langsung antara klien dan server, di mana server menyediakan layanan dan klien mengajukan permintaan. Model ini efektif untuk sistem dengan interaksi yang deterministik dan jumlah pengguna yang relatif stabil. Namun, ketika skala sistem bertambah dan jumlah klien meningkat secara signifikan, model ini menjadi tidak efisien karena menimbulkan bottleneck pada server pusat.

Sebaliknya, arsitektur **publish–subscribe** memisahkan pengirim (publisher) dan penerima (subscriber) melalui mekanisme *event bus* atau *broker*. Publisher tidak perlu mengetahui siapa subscriber-nya; ia cukup menerbitkan pesan ke topik tertentu. Arsitektur ini memungkinkan **loose coupling**, **scalability**, dan **asynchronous communication**. Dalam konteks log aggregator, pendekatan ini sangat relevan karena sistem harus mampu menerima aliran data dari berbagai sumber tanpa menunggu konsumen tertentu siap memprosesnya.

Dari sudut pandang desain sistem terdistribusi, Pub/Sub lebih unggul dalam hal **decoupling temporal dan spasial**, yaitu pengirim dan penerima tidak harus aktif pada waktu yang sama maupun berada di lokasi yang sama. Kekurangannya adalah meningkatnya kompleksitas dalam menjaga **reliability** dan **ordering** pesan. Namun, untuk sistem seperti log aggregator yang berorientasi pada throughput dan event-driven processing, model Pub/Sub memberikan keseimbangan ideal antara efisiensi dan skalabilitas.  
*(Tanenbaum & Van Steen, 2007, Bab 2)*

---

## T3 – At-least-once vs Exactly-once Delivery dan Pentingnya Idempotent Consumer

Dalam sistem terdistribusi, *message delivery semantics* menentukan bagaimana pesan dikirim dan diterima. Tanenbaum dan Van Steen (2007) menjelaskan tiga model utama: *at-most-once*, *at-least-once*, dan *exactly-once*.  
- *At-most-once* menjamin pesan tidak dikirim lebih dari satu kali, namun dapat hilang.  
- *At-least-once* memastikan pesan akhirnya diterima, meskipun bisa dikirim berulang kali.  
- *Exactly-once* menjamin pesan dikirim dan diproses tepat satu kali, namun memerlukan koordinasi dan biaya tinggi.

Dalam implementasi Pub/Sub log aggregator, pendekatan *at-least-once* lebih realistis karena jaringan dan proses dapat gagal sewaktu-waktu. Namun hal ini menimbulkan risiko **duplikasi pesan**. Untuk itu, diperlukan mekanisme **idempotent consumer**, yaitu konsumen yang memberikan hasil sama meski menerima pesan yang sama berulang kali. Dengan menerapkan kunci unik seperti `(topic, event_id)` dan menggunakan deduplication store persisten, sistem dapat memastikan tidak ada event yang diproses dua kali. Dengan demikian, idempotensi menjadi fondasi agar *at-least-once delivery* dapat memberikan efek *exactly-once* pada tingkat aplikasi.  
*(Tanenbaum & Van Steen, 2007, Bab 3)*

---

## T4 – Skema Penamaan Topic dan Event_ID serta Dampaknya terhadap Deduplication

Penamaan dalam sistem terdistribusi berfungsi sebagai sarana identifikasi dan lokalisasi objek. Menurut Tanenbaum dan Van Steen (2007), skema penamaan yang baik harus menjamin **keunikan**, **ketahanan terhadap benturan (collision-resistant)**, dan **independensi lokasi**. Dalam arsitektur Pub/Sub, *topic name* digunakan untuk mengelompokkan jenis pesan, sedangkan *event_id* bertugas mengidentifikasi event secara unik di dalam topik tersebut.

Salah satu strategi yang digunakan adalah penamaan topik secara hierarkis, misalnya `sensor.temp` atau `system.log.error`, yang memudahkan proses filtering dan routing. Sementara itu, `event_id` dapat dihasilkan menggunakan **UUID** agar probabilitas duplikasi mendekati nol. Kombinasi `(topic, event_id)` kemudian berperan sebagai **primary key** untuk sistem deduplication. Dengan menyimpan pasangan ini di dalam database persisten seperti SQLite, sistem dapat mendeteksi event yang telah diproses sebelumnya dan mencegah pemrosesan ulang.

Dampaknya terhadap deduplication sangat signifikan: skema penamaan yang unik dan konsisten memungkinkan konsumen untuk menegakkan **idempotency** tanpa memerlukan sinkronisasi global. Dengan demikian, walaupun pesan dapat dikirim lebih dari sekali oleh publisher, hasil akhir sistem tetap konsisten.  
*(Tanenbaum & Van Steen, 2007, Bab 4)*

---

## T5 – Ordering dalam Sistem Terdistribusi dan Pendekatan Praktis

Dalam sistem terdistribusi, Tanenbaum dan Van Steen (2007) menekankan bahwa **tidak adanya global clock** menyebabkan setiap node memiliki persepsi waktu yang berbeda. Hal ini menjadikan pengurutan (ordering) pesan sebagai tantangan utama. Ada beberapa jenis ordering:  
- **FIFO ordering** memastikan pesan dari satu pengirim diterima secara berurutan.  
- **Causal ordering** menjamin urutan pesan mengikuti hubungan sebab-akibat antar event.  
- **Total ordering** memastikan semua pesan diterima dalam urutan identik di setiap penerima.

Total ordering ideal tetapi mahal secara performa karena memerlukan sinkronisasi global. Dalam implementasi Pub/Sub log aggregator, ordering ketat biasanya tidak diperlukan. Pendekatan yang lebih praktis adalah menggunakan **timestamp** pada setiap event, digabungkan dengan **monotonic counter lokal** di sisi publisher. Hal ini memungkinkan sistem untuk merekonstruksi urutan relatif event dalam satu topik tanpa bergantung pada clock global. Meskipun metode ini memiliki batasan seperti *clock skew* dan keterlambatan jaringan, untuk sistem log aggregator yang fokus pada konsistensi eventual, pendekatan ini cukup efisien dan sederhana.  
*(Tanenbaum & Van Steen, 2007, Bab 5)*

---

## T6 – Failure Modes dan Strategi Mitigasi

Kegagalan dalam sistem terdistribusi dapat muncul dalam berbagai bentuk: **duplikasi pesan**, **pesan keluar dari urutan**, **node crash**, atau **kegagalan jaringan**. Tanenbaum dan Van Steen (2007) membedakan antara *transient failure* (sementara), *intermittent failure* (berulang), dan *permanent failure* (tetap). Dalam konteks Pub/Sub log aggregator, kegagalan semacam ini dapat menyebabkan kehilangan data atau pemrosesan berulang.

Untuk mengatasinya, sistem menerapkan beberapa strategi mitigasi. Pertama, **retry mechanism** dengan interval *exponential backoff* memastikan pesan dikirim ulang tanpa membebani jaringan. Kedua, **dedup store** yang tahan terhadap restart menjamin bahwa pesan duplikat tidak diproses ulang setelah recovery. Ketiga, penggunaan **asynchronous queue** memungkinkan sistem tetap beroperasi meski sebagian node gagal. Dengan kombinasi ini, sistem dapat mencapai **fault tolerance** tanpa bergantung pada konsensus global.  
*(Tanenbaum & Van Steen, 2007, Bab 6)*

---

## T7 – Eventual Consistency melalui Idempotency dan Deduplication

Konsistensi dalam sistem terdistribusi tidak selalu berarti keadaan yang sama di setiap node pada waktu yang sama. Tanenbaum dan Van Steen (2007) memperkenalkan konsep **eventual consistency**, di mana semua node akan konvergen ke state yang sama seiring waktu, asalkan tidak ada update baru yang dilakukan. Dalam Pub/Sub log aggregator, hal ini dicapai melalui kombinasi **idempotent consumer** dan **deduplication**.  

Ketika publisher mengirim pesan berulang, dedup store memastikan hanya event unik yang benar-benar diproses. Dengan demikian, meskipun terjadi pengiriman berulang, keadaan akhir sistem tetap konsisten. Pendekatan ini memungkinkan sistem mempertahankan **availability tinggi** tanpa mengorbankan integritas data, karena hasil akhir yang diamati akan sama seperti jika setiap event hanya diproses sekali. Idempotensi dan dedup bersama-sama membentuk dasar *eventual consistency* dalam arsitektur terdistribusi yang asinkron.  
*(Tanenbaum & Van Steen, 2007, Bab 7)*

---

## T8 – Metrik Evaluasi Sistem dan Kaitannya dengan Desain

Evaluasi sistem terdistribusi harus mencakup dimensi performa dan reliabilitas. Tanenbaum dan Van Steen (2007) menyoroti beberapa metrik utama: **throughput**, **latency**, **reliability**, dan **scalability**. Dalam konteks log aggregator, *throughput* mengukur jumlah event yang dapat diproses per detik, sementara *latency* mencerminkan waktu yang dibutuhkan dari penerimaan hingga penyimpanan event.  

Selain itu, **duplicate rate** dan **dedup efficiency** menjadi indikator penting untuk menilai efektivitas idempotensi. Semakin tinggi efisiensi deduplication, semakin baik sistem dalam mencegah pemrosesan ganda. Metrik lain seperti *uptime*, *error rate*, dan *queue utilization* membantu menilai stabilitas sistem saat beban tinggi.  

Keterkaitan antara metrik dan desain sangat erat: penggunaan batch besar meningkatkan throughput tetapi dapat menaikkan latency; penerapan total ordering memperkuat konsistensi tetapi menurunkan performa. Oleh karena itu, pengembang harus menyeimbangkan faktor-faktor tersebut sesuai kebutuhan aplikasi.  
*(Tanenbaum & Van Steen, 2007, Bab 1–7)*

---

## Daftar Pustaka

Tanenbaum, A. S., & Van Steen, M. (2007). *Distributed Systems: Principles and Paradigms* (2nd ed.). Pearson Education.
