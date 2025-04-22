import json
import os
from getpass import getpass

class ContaBancaria:
    def __init__(self, numero, cliente, saldo=0.0):
        self.numero = numero
        self.cliente = cliente
        self.saldo = saldo
        self.extrato = []
        self.saques_realizados = 0
        self.LIMITE_SAQUES = 3
        self.LIMITE_POR_SAQUE = 500.0

    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor
            self.extrato.append(f"Depósito: +R$ {valor:.2f}")
            return True
        return False

    def sacar(self, valor):
        if self.saques_realizados >= self.LIMITE_SAQUES:
            return "Limite diário de saques atingido."
        elif valor > self.LIMITE_POR_SAQUE:
            return f"Limite por saque: R$ {self.LIMITE_POR_SAQUE:.2f}."
        elif valor > self.saldo:
            return "Saldo insuficiente."
        elif valor > 0:
            self.saldo -= valor
            self.extrato.append(f"Saque: -R$ {valor:.2f}")
            self.saques_realizados += 1
            return True
        return "Valor inválido."

    def transferir(self, valor, conta_destino):
        if valor > self.saldo:
            return "Saldo insuficiente."
        elif valor <= 0:
            return "Valor inválido."
        else:
            self.saldo -= valor
            conta_destino.saldo += valor
            self.extrato.append(f"Transferência para {conta_destino.numero}: -R$ {valor:.2f}")
            conta_destino.extrato.append(f"Transferência de {self.numero}: +R$ {valor:.2f}")
            return True

    def ver_extrato(self):
        print(f"\n=== EXTRATO CONTA {self.numero} ===")
        print(f"Cliente: {self.cliente}")
        print("\nMovimentações:")
        for mov in self.extrato[-10:] if len(self.extrato) > 10 else self.extrato:
            print(mov)
        print(f"\nSaldo: R$ {self.saldo:.2f}")
        print("="*30)

class Banco:
    def __init__(self):
        self.contas = {}
        self.usuarios = {}
        self.carregar_dados()

    def carregar_dados(self):
        if os.path.exists('banco.json'):
            with open('banco.json', 'r') as f:
                dados = json.load(f)
                for num, conta_data in dados.get('contas', {}).items():
                    conta = ContaBancaria(
                        num,
                        conta_data['cliente'],
                        conta_data['saldo']
                    )
                    conta.extrato = conta_data['extrato']
                    conta.saques_realizados = conta_data['saques']
                    self.contas[num] = conta
                self.usuarios = dados.get('usuarios', {})

    def salvar_dados(self):
        dados = {
            'contas': {
                num: {
                    'cliente': conta.cliente,
                    'saldo': conta.saldo,
                    'extrato': conta.extrato,
                    'saques': conta.saques_realizados
                }
                for num, conta in self.contas.items()
            },
            'usuarios': self.usuarios
        }
        with open('banco.json', 'w') as f:
            json.dump(dados, f)

    def cadastrar_usuario(self, cliente, senha):
        if cliente in self.usuarios:
            return False, "Usuário já existe!"
        self.usuarios[cliente] = {'senha': senha, 'conta': None}
        return True, "Usuário cadastrado com sucesso!"

    def cadastrar_conta_bancaria(self, cliente):
        if cliente not in self.usuarios:
            return False, "Usuário não encontrado!"
        
        if self.usuarios[cliente]['conta'] is not None:
            return False, "Usuário já possui conta cadastrada!"
        
        num_conta = str(len(self.contas) + 1).zfill(4)
        self.contas[num_conta] = ContaBancaria(num_conta, cliente)
        self.usuarios[cliente]['conta'] = num_conta
        self.salvar_dados()
        return True, f"Conta {num_conta} criada com sucesso para {cliente}!"

    def login(self, cliente, senha):
        usuario = self.usuarios.get(cliente)
        if usuario and usuario['senha'] == senha:
            return usuario['conta']
        return None

def menu_principal():
    print("\n=== BANCO PYTHON ===")
    print("1. Criar usuário")
    print("2. Criar conta bancária")
    print("3. Acessar conta")
    print("4. Sair")
    return input("Opção: ")

def menu_conta():
    print("\n=== MENU CONTA ===")
    print("1. Depositar")
    print("2. Sacar")
    print("3. Transferir")
    print("4. Extrato")
    print("5. Sair")
    return input("Opção: ")

def operacao_depositar(conta, banco):
    try:
        valor = float(input("Valor: R$ "))
        if conta.depositar(valor):
            banco.salvar_dados()
            print("Depósito realizado!")
        else:
            print("Valor inválido!")
    except ValueError:
        print("Digite um número válido!")

def operacao_sacar(conta, banco):
    try:
        valor = float(input("Valor: R$ "))
        res = conta.sacar(valor)
        if res is True:
            banco.salvar_dados()
            print("Saque realizado!")
        else:
            print(res)
    except ValueError:
        print("Digite um número válido!")

def operacao_transferir(conta, banco):
    try:
        destino = input("Conta destino: ").strip()
        if destino not in banco.contas:
            print("Conta não encontrada!")
        else:
            valor = float(input("Valor: R$ "))
            res = conta.transferir(valor, banco.contas[destino])
            if res is True:
                banco.salvar_dados()
                print("Transferência realizada!")
            else:
                print(res)
    except ValueError:
        print("Digite um número válido!")

def main():
    banco = Banco()
    
    while True:
        opcao = menu_principal()
        
        if opcao == "1":
            cliente = input("Nome: ").strip()
            senha = getpass("Senha: ")
            sucesso, mensagem = banco.cadastrar_usuario(cliente, senha)
            print(mensagem)
            if sucesso:
                banco.salvar_dados()
                
        elif opcao == "2":
            cliente = input("Nome do usuário: ").strip()
            sucesso, mensagem = banco.cadastrar_conta_bancaria(cliente)
            print(mensagem)
            if sucesso:
                banco.salvar_dados()
                
        elif opcao == "3":
            cliente = input("Usuário: ").strip()
            senha = getpass("Senha: ")
            num_conta = banco.login(cliente, senha)
            
            if num_conta:
                conta = banco.contas[num_conta]
                print(f"\nBem-vindo, {conta.cliente}!")
                
                while True:
                    op = menu_conta()
                    
                    if op == "1":
                        operacao_depositar(conta, banco)
                    elif op == "2":
                        operacao_sacar(conta, banco)
                    elif op == "3":
                        operacao_transferir(conta, banco)
                    elif op == "4":
                        conta.ver_extrato()
                    elif op == "5":
                        print("Sessão encerrada.")
                        break
                    else:
                        print("Opção inválida!")
            else:
                print("Usuário ou senha incorretos!")
                
        elif opcao == "4":
            print("Sistema encerrado.")
            break
            
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()