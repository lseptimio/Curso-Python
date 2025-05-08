import json

# ======= CLASSES =======

class Cliente:
    def __init__(self, nome, cpf):
        self.nome = nome
        self.cpf = cpf
        self.contas = []

    def adicionar_conta(self, conta):
        self.contas.append(conta)

    def __str__(self):
        return f"Cliente: {self.nome} - CPF: {self.cpf}"


class Conta:
    def __init__(self, numero, cliente, saldo=0):
        self.numero = numero
        self.cliente = cliente
        self.saldo = saldo
        self.transacoes = []

    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor
            self.transacoes.append(f"Depósito: +{valor}")
        else:
            print("Valor inválido para depósito.")

    def sacar(self, valor):
        if 0 < valor <= self.saldo:
            self.saldo -= valor
            self.transacoes.append(f"Saque: -{valor}")
        else:
            print("Saldo insuficiente ou valor inválido.")

    def extrato(self):
        print(f"\nExtrato da conta {self.numero}")
        for transacao in self.transacoes:
            print(transacao)
        print(f"Saldo atual: {self.saldo}\n")

    def transferir(self, destino, valor):
        if 0 < valor <= self.saldo:
            self.saldo -= valor
            destino.saldo += valor
            self.transacoes.append(f"Transferência enviada: -{valor}")
            destino.transacoes.append(f"Transferência recebida: +{valor}")
        else:
            print("Transferência não realizada. Verifique o saldo.")


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, saldo=0, limite=500):
        super().__init__(numero, cliente, saldo)
        self.limite = limite

    def sacar(self, valor):
        if 0 < valor <= (self.saldo + self.limite):
            self.saldo -= valor
            self.transacoes.append(f"Saque CC: -{valor}")
        else:
            print("Saldo e limite insuficientes.")


class Banco:
    def __init__(self):
        self.clientes = []
        self.contas = []

    def adicionar_cliente(self, cliente):
        self.clientes.append(cliente)

    def adicionar_conta(self, conta):
        self.contas.append(conta)
        conta.cliente.adicionar_conta(conta)

    def autenticar(self, cpf, numero_conta):
        for conta in self.contas:
            if conta.numero == numero_conta and conta.cliente.cpf == cpf:
                return conta
        return None

    def salvar_dados(self, arquivo='banco_dados.json'):
        dados = {
            "clientes": [
                {"nome": c.nome, "cpf": c.cpf}
                for c in self.clientes
            ],
            "contas": [
                {
                    "numero": conta.numero,
                    "cpf": conta.cliente.cpf,
                    "saldo": conta.saldo,
                    "tipo": conta.__class__.__name__,
                }
                for conta in self.contas
            ]
        }
        with open(arquivo, 'w') as f:
            json.dump(dados, f)

    def carregar_dados(self, arquivo='banco_dados.json'):
        try:
            with open(arquivo, 'r') as f:
                dados = json.load(f)

            cpf_cliente = {}
            for c in dados['clientes']:
                cliente = Cliente(c['nome'], c['cpf'])
                self.clientes.append(cliente)
                cpf_cliente[c['cpf']] = cliente

            for conta in dados['contas']:
                cliente = cpf_cliente.get(conta['cpf'])
                if conta['tipo'] == "ContaCorrente":
                    nova_conta = ContaCorrente(conta['numero'], cliente, conta['saldo'])
                else:
                    nova_conta = Conta(conta['numero'], cliente, conta['saldo'])
                self.contas.append(nova_conta)
                cliente.adicionar_conta(nova_conta)
        except FileNotFoundError:
            print("Arquivo de dados não encontrado. Iniciando banco vazio.")


# ======= INTERFACE CLI =======

def menu_conta(conta):
    while True:
        print(f"\n--- Conta {conta.numero} ---")
        print("1. Saldo e extrato")
        print("2. Depósito")
        print("3. Saque")
        print("4. Voltar")
        opcao = input("Escolha: ")

        if opcao == '1':
            conta.extrato()
        elif opcao == '2':
            valor = float(input("Valor a depositar: "))
            conta.depositar(valor)
        elif opcao == '3':
            valor = float(input("Valor a sacar: "))
            conta.sacar(valor)
        elif opcao == '4':
            break
        else:
            print("Opção inválida.\n")


def menu_principal(banco):
    while True:
        print("\n=== Banco POO ===")
        print("1. Criar cliente e conta")
        print("2. Acessar conta")
        print("3. Salvar e sair")
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            nome = input("Nome: ")
            cpf = input("CPF: ")
            cliente = Cliente(nome, cpf)
            numero = int(input("Número da conta: "))
            conta = ContaCorrente(numero, cliente, saldo=0)
            banco.adicionar_cliente(cliente)
            banco.adicionar_conta(conta)
            print("Conta criada com sucesso!\n")

        elif escolha == '2':
            cpf = input("Digite seu CPF: ")
            numero = int(input("Número da conta: "))
            conta = banco.autenticar(cpf, numero)
            if conta:
                menu_conta(conta)
            else:
                print("Conta não encontrada.\n")

        elif escolha == '3':
            banco.salvar_dados()
            print("Dados salvos. Saindo...")
            break
        else:
            print("Opção inválida.\n")


# ======= EXECUÇÃO =======

if __name__ == '__main__':
    banco = Banco()
    banco.carregar_dados()
    menu_principal(banco)
