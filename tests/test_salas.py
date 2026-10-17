from acta.salas import ALFABETO, codigo_valido, generar_codigo


def test_generar():
    c = generar_codigo()
    assert len(c) == 8 and codigo_valido(c) and set(c) <= set(ALFABETO)


def test_invalidos():
    for x in [None, "", "ABC", "ABCDEFG0", "abcdefgh"]:
        assert not codigo_valido(x)
