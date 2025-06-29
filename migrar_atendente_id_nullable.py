import sqlite3

# Caminho do banco de dados (ajuste se necessário)
DB_PATH = 'app/cadastro.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 1. Permitir NULL em atendente_id
c.execute('''
PRAGMA foreign_keys=off;
''')
c.execute('''
ALTER TABLE cadastro RENAME TO cadastro_old;
''')
c.execute('''
CREATE TABLE cadastro (
    id INTEGER PRIMARY KEY,
    data_hora VARCHAR(20),
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(11) NOT NULL,
    telefone VARCHAR(15),
    assentamento VARCHAR(255),
    municipio_id INTEGER NOT NULL,
    estado_id INTEGER NOT NULL,
    descricao_id INTEGER NOT NULL,
    instituicao_id INTEGER NOT NULL,
    atendente_id INTEGER,
    atendida BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY(municipio_id) REFERENCES municipio(id),
    FOREIGN KEY(estado_id) REFERENCES estado(id),
    FOREIGN KEY(descricao_id) REFERENCES descricao(id),
    FOREIGN KEY(instituicao_id) REFERENCES instituicao(id),
    FOREIGN KEY(atendente_id) REFERENCES user(id) ON DELETE SET NULL
);
''')
c.execute('''
INSERT INTO cadastro (id, data_hora, nome, cpf, telefone, assentamento, municipio_id, estado_id, descricao_id, instituicao_id, atendente_id, atendida)
SELECT id, data_hora, nome, cpf, telefone, assentamento, municipio_id, estado_id, descricao_id, instituicao_id, atendente_id, atendida FROM cadastro_old;
''')
c.execute('''
DROP TABLE cadastro_old;
''')
c.execute('''
PRAGMA foreign_keys=on;
''')

conn.commit()
conn.close()

print('Migração concluída: atendente_id agora aceita NULL e ON DELETE SET NULL está ativo.')
