import unittest
import os
import json
import sqlite3
from app import app, DATABASE


class SurveyAppTestCase(unittest.TestCase):

    TEST_PELAKSANA = 'Asep Penilai [TEST]'

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        # Ensure a clean slate for the test persona before each test
        self._delete_test_records()

    def tearDown(self):
        # Remove all records written by this test run to avoid polluting the DB
        self._delete_test_records()

    def _delete_test_records(self):
        conn = sqlite3.connect(DATABASE)
        try:
            conn.execute(
                'DELETE FROM responses WHERE nama_pelaksana = ?',
                (self.TEST_PELAKSANA,)
            )
            conn.commit()
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Page-load tests
    # ------------------------------------------------------------------

    def test_survey_page_loads(self):
        """Main survey form returns 200 and contains expected content."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CeKReK', response.data)
        self.assertIn(b'Form Penilaian Awal', response.data)

    def test_dashboard_page_loads(self):
        """Dashboard page returns 200."""
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------
    # Submission test
    # ------------------------------------------------------------------

    def test_survey_submission(self):
        """Full form submission stores data correctly and export is available."""
        payload = {
            'nama_pelaksana': self.TEST_PELAKSANA,
            'tanggal': '2026-08-27',
            'waktu': '23:30',
            'lokasi': 'Puskesmas Mojo',

            # GPS metadata
            'gps_lat': '-7.8925',
            'gps_lon': '111.9615',
            'gps_distance': '50',
            'gps_verified': '1',

            # Poli
            'poli_klaster': 'Klaster 2 (Ibu, Anak, Prasekolah, Remaja)',
            'poli_q1_jawab': 'Ya',
            'poli_q2_jawab': 'Tidak',
            'poli_q2_detail': 'AC tidak dingin',
            'poli_q3_checklist': [
                'Dokter/Petugas menunjukkan senyum saat sambut pasien/penerima layanan',
                'Dokter/Petugas mengucapkan salam saat sambut pasien/penerima layanan',
            ],
            'poli_q4_jawab': 'Ya',

            # Lab
            'lab_q1_jawab': 'Ya',
            'lab_q2_jawab': 'Ya',
            'lab_q3_checklist': [
                'Petugas menunjukkan senyum saat sambut pasien/penerima layanan',
                'Petugas mengucapkan salam saat sambut pasien/penerima layanan',
            ],

            # Farmasi
            'farmasi_q1_jawab': 'Ya',
            'farmasi_q2_jawab': 'Ya',
            'farmasi_q3_jawab': 'Tidak',
            'farmasi_q3_detail': 'Obat batuk kosong',
            'farmasi_q4_checklist': [
                'Petugas Farmasi menunjukkan senyum saat menyambut',
                'Petugas Farmasi mengkonfirmasi identitas pasien',
            ],
            'farmasi_q5_jawab': 'Ya',
            'farmasi_q6_jawab': 'Ya',

            # Keluhan
            'keluhan_q1_jawab': 'Ya',
            'keluhan_q2_jawab': 'Ya',
            'keluhan_q3_checklist': [
                'Petugas menawarkan bantuan',
                'Petugas menanyakan nama penerima dan mencatat identitas penerima layanan',
            ],
        }

        response = self.client.post('/submit', data=payload)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('dikirim', data['message'])

        # Verify the record is persisted with correct values — use named columns
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM responses WHERE nama_pelaksana = ?',
                (self.TEST_PELAKSANA,)
            )
            row = cursor.fetchone()
        finally:
            conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row['lokasi'],       'Puskesmas Mojo')
        self.assertEqual(row['gps_lat'],      '-7.8925')
        self.assertEqual(row['gps_lon'],      '111.9615')
        self.assertEqual(row['gps_distance'],  50.0)
        self.assertEqual(row['gps_verified'],   1)
        self.assertEqual(row['poli_q2_detail'], 'AC tidak dingin')

        # Export should succeed now that data exists
        export_resp = self.client.get('/export')
        self.assertEqual(export_resp.status_code, 200)
        self.assertIn('text/csv', export_resp.headers['Content-Type'])


if __name__ == '__main__':
    unittest.main()
