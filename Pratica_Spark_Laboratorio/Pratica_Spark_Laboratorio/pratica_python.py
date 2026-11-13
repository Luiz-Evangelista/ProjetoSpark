
import csv
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


# Caminho do arquivo CSV com os dados das vendas
ENTRADA = Path(__file__).resolve().parent / "dados" / "vendas.csv"


# Converte o preço para decimal e verifica se o valor é válido
def valor_decimal(campo):
    try:
        valor = Decimal((campo or "").strip())
    except InvalidOperation:
        return None

    return valor if valor.is_finite() else None


# Separa as vendas válidas das que precisam ser descartadas
def resumir_parte(linhas):
    rejeitadas = []

    # Guarda os totais de vendas, unidades e faturamento por categoria
    totais = defaultdict(lambda: [0, 0, Decimal("0.00")])

    for linha in linhas:
        categoria = (linha["categoria"] or "").strip()

        # Verifica se a quantidade é um número inteiro
        try:
            quantidade = int(linha["quantidade"] or "")
        except ValueError:
            quantidade = 0

        # Converte o preço do produto
        preco = valor_decimal(linha["preco_unitario"])

        # Descarta os registros que possuem dados inválidos
        if not categoria or quantidade <= 0 or preco is None or preco <= 0:
            rejeitadas.append(linha)
            continue

        # Atualiza os valores da categoria
        total = totais[categoria]
        total[0] += 1
        total[1] += quantidade
        total[2] += quantidade * preco

    # Retorna os registros descartados e os totais calculados
    return rejeitadas, totais


# Formata os valores para aparecerem no formato de moeda brasileira
def moeda(valor):
    return "R$ " + f"{valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def main():
    # Abre o arquivo e faz a leitura dos dados em formato CSV
    with ENTRADA.open(encoding="utf-8-sig", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))

    # Divide os registros em duas partes
    corte = len(linhas) // 2
    partes = [linhas[:corte], linhas[corte:]]

    rejeitadas = []

    # Armazena o resultado geral de cada categoria
    resumo = defaultdict(lambda: [0, 0, Decimal("0.00")])

    print("Simulação didática em Python")
    print("\n1. Registros por partição")

    # Processa cada parte separadamente
    for numero, parte in enumerate(partes):
        print(f"Partição {numero}: {len(parte)} registros")

        # Calcula os resultados de cada parte
        rejeitadas_parte, parcial = resumir_parte(parte)
        rejeitadas.extend(rejeitadas_parte)

        # Junta os resultados das duas partes
        for categoria, (vendas, unidades, faturamento) in parcial.items():
            total = resumo[categoria]
            total[0] += vendas
            total[1] += unidades
            total[2] += faturamento

    # Mostra os registros que foram descartados
    print("\n2. Registros descartados pelo filtro")
    for linha in rejeitadas:
        preco = linha["preco_unitario"] or "vazio"
        print(
            f'{linha["categoria"]} | {linha["produto"]} | quantidade {linha["quantidade"]} | preço {preco}')

    # Exibe o faturamento total de cada categoria
    print("\n3. Faturamento por categoria")
    print(f'{"Categoria":<13} {"Vendas":>6} {"Unidades":>8} {"Faturamento":>13}')

    # Organiza as categorias pelo maior faturamento
    for categoria, (vendas, unidades, faturamento) in sorted(
        resumo.items(), key=lambda item: (-item[1][2], item[0])
    ):
        print(f"{categoria:<13} {vendas:>6} {unidades:>8} {moeda(faturamento):>13}")

    # Soma o faturamento de todas as categorias
    faturamento_geral = sum(total[2] for total in resumo.values())

    print(f"\nFaturamento geral: {moeda(faturamento_geral)}")


# Executa a função principal
if __name__ == "__main__":
    main()
