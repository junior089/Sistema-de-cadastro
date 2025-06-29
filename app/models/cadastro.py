from app import db
from datetime import datetime
from app.utils.logger_config import get_logger, log_database_operation

logger = get_logger('models')

class Cadastro(db.Model):
    """Registration entity."""
    __tablename__ = 'cadastro'

    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(11), nullable=False)
    telefone = db.Column(db.String(15), nullable=True)
    assentamento = db.Column(db.String(255), nullable=True)
    municipio_id = db.Column(db.Integer, db.ForeignKey('municipio.id'), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado.id'), nullable=False)
    descricao_id = db.Column(db.Integer, db.ForeignKey('descricao.id'), nullable=False)
    instituicao_id = db.Column(db.Integer, db.ForeignKey('instituicao.id'), nullable=False)
    atendente_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    atendida = db.Column(db.Boolean, default=False, nullable=False)

    senha_chamada = db.Column(db.String(8), nullable=True)  # Senha de chamada gerada automaticamente
    status_chamada = db.Column(db.String(20), default='aguardando', nullable=False)  # aguardando, chamado, atendido, ausente, cancelado
    horario_chamada = db.Column(db.DateTime, nullable=True)  # Última vez chamado
    historico_chamadas = db.Column(db.Text, nullable=True)  # JSON com histórico de chamadas
    prioridade = db.Column(db.Integer, default=0, nullable=False)  # 0=normal, 1=alta, 2=urgente
    posicao_fila = db.Column(db.Integer, nullable=True)  # Posição na fila de espera
    observacoes = db.Column(db.Text, nullable=True)  # Observações sobre a chamada

    municipio = db.relationship('Municipio', back_populates='cadastros')
    estado = db.relationship('Estado', back_populates='cadastros')
    descricao = db.relationship('Descricao', back_populates='cadastros')
    instituicao = db.relationship('Instituicao', back_populates='cadastros')
    atendente = db.relationship('User', back_populates='cadastros')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug(f"Novo objeto Cadastro criado - Nome: {kwargs.get('nome', 'N/A')}")

    def __repr__(self):
        return f'<Cadastro {self.nome}>'

    def gerar_senha_chamada(self, tamanho=4):
        import random
        import string
        logger.debug(f"Gerando senha de chamada para cadastro ID: {self.id}")
        
        # Gera senha com números e letras para facilitar a identificação
        caracteres = string.ascii_uppercase + string.digits
        # Remove caracteres confusos (0, O, 1, I, etc.)
        caracteres = caracteres.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
        self.senha_chamada = ''.join(random.choice(caracteres) for _ in range(tamanho))
        
        # Define prioridade baseada em critérios (pode ser expandido)
        if self.prioridade == 0:
            self.senha_chamada = f"LAB{self.senha_chamada}"  # Laboratório normal
        elif self.prioridade == 1:
            self.senha_chamada = f"PRI{self.senha_chamada}"  # Prioridade alta
        elif self.prioridade == 2:
            self.senha_chamada = f"URG{self.senha_chamada}"  # Urgente
        
        logger.info(f"Senha de chamada gerada - Cadastro ID: {self.id} - Senha: {self.senha_chamada} - Prioridade: {self.prioridade}")

    def definir_prioridade(self, nivel, observacoes=None):
        """Define a prioridade da chamada (0=normal, 1=alta, 2=urgente)"""
        logger.debug(f"Definindo prioridade - Cadastro ID: {self.id} - Nível: {nivel}")
        
        nivel_anterior = self.prioridade
        self.prioridade = nivel
        
        # Atualiza observações
        if observacoes:
            self.observacoes = observacoes
        else:
            prioridades = ['NORMAL', 'ALTA', 'URGENTE']
            self.observacoes = f"Prioridade {prioridades[nivel]} definida"
        
        # Regenera senha se a prioridade mudou
        if nivel_anterior != nivel:
            self.gerar_senha_chamada()
        
        logger.info(f"Prioridade definida - Cadastro ID: {self.id} - Nível anterior: {nivel_anterior} - Novo nível: {nivel}")

    def entrar_fila(self):
        """Coloca o cadastro na fila de espera"""
        logger.debug(f"Entrando na fila - Cadastro ID: {self.id}")
        
        from app.models.cadastro import Cadastro
        # Busca a última posição na fila
        ultima_posicao = db.session.query(db.func.max(Cadastro.posicao_fila)).scalar() or 0
        self.posicao_fila = ultima_posicao + 1
        self.status_chamada = 'aguardando'
        
        logger.info(f"Entrou na fila - Cadastro ID: {self.id} - Posição: {self.posicao_fila}")

    def sair_fila(self):
        """Remove o cadastro da fila"""
        logger.debug(f"Saindo da fila - Cadastro ID: {self.id}")
        
        posicao_anterior = self.posicao_fila
        self.posicao_fila = None
        self.status_chamada = 'chamado'
        
        logger.info(f"Saiu da fila - Cadastro ID: {self.id} - Posição anterior: {posicao_anterior}")

    def proximo_fila(self):
        """Retorna o próximo cadastro na fila por prioridade"""
        from app.models.cadastro import Cadastro
        logger.debug("Buscando próximo da fila")
        
        proximo = Cadastro.query.filter(
            Cadastro.status_chamada == 'aguardando',
            Cadastro.posicao_fila.isnot(None)
        ).order_by(
            Cadastro.prioridade.desc(),
            Cadastro.posicao_fila.asc()
        ).first()
        
        if proximo:
            logger.info(f"Próximo da fila encontrado - Cadastro ID: {proximo.id} - Nome: {proximo.nome} - Senha: {proximo.senha_chamada}")
        else:
            logger.info("Nenhum cadastro na fila encontrado")
        
        return proximo

    def tempo_espera(self):
        """Calcula o tempo de espera desde o cadastro"""
        if self.data_hora:
            tempo = datetime.now() - self.data_hora
            logger.debug(f"Tempo de espera calculado - Cadastro ID: {self.id} - Tempo: {tempo}")
            return tempo
        logger.warning(f"Não foi possível calcular tempo de espera - Cadastro ID: {self.id} - Data/hora não definida")
        return None

    def save(self, user=None):
        """Método personalizado para salvar com logging"""
        try:
            if self.id is None:
                # Novo cadastro
                logger.info(f"Criando novo cadastro - Nome: {self.nome} - CPF: {self.cpf}")
                log_database_operation('CREATE', 'cadastro', None, user)
            else:
                # Atualizando cadastro existente
                logger.info(f"Atualizando cadastro - ID: {self.id} - Nome: {self.nome}")
                log_database_operation('UPDATE', 'cadastro', self.id, user)
            
            db.session.add(self)
            db.session.commit()
            
            logger.info(f"Cadastro salvo com sucesso - ID: {self.id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao salvar cadastro - Nome: {self.nome} - Erro: {str(e)}")
            return False

    def delete(self, user=None):
        """Método personalizado para deletar com logging"""
        try:
            cadastro_id = self.id
            nome = self.nome
            
            logger.info(f"Deletando cadastro - ID: {cadastro_id} - Nome: {nome}")
            log_database_operation('DELETE', 'cadastro', cadastro_id, user)
            
            db.session.delete(self)
            db.session.commit()
            
            logger.info(f"Cadastro deletado com sucesso - ID: {cadastro_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao deletar cadastro - ID: {self.id} - Erro: {str(e)}")
            return False

    @classmethod
    def buscar_por_cpf(cls, cpf, user=None):
        """Busca cadastro por CPF com logging"""
        logger.debug(f"Buscando cadastro por CPF - CPF: {cpf}")
        
        try:
            cadastro = cls.query.filter_by(cpf=cpf).first()
            if cadastro:
                logger.info(f"Cadastro encontrado por CPF - ID: {cadastro.id} - Nome: {cadastro.nome}")
                log_database_operation('READ', 'cadastro', cadastro.id, user)
            else:
                logger.info(f"Cadastro não encontrado por CPF - CPF: {cpf}")
            
            return cadastro
        except Exception as e:
            logger.error(f"Erro ao buscar cadastro por CPF - CPF: {cpf} - Erro: {str(e)}")
            return None

    @classmethod
    def buscar_por_telefone(cls, telefone, user=None):
        """Busca cadastro por telefone com logging"""
        logger.debug(f"Buscando cadastro por telefone - Telefone: {telefone}")
        
        try:
            cadastro = cls.query.filter_by(telefone=telefone).first()
            if cadastro:
                logger.info(f"Cadastro encontrado por telefone - ID: {cadastro.id} - Nome: {cadastro.nome}")
                log_database_operation('READ', 'cadastro', cadastro.id, user)
            else:
                logger.info(f"Cadastro não encontrado por telefone - Telefone: {telefone}")
            
            return cadastro
        except Exception as e:
            logger.error(f"Erro ao buscar cadastro por telefone - Telefone: {telefone} - Erro: {str(e)}")
            return None

    @classmethod
    def buscar_por_nome(cls, nome, user=None):
        """Busca cadastro por nome com logging"""
        logger.debug(f"Buscando cadastro por nome - Nome: {nome}")
        
        try:
            cadastro = cls.query.filter(cls.nome.ilike(nome)).first()
            if cadastro:
                logger.info(f"Cadastro encontrado por nome - ID: {cadastro.id} - Nome: {cadastro.nome}")
                log_database_operation('READ', 'cadastro', cadastro.id, user)
            else:
                logger.info(f"Cadastro não encontrado por nome - Nome: {nome}")
            
            return cadastro
        except Exception as e:
            logger.error(f"Erro ao buscar cadastro por nome - Nome: {nome} - Erro: {str(e)}")
            return None

    def get_senhas_anteriores(self):
        """Retorna histórico de senhas anteriores"""
        import json
        logger.debug(f"Buscando senhas anteriores - Cadastro ID: {self.id}")
        
        if not self.historico_chamadas:
            return []
        
        try:
            historico = json.loads(self.historico_chamadas)
            senhas_anteriores = []
            
            for chamada in historico:
                if 'senha' in chamada:
                    senhas_anteriores.append({
                        'senha': chamada['senha'],
                        'data_hora': chamada.get('data_hora', ''),
                        'usuario': chamada.get('usuario', ''),
                        'status': chamada.get('status', '')
                    })
            
            logger.debug(f"Senhas anteriores encontradas - Cadastro ID: {self.id} - Quantidade: {len(senhas_anteriores)}")
            return senhas_anteriores
            
        except Exception as e:
            logger.error(f"Erro ao buscar senhas anteriores - Cadastro ID: {self.id} - Erro: {str(e)}")
            return []

    def registrar_chamada(self, usuario, acao="chamado", senha=None):
        import json
        from datetime import datetime
        logger.debug(f"Registrando chamada - Cadastro ID: {self.id} - Usuário: {usuario} - Ação: {acao}")
        
        historico = []
        if self.historico_chamadas:
            try:
                historico = json.loads(self.historico_chamadas)
            except Exception as e:
                logger.warning(f"Erro ao carregar histórico de chamadas - Cadastro ID: {self.id} - Erro: {str(e)}")
                historico = []
        
        nova_chamada = {
            'usuario': usuario,
            'data_hora': datetime.now().isoformat(),
            'status': self.status_chamada,
            'acao': acao,
            'observacoes': self.observacoes,
            'senha': senha or self.senha_chamada,
            'prioridade': self.prioridade
        }
        historico.append(nova_chamada)
        self.historico_chamadas = json.dumps(historico)
        
        logger.info(f"Chamada registrada - Cadastro ID: {self.id} - Usuário: {usuario} - Ação: {acao} - Senha: {nova_chamada['senha']}")

    @classmethod
    def buscar_por_senha(cls, senha, user=None):
        """Busca cadastro por senha de chamada com logging"""
        logger.debug(f"Buscando cadastro por senha - Senha: {senha}")
        
        try:
            cadastro = cls.query.filter_by(senha_chamada=senha).first()
            if cadastro:
                logger.info(f"Cadastro encontrado por senha - ID: {cadastro.id} - Nome: {cadastro.nome} - Senha: {senha}")
                log_database_operation('READ', 'cadastro', cadastro.id, user)
            else:
                logger.info(f"Cadastro não encontrado por senha - Senha: {senha}")
            
            return cadastro
        except Exception as e:
            logger.error(f"Erro ao buscar cadastro por senha - Senha: {senha} - Erro: {str(e)}")
            return None

    @classmethod
    def listar_por_prioridade(cls, prioridade=None, user=None):
        """Lista cadastros por prioridade com logging"""
        logger.debug(f"Listando cadastros por prioridade - Prioridade: {prioridade}")
        
        try:
            if prioridade is not None:
                cadastros = cls.query.filter_by(prioridade=prioridade).order_by(cls.data_hora.desc()).all()
            else:
                cadastros = cls.query.order_by(cls.prioridade.desc(), cls.data_hora.desc()).all()
            
            logger.info(f"Cadastros encontrados por prioridade - Prioridade: {prioridade} - Quantidade: {len(cadastros)}")
            log_database_operation('READ', 'cadastro', None, user)
            
            return cadastros
        except Exception as e:
            logger.error(f"Erro ao listar cadastros por prioridade - Prioridade: {prioridade} - Erro: {str(e)}")
            return []

    @classmethod
    def listar_aguardando_chamada(cls, user=None):
        """Lista cadastros aguardando chamada com logging"""
        logger.debug("Listando cadastros aguardando chamada")
        
        try:
            cadastros = cls.query.filter(
                cls.status_chamada == 'aguardando',
                cls.senha_chamada.isnot(None)
            ).order_by(
                cls.prioridade.desc(),
                cls.data_hora.asc()
            ).all()
            
            logger.info(f"Cadastros aguardando chamada encontrados - Quantidade: {len(cadastros)}")
            log_database_operation('READ', 'cadastro', None, user)
            
            return cadastros
        except Exception as e:
            logger.error(f"Erro ao listar cadastros aguardando chamada - Erro: {str(e)}")
            return []
