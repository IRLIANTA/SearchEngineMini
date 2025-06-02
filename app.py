import streamlit as st
import pandas as pd
import re
import seaborn as sns
from collections import defaultdict
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
import nltk
import string
from collections import Counter
from nltk.corpus import stopwords
from wordcloud import WordCloud
import nltk
nltk.download('stopwords')


# Load dataset
df = pd.read_csv("beritaOlahraga.csv")

# Build inverted index
inverted_index = defaultdict(set)
for idx, row in df.iterrows():
    words = re.findall(r"\w+", str(row['Text']).lower())
    for word in set(words):
        inverted_index[word].add(idx)

# Search function
def search_word(word):
    return list(inverted_index.get(word.lower(), []))

def boolean_search(term1, term2, operator):
    s1 = inverted_index.get(term1.lower(), set())
    s2 = inverted_index.get(term2.lower(), set())
    if operator == "AND":
        return list(s1 & s2)
    elif operator == "OR":
        return list(s1 | s2)
    elif operator == "NOT":
        return list(s1 - s2)
    else:
        return []

# Highlight function
def highlight(text, word):
    pattern = re.compile(rf"(\b{re.escape(word)}\b)", re.IGNORECASE)
    return pattern.sub(r"<span style='background-color: #561C24;'>\1</span>", text)

# Sidebar branding
st.sidebar.markdown(
    """
    <h1 style="font-weight:bold; font-size:4rem; text-align: center; font-style: italic;">
        Uts<span style="color:red;">STKI</span>
    </h1>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

# Menu
with st.sidebar:
    selected = option_menu(
        "Main Menu",
        ["Home", "Inverted Index", "Boolean Retrieval", "Tentang Dataset"],
        icons=["house", "search", "filter", "bar-chart"],
        menu_icon="cast",
        default_index=0
    )

# Boolean operation helpers
def operasi_and(term1, term2):
    try:
        result_indices = boolean_search(term1, term2, "AND")
        return format_result(result_indices)
    except Exception as e:
        return {"error": f"Terjadi kesalahan: {str(e)}"}

def operasi_or(term1, term2):
    try:
        result_indices = boolean_search(term1, term2, "OR")
        return format_result(result_indices)
    except Exception as e:
        return {"error": f"Terjadi kesalahan: {str(e)}"}

def operasi_not(term1, term2):
    try:
        result_indices = boolean_search(term1, term2, "NOT")
        return format_result(result_indices)
    except Exception as e:
        return {"error": f"Terjadi kesalahan: {str(e)}"}

def format_result(result_indices):
    if not result_indices:
        return {"error": "Tidak ditemukan hasil."}
    articles = []
    for idx in result_indices:
        row = df.iloc[idx]
        articles.append({
            "no": row['No'],
            "judul": row['Judul'],
            "text": row['Text'],
            "url": row['Url']
        })
    return {
        "message": f"Ditemukan {len(articles)} hasil.",
        "articles": articles
    }

# Halaman: Home
if selected == "Home":
    st.image("webscraping.jpg")
    st.title("Tugas Ujian Tengah Semester")
    st.subheader("Mata Kuliah - Sistem Temu Kembali Informasi")
    st.write("""
        Aplikasi ini dibuat untuk melakukan pencarian sederhana berdasarkan konten berita olahraga dengan dataset yang sudah kami scrapping di tugas sebelumnya.

        Fitur utama:
        - Pencarian menggunakan **Inverted Index**.
        - Pencarian menggunakan **Boolean Retrieval (AND, OR, NOT)**.
        - Visualisasi ringkas dari isi dataset.
    """)
    st.markdown("---")
    st.title("Anggota Kelompok;")
    st.subheader("IRLIANTA RIZKIAWAN")
    st.write("""
        - NIM = 221220003
        - Angkatan = 2022
    """)
    st.subheader("IQBAL APRI KURNIAWAN")
    st.write("""
        - NIM = 221220033
        - Angkatan = 2022
    """)

# Halaman: Inverted Index
elif selected == "Inverted Index":
    st.title("Pencarian dengan Inverted Index")

    query = st.text_input("Masukkan kata untuk dicari")
    if query:
        results = search_word(query)
        if results:
            st.success(f"Ditemukan {len(results)} hasil:")
            for idx in results:
                row = df.iloc[idx]
                highlighted_title = highlight(row['Judul'], query)
                highlighted_text = highlight(row['Text'], query)
                st.markdown(f"**{row['No']} - {highlighted_title}**", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: justify;'>{highlighted_text}</div>", unsafe_allow_html=True)
                st.markdown(f"[Baca Selengkapnya]({row['Url']})", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.warning("Tidak ditemukan hasil untuk kata tersebut.")

    st.markdown("---")
    st.markdown("## 📚 Apa itu Inverted Index?")
    st.write("""
**Inverted Index** adalah struktur data yang digunakan untuk mempercepat pencarian kata dalam sekumpulan dokumen.

Struktur ini bekerja seperti indeks pada akhir buku, yaitu menghubungkan setiap kata dengan daftar dokumen di mana kata tersebut muncul.

### 🔍 Cara Kerja:
- Sistem membaca seluruh dokumen dan menyusun daftar semua kata unik.
- Untuk setiap kata, sistem menyimpan daftar dokumen yang mengandung kata tersebut.
- Saat pengguna mencari kata tertentu, sistem langsung mengambil daftar dokumen dari indeks — tanpa membaca semua teks secara manual.

### 🤝 Hubungannya dengan Boolean Retrieval:
Inverted Index memudahkan penerapan operasi seperti **AND**, **OR**, dan **NOT** dalam pencarian Boolean. Setiap operasi dilakukan pada daftar indeks dokumen dari masing-masing kata.
""")


# Halaman: Boolean Retrieval
elif selected == "Boolean Retrieval":
    st.title("Pencarian dengan Boolean Retrieval")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        term1 = st.text_input("Kata Pertama")
    with col2:
        operator = st.selectbox("Operator", ["AND", "OR", "NOT"])
    with col3:
        term2 = st.text_input("Kata Kedua")

    # Cek apakah user sudah memasukkan term dan operator valid untuk pencarian
    is_search_ready = term1 and ((operator != "NOT" and term2) or (operator == "NOT" and term2))

    st.markdown("---")

    if not is_search_ready:
        st.markdown("## Apa itu Boolean Retrieval?")
        st.write("""
        Boolean Retrieval adalah metode pencarian informasi yang menggunakan operator logika seperti AND, OR, dan NOT
        untuk menemukan dokumen yang sesuai berdasarkan kata kunci (terms) yang diberikan.

        **Operator yang digunakan:**
        - **AND**: Mengembalikan dokumen yang mengandung **kedua** kata kunci.
        - **OR**: Mengembalikan dokumen yang mengandung **salah satu atau kedua** kata kunci.
        - **NOT**: Mengembalikan dokumen yang mengandung kata pertama **tetapi tidak mengandung** kata kedua.

        Contoh:
        - **"bola" AND "liga"** → hanya menampilkan berita yang mengandung kedua kata.
        - **"bola" OR "liga"** → menampilkan semua berita yang mengandung kata bola, liga, atau keduanya.
        - **"bola" NOT "liga"** → menampilkan berita yang hanya mengandung kata bola tetapi tidak mengandung liga.
        """)
    else:
        # Tempatkan di sini kode pencarian dan hasilnya
        # Contoh sederhana:
        result = None
        if operator == "AND":
            result = operasi_and(term1, term2)
        elif operator == "OR":
            result = operasi_or(term1, term2)
        elif operator == "NOT":
            result = operasi_not(term1, term2)

        if result and "error" in result:
            st.error(result["error"])
        else:
            st.success(result["message"])
            for artikel in result["articles"]:
                highlighted_judul = highlight(artikel['judul'], term1)
                highlighted_text = highlight(artikel['text'], term1)

                if operator != "NOT":
                    highlighted_judul = highlight(highlighted_judul, term2)
                    highlighted_text = highlight(highlighted_text, term2)

                st.markdown(f"**{artikel['no']}. {highlighted_judul}**", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: justify;'>{highlighted_text}</div>", unsafe_allow_html=True)
                st.markdown(f"[Baca Selengkapnya]({artikel['url']})", unsafe_allow_html=True)
                st.markdown("---")


# Halaman Visualisasi Dataset
elif selected == "Tentang Dataset":
    st.title("Tentang Dataset")

    st.markdown("## Tentang Dataset dan Proses Pembuatan")
    st.write("""
    Dataset yang digunakan dalam proyek ini diperoleh melalui proses **web scraping** dari situs berita olahraga terpercaya. Dataset ini berisi kumpulan artikel yang mencakup berbagai kategori berita olahraga, termasuk sepak bola dan non-sepak bola.

    ### Struktur Dataset:
    Setiap entri dalam dataset terdiri dari beberapa kolom:
    - **No**: Nomor urut data
    - **Judul**: Judul artikel berita
    - **Text**: Isi lengkap dari artikel
    - **Kategori**: Jenis berita (sepak bola / non-sepak bola)
    - **URL**: Alamat link sumber berita

    ### Tahap Pembuatan Dataset:
    Proses pembuatan dataset dilakukan dengan tahapan berikut:

    1. **Identifikasi Sumber Data**:
    - Menentukan dua situs berita digital terpercaya yang memiliki banyak artikel olahraga.
    
    2. **Web Scraping**:
    - Menggunakan Python (dengan `requests`, `BeautifulSoup`, dan/atau `Selenium`) untuk mengambil data dari halaman berita.
    - Data yang diambil meliputi: judul, isi teks, dan kategori.

    3. **Pembersihan Data**:
    - Menghapus tag HTML yang tidak diperlukan.
    - Menghilangkan karakter aneh atau whitespace berlebihan.
    - Normalisasi teks menjadi lowercase.

    4. **Penyimpanan Data**:
    - Dataset disimpan dalam format CSV agar mudah digunakan untuk analisis dan pencarian.

    5. **Klasifikasi Awal**:
    - Artikel dikelompokkan ke dalam kategori `sepak bola` dan `non-sepak bola` secara manual atau dengan kata kunci tertentu.
    """)

    st.markdown("## Visualisasi Dataset")
    st.markdown("---")

    # Bar chart jumlah kata per berita berdasarkan kategori
    st.subheader("Jumlah Kata per Berita berdasarkan Kategori")
    df['Jumlah_Kata'] = df['Text'].apply(lambda x: len(str(x).split()))
    fig4, ax4 = plt.subplots(figsize=(10, 6), constrained_layout=True)
    sns.barplot(x='Kategori', y='Jumlah_Kata', data=df, ax=ax4)
    ax4.set_title("Jumlah Kata per Berita")
    ax4.set_xlabel("Kategori")
    ax4.set_ylabel("Jumlah Kata")
    ax4.tick_params(axis='x', rotation=90)
    st.pyplot(fig4)

    # Visualisasi jumlah berita per kategori (Pie Chart)
    st.subheader("Jumlah Berita per Kategori")
    kategori_counts = df['Kategori'].value_counts()
    fig5, ax5 = plt.subplots(figsize=(8, 8))
    ax5.pie(
        kategori_counts,
        labels=kategori_counts.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=plt.cm.Paired.colors
    )
    ax5.axis('equal')  # Agar pie chart bulat
    ax5.set_title('Distribusi Jumlah Berita per Kategori')
    st.pyplot(fig5)


    # Distribusi panjang berita (jumlah kata)
    st.subheader("Distribusi Panjang Berita (Jumlah Kata)")
    df['Jumlah_Kata'] = df['Text'].apply(lambda x: len(str(x).split()))
    fig6, ax6 = plt.subplots(figsize=(10, 6))
    sns.histplot(df['Jumlah_Kata'], bins=20, kde=True, ax=ax6, color='purple')
    ax6.set_title('Distribusi Panjang Berita (Jumlah Kata)')
    ax6.set_xlabel('Jumlah Kata')
    ax6.set_ylabel('Frekuensi')
    st.pyplot(fig6)

    # WordCloud
    st.subheader("Word Cloud 10 Kata Paling Sering Muncul (tanpa stopwords)")
    all_text = ' '.join(df['Text'].dropna().tolist()).lower()
    words = [word.strip(string.punctuation) for word in all_text.split()]
    stop_words = set(stopwords.words('indonesian'))
    filtered_words = [w for w in words if w not in stop_words and w != '']
    common_words = Counter(filtered_words).most_common(10)
    top_words_dict = {word.upper(): count for word, count in common_words}
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap='plasma'
    ).generate_from_frequencies(top_words_dict)
    fig3, ax3 = plt.subplots(figsize=(10,6))
    ax3.imshow(wordcloud, interpolation='bilinear')
    ax3.axis("off")
    st.pyplot(fig3)

    st.write("10 Kata paling sering muncul:")
    for word, count in top_words_dict.items():
        st.write(f"{word}: {count} kali")

    # Bar Chart Judul Artikel Terpanjang
    st.subheader("10 Judul Artikel Berita Terpanjang (Berdasarkan Jumlah Kata)")

    # Tambahkan kolom Jumlah_Kata dan Kategori (jika belum ada)
    df['Jumlah_Kata'] = df['Text'].apply(lambda x: len(str(x).split()))
    if 'Kategori' not in df.columns:
        df['Kategori'] = df['Judul'].apply(lambda x: 'Liga' if 'liga' in str(x).lower() else 'Lainnya')

    top_10_berita = df.sort_values(by='Jumlah_Kata', ascending=False).head(10)

    fig4, ax4 = plt.subplots(figsize=(12, 8))
    sns.barplot(
        y=top_10_berita['Judul'],
        x=top_10_berita['Jumlah_Kata'],
        hue=top_10_berita['Kategori'],
        dodge=False,
        ax=ax4
    )
    ax4.set_title("10 Judul Artikel Berita Terpanjang (Berdasarkan Jumlah Kata)")
    ax4.set_xlabel("Jumlah Kata")
    ax4.set_ylabel("Judul Artikel")
    ax4.legend(title="Kategori")
    st.pyplot(fig4)
