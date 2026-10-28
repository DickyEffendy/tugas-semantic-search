# Semantic Search & Vector Database

## Project Information

**Nama Project:** Semantic Search untuk Konsep Teknologi

**Tema Dataset:** Konsep AI dan Machine Learning, Backend API, Frontend,
Database, dan Data Science.

**Deskripsi Singkat:**

Project ini membangun aplikasi pencarian semantik berbahasa Indonesia
menggunakan Python, FastAPI, Sentence Transformers, dan Qdrant. Aplikasi
mengubah dokumen dan pertanyaan pengguna menjadi embedding, kemudian
mencari dokumen dengan kedekatan vektor paling tinggi. Sistem
mengembalikan teks, kategori, dan similarity score untuk setiap hasil.

## Dataset

### Jumlah Data

Dataset berisi **30 dokumen**. Setiap dokumen mempunyai field `text` dan
`category`. Setiap kategori berisi enam dokumen.

### Kategori yang Digunakan

  Kategori                    Jumlah data
  ------------------------- -------------
  AI dan Machine Learning               6
  Backend API                           6
  Frontend                              6
  Database                              6
  Data Science                          6
  **Total**                        **30**

### Kenapa memilih dataset tersebut?

Saya memilih topik teknologi karena konsep AI, pengembangan aplikasi,
database, dan data science mempunyai istilah yang saling berhubungan,
tetapi tetap memiliki fokus berbeda. Kondisi ini cocok untuk menguji
apakah sistem dapat menemukan dokumen yang sesuai ketika pengguna
memakai kalimat yang berbeda dari teks dataset. Topik ini juga
memudahkan saya menguji hasil yang relevan dan hasil yang tidak relevan.

## Tech Stack

  ---------------------------------------------------------------------------------------------------
  Teknologi                                                       Fungsi
  --------------------------------------------------------------- -----------------------------------
  Python 3.11.7                                                   Bahasa pemrograman aplikasi

  FastAPI                                                         Membuat API untuk indexing,
                                                                  pencarian, dan pemeriksaan status

  Uvicorn                                                         Menjalankan server FastAPI

  Sentence Transformers                                           Mengubah dokumen dan query menjadi
                                                                  embedding

  `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`   Model embedding yang digunakan

  Qdrant Client                                                   Menghubungkan aplikasi Python
                                                                  dengan vector database

  Qdrant local persistent storage                                 Menyimpan vektor dan payload pada
                                                                  penyimpanan lokal

  Cosine similarity                                               Metrik untuk membandingkan
                                                                  kedekatan vektor

  JSON                                                            Format penyimpanan dataset awal

  Swagger UI                                                      Menguji endpoint melalui browser
  ---------------------------------------------------------------------------------------------------

## Application Flow

### Proses indexing

``` text
Dataset (data.json)
        ↓
Embedding Model
        ↓
Vector Embedding
        ↓
Qdrant
```

Aplikasi membaca 30 dokumen dari `data.json`. Model embedding mengubah
setiap teks menjadi deretan angka yang mewakili karakteristik maknanya.
Aplikasi kemudian menyimpan vektor tersebut di collection Qdrant. Setiap
point juga menyimpan payload yang berisi teks asli dan kategori dokumen.

### Proses pencarian

``` text
User Query
    ↓
Embedding Model
    ↓
Query Vector
    ↓
Qdrant Search
    ↓
Top-K Results
```

Saat pengguna mengirim pertanyaan, aplikasi menggunakan model embedding
yang sama untuk mengubah pertanyaan menjadi vektor. Qdrant membandingkan
vektor query dengan vektor dokumen yang tersimpan menggunakan metrik
cosine. Sistem lalu mengembalikan sejumlah hasil sesuai nilai `top_k`.
Respons API berisi teks, kategori, dan similarity score.

## Embedding Model

**Model yang digunakan:**

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

### Fungsi embedding model pada project ini

Embedding model mengubah teks menjadi representasi numerik agar aplikasi
dapat membandingkan kedekatan makna antara pertanyaan pengguna dan
dokumen. Model yang sama memproses dokumen saat indexing dan query saat
pencarian. Karena itu, sistem dapat menemukan dokumen yang relevan
meskipun susunan kata pada query berbeda dari teks dokumen.

Hasil indexing aktual menunjukkan dimensi embedding **384**. Model ini
tidak menjamin setiap hasil selalu relevan. Kualitas hasil juga
bergantung pada isi dataset, rumusan query, dan kemampuan model
merepresentasikan hubungan makna.

## Vector Database

### Apa fungsi Qdrant pada aplikasi?

Qdrant menyimpan embedding dokumen dan mencari vektor yang paling dekat
dengan embedding query. Dalam project ini, Qdrant berjalan dengan mode
**local persistent storage**, sehingga aplikasi tidak memerlukan server
Qdrant terpisah atau Docker. Pengujian setelah server dimulai ulang
menunjukkan collection masih tersedia dan 30 data tetap tersimpan.

Collection yang digunakan bernama `semantic_search_collection` dengan
metrik `COSINE`.

### Apa saja data yang disimpan di payload?

Payload setiap point menyimpan dua field:

-   `text`: teks asli dokumen.
-   `category`: kategori dokumen.

Setiap point juga memiliki ID dan vector embedding. ID dan vector
merupakan bagian dari point Qdrant, bukan field payload.

## API Endpoint

  -----------------------------------------------------------------------
  Method                  Endpoint                Fungsi
  ----------------------- ----------------------- -----------------------
  GET                     `/`                     Menampilkan informasi
                                                  dasar aplikasi dan rute
                                                  utama

  GET                     `/health`               Memeriksa status
                                                  aplikasi, collection,
                                                  dan jumlah data

  POST                    `/index`                Mengubah dataset
                                                  menjadi embedding dan
                                                  menyimpannya di Qdrant

  POST                    `/search`               Mencari dokumen
                                                  berdasarkan kedekatan
                                                  vektor
  -----------------------------------------------------------------------

### Cara menjalankan aplikasi

1.  Buka folder `tugas-semantic-search` di VS Code.

2.  Buat virtual environment dengan Python 3.11:

    ``` powershell
    py -3.11 -m venv .venv
    ```

3.  Aktifkan virtual environment di PowerShell:

    ``` powershell
    .\.venv\Scripts\Activate.ps1
    ```

    Jika PowerShell memblokir script, jalankan perintah berikut untuk
    sesi terminal saat ini, kemudian aktifkan ulang environment:

    ``` powershell
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    .\.venv\Scripts\Activate.ps1
    ```

4.  Pasang dependency:

    ``` powershell
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    ```

5.  Jalankan server:

    ``` powershell
    python -m uvicorn main:app --host 127.0.0.1 --port 8000
    ```

6.  Buka `http://127.0.0.1:8000/docs` di browser. Jalankan `POST /index`
    sebelum melakukan pencarian pertama. Pada pemakaian awal, komputer
    perlu mengunduh model embedding dari internet.

Biarkan server tetap berjalan selama pengujian. Untuk menghentikannya,
tekan `Ctrl+C` pada terminal server.

## Example Request

Request berikut benar-benar digunakan saat pengujian melalui Swagger UI.
Query ini meminta dokumen tentang penyimpanan data terstruktur dan
hubungan antartabel.

``` json
{
  "query": "Bagaimana cara menyimpan informasi terstruktur dan menghubungkan data antar tabel?",
  "top_k": 3
}
```

## Example Response

Berikut response aktual dari aplikasi pada pengujian tersebut. Nilai
score berasal dari respons API, bukan angka contoh.

``` json
{
  "query": "Bagaimana cara menyimpan informasi terstruktur dan menghubungkan data antar tabel?",
  "top_k_requested": 3,
  "result_count": 3,
  "results": [
    {
      "text": "Database relasional menyimpan data dalam tabel yang memiliki baris, kolom, kunci, dan hubungan antar tabel.",
      "category": "Database",
      "score": 0.8039
    },
    {
      "text": "SQL digunakan untuk membaca, menambah, mengubah, dan menghapus data dalam sistem basis data relasional.",
      "category": "Database",
      "score": 0.5672
    },
    {
      "text": "Indeks database mempercepat pencarian baris tertentu dengan struktur tambahan, tetapi membutuhkan ruang penyimpanan dan biaya saat data berubah.",
      "category": "Database",
      "score": 0.5458
    }
  ]
}
```

## Experiment 1 - Semantic Search

Setiap query dijalankan melalui endpoint `POST /search` dengan
`top_k = 3`. Penilaian relevansi berikut membandingkan maksud pertanyaan
dengan hasil peringkat pertama. Similarity score merupakan skor
kedekatan vektor, bukan probabilitas bahwa jawaban benar.

### Query 1

**Query:**

> Bagaimana menemukan kalimat dengan arti serupa meskipun menggunakan
> kata yang berbeda?

**Top Result:** "Semantic search mencari dokumen berdasarkan kedekatan
makna, meskipun kata-kata pada pertanyaan berbeda dari isi dokumen."

**Kategori:** AI dan Machine Learning

**Similarity Score:** `0.4653`

**Apakah hasilnya relevan? Kenapa?**

Ya. Hasil tersebut menjelaskan prinsip semantic search yang dicari dalam
pertanyaan, yaitu menemukan dokumen berdasarkan makna meskipun
kata-katanya tidak sama persis.

### Query 2

**Query:**

> Saya ingin membuat server web Python dengan dokumentasi endpoint
> otomatis.

**Top Result:** "Endpoint API adalah alamat dan metode HTTP yang
digunakan klien untuk meminta atau mengirim data ke server."

**Kategori:** Backend API

**Similarity Score:** `0.5774`

**Apakah hasilnya relevan? Kenapa?**

Hasil ini cukup relevan karena menjelaskan endpoint API yang digunakan
server. Namun, hasil peringkat kedua, yaitu "FastAPI adalah framework
Python untuk membangun layanan backend dan REST API dengan validasi data
serta dokumentasi otomatis." dengan score `0.5359`, lebih langsung
menjawab kebutuhan tentang server Python dan dokumentasi otomatis.
Pengujian ini menunjukkan bahwa score tertinggi tidak selalu menandai
dokumen yang paling tepat untuk kebutuhan spesifik pengguna.

### Query 3

**Query:**

> Teknologi apa yang cocok untuk membuat tampilan situs interaktif dan
> responsif?

**Top Result:** "Responsive design menyesuaikan tata letak situs dengan
ukuran layar ponsel, tablet, dan komputer."

**Kategori:** Frontend

**Similarity Score:** `0.6331`

**Apakah hasilnya relevan? Kenapa?**

Ya. Responsive design berkaitan langsung dengan tampilan situs yang
responsif. Dua hasil berikutnya juga relevan: JavaScript membahas
interaktivitas halaman, sedangkan CSS mengatur tata letak dan
responsivitas.

### Query 4

**Query:**

> Bagaimana cara menyimpan informasi terstruktur dan menghubungkan data
> antar tabel?

**Top Result:** "Database relasional menyimpan data dalam tabel yang
memiliki baris, kolom, kunci, dan hubungan antar tabel."

**Kategori:** Database

**Similarity Score:** `0.8039`

**Apakah hasilnya relevan? Kenapa?**

Ya. Hasil pertama secara langsung menjelaskan tabel, kunci, dan hubungan
antartabel. Hasil kedua tentang SQL dan hasil ketiga tentang indeks
database juga masih berhubungan dengan pengelolaan basis data, meskipun
tidak menjawab pertanyaan sejelas hasil pertama.

### Query 5

**Query:**

> Metode apa yang digunakan untuk mengukur seberapa baik model
> klasifikasi membuat prediksi?

**Top Result:** "Model klasifikasi memprediksi kelas seperti spam atau
bukan spam berdasarkan pola yang dipelajari dari data pelatihan."

**Kategori:** AI dan Machine Learning

**Similarity Score:** `0.6423`

**Apakah hasilnya relevan? Kenapa?**

Hasil pertama masih berkaitan dengan model klasifikasi, tetapi belum
langsung menjelaskan cara mengukur performanya. Hasil peringkat kedua
lebih tepat, yaitu "Metrik evaluasi seperti precision, recall, F1-score,
dan accuracy membantu menilai performa model klasifikasi." dengan score
`0.6143`. Hasil ini menunjukkan bahwa urutan score tidak selalu sama
dengan urutan kegunaan jawaban untuk pertanyaan tertentu.

## Experiment 2 - Top-K

### Query

> Bagaimana cara menyimpan informasi terstruktur dan menghubungkan data
> antar tabel?

### Top-K = 1

**Actual Result:**

1.  Database relasional menyimpan data dalam tabel yang memiliki baris,
    kolom, kunci, dan hubungan antar tabel. Kategori: Database.
    Similarity score: `0.8039`.

### Top-K = 3

**Actual Result:**

1.  Database relasional menyimpan data dalam tabel yang memiliki baris,
    kolom, kunci, dan hubungan antar tabel. Kategori: Database.
    Similarity score: `0.8039`.
2.  SQL digunakan untuk membaca, menambah, mengubah, dan menghapus data
    dalam sistem basis data relasional. Kategori: Database. Similarity
    score: `0.5672`.
3.  Indeks database mempercepat pencarian baris tertentu dengan struktur
    tambahan, tetapi membutuhkan ruang penyimpanan dan biaya saat data
    berubah. Kategori: Database. Similarity score: `0.5458`.

### Top-K = 5

**Actual Result:**

1.  Database relasional menyimpan data dalam tabel yang memiliki baris,
    kolom, kunci, dan hubungan antar tabel. Kategori: Database.
    Similarity score: `0.8039`.
2.  SQL digunakan untuk membaca, menambah, mengubah, dan menghapus data
    dalam sistem basis data relasional. Kategori: Database. Similarity
    score: `0.5672`.
3.  Indeks database mempercepat pencarian baris tertentu dengan struktur
    tambahan, tetapi membutuhkan ruang penyimpanan dan biaya saat data
    berubah. Kategori: Database. Similarity score: `0.5458`.
4.  Pandas membantu membersihkan, menggabungkan, mengubah, dan
    menganalisis data tabular menggunakan struktur DataFrame. Kategori:
    Data Science. Similarity score: `0.5249`.
5.  Visualisasi data menyajikan pola melalui grafik seperti diagram
    batang, grafik garis, histogram, dan scatter plot. Kategori: Data
    Science. Similarity score: `0.4657`.

### Apa perubahan yang terlihat ketika nilai Top-K diperbesar?

Saat `top_k` berubah dari 1 menjadi 3 dan 5, jumlah dokumen yang
dikembalikan meningkat. Tiga hasil pertama tetap sama, lalu Top-K = 5
menambahkan dua dokumen dari kategori Data Science.

### Apakah menambah Top-K selalu membuat hasil pencarian lebih baik?

Tidak. Top-K yang lebih besar memberikan lebih banyak pilihan, tetapi
tidak menjamin semua dokumen tambahan relevan. Pada pengujian ini, hasil
keempat dan kelima masih berhubungan secara umum dengan pengolahan
informasi, tetapi tidak menjawab pertanyaan tentang hubungan antartabel
secara langsung.

## Experiment 3 - Bad Retrieval

### Query

> Apa resep nasi goreng yang enak untuk makan malam?

### Actual Results

  --------------------------------------------------------------------------
  Peringkat        Hasil              Kategori              Similarity Score
  ---------------- ------------------ ---------------- ---------------------
  1                Pandas membantu    Data Science                  `0.1459`
                   membersihkan,                       
                   menggabungkan,                      
                   mengubah, dan                       
                   menganalisis data                   
                   tabular                             
                   menggunakan                         
                   struktur                            
                   DataFrame.                          

  2                Machine learning   AI dan Machine                `0.1241`
                   memungkinkan       Learning         
                   komputer                            
                   mempelajari pola                    
                   dari contoh data                    
                   untuk membuat                       
                   prediksi atau                       
                   keputusan tanpa                     
                   aturan yang                         
                   ditulis satu per                    
                   satu.                               

  3                Primary key adalah Database                      `0.1191`
                   kolom atau                          
                   gabungan kolom                      
                   yang                                
                   mengidentifikasi                    
                   setiap baris                        
                   secara unik dalam                   
                   tabel.                              
  --------------------------------------------------------------------------

### Kenapa hasil tersebut kurang relevan?

Ketiga hasil tidak menjawab pertanyaan tentang resep nasi goreng. Hasil
pertama membahas pengolahan data, hasil kedua membahas machine learning,
dan hasil ketiga menjelaskan primary key pada database. Skor teratas
hanya `0.1459`, jauh di bawah skor beberapa query yang relevan dalam
eksperimen ini.

### Apa yang mungkin menyebabkan hasil tersebut?

Dataset hanya memuat konsep teknologi, bukan resep atau bahan makanan.
Qdrant tetap mengembalikan vektor terdekat yang tersedia walaupun
dokumen tersebut tidak menjawab pertanyaan. Aplikasi ini belum
menerapkan ambang score untuk menolak hasil yang terlalu jauh dari
query. Skor kemiripan juga bukan probabilitas kebenaran, sehingga sistem
tetap memerlukan evaluasi relevansi dan dapat dikembangkan dengan
mekanisme abstain atau pesan "tidak ditemukan hasil yang cukup relevan".

## Personal Reflection

Jawaban di bawah merupakan draf refleksi yang disusun dari proses
menjalankan project. Sesuaikan kalimatnya jika ada bagian yang tidak
menggambarkan pemahaman atau pengalaman pribadi.

### 1. Sebelum mengerjakan tugas ini, bagaimana kalian membayangkan search engine bekerja? Apakah ada perbedaan setelah mempelajari semantic search?

Awalnya saya membayangkan search engine terutama mencari kata yang sama
dengan kata dalam pertanyaan. Setelah menjalankan project, saya memahami
bahwa semantic search mengubah teks menjadi embedding dan mencari
dokumen berdasarkan kedekatan vektor. Sistem dapat menemukan teks dengan
susunan kata berbeda, tetapi hasilnya tetap bergantung pada model dan
isi dataset.

### 2. Apa perbedaan terbesar antara keyword search dan semantic search?

Keyword search berfokus pada kecocokan kata atau istilah. Semantic
search membandingkan representasi vektor untuk mencari kedekatan makna.
Dari eksperimen ini, semantic search dapat menemukan dokumen yang
relevan meskipun kata-katanya berbeda. Namun, hasilnya juga dapat
meleset, seperti terlihat pada pengujian query tentang resep nasi
goreng.

### 3. Apa fungsi embedding di dalam semantic search?

Embedding mengubah teks menjadi deretan angka yang mewakili
karakteristik maknanya. Aplikasi menggunakan embedding dokumen dan
embedding query untuk menghitung kedekatan vektor. Tanpa representasi
ini, Qdrant tidak dapat melakukan pencarian vektor seperti yang
digunakan pada project.

### 4. Kenapa embedding tidak cukup hanya disimpan di list Python jika jumlah data menjadi sangat banyak?

List Python dapat menyimpan vektor, tetapi tidak menyediakan seluruh
kemampuan pencarian vektor dan pengelolaan data yang dibutuhkan ketika
dataset bertambah. Vector database seperti Qdrant menyediakan
penyimpanan vektor, payload, dan mekanisme pencarian yang dirancang
untuk retrieval. Untuk dataset kecil, list mungkin cukup untuk percobaan
sederhana, tetapi pendekatan itu menjadi kurang praktis ketika jumlah
data dan kebutuhan pencarian meningkat.

### 5. Bagian project mana yang paling sulit kalian pahami?

Bagian yang paling menantang bagi saya adalah menyiapkan lingkungan
Python dan memahami hubungan antara embedding, Qdrant, dan similarity
score. Saya perlu memastikan virtual environment aktif, library
terpasang, server berjalan, serta data tetap tersedia setelah server
dimulai ulang. Pengujian bertahap membantu saya membedakan masalah
konfigurasi dari hasil pencarian yang kurang relevan.

### 6. Bagian kode mana yang paling banyak dibantu oleh AI?

Saya menggunakan bantuan AI terutama untuk menyusun struktur awal
aplikasi FastAPI, menghubungkan Sentence Transformers dengan Qdrant,
menyiapkan endpoint `/index` dan `/search`, serta memahami pesan error
saat menjalankan aplikasi. Saya juga menggunakan bantuan AI untuk
menyusun skenario eksperimen dan menganalisis hasil aktual.

### 7. Jelaskan dengan bahasa kalian sendiri bagaimana bagian kode tersebut bekerja.

Endpoint `/index` membaca data dari `data.json`, mengubah setiap teks
menjadi embedding, lalu menyimpan vektor, teks, dan kategori ke Qdrant.
Endpoint `/search` mengubah query pengguna menjadi embedding dengan
model yang sama. Qdrant mencari vektor yang paling dekat dan
mengembalikan dokumen sesuai nilai Top-K. API kemudian menampilkan teks,
kategori, dan similarity score dari setiap hasil.

### 8. Aplikasi semantic search yang dibuat bisa dikembangkan menjadi aplikasi apa jika project dilanjutkan?

Aplikasi ini dapat dikembangkan menjadi mesin pencari catatan kuliah,
pencarian FAQ kampus, atau pencarian dokumen pembelajaran. Pengembangan
tersebut memerlukan dataset yang lebih lengkap dan sesuai dengan
kebutuhan pengguna. Sistem juga perlu pengujian relevansi yang lebih
terstruktur dan mekanisme untuk memberi tahu pengguna ketika tidak ada
hasil yang cukup sesuai.

## AI Usage

### AI tools yang digunakan

ChatGPT.

### AI digunakan untuk membantu bagian apa?

ChatGPT membantu menyusun kode awal, menjelaskan fungsi embedding dan
Qdrant, memberi panduan instalasi Python serta library, menelusuri
masalah saat aktivasi virtual environment, dan menyusun langkah
pengujian API. ChatGPT juga membantu menafsirkan respons yang muncul
pada setiap eksperimen.

### Bagian apa yang kalian ubah atau tentukan sendiri setelah mendapatkan hasil dari AI?

Saya menjalankan perintah instalasi dan server pada komputer sendiri,
menguji endpoint melalui Swagger UI, mengirim lima query eksperimen,
membandingkan Top-K, menguji query di luar topik dataset, dan memeriksa
persistensi setelah server dimulai ulang. Saya menggunakan respons
aktual dari aplikasi untuk mencatat teks hasil dan similarity score,
kemudian menilai apakah dokumen tersebut sesuai dengan maksud query.
