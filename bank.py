from abc import ABC, abstractmethod
from datetime import datetime

class Cliente:
    def __init__(self, nome, cpf, data_nascimento, endereco):
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)
    
    def adicionar_conta(self, conta):
        self.contas.append(conta)
    
    def exibir_dados(self):
        print("\n" + "="*40)
        print("Dados do Cliente:")
        print(f"Nome: {self.nome}")
        print(f"CPF: {self.cpf}")
        print(f"Data de Nascimento: {self.data_nascimento}")
        print(f"Endereço: {self.endereco}")
        print("Contas:")
        print("="*40)
        for conta in self.contas:
            conta.exibir_dados()
        print("="*40)

class PessoaFisica(Cliente):
    def __init__(self, nome, cpf, data_nascimento, endereco):
        super().__init__(nome, cpf, data_nascimento, endereco)

    def __str__(self):
        return f"{self.nome} (CPF: {self.cpf})"

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)
    
    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        if valor > saldo:
            print("Saldo insuficiente.")
            return False
        elif valor > 0:
            self._saldo -= valor
            self._historico.adicionar_transacao(Saque(valor))
            print(f"Saque de R${valor:.2f} realizado com sucesso.")
            return True
        else:
            print("Operação inválida.")
            return False
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            self._historico.adicionar_transacao(Deposito(valor))
            print(f"Depósito de R${valor:.2f} realizado com sucesso.")
            return True
        else:
            print("Operação inválida.")
            return False

    def transferir(self, valor, conta_destino):
        if self.sacar(valor):
            conta_destino.depositar(valor)
            print(f"Transferência de R${valor:.2f} realizada com sucesso para a conta {conta_destino.numero}.")

    def exibir_dados(self):
        print("\n" + "="*40)
        print(f"Conta {self.numero}:")
        print(f"Agência: {self.agencia}")
        print(f"Saldo: R${self.saldo:.2f}")
        print(f"Titular: {self.cliente.nome}")
        print("="*40)

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self._historico.transacoes if transacao["tipo"] == "Saque"]
        )

        if valor > self._saldo + self._limite:
            print("Valor excede o limite da conta.")
        elif numero_saques >= self._limite_saques:
            print("Número máximo de saques excedido.")
        else:
            super().sacar(valor)

    def __str__(self):
        return f"""
        Agência:\t {self.agencia}
        C/C:\t\t {self.numero}
        Titular:\t {self.cliente.nome}
        """

class Historico:
    def __init__(self):
        self._transacoes = []
    
    @property  
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        })

    def exibir_historico(self):
        if not self._transacoes:
            print("Nenhuma transação registrada.")
            return
        print("\nHistórico de Transações:")
        print("="*40)
        for transacao in self._transacoes:
            print(f"Tipo: {transacao['tipo']}, Valor: R${transacao['valor']:.2f}, Data: {transacao['data']}")
        print("="*40)

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def criar_conta(cliente):
    numero = input("Informe o número da nova conta: ")
    conta = ContaCorrente.nova_conta(cliente, numero)
    cliente.adicionar_conta(conta)
    print("\n" + "="*40)
    print(f"Conta {numero} criada com sucesso.")
    print("="*40)

def exibir_contas(cliente):
    if not cliente.contas:
        print("\nNenhuma conta encontrada.")
        return
    print("\n" + "="*40)
    print("Todas as Contas e Movimentos:")
    print("="*40)
    for conta in cliente.contas:
        conta.exibir_dados()
        conta.historico.exibir_historico()
    print("="*40)

def main():
    print("="*40)
    print("Bem-vindo ao Sistema de Banco")
    print("="*40)
    
    nome = input("Informe o nome do cliente: ")
    cpf = input("Informe o CPF do cliente: ")
    data_nascimento = input("Informe a data de nascimento do cliente (DD/MM/AAAA): ")
    endereco = input("Informe o endereço do cliente: ")
    
    cliente = PessoaFisica(nome, cpf, data_nascimento, endereco)

    while True:
        print("\n" + "="*40)
        print("Menu:")
        print("1. Exibir dados do cliente")
        print("2. Criar nova conta")
        print("3. Realizar depósito")
        print("4. Realizar saque")
        print("5. Realizar transferência")
        print("6. Exibir todas as contas e seus movimentos")
        print("7. Sair")
        print("="*40)
        
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            cliente.exibir_dados()
        elif opcao == '2':
            criar_conta(cliente)
        elif opcao == '3':
            numero_conta = input("Informe o número da conta para depósito: ")
            valor = float(input("Informe o valor do depósito: "))
            conta = next((c for c in cliente.contas if c.numero == numero_conta), None)
            if conta:
                conta.depositar(valor)
            else:
                print("Conta não encontrada.")
        elif opcao == '4':
            numero_conta = input("Informe o número da conta para saque: ")
            valor = float(input("Informe o valor do saque: "))
            conta = next((c for c in cliente.contas if c.numero == numero_conta), None)
            if conta:
                conta.sacar(valor)
            else:
                print("Conta não encontrada.")
        elif opcao == '5':
            numero_conta_origem = input("Informe o número da conta de origem: ")
            numero_conta_destino = input("Informe o número da conta de destino: ")
            valor = float(input("Informe o valor da transferência: "))
            conta_origem = next((c for c in cliente.contas if c.numero == numero_conta_origem), None)
            conta_destino = next((c for c in cliente.contas if c.numero == numero_conta_destino), None)
            if conta_origem and conta_destino:
                conta_origem.transferir(valor, conta_destino)
            else:
                print("Uma ou ambas as contas não foram encontradas.")
        elif opcao == '6':
            exibir_contas(cliente)
        elif opcao == '7':
            print("\n" + "="*40)
            print("Saindo... Até logo!")
            print("="*40)
            break
        else:
            print("\nOpção inválida. Tente novamente.")
            print("="*40)

if __name__ == "__main__":
    main()
