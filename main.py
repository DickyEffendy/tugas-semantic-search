from contextlib import asynccontextmanager
from functools import lru_cache
import json
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "data.json"
QDRANT_PATH = BASE_DIR / "qdrant_data"

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
COLLECTION_NAME = "semantic_search_collection"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Qdrant berjalan dalam mode lokal dan menyimpan data ke folder qdrant_data.
# Jalankan aplikasi hanya dalam satu proses agar file database tidak terkunci.
client = QdrantClient(path=str(QDRANT_PATH))


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Muat model satu kali, lalu gunakan kembali untuk permintaan berikutnya."""
    return SentenceTransformer(MODEL_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    client.close()


app = FastAPI(
    title="Semantic Search & Vector Database",
    description=(
        "API pencarian semantik berbahasa Indonesia menggunakan Sentence Transformers "
        "dan Qdrant local persistent storage."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


class SearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=2000,
        description="Kalimat atau pertanyaan yang ingin dicari berdasarkan makna.",
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=50,
        description="Jumlah hasil paling mirip yang diminta.",
    )


def get_embedding_model() -> SentenceTransformer:
    try:
        return get_model()
    except Exception as exc:
        logger.exception("Gagal memuat model embedding.")
        raise HTTPException(
            status_code=503,
            detail=(
                "Model embedding belum berhasil dimuat. Pastikan komputer terhubung "
                "ke internet saat pemakaian pertama, lalu coba lagi. "
                f"Detail teknis: {type(exc).__name__}: {exc}"
            ),
        ) from exc


def load_dataset() -> list[dict[str, str]]:
    """Baca dan validasi dataset lokal sebelum indexing."""
    if not DATASET_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"File dataset tidak ditemukan: {DATASET_PATH.name}",
        )

    try:
        raw_data = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Format JSON pada {DATASET_PATH.name} tidak valid: {exc}",
        ) from exc

    if not isinstance(raw_data, list):
        raise HTTPException(
            status_code=500,
            detail="Isi data.json harus berupa daftar/list objek.",
        )

    documents: list[dict[str, str]] = []
    for row_number, item in enumerate(raw_data, start=1):
        if not isinstance(item, dict):
            raise HTTPException(
                status_code=500,
                detail=f"Data nomor {row_number} harus berupa objek JSON.",
            )

        text = item.get("text")
        category = item.get("category")

        if not isinstance(text, str) or not text.strip():
            raise HTTPException(
                status_code=500,
                detail=f"Data nomor {row_number} memiliki field text kosong atau tidak valid.",
            )
        if not isinstance(category, str) or not category.strip():
            raise HTTPException(
                status_code=500,
                detail=f"Data nomor {row_number} memiliki field category kosong atau tidak valid.",
            )

        documents.append({"text": text.strip(), "category": category.strip()})

    categories = {item["category"] for item in documents}
    if len(documents) < 20:
        raise HTTPException(
            status_code=500,
            detail=f"Dataset harus berisi minimal 20 data. Saat ini: {len(documents)}.",
        )
    if len(categories) < 3:
        raise HTTPException(
            status_code=500,
            detail=f"Dataset harus memiliki minimal 3 kategori. Saat ini: {len(categories)}.",
        )

    return documents


@app.get("/")
def root():
    return {
        "project": "Semantic Search & Vector Database",
        "docs": "/docs",
        "health": "/health",
        "index_endpoint": "POST /index",
        "search_endpoint": "POST /search",
    }


@app.get("/health")
def health():
    try:
        collection_exists = client.collection_exists(
            collection_name=COLLECTION_NAME
        )
        indexed_count = (
            client.count(collection_name=COLLECTION_NAME, exact=True).count
            if collection_exists
            else 0
        )
    except Exception as exc:
        logger.exception("Pemeriksaan Qdrant gagal.")
        raise HTTPException(
            status_code=503,
            detail=(
                "Qdrant local storage tidak dapat diakses. Pastikan tidak ada "
                "proses aplikasi lain yang sedang menggunakan folder qdrant_data. "
                f"Detail teknis: {type(exc).__name__}: {exc}"
            ),
        ) from exc

    return {
        "status": "ok",
        "model_name": MODEL_NAME,
        "model_loaded": get_model.cache_info().currsize > 0,
        "qdrant_mode": "local persistent",
        "collection_exists": collection_exists,
        "indexed_count": indexed_count,
    }


@app.post("/index")
def index_dataset():
    """
    Buat ulang collection lalu masukkan seluruh data.json ke Qdrant.
    Memanggil endpoint ini lagi akan mengganti isi collection dengan dataset terbaru.
    """
    documents = load_dataset()
    model = get_embedding_model()
    texts = [item["text"] for item in documents]

    try:
        embeddings = model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
    except Exception as exc:
        logger.exception("Pembuatan embedding dataset gagal.")
        raise HTTPException(
            status_code=500,
            detail=f"Gagal membuat embedding dataset: {type(exc).__name__}: {exc}",
        ) from exc

    if len(embeddings) != len(documents) or len(embeddings.shape) != 2:
        raise HTTPException(
            status_code=500,
            detail="Bentuk embedding tidak sesuai dengan jumlah dokumen.",
        )

    vector_size = int(embeddings.shape[1])

    try:
        # Menghapus collection lama mencegah data usang atau ukuran vektor yang tidak cocok.
        if client.collection_exists(collection_name=COLLECTION_NAME):
            client.delete_collection(collection_name=COLLECTION_NAME)

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )

        points = [
            PointStruct(
                id=index,
                vector=embeddings[index - 1].tolist(),
                payload={
                    "text": document["text"],
                    "category": document["category"],
                },
            )
            for index, document in enumerate(documents, start=1)
        ]

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
            wait=True,
        )
        indexed_count = client.count(
            collection_name=COLLECTION_NAME,
            exact=True,
        ).count
    except Exception as exc:
        logger.exception("Indexing ke Qdrant gagal.")
        raise HTTPException(
            status_code=500,
            detail=f"Gagal menyimpan embedding ke Qdrant: {type(exc).__name__}: {exc}",
        ) from exc

    return {
        "status": "ok",
        "message": "Dataset berhasil diubah menjadi embedding dan disimpan di Qdrant.",
        "collection_name": COLLECTION_NAME,
        "indexed_count": indexed_count,
        "categories": sorted({item["category"] for item in documents}),
        "embedding_dimension": vector_size,
        "distance_metric": "COSINE",
    }


@app.post("/search")
def semantic_search(request: SearchRequest):
    """Cari dokumen dengan kedekatan vektor terhadap embedding query pengguna."""
    try:
        if not client.collection_exists(collection_name=COLLECTION_NAME):
            raise HTTPException(
                status_code=409,
                detail="Dataset belum di-index. Jalankan POST /index terlebih dahulu.",
            )

        indexed_count = client.count(
            collection_name=COLLECTION_NAME,
            exact=True,
        ).count
        if indexed_count == 0:
            raise HTTPException(
                status_code=409,
                detail="Collection belum memiliki data. Jalankan POST /index terlebih dahulu.",
            )

        model = get_embedding_model()
        query_embedding = model.encode(
            [request.query],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0].tolist()

        response = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=min(request.top_k, indexed_count),
            with_payload=True,
        )

        results = []
        for point in response.points:
            payload = point.payload or {}
            results.append(
                {
                    "text": payload.get("text", ""),
                    "category": payload.get("category", ""),
                    "score": round(float(point.score), 4),
                }
            )

        return {
            "query": request.query,
            "top_k_requested": request.top_k,
            "result_count": len(results),
            "results": results,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Semantic search gagal.")
        raise HTTPException(
            status_code=500,
            detail=f"Semantic search gagal: {type(exc).__name__}: {exc}",
        ) from exc
