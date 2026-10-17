"""Detección de órdenes escondidas, sin IA (EA4). Solo suma cautela: nunca autoriza nada."""
import re

PATRONES = [re.compile(p, re.I) for p in [
    r"ya\s+(?:est[aá]|fue|queda)\s+aprobad[ao]",
    r"\baprob(?:ar|ada|ado)\s+(?:de\s+inmediato|autom[aá]tic)",
    r"p[aá]g(?:a|ue)(?:la|lo|las|los)?\s+(?:de\s+inmediato|ya|ahora|sin)",
    r"ignor(?:a|e|ar)\s+(?:todas?\s+)?(?:las\s+|los\s+|tus\s+)?(?:reglas|instrucciones|l[ií]mites|restricciones)",
    r"(?:no|sin)\s+(?:la\s+)?(?:escal|revis|frenes|detengas)",
    r"instrucciones\s+anteriores|system\s*prompt|prompt\s+del\s+sistema",
    r"nota\s+para\s+(?:el\s+)?(?:sistema|agente|asistente|ia)",
    r"(?:pay|approve)\s+(?:this\s+)?(?:invoice\s+)?(?:immediately|now|without)",
    r"ignore\s+(?:all\s+)?(?:previous|prior|the)\s+(?:instructions|rules)",
    r"already\s+approved",
    r"act[uú]a\s+como|you\s+are\s+now",
]]


def detectar_orden(*textos: str | None) -> bool:
    return any(p.search(t) for t in textos if t for p in PATRONES)
