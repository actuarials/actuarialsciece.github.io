from flask import Flask, render_template, request
import locale
import csv
from utils import tabel_mortalita, hitung_brpvfb, hitung_pvfb, hitung_iuran_normal, hitung_kewajiban_aktuaria, format_as_currency

app = Flask(__name__, template_folder='templates')

tabel_mortalita = {}
with open('mortalita.csv', mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if 'n' in row:
            try:
                n = int(row['n'])
                tabel_mortalita[n] = {
                    'q': float(row['q']),
                    'p': float(row['p']),
                    'l': float(row['l']),
                    'v': float(row['v']),
                    'd': float(row['d'])
                }
            except ValueError:
                pass

def format_as_currency(value):
    return locale.currency(value, grouping=True)

n111 = 111

def hitung_brpvfb(k, y, r, sr_minus_1, i):
    br = k * (r - y) * sr_minus_1
    N = 0
    D = tabel_mortalita[r]['d']
    for n_value in range(r, n111 + 1):
        if n_value in tabel_mortalita:
            N += tabel_mortalita[n_value]['d']
    a = N / D
    v = 1 / ((1 + i) ** (r - y)) if y < r else 1
    Ly = tabel_mortalita[y]['l']
    Lr = tabel_mortalita[r]['l']
    p = Lr / Ly
    pvfb = br * a * v * p
    return br, pvfb

def hitung_pvfb(k, y, r, sr_minus_1, i):
    br = k * (r - y) * sr_minus_1
    N = 0
    D = tabel_mortalita[r]['d']
    for n_value in range(r, n111 + 1):
        if n_value in tabel_mortalita:
            N += tabel_mortalita[n_value]['d']
    a = N / D
    Lr = tabel_mortalita[r]['l']
    p_values = [Lr / tabel_mortalita[age]['l'] for age in range(y, r + 1)]
    pvfb_values = []
    for age in range(y, r + 1):
        br_age = k * (r - y) * sr_minus_1
        a_age = N / D
        v_age = 1 / ((1 + i) ** (r - age))
        p_age = p_values[age - y]
        pvfb_age = br_age * a_age * v_age * p_age
        pvfb_values.append(pvfb_age)
    return pvfb_values

def hitung_iuran_normal(pvfb_values, r, y):
    normal_contributions = {}
    total_normal_contributions = 0
    for age, pvfb in enumerate(pvfb_values, start=y):
        age_key = f'{age}'
        normal_contributions[age_key] = pvfb / (r - y)
        total_normal_contributions += normal_contributions[age_key]
    normal_contributions['Total'] = total_normal_contributions
    return normal_contributions

def hitung_kewajiban_aktuaria(pvfb_values, y, x, r):
    pensiun_benefits = {}
    total_pensiun_benefits = 0
    for age, pvfb in enumerate(pvfb_values, start=y):
        age_key = f'{age}'
        pensiun_benefits[age_key] = ((x - y) / (r - y)) * pvfb
        total_pensiun_benefits += pensiun_benefits[age_key]
    pensiun_benefits['Total'] = total_pensiun_benefits
    return pensiun_benefits


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/hitung', methods=['GET', 'POST'])
def hitung():
    br_value = None
    pvfb_value = None
    pvfb_values_result = {}
    normal_contributions_result = {}
    pensiun_benefits_result = {}

    if request.method == 'POST':
        try:
            k_percent_str = request.form['k_percent']
            k_percent_str = k_percent_str.replace(',', '.')
            k = float(k_percent_str) / 100.0

            i_str = request.form['i']
            i_str = i_str.replace(',', '.')
            i = float(i_str) / 100.0

            y = int(request.form['y'])
            x = int(request.form['x'])
            r = int(request.form['r'])
            sr_minus_1_str = request.form['sr_minus_1']
            sr_minus_1_str = sr_minus_1_str.replace('.', '').replace(',', '.')
            sr_minus_1 = float(sr_minus_1_str)

            if k < 0 or k > 1 or y < 0 or r <= y or sr_minus_1 < 0:
                return "Masukan tidak valid. Pastikan k dalam rentang 0-100%, y >= 0, r > y, dan sr_minus_1 >= 0."

            pvfb_values = hitung_pvfb(k, y, r, sr_minus_1, i)

            pvfb_values_formatted = {f'PVFB{age}': locale.currency(pvfb, grouping=True, symbol='Rp') for age, pvfb in enumerate(pvfb_values, start=y)}

            normal_contributions = hitung_iuran_normal(pvfb_values, r, y)
            pensiun_benefits = hitung_kewajiban_aktuaria(pvfb_values, y, x, r)

            pvfb_values_result = pvfb_values_formatted
            normal_contributions_result = normal_contributions
            pensiun_benefits_result = pensiun_benefits

            br, pvfb = hitung_brpvfb(k, y, r, sr_minus_1, i)
            br_value = locale.currency(br, grouping=True, symbol='Rp')
            pvfb_value = locale.currency(pvfb, grouping=True, symbol='Rp')
        except ValueError:
            return "Masukan tidak valid. Pastikan k (persentase), y, r, dan sr_minus_1 adalah angka."

    return render_template('hitung.html', br_value=br_value, pvfb_value=pvfb_value, pvfb_values=pvfb_values_result, normal_contributions=normal_contributions_result, pensiun_benefits=pensiun_benefits_result)

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
    app.jinja_env.filters['format_as_currency'] = format_as_currency
    app.run(debug=True)
