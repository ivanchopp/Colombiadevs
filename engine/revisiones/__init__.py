class NoEvaluable(Exception):
    """Falta un dato para evaluar una revisión. Se convierte en FALLA y escalar (R1.3)."""

    def __init__(self, mensaje, nivel="PERSONA"):
        super().__init__(mensaje)
        self.nivel = nivel
