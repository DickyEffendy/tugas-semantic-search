# Laporan Pengujian Aktual

Laporan ini merangkum respons yang diamati melalui Swagger UI saat
project dijalankan secara lokal. Skor yang dicatat berasal dari respons
API aktual.

## Status indexing dan persistensi

-   Dataset: 30 dokumen.
-   Kategori: AI dan Machine Learning, Backend API, Data Science,
    Database, Frontend.
-   Dimensi embedding: 384.
-   Distance metric: COSINE.
-   Setelah server dimulai ulang, `GET /health` tetap mengembalikan
    `collection_exists: true` dan `indexed_count: 30`.
-   Pencarian setelah restart mengembalikan tiga hasil database yang
    sama dengan score `0.8039`, `0.5672`, dan `0.5458`.

## Experiment 1: Semantic Search

  ----------------------------------------------------------------------------
  Query           Hasil          Kategori                  Score Penilaian
                  peringkat                                      
                  pertama                                        
  --------------- -------------- ------------- ----------------- -------------
  Bagaimana       Semantic       AI dan                   0.4653 Relevan
  menemukan       search mencari Machine                         dengan maksud
  kalimat dengan  dokumen        Learning                        query.
  arti serupa     berdasarkan                                    
  meskipun        kedekatan                                      
  menggunakan     makna,                                         
  kata yang       meskipun                                       
  berbeda?        kata-kata pada                                 
                  pertanyaan                                     
                  berbeda dari                                   
                  isi dokumen.                                   

  Saya ingin      Endpoint API   Backend API              0.5774 Cukup
  membuat server  adalah alamat                                  relevan,
  web Python      dan metode                                     tetapi hasil
  dengan          HTTP yang                                      kedua tentang
  dokumentasi     digunakan                                      FastAPI lebih
  endpoint        klien untuk                                    langsung
  otomatis.       meminta atau                                   menjawab
                  mengirim data                                  kebutuhan
                  ke server.                                     dokumentasi
                                                                 otomatis.

  Teknologi apa   Responsive     Frontend                 0.6331 Relevan
  yang cocok      design                                         dengan
  untuk membuat   menyesuaikan                                   kebutuhan
  tampilan situs  tata letak                                     tampilan
  interaktif dan  situs dengan                                   responsif.
  responsif?      ukuran layar                                   
                  ponsel,                                        
                  tablet, dan                                    
                  komputer.                                      

  Bagaimana cara  Database       Database                 0.8039 Sangat
  menyimpan       relasional                                     relevan
  informasi       menyimpan data                                 dengan
  terstruktur dan dalam tabel                                    pertanyaan
  menghubungkan   yang memiliki                                  tentang
  data antar      baris, kolom,                                  hubungan
  tabel?          kunci, dan                                     antartabel.
                  hubungan antar                                 
                  tabel.                                         

  Metode apa yang Model          AI dan                   0.6423 Masih
  digunakan untuk klasifikasi    Machine                         terkait,
  mengukur        memprediksi    Learning                        tetapi hasil
  seberapa baik   kelas seperti                                  kedua tentang
  model           spam atau                                      precision,
  klasifikasi     bukan spam                                     recall,
  membuat         berdasarkan                                    F1-score, dan
  prediksi?       pola yang                                      accuracy
                  dipelajari                                     lebih
                  dari data                                      langsung
                  pelatihan.                                     menjawab
                                                                 pertanyaan.
  ----------------------------------------------------------------------------

## Experiment 2: Top-K

Query:
`Bagaimana cara menyimpan informasi terstruktur dan menghubungkan data antar tabel?`

-   **Top-K = 1:** hasil pertama kategori Database, score `0.8039`.
-   **Top-K = 3:** hasil kategori Database dengan score `0.8039`,
    `0.5672`, dan `0.5458`.
-   **Top-K = 5:** tiga hasil database di atas, ditambah dokumen Pandas
    kategori Data Science dengan score `0.5249` dan visualisasi data
    kategori Data Science dengan score `0.4657`.

Kesimpulan: nilai Top-K yang lebih tinggi menambah jumlah kandidat,
tetapi dua hasil tambahan tidak menjawab pertanyaan tentang hubungan
antartabel secara langsung.

## Experiment 3: Bad Retrieval

Query: `Apa resep nasi goreng yang enak untuk makan malam?`

  --------------------------------------------------------------------------
  Peringkat        Hasil              Kategori                         Score
  ---------------- ------------------ ---------------- ---------------------
  1                Pandas membantu    Data Science                    0.1459
                   membersihkan,                       
                   menggabungkan,                      
                   mengubah, dan                       
                   menganalisis data                   
                   tabular                             
                   menggunakan                         
                   struktur                            
                   DataFrame.                          

  2                Machine learning   AI dan Machine                  0.1241
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

  3                Primary key adalah Database                        0.1191
                   kolom atau                          
                   gabungan kolom                      
                   yang                                
                   mengidentifikasi                    
                   setiap baris                        
                   secara unik dalam                   
                   tabel.                              
  --------------------------------------------------------------------------

Ketiga hasil tidak menjawab pertanyaan resep karena dataset hanya berisi
konsep teknologi. Qdrant tetap mengembalikan vektor terdekat dari data
yang tersedia. Project belum menerapkan ambang score untuk menolak hasil
yang tidak relevan.
