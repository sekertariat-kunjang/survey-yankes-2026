import os
import logging
import sqlite3
import json
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
import pandas as pd

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'cekrek-yankes-secret-key-2026')
DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'survey.db')

# Admin credentials (default can be overridden via environment variables)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------------------------------------------------
# Scoring configuration — centralised so methodology changes happen here only
# ---------------------------------------------------------------------------
CHECKLIST_TOTALS = {
    'poli':    10,
    'lab':      8,
    'farmasi': 12,
    'keluhan':  8,
}
TOTAL_CHECKLIST_ITEMS = sum(CHECKLIST_TOTALS.values())  # 38

SCORE_WEIGHT_YES_NO    = 0.5
SCORE_WEIGHT_CHECKLIST = 0.5

YES_NO_KEYS = [
    'poli_q1_jawab', 'poli_q2_jawab', 'poli_q4_jawab',
    'lab_q1_jawab',  'lab_q2_jawab',
    'farmasi_q1_jawab', 'farmasi_q2_jawab', 'farmasi_q3_jawab',
    'farmasi_q5_jawab', 'farmasi_q6_jawab',
    'keluhan_q1_jawab', 'keluhan_q2_jawab',
]

SECTION_CONFIG = {
    'poli': {
        'yn_keys':   ['poli_q1_jawab', 'poli_q2_jawab', 'poli_q4_jawab'],
        'chk_key':   'poli_q3_checklist',
        'chk_total': CHECKLIST_TOTALS['poli'],
    },
    'lab': {
        'yn_keys':   ['lab_q1_jawab', 'lab_q2_jawab'],
        'chk_key':   'lab_q3_checklist',
        'chk_total': CHECKLIST_TOTALS['lab'],
    },
    'farmasi': {
        'yn_keys':   ['farmasi_q1_jawab', 'farmasi_q2_jawab', 'farmasi_q3_jawab',
                      'farmasi_q5_jawab', 'farmasi_q6_jawab'],
        'chk_key':   'farmasi_q4_checklist',
        'chk_total': CHECKLIST_TOTALS['farmasi'],
    },
    'keluhan': {
        'yn_keys':   ['keluhan_q1_jawab', 'keluhan_q2_jawab'],
        'chk_key':   'keluhan_q3_checklist',
        'chk_total': CHECKLIST_TOTALS['keluhan'],
    },
}

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_pelaksana TEXT NOT NULL,
                tanggal TEXT NOT NULL,
                waktu TEXT NOT NULL,
                lokasi TEXT NOT NULL,

                -- GPS Metadata
                gps_lat TEXT,
                gps_lon TEXT,
                gps_distance REAL,
                gps_verified INTEGER, -- 1 = Verified (<300m), 0 = Manual / Out of bounds, -1 = Error / Disabled

                -- Ruang Poli Rawat Jalan
                poli_klaster TEXT,
                poli_q1_jawab TEXT,
                poli_q1_detail TEXT,
                poli_q2_jawab TEXT,
                poli_q2_detail TEXT,
                poli_q3_checklist TEXT, -- JSON array of selected items
                poli_q4_jawab TEXT,
                poli_q4_detail TEXT,

                -- Ruang Laboratorium
                lab_q1_jawab TEXT,
                lab_q1_detail TEXT,
                lab_q2_jawab TEXT,
                lab_q2_detail TEXT,
                lab_q3_checklist TEXT,

                -- Ruang Farmasi/Apotek
                farmasi_q1_jawab TEXT,
                farmasi_q1_detail TEXT,
                farmasi_q2_jawab TEXT,
                farmasi_q2_detail TEXT,
                farmasi_q3_jawab TEXT,
                farmasi_q3_detail TEXT,
                farmasi_q4_checklist TEXT,
                farmasi_q5_jawab TEXT,
                farmasi_q5_detail TEXT,
                farmasi_q6_jawab TEXT,
                farmasi_q6_detail TEXT,

                -- Ruang Pelayanan Informasi & Penanganan Keluhan
                keluhan_q1_jawab TEXT,
                keluhan_q1_detail TEXT,
                keluhan_q2_jawab TEXT,
                keluhan_q2_detail TEXT,
                keluhan_q3_checklist TEXT,

                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    finally:
        conn.close()

# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def _safe_parse_checklist(value):
    """Parse a JSON checklist string; return empty list on any error."""
    try:
        return json.loads(value or '[]')
    except (json.JSONDecodeError, TypeError):
        return []


def _compute_compliance_score(row):
    """Return yes_no_score, checklist_score, and final weighted score for a row."""
    yes_count = sum(1 for k in YES_NO_KEYS if row[k] and row[k].lower() == 'ya')
    total_q   = sum(1 for k in YES_NO_KEYS if row[k])

    checklist_checked = sum(
        len(_safe_parse_checklist(row[cfg['chk_key']]))
        for cfg in SECTION_CONFIG.values()
    )

    yes_no_score    = (yes_count / total_q * 100)            if total_q > 0               else 0
    checklist_score = (checklist_checked / TOTAL_CHECKLIST_ITEMS * 100) if TOTAL_CHECKLIST_ITEMS > 0 else 0
    final_score     = yes_no_score * SCORE_WEIGHT_YES_NO + checklist_score * SCORE_WEIGHT_CHECKLIST

    return {
        'score':           round(final_score,     1),
        'yes_no_score':    round(yes_no_score,    1),
        'checklist_score': round(checklist_score, 1),
    }

# ---------------------------------------------------------------------------
# Initialize database on startup
# ---------------------------------------------------------------------------
init_db()

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('survey.html')


@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.form

        # Serialize checklist arrays to JSON strings
        poli_q3   = json.dumps(request.form.getlist('poli_q3_checklist'))
        lab_q3    = json.dumps(request.form.getlist('lab_q3_checklist'))
        farmasi_q4 = json.dumps(request.form.getlist('farmasi_q4_checklist'))
        keluhan_q3 = json.dumps(request.form.getlist('keluhan_q3_checklist'))

        # Parse optional GPS metadata
        gps_lat = data.get('gps_lat', '')
        gps_lon = data.get('gps_lon', '')

        gps_distance = None
        gps_distance_str = data.get('gps_distance', '')
        if gps_distance_str:
            try:
                gps_distance = float(gps_distance_str)
            except ValueError:
                pass

        gps_verified = -1
        gps_verified_str = data.get('gps_verified', '')
        if gps_verified_str:
            try:
                gps_verified = int(gps_verified_str)
            except ValueError:
                pass

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO responses (
                    nama_pelaksana, tanggal, waktu, lokasi,
                    gps_lat, gps_lon, gps_distance, gps_verified,
                    poli_klaster, poli_q1_jawab, poli_q1_detail, poli_q2_jawab, poli_q2_detail, poli_q3_checklist, poli_q4_jawab, poli_q4_detail,
                    lab_q1_jawab, lab_q1_detail, lab_q2_jawab, lab_q2_detail, lab_q3_checklist,
                    farmasi_q1_jawab, farmasi_q1_detail, farmasi_q2_jawab, farmasi_q2_detail, farmasi_q3_jawab, farmasi_q3_detail, farmasi_q4_checklist, farmasi_q5_jawab, farmasi_q5_detail, farmasi_q6_jawab, farmasi_q6_detail,
                    keluhan_q1_jawab, keluhan_q1_detail, keluhan_q2_jawab, keluhan_q2_detail, keluhan_q3_checklist
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('nama_pelaksana'),
                data.get('tanggal'),
                data.get('waktu'),
                data.get('lokasi'),

                gps_lat,
                gps_lon,
                gps_distance,
                gps_verified,

                data.get('poli_klaster'),
                data.get('poli_q1_jawab'),
                data.get('poli_q1_detail', ''),
                data.get('poli_q2_jawab'),
                data.get('poli_q2_detail', ''),
                poli_q3,
                data.get('poli_q4_jawab'),
                data.get('poli_q4_detail', ''),

                data.get('lab_q1_jawab'),
                data.get('lab_q1_detail', ''),
                data.get('lab_q2_jawab'),
                data.get('lab_q2_detail', ''),
                lab_q3,

                data.get('farmasi_q1_jawab'),
                data.get('farmasi_q1_detail', ''),
                data.get('farmasi_q2_jawab'),
                data.get('farmasi_q2_detail', ''),
                data.get('farmasi_q3_jawab'),
                data.get('farmasi_q3_detail', ''),
                farmasi_q4,
                data.get('farmasi_q5_jawab'),
                data.get('farmasi_q5_detail', ''),
                data.get('farmasi_q6_jawab'),
                data.get('farmasi_q6_detail', ''),

                data.get('keluhan_q1_jawab'),
                data.get('keluhan_q1_detail', ''),
                data.get('keluhan_q2_jawab'),
                data.get('keluhan_q2_detail', ''),
                keluhan_q3,
            ))
            conn.commit()
        finally:
            conn.close()

        return jsonify({'status': 'success', 'message': 'Survei berhasil dikirim! Terima kasih.'})

    except Exception as e:
        logger.error('Submit error: %s', e, exc_info=True)
        return jsonify({'status': 'error', 'message': 'Terjadi kesalahan saat menyimpan data. Hubungi administrator.'}), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('dashboard'))
        else:
            error = 'Nama pengguna atau kata sandi tidak sesuai. Silakan coba lagi.'

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
@admin_required
def dashboard():
    conn = get_db_connection()
    try:
        total_responses = conn.execute('SELECT COUNT(*) FROM responses').fetchone()[0]

        location_counts_query = conn.execute('''
            SELECT lokasi, COUNT(*) as count
            FROM responses
            GROUP BY lokasi
            ORDER BY count DESC
        ''').fetchall()
        location_data = {row['lokasi']: row['count'] for row in location_counts_query}

        all_responses = conn.execute('SELECT * FROM responses').fetchall()
    finally:
        conn.close()

    # Build per-row compliance data for the table and detail modal
    compliance_scores = []
    for row in all_responses:
        scores = _compute_compliance_score(row)
        compliance_scores.append({
            'id':             row['id'],
            'nama_pelaksana': row['nama_pelaksana'],
            'tanggal':        row['tanggal'],
            'waktu':          row['waktu'],
            'lokasi':         row['lokasi'],
            'gps_lat':        row['gps_lat'],
            'gps_lon':        row['gps_lon'],
            'gps_distance':   row['gps_distance'],
            'gps_verified':   row['gps_verified'],
            'raw':            dict(row),
            **scores,
        })

    avg_score = (
        round(sum(item['score'] for item in compliance_scores) / len(compliance_scores), 1)
        if compliance_scores else 0
    )

    # Per-section performance aggregation
    section_performances = {s: 0.0 for s in SECTION_CONFIG}
    if all_responses:
        for section, cfg in SECTION_CONFIG.items():
            yn_keys   = cfg['yn_keys']
            chk_key   = cfg['chk_key']
            chk_total = cfg['chk_total']

            s_yes_no  = []
            s_chk_pct = []

            for row in all_responses:
                yn_yes = sum(1 for k in yn_keys if row[k] and row[k].lower() == 'ya')
                yn_tot = sum(1 for k in yn_keys if row[k])
                if yn_tot > 0:
                    s_yes_no.append(yn_yes / yn_tot)

                chk_cnt = len(_safe_parse_checklist(row[chk_key]))
                s_chk_pct.append(chk_cnt / chk_total)

            avg_yn  = (sum(s_yes_no)  / len(s_yes_no)  * 100) if s_yes_no  else 0
            avg_chk = (sum(s_chk_pct) / len(s_chk_pct) * 100) if s_chk_pct else 0
            section_performances[section] = round((avg_yn + avg_chk) / 2, 1)

    return render_template(
        'dashboard.html',
        total_responses=total_responses,
        location_data=json.dumps(location_data),
        compliance_scores=compliance_scores,
        avg_score=avg_score,
        section_performances=section_performances,
    )


@app.route('/export')
@admin_required
def export_csv():
    conn = get_db_connection()
    try:
        df = pd.read_sql_query('SELECT * FROM responses', conn)
    except Exception as e:
        logger.error('Export DB read error: %s', e, exc_info=True)
        return 'Gagal membaca data. Hubungi administrator.', 500
    finally:
        conn.close()

    try:
        checklist_cols = ['poli_q3_checklist', 'lab_q3_checklist', 'farmasi_q4_checklist', 'keluhan_q3_checklist']
        for col in checklist_cols:
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: ', '.join(_safe_parse_checklist(x)) if x else ''
                )

        filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'survey_responses.csv')
        df.to_csv(filepath, index=False, encoding='utf-8-sig')

        return send_file(
            filepath,
            as_attachment=True,
            download_name='hasil_survei_cekrek.csv',
            mimetype='text/csv',
        )
    except Exception as e:
        logger.error('Export CSV write error: %s', e, exc_info=True)
        return 'Gagal membuat file CSV. Hubungi administrator.', 500


@app.route('/backup-db')
@admin_required
def backup_db():
    if not os.path.exists(DATABASE):
        return 'Database tidak ditemukan.', 404

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'survey_backup_{timestamp}.db'

    try:
        backup_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, backup_filename)

        source_conn = get_db_connection()
        dest_conn = sqlite3.connect(backup_path)
        with dest_conn:
            source_conn.backup(dest_conn)
        dest_conn.close()
        source_conn.close()

        return send_file(
            backup_path,
            as_attachment=True,
            download_name=backup_filename,
            mimetype='application/x-sqlite3',
        )
    except Exception as e:
        logger.error('Database backup error: %s', e, exc_info=True)
        return 'Gagal melakukan backup database. Hubungi administrator.', 500


if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
