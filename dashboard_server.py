import http.server
import socketserver
import json
import csv
import os
from datetime import datetime

# Railway fornece PORT via variável de ambiente, senão usa 8080
PORT = int(os.environ.get('PORT', 8080))
CSV_FILE = 'historico_tracker.csv'

# Handler customizado para lidar com arquivos estáticos e endpoints de API
class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 1. Endpoint da API que retorna dados do CSV formatados em JSON
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            # Permite CORS para desenvolvimento local se necessário
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            data = self.read_csv_data()
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return
            
        # 2. Rota raiz '/' redireciona para serve o 'dashboard.html'
        elif self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            with open('dashboard.html', 'r', encoding='utf-8') as f:
                self.wfile.write(f.read().encode('utf-8'))
            return
            
        # 3. Serve as capturas de fotos de forma dinâmica
        elif self.path.startswith('/capturas/'):
            # Corrige caminhos relativos de imagem
            relative_path = self.path.lstrip('/')
            if os.path.exists(relative_path):
                self.send_response(200)
                self.send_header('Content-type', 'image/jpeg')
                self.end_headers()
                with open(relative_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
            return
            
        # 4. Caso contrário, deixa o handler padrão servir outros arquivos estáticos
        return super().do_GET()

    def read_csv_data(self):
        records = []
        
        # Se o arquivo CSV não existir ou estiver vazio, envia dados mockados simulando um dia perfeito de sol
        # Isso garante que a interface fique maravilhosa no primeiro uso do usuário!
        if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) < 50:
            print("[SERVER] historico_tracker.csv não encontrado ou vazio. Servindo dados demonstrativos premium...")
            base_time = datetime.now().replace(hour=8, minute=0, second=0)
            for i in range(30):
                # Simula o movimento do sol ao longo de 8 horas (de 90 a 140 graus em Pan, e oscilando de 70 a 110 em Tilt)
                hour_offset = i * 15 # minutos
                record_time = datetime.fromtimestamp(base_time.timestamp() + hour_offset * 60)
                
                # Simula trajetória solar suave
                pan_val = int(45 + (i * 3.5)) # de 45 a 150 graus
                tilt_val = int(80 + (15 * (i % 5 - 2) / 5)) # oscilando levemente na altura
                
                records.append({
                    'Data_Hora': record_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'Caminho_Imagem': 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=400&q=80', # Imagem demo premium
                    'Posicao_Pan': pan_val,
                    'Posicao_Tilt': tilt_val,
                    'is_mock': True
                })
            return records

        # Se houver dados reais no CSV, faz o parse e os envia
        try:
            with open(CSV_FILE, mode='r', encoding='utf-8') as f:
                # O delimitador ';' foi otimizado para o Excel em português
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    records.append({
                        'Data_Hora': row.get('Data_Hora', ''),
                        'Caminho_Imagem': row.get('Caminho_Imagem', ''),
                        'Posicao_Pan': int(row.get('Posicao_Pan', 90)),
                        'Posicao_Tilt': int(row.get('Posicao_Tilt', 90)),
                        'is_mock': False
                    })
        except Exception as e:
            print(f"[SERVER ERROR] Erro ao ler CSV: {e}")
            
        return records

def run_server():
    # Permite reutilizar a porta HTTP imediatamente se reiniciar
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("0.0.0.0", PORT), DashboardHandler) as httpd:
        print(f"\n=======================================================")
        print(f"🔥 SOLAR TRACKER DASHBOARD INICIALIZADO COM SUCESSO! 🔥")
        print(f"👉 Porta: {PORT}")
        print(f"👉 Pressione CTRL+C no terminal para encerrar o servidor.")
        print(f"=======================================================\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[SERVER] Servidor do Dashboard encerrado pelo usuário.")

if __name__ == '__main__':
    run_server()
