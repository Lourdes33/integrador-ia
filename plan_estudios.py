# plan_estudios.py

PLAN_LSI_2023 = {
    "101": {"nombre": "Algoritmos y Estructuras de Datos I", "regulares": [], "aprobadas": []},
    "102": {"nombre": "Álgebra", "regulares": [], "aprobadas": []},
    "103": {"nombre": "Algoritmos y Estructuras de Datos II", "regulares": ["101"], "aprobadas": ["101"]},
    "104": {"nombre": "Lógica y Matemática Computacional", "regulares": ["102"], "aprobadas": ["102"]},
    "201": {"nombre": "Paradigmas y Lenguajes", "regulares": ["103"], "aprobadas": ["101"]},
    "204": {"nombre": "Programación Orientada a Objetos", "regulares": ["201"], "aprobadas": ["103"]},
    "303": {"nombre": "Ingeniería de Software I", "regulares": ["204", "206"], "aprobadas": ["201"]},
    "401": {"nombre": "Inteligencia Artificial", "regulares": ["304"], "aprobadas": ["203"]},
    "507": {"nombre": "Proyecto Integrador de Carrera", "regulares": ["403", "404", "405"], "aprobadas": ["305", "306"]}
}