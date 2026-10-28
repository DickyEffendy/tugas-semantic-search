from datetime import datetime
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_DIR = Path(__file__).resolve().parent
BASE_URL = os.environ.get("SEMANTIC_SEARCH_URL", "http://127.0.0.1:8000").rstrip("/")

QUERIES = [
    "Bagaimana aplikasi dapat menemukan kalimat yang artinya sama walaupun susunan katanya berbeda?",
    "Saya ingin membuat server web Python dengan dokumentasi endpoint otomatis.",
    "Cara menampilkan informasi dalam bentuk grafik agar pola data mudah dipahami.",
    "Bagaimana menyimpan catatan dalam tabel dan menghubungkan data antar tabel?",
    "Metode yang digunakan komputer untuk belajar dari contoh dan memprediksi hasil.",
]
TOP_K_QUERY = QUERIES[0]
BAD_RETRIEVAL_QUERY = "Bagaimana cara membuat nasi goreng tanpa kompor untuk makan malam?"


def post_json(path: str, payload=None):
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(
        f"{BASE_URL}{path}",
        data=body,
        headers=headers,
        method="POST",
    )

    try:
        with urlopen(request, timeout=600) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Endpoint {path} mengembalikan HTTP {exc.code}: {detail}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(
            f"Tidak dapat terhubung ke {BASE_URL}. "
            "Jalankan server terlebih dahulu dengan perintah "
            "'python -m uvicorn main:app --host 127.0.0.1 --port 8000'. "
            f"Detail: {exc}"
        ) from exc


def format_result(result: dict, number: int | None = None) -> str:
    prefix = f"{number}. " if number is not None else ""
    text = str(result.get("text", "")).replace("\n", " ").strip()
    category = result.get("category", "")
    score = result.get("score", None)
    return f"{prefix}**{text}**  \n   Kategori: {category} | Similarity score: {score}"


def build_report(index_response, experiment_results, top_k_results, bad_response, example_response):
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    lines = [
        "## Hasil Eksperimen Aktual",
        "",
        f"Waktu pengujian: {now}",
        "",
        "Hasil di bawah diambil langsung dari API yang sedang berjalan. Skor tidak dibuat secara manual.",
        "",
        "### Status indexing",
        "",
        f"- Jumlah data yang di-index: {index_response.get('indexed_count')}",
        f"- Dimensi embedding: {index_response.get('embedding_dimension')}",
        f"- Kategori: {', '.join(index_response.get('categories', []))}",
        "",
        "### Experiment 1: Semantic Search",
        "",
    ]

    for index, (query, response) in enumerate(experiment_results, start=1):
        lines.extend([
            f"#### Query {index}",
            "",
            f"**Query:** {query}",
            "",
        ])
        results = response.get("results", [])
        if not results:
            lines.extend(["Tidak ada hasil yang dikembalikan.", ""])
        else:
            lines.append("**Top result:**")
            lines.append("")
            lines.append(format_result(results[0]))
            lines.append("")
            lines.append("**Hasil teratas lainnya (top_k=3):**")
            lines.append("")
            for result_number, result in enumerate(results, start=1):
                lines.append(format_result(result, result_number))
                lines.append("")
        lines.extend([
            "**Penilaian relevansi:** Tulis penilaian setelah membaca hasil aktual. Jelaskan apakah hasil menjawab maksud query dan mengapa.",
            "",
        ])

    lines.extend([
        "### Example Request dan Response Aktual",
        "",
        "Request yang benar-benar dikirim:",
        "",
        "```json",
        json.dumps({"query": QUERIES[0], "top_k": 3}, ensure_ascii=False, indent=2),
        "```",
        "",
        "Response aktual dari API:",
        "",
        "```json",
        json.dumps(example_response, ensure_ascii=False, indent=2),
        "```",
        "",
        "### Experiment 2: Top-K",
        "",
        f"**Query yang digunakan:** {TOP_K_QUERY}",
        "",
    ])

    for top_k in (1, 3, 5):
        response = top_k_results[top_k]
        lines.extend([f"#### Top-K = {top_k}", ""])
        results = response.get("results", [])
        if not results:
            lines.extend(["Tidak ada hasil yang dikembalikan.", ""])
        else:
            for result_number, result in enumerate(results, start=1):
                lines.append(format_result(result, result_number))
                lines.append("")
        lines.append("")

    lines.extend([
        "**Analisis perubahan Top-K:** Bandingkan hasil aktual. Top-K yang lebih besar menampilkan lebih banyak kandidat, tetapi tidak menjamin semua kandidat tambahan relevan.",
        "",
        "### Experiment 3: Kandidat Bad Retrieval",
        "",
        f"**Query uji:** {BAD_RETRIEVAL_QUERY}",
        "",
        "Hasil aktual:",
        "",
    ])

    bad_results = bad_response.get("results", [])
    if not bad_results:
        lines.extend(["API tidak mengembalikan hasil.", ""])
    else:
        for result_number, result in enumerate(bad_results, start=1):
            lines.append(format_result(result, result_number))
            lines.append("")

    lines.extend([
        "**Evaluasi manual:** Pastikan hasil di atas memang kurang relevan. Jika masih relevan, ubah `BAD_RETRIEVAL_QUERY` di `run_experiments.py` menjadi pertanyaan dari topik yang tidak ada dalam dataset, lalu jalankan skrip kembali.",
        "",
        "**Mengapa retrieval kurang relevan:** Setelah memilih contoh yang benar-benar kurang relevan, jelaskan kemungkinan penyebabnya, misalnya cakupan dataset terbatas, query terlalu jauh dari isi data, atau embedding menilai kemiripan konteks yang tidak sesuai dengan kebutuhan pengguna.",
        "",
    ])
    return "\n".join(lines)


def update_readme(report_text: str) -> bool:
    readme_path = BASE_DIR / "README.md"
    if not readme_path.exists():
        return False

    readme = readme_path.read_text(encoding="utf-8")
    start_marker = "<!-- EXPERIMENT_RESULTS_START -->"
    end_marker = "<!-- EXPERIMENT_RESULTS_END -->"

    if start_marker not in readme or end_marker not in readme:
        return False

    start = readme.index(start_marker) + len(start_marker)
    end = readme.index(end_marker)
    updated = readme[:start] + "\n\n" + report_text.strip() + "\n\n" + readme[end:]
    readme_path.write_text(updated, encoding="utf-8")
    return True


def main():
    print(f"Memeriksa server di {BASE_URL} ...")
    index_response = post_json("/index")
    print(f"Indexing selesai: {index_response.get('indexed_count')} data.")

    experiment_results = []
    for index, query in enumerate(QUERIES, start=1):
        response = post_json("/search", {"query": query, "top_k": 3})
        experiment_results.append((query, response))
        top = response.get("results", [{}])[0]
        print(
            f"Query {index}/5 selesai. "
            f"Top score: {top.get('score', 'tidak ada')} | "
            f"Kategori: {top.get('category', 'tidak ada')}"
        )

    top_k_results = {}
    for top_k in (1, 3, 5):
        top_k_results[top_k] = post_json(
            "/search",
            {"query": TOP_K_QUERY, "top_k": top_k},
        )
        print(f"Pengujian Top-K={top_k} selesai.")

    bad_response = post_json(
        "/search",
        {"query": BAD_RETRIEVAL_QUERY, "top_k": 5},
    )
    example_response = experiment_results[0][1]

    report = build_report(
        index_response,
        experiment_results,
        top_k_results,
        bad_response,
        example_response,
    )

    report_path = BASE_DIR / "EXPERIMENT_RESULTS.md"
    report_path.write_text("# Laporan Pengujian\n\n" + report + "\n", encoding="utf-8")
    readme_updated = update_readme(report)

    print("\nPengujian selesai.")
    print(f"Laporan aktual tersimpan di: {report_path.name}")
    if readme_updated:
        print("Bagian hasil eksperimen di README.md juga sudah diperbarui.")
    else:
        print("README.md tidak diperbarui otomatis karena penanda bagian eksperimen tidak ditemukan.")
    print(
        "\nPenting: baca hasil kandidat Bad Retrieval dan isi penilaian relevansi "
        "berdasarkan hasil yang benar-benar muncul."
    )


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(f"\nPENGUJIAN BELUM SELESAI:\n{exc}")
        raise SystemExit(1)
