import csv
import locale

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
