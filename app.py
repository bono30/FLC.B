
from flask import Flask, render_template, request, jsonify, send_file
import os
import math
import csv
import matplotlib.pyplot as plt

app = Flask(__name__)

data_store = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/salvar', methods=['POST'])
def salvar():
    dados = request.json
    diametro = float(dados['diametro'])
    eixo_maior = math.dist(dados['maior'][0], dados['maior'][1])
    eixo_menor = math.dist(dados['menor'][0], dados['menor'][1])

    epsilon_maior = math.log(eixo_maior / diametro)
    epsilon_menor = math.log(eixo_menor / diametro)

    resultado = {
        'ID': len(data_store) + 1,
        'Eixo_maior_mm': round(eixo_maior, 3),
        'Eixo_menor_mm': round(eixo_menor, 3),
        'Deformacao_maior': round(epsilon_maior, 5),
        'Deformacao_menor': round(epsilon_menor, 5)
    }

    data_store.append(resultado)
    gerar_grafico()
    salvar_csv()
    return jsonify(data_store)

def salvar_csv():
    if not data_store:
        return
    os.makedirs('data', exist_ok=True)
    csv_path = 'data/resultados.csv'
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = data_store[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in data_store:
            writer.writerow(data)

def gerar_grafico():
    eps1 = [d['Deformacao_maior'] for d in data_store]
    eps2 = [d['Deformacao_menor'] for d in data_store]

    plt.figure(figsize=(6,6))
    plt.scatter(eps1, eps2, color='blue')
    plt.xlabel('Deformação Maior (ε₁)')
    plt.ylabel('Deformação Menor (ε₂)')
    plt.title('Curva FLC (Forming Limit Curve)')
    plt.grid(True)
    plt.savefig('static/flc_plot.png')
    plt.close()

@app.route('/baixar_csv')
def baixar_csv():
    return send_file('data/resultados.csv', as_attachment=True)

@app.route('/resetar', methods=['POST'])
def resetar():
    global data_store
    data_store = []
    if os.path.exists('data/resultados.csv'):
        os.remove('data/resultados.csv')
    if os.path.exists('static/flc_plot.png'):
        os.remove('static/flc_plot.png')
    return jsonify({'status': 'resetado'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
