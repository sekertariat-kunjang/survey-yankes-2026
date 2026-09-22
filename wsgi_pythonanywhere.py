# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PythonAnywhere WSGI Configuration File for CeKReK
# Akun: cekrek (cekrek.pythonanywhere.com)
#
# Salin seluruh isi file ini ke dalam editor WSGI di PythonAnywhere:
# /var/www/cekrek_pythonanywhere_com_wsgi.py
# (Dapat diakses melalui Web Tab -> Klik link "WSGI configuration file")
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import sys
import os

# 1. Tambahkan path folder proyek ke sys.path
project_home = '/home/cekrek/survey-yankes-2026'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 2. Atur direktori kerja saat ini (working directory)
os.chdir(project_home)

# 3. Impor objek Flask app sebagai 'application' (dibutuhkan oleh WSGI PythonAnywhere)
from app import app as application
