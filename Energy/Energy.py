import math

trayectoria = []

def parse_number(val: str) -> int | float | None:
    try:
        num = float(val)
        return int(num) if num.is_integer() else num
    except ValueError:
        return None

def inputNumber(msg: str) -> int | float:
    while True:
        val = input(msg)
        num = parse_number(val)
        if num is not None:
            return num
        print("Valor invalido")

def putValues():
    print("Valores de altura. Primer valor es el punto de referencia (recomendado: valores enteros)")
    while True:
        val = input("Altura (c para terminar): ")
        if val.lower() == "c":
            break
        num = parse_number(val)
        if num is None:
            print("Valor invalido")
        else:
            trayectoria.append(num)

def calculate(m, v0, g, h_increse):
    h_ref = trayectoria[0]
    Et = 0.5 * m * (v0 ** 2) + m * g * (trayectoria[0] - h_ref)
    print(f"Energia total inicial (Et): {Et:.2f}\n")

    for index in range(len(trayectoria) - 1):
        height = trayectoria[index] - h_ref
        next_height = trayectoria[index + 1] - h_ref
        print(f"Desde {trayectoria[index]:.2f} a {trayectoria[index + 1]:.2f} (relativo: {height:.2f} a {next_height:.2f})")

        h = height
        h_increment = h_increse if next_height > height else -h_increse

        while (h_increment > 0 and h <= next_height) or (h_increment < 0 and h >= next_height):
            Ep = m * g * h
            Ec = Et - Ep
            if Ec < 0:
                print(f"    No hay energia cinetica para llegar al siguente punto")
                break
            v = math.sqrt(2 * Ec / m)
            print(f"  Altura relativa {h:.2f} (real: {h + h_ref:.2f}) -> Ep={Ep:.2f}, Ec={Ec:.2f}, v={v:.2f}")
            h += h_increment

def init():
    m = inputNumber("Masa del objeto: ")
    putValues()
    print(f"Trayectoria: {trayectoria}")
    v0 = inputNumber("Velocidad inicial: ")
    g = inputNumber("Gravedad: ")
    h_increment = inputNumber("incremento (recomendado 0.01 a 1): ")
    print("\nSIMULACION INICIADA\n")
    calculate(m, v0, g, h_increment)

init()

