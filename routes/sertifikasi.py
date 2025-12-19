from flask import Blueprint, render_template, request, jsonify, current_app
from datetime import date
from ses_auth import login_required
from models import sertifikasi_model

sertifikasi_bp = Blueprint('sertifikasi', __name__, url_prefix='/sertifikasi')


# ======================= HALAMAN UTAMA ==========================
@sertifikasi_bp.route('/')
@login_required
def index():
    mysql = current_app.config['mysql']

    # Auto update status Active/Deactive
    sertifikasi_model.auto_deactivate(mysql)

    data = sertifikasi_model.get_all(mysql)
    mc_types = sertifikasi_model.get_mc_type(mysql)

    return render_template('sertifikasi.html', sertifikasi=data, mc_types=mc_types)


# ======================= GET CODE BY TYPE =======================
@sertifikasi_bp.route('/get_code_by_type/<mc_type>')
@login_required
def get_code_by_type(mc_type):
    mysql = current_app.config['mysql']
    data = sertifikasi_model.get_code_by_type(mysql, mc_type)
    return jsonify(data)


# ======================= GET DESCRIPTION ========================
@sertifikasi_bp.route('/get_description', methods=['GET'])
@login_required
def get_description():
    mc_type = request.args.get('mc_type')
    mc_code = request.args.get('mc_code')

    if not mc_type or not mc_code:
        return jsonify(""), 200

    mysql = current_app.config['mysql']
    desc = sertifikasi_model.get_description(mysql, mc_type, mc_code)

    return jsonify(desc)


# ======================= GET BIDANG USAHA =======================
@sertifikasi_bp.route('/get_bidang_usaha', methods=['GET'])
@login_required
def get_bidang_usaha():
    mc_type = request.args.get('mc_type')
    mc_code = request.args.get('mc_code')

    mysql = current_app.config['mysql']
    desc = sertifikasi_model.get_description(mysql, mc_type, mc_code)

    return jsonify({"bidang_usaha": desc})


# ======================= GET BY ID ==============================
@sertifikasi_bp.route('/get/<int:id>')
@login_required
def get_by_id(id):
    mysql = current_app.config['mysql']
    data = sertifikasi_model.get_by_id(mysql, id)
    return jsonify(data)


# ======================== SAVE (INSERT / UPDATE) ================
@sertifikasi_bp.route('/save', methods=['POST'])
@login_required
def save_sertifikasi():
    mysql = current_app.config['mysql']
    form = request.get_json() or {}

    mc_type = form.get("mc_type")
    mc_code = form.get("mc_code")

    # Pastikan mc_code tidak undefined / None
    if not mc_type or not mc_code:
        return jsonify({"success": False, "message": "Kode EA tidak boleh kosong."}), 400

    # Ambil bidang usaha otomatis
    bidang_usaha = sertifikasi_model.get_description(mysql, mc_type, mc_code)

    if not bidang_usaha:
        return jsonify({"success": False, "message": "Bidang usaha tidak ditemukan."}), 400

    # Tentukan status otomatis
    today = date.today().isoformat()
    tgl_akhir = form.get("tgl_akhir")
    status = "Active" if tgl_akhir and tgl_akhir >= today else "Deactive"

    data = {
        "nama_client": form.get("nama_client"),
        "jenis_iso": form.get("jenis_iso"),
        "no_cert": form.get("no_cert"),
        "mc_type": mc_type,
        "mc_code": mc_code,
        "bidang_usaha": bidang_usaha,
        "kota": form.get("kota"),
        "alamat": form.get("alamat"),
        "status": status,
        "tgl_awal": form.get("tgl_awal"),
        "tgl_akhir": form.get("tgl_akhir")
    }

    # UPDATE
    if form.get("id"):
        sertifikasi_model.update(mysql, form.get("id"), data)
    else:
        sertifikasi_model.insert(mysql, data)

    return jsonify({"success": True})


# ===================== GET CLIENT BY KOTA =======================
@sertifikasi_bp.route('/get_client_by_kota', methods=['GET'])
@login_required
def get_client_by_kota_route():
    kota = request.args.get('kota')
    if not kota:
        return jsonify({'status': 'error', 'message': 'Kota tidak diberikan'}), 400

    mysql = current_app.config['mysql']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT nama_client, status
        FROM sertifikasi
        WHERE kota = %s
        ORDER BY nama_client
    """, [kota])
    rows = cur.fetchall()
    cur.close()

    data = [{'nama_client': r[0], 'status': r[1]} for r in rows]
    return jsonify({'status': 'success', 'data': data})


# ========================== DELETE ==============================
@sertifikasi_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    mysql = current_app.config['mysql']
    sertifikasi_model.delete(mysql, id)
    return jsonify({'status': 'success'})
