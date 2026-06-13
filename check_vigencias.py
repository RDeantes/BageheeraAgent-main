from vigencias import listar_vencidos


def main():
    vencidos = listar_vencidos()
    print("VIGENCIAS VENCIDAS:", vencidos)
    return vencidos


if __name__ == "__main__":
    main()
