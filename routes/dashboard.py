from flask import Blueprint, render_template, current_app, jsonify, request, session
from models import sertifikasi_model
from ses_auth import login_required
import json

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


# =============================
#        HALAMAN DASHBOARD
# =============================
@dashboard_bp.route('/')
@login_required
def dashboard():
    mysql = current_app.config['mysql']

    total_perusahaan = sertifikasi_model.count_perusahaan(mysql)
    total_sertifikat = sertifikasi_model.count_sertifikat(mysql)
    total_active = sertifikasi_model.count_active(mysql)
    tren_iso = sertifikasi_model.tren_iso(mysql)
    tren_teratas = tren_iso[0]['jenis_iso'] if tren_iso else '-'

    trend_up, trend_down = sertifikasi_model.get_growing_trend_per_jenis_per_tahun(mysql)

    jenis_labels, jenis_data = sertifikasi_model.chart_per_jenis(mysql)
    trend_labels, trend_data = sertifikasi_model.chart_trend(mysql)
    usaha_labels, usaha_data = sertifikasi_model.chart_per_usaha(mysql)

    rekomendasi_bidang_usaha = sertifikasi_model.get_rekomendasi_bidang_usaha(mysql)

    # === Ranking perusahaan (Top 5) ===
    ranking_perusahaan = sertifikasi_model.ranking_perusahaan(mysql, limit=5)

    return render_template(
        'dashboard.html',
        total_perusahaan=total_perusahaan,
        total_sertifikat=total_sertifikat,
        total_active=total_active,
        tren_iso=tren_iso,
        tren_teratas=tren_teratas,
        jenis_labels=json.dumps(jenis_labels),
        jenis_data=json.dumps(jenis_data),
        trend_labels=json.dumps(trend_labels),
        trend_data=json.dumps(trend_data),
        usaha_labels=json.dumps(usaha_labels),
        usaha_data=json.dumps(usaha_data),
        trend_up=trend_up,
        trend_down=trend_down,
        rekomendasi_bidang_usaha=rekomendasi_bidang_usaha,
        ranking_perusahaan=ranking_perusahaan
    )


# =============================
#       TOGGLE THEME
# =============================
@dashboard_bp.route('/toggle_theme', methods=['POST'])
@login_required
def toggle_theme():
    try:
        data = request.get_json() or {}
        new_theme = data.get('theme', 'light')
        session['theme'] = new_theme
        return jsonify({'status': 'success', 'theme': new_theme})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ==========================================================
#               RANKING KOTA — API BARU
# ==========================================================
@dashboard_bp.route('/ranking_kota')
@login_required
def ranking_kota():
    mysql = current_app.config['mysql']
    data = sertifikasi_model.ranking_kota(mysql)
    return jsonify(data)


# ==========================================================
#               DETAIL KOTA — API BARU
# ==========================================================
@dashboard_bp.route('/detail_kota/<kota>')
@login_required
def detail_kota(kota):
    mysql = current_app.config['mysql']
    data = sertifikasi_model.detail_kota(mysql, kota)
    return jsonify(data)
