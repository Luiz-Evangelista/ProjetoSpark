
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


# Caminho onde está o arquivo CSV com os dados das vendas
ENTRADA = Path(__file__).resolve().parent / "dados" / "vendas.csv"

# Define os tipos de dados de cada coluna do arquivo
ESQUEMA = (
    "categoria STRING, produto STRING, "
    "quantidade INT, preco_unitario DECIMAL(12,2)"
)


def main():
    # Inicia o Spark e configura a execução local
    spark = (
        SparkSession.builder.appName("PraticaSparkVendas")
        .master("local[2]")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", 2)
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )

    # Mostra apenas os avisos no terminal
    spark.sparkContext.setLogLevel("WARN")

    try:
        # Lê o arquivo CSV usando o esquema definido acima
        vendas = (
            spark.read.schema(ESQUEMA)
            .options(
                header=True,
                enforceSchema=False,
                ignoreLeadingWhiteSpace=True,
                ignoreTrailingWhiteSpace=True,
            )
            .csv(ENTRADA.as_posix())
            .repartition(2)
        )

        # Mostra quantos registros ficaram em cada partição
        print("\n1. Registros por partição", flush=True)
        (
            vendas.select(F.spark_partition_id().alias("particao"))
            .groupBy("particao")
            .agg(F.count("*").alias("registros"))
            .orderBy("particao")
            .show()
        )

        # Verifica quais vendas estão preenchidas corretamente
        # Se algum campo estiver vazio, considera a venda inválida
        venda_valida = F.coalesce(
            (F.col("categoria") != "")
            & (F.col("quantidade") > 0)
            & (F.col("preco_unitario") > 0),
            F.lit(False),
        )

        # Exibe os registros que foram considerados inválidos
        print("\n2. Registros descartados pelo filtro", flush=True)
        vendas.filter(~venda_valida).orderBy(
            "categoria", "produto").show(truncate=False)

        # Filtra as vendas válidas e calcula o valor de cada venda
        resumo = (
            vendas.filter(venda_valida)
            .withColumn(
                "valor_venda", F.col("quantidade") * F.col("preco_unitario")
            )

            # Agrupa os resultados por categoria
            .groupBy("categoria")
            .agg(
                F.count("*").alias("vendas"),
                F.sum("quantidade").alias("unidades"),
                F.sum("valor_venda").alias("faturamento"),
            )

            # Organiza as categorias pelo maior faturamento
            .orderBy(F.desc("faturamento"), "categoria")
        )

        # Mostra o resultado final do faturamento por categoria
        print("\n3. Faturamento por categoria", flush=True)
        print("filter, withColumn e groupBy definem o plano do resumo.", flush=True)
        print("A ação show() solicita o resultado e exibe a tabela.", flush=True)
        resumo.show(truncate=False)

    finally:
        # Encerra o Spark depois que terminar a execução
        spark.stop()


# Executa a função principal do programa
if __name__ == "__main__":
    main()
