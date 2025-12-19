from datetime import date

# ===============================
#  GET DESCRIPTION
# ===============================
def get_description(mysql, mc_type, mc_code):
    mc_code = mc_code.strip()
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT mc_description
        FROM md_code
        WHERE TRIM(mc_type) = %s AND TRIM(mc_code) = %s
        LIMIT 1
    """, (mc_type, mc_code))
    row = cur.fetchone()
    cur.close()
    return row[0] if row else ""


# ===============================
#  GET ALL SERTIFIKASI
# ===============================
def get_all(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, nama_client, jenis_iso, no_cert,
               bidang_usaha, status, tgl_awal, tgl_akhir,
               kota, alamat
        FROM sertifikasi
        ORDER BY id DESC
    """)
    rows = cur.fetchall()
    cur.close()
    return rows


# ===============================
# GET BIDANG USAHA BY CODE
# ===============================
def get_bidang_usaha_by_code(mysql, mc_code):
    mc_code = mc_code.strip()

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT mc_description
        FROM md_code
        WHERE TRIM(mc_code) = %s
        LIMIT 1
    """, (mc_code,))
    row = cur.fetchone()
    cur.close()
    return row[0] if row else ""


# ===============================
#  GET BY ID
# ===============================
def get_by_id(mysql, id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, nama_client, jenis_iso, no_cert,
               mc_type, mc_code, bidang_usaha,
               tgl_awal, tgl_akhir, alamat, kota
        FROM sertifikasi
        WHERE id = %s
    """, (id,))
    row = cur.fetchone()
    cur.close()

    if not row:
        return {}

    return {
        "id": row[0],
        "nama_client": row[1],
        "jenis_iso": row[2],
        "no_cert": row[3],
        "mc_type": row[4],
        "mc_code": row[5],
        "bidang_usaha": row[6],
        "tgl_awal": row[7].strftime('%Y-%m-%d') if row[7] else "",
        "tgl_akhir": row[8].strftime('%Y-%m-%d') if row[8] else "",
        "alamat": row[9],
        "kota": row[10]
    }


# ===============================
#  GET MC TYPE
# ===============================
def get_mc_type(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT mc_type FROM md_code ORDER BY mc_type")
    rows = cur.fetchall()
    cur.close()
    return [r[0] for r in rows]


# ===============================
# GET CODE BY TYPE
# ===============================
def get_code_by_type(mysql, mc_type):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT DISTINCT mc_code
        FROM md_code
        WHERE TRIM(mc_type) = %s
        ORDER BY mc_code
    """, (mc_type,))
    rows = cur.fetchall()
    cur.close()
    return [r[0] for r in rows]


# ===============================
#  INSERT
# ===============================
def insert(mysql, data):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO sertifikasi 
        (nama_client, jenis_iso, no_cert, mc_type, mc_code,
         bidang_usaha, alamat, kota, status, tgl_awal, tgl_akhir)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        data["nama_client"],
        data["jenis_iso"],
        data["no_cert"],
        data["mc_type"],
        data["mc_code"],
        data["bidang_usaha"],
        data["alamat"],
        data["kota"],
        data["status"],
        data["tgl_awal"],
        data["tgl_akhir"]
    ))
    mysql.connection.commit()
    cur.close()
    return True


# ===============================
#  UPDATE
# ===============================
def update(mysql, id, data):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE sertifikasi 
        SET nama_client=%s, jenis_iso=%s, no_cert=%s,
            mc_type=%s, mc_code=%s, bidang_usaha=%s,
            kota=%s, alamat=%s, tgl_awal=%s, tgl_akhir=%s
        WHERE id=%s
    """, (
        data["nama_client"],
        data["jenis_iso"],
        data["no_cert"],
        data["mc_type"],
        data["mc_code"],
        data["bidang_usaha"],
        data["kota"],
        data["alamat"],
        data["tgl_awal"],
        data["tgl_akhir"],
        id
    ))

    mysql.connection.commit()
    cur.close()



# ===============================
#  DELETE
# ===============================
def delete(mysql, id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM sertifikasi WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()


# ===============================
# AUTO UPDATE STATUS
# ===============================
def auto_deactivate(mysql):
    today = date.today().isoformat()
    cur = mysql.connection.cursor()
    cur.execute("UPDATE sertifikasi SET status='Deactive' WHERE tgl_akhir < %s", [today])
    cur.execute("UPDATE sertifikasi SET status='Active' WHERE tgl_akhir >= %s", [today])
    mysql.connection.commit()
    cur.close()



#  ANALYTICS SECTION
def count_per_jenis(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT jenis_iso, COUNT(*) FROM sertifikasi GROUP BY jenis_iso")
    result = cur.fetchall()
    cur.close()
    return result


def count_trend(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT DATE_FORMAT(tgl_awal, '%Y-%m') AS bulan, COUNT(*)
        FROM sertifikasi GROUP BY bulan ORDER BY bulan
    """)
    result = cur.fetchall()
    cur.close()
    return result


def trend_per_month(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT DATE_FORMAT(tgl_awal, '%Y-%m') AS bulan, COUNT(*) 
        FROM sertifikasi GROUP BY bulan ORDER BY bulan
    """)
    result = cur.fetchall()
    cur.close()
    return result


def count_perusahaan(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(DISTINCT nama_client) FROM sertifikasi")
    result = cur.fetchone()[0]
    cur.close()
    return result


def count_sertifikat(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(DISTINCT jenis_iso) FROM sertifikasi")
    result = cur.fetchone()[0]
    cur.close()
    return result


def count_active(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM sertifikasi WHERE status = 'Active'")
    result = cur.fetchone()[0]
    cur.close()
    return result


def tren_iso(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT jenis_iso, COUNT(*) AS total 
        FROM sertifikasi GROUP BY jenis_iso ORDER BY total DESC
    """)
    rows = cur.fetchall()
    cur.close()
    return [{'jenis_iso': r[0], 'total': r[1]} for r in rows]


def chart_per_jenis(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT jenis_iso, COUNT(*) FROM sertifikasi 
        GROUP BY jenis_iso ORDER BY COUNT(*) DESC
    """)
    rows = cur.fetchall()
    cur.close()
    labels = [r[0] for r in rows]
    data = [r[1] for r in rows]
    return labels, data


def chart_trend(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT DATE_FORMAT(tgl_awal, '%Y-%m') as bulan, COUNT(*) 
        FROM sertifikasi GROUP BY bulan ORDER BY bulan
    """)
    rows = cur.fetchall()
    cur.close()
    labels = [r[0] for r in rows]
    data = [r[1] for r in rows]
    return labels, data


def chart_per_usaha(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT bidang_usaha, COUNT(*) FROM sertifikasi
        GROUP BY bidang_usaha ORDER BY COUNT(*) DESC
    """)
    rows = cur.fetchall()
    cur.close()
    labels = [r[0] for r in rows]
    data = [r[1] for r in rows]
    return labels, data


def get_growing_trend(mysql):
    _, trend_data = chart_trend(mysql)
    if len(trend_data) >= 2:
        last = trend_data[-1]
        prev = trend_data[-2]
        if prev > 0:
            percent = round(((last - prev) / prev) * 100, 1)
            return percent
    return 0


def get_growing_trend_per_jenis_per_tahun(mysql):
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT jenis_iso, COUNT(*) FROM sertifikasi
        WHERE YEAR(tgl_awal) = YEAR(CURDATE())
        GROUP BY jenis_iso
    """)
    data_ini_rows = cur.fetchall()
    data_ini = {row[0]: row[1] for row in data_ini_rows}
    total_ini = sum(data_ini.values())

    cur.execute("""
        SELECT jenis_iso, COUNT(*) FROM sertifikasi
        WHERE YEAR(tgl_awal) = YEAR(CURDATE()) - 1
        GROUP BY jenis_iso
    """)
    data_lalu_rows = cur.fetchall()
    data_lalu = {row[0]: row[1] for row in data_lalu_rows}
    total_lalu = sum(data_lalu.values())

    jenis_set = set(data_ini.keys()) | set(data_lalu.keys())

    growing = []
    for jenis in jenis_set:
        ini = data_ini.get(jenis, 0)
        lalu = data_lalu.get(jenis, 0)
        share_ini = ini / total_ini if total_ini > 0 else 0
        share_lalu = lalu / total_lalu if total_lalu > 0 else 0
        percent = round((share_ini - share_lalu) * 100)
        trend = 'up' if percent >= 0 else 'down'
        growing.append({
            'jenis_iso': jenis,
            'percent': abs(percent),
            'trend': trend
        })

    trend_up = sorted([g for g in growing if g['trend'] == 'up'],
                      key=lambda x: x['percent'], reverse=True)[:3]
    trend_down = sorted([g for g in growing if g['trend'] == 'down'],
                        key=lambda x: x['percent'], reverse=True)[:3]

    return trend_up, trend_down


def get_rekomendasi_bidang_usaha(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT bidang_usaha, COUNT(*) as total
        FROM sertifikasi
        GROUP BY bidang_usaha
        ORDER BY total DESC
    """)
    rows = cur.fetchall()
    cur.close()

    if not rows:
        return {
            'top': {},
            'bottom': {},
            'marketing': 'Tidak ada data.'
        }

    top = {'bidang_usaha': rows[0][0], 'total': rows[0][1]}
    bottom = {'bidang_usaha': rows[-1][0], 'total': rows[-1][1]}

    marketing = (
        f"Bidang usaha dengan jumlah paling sedikit: {bottom['bidang_usaha']}. "
        "Strategi promosi: Analisis SWOT, identifikasi target pasar, testimoni klien, "
        "dan insentif diskon untuk menarik minat."
    )

    return {
        'top': top,
        'bottom': bottom,
        'marketing': marketing
    }



#  RANKING
def ranking_perusahaan(mysql, limit=5):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT nama_client, Kota, COUNT(*) as total
        FROM sertifikasi
        GROUP BY nama_client, Kota
        ORDER BY total DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()

    hasil = []
    urutan = 1
    for row in rows:
        hasil.append({
            'rank': urutan,
            'nama_client': row[0],
            'Kota': row[1],
            'total': row[2]
        })
        urutan += 1
    return hasil


def ranking_kota(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT Kota, COUNT(*) AS total 
        FROM sertifikasi
        GROUP BY Kota
        ORDER BY total DESC
    """)
    rows = cur.fetchall()
    cur.close()

    return [{'Kota': r[0], 'total': r[1]} for r in rows]


def detail_kota(mysql, kota):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT nama_client, status
        FROM sertifikasi
        WHERE Kota = %s
    """, [kota])
    rows = cur.fetchall()
    cur.close()

    return [{'nama_client': r[0], 'status': r[1]} for r in rows]