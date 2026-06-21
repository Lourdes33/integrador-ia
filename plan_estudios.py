# Base de Conocimiento Determinística: Régimen de Correlatividades LSI 2023 (Res. 2024-723-CS)

PLAN_LSI_2023 = {
    # --- PRIMER AÑO ---
    "101": {"nombre": "Algoritmos y Estructuras de Datos I", "regulares": [], "aprobadas": []},
    "102": {"nombre": "Álgebra", "regulares": [], "aprobadas": []},
    "103": {"nombre": "Algoritmos y Estructuras de Datos II", "regulares": ["101"], "aprobadas": []},
    "104": {"nombre": "Lógica y Matemática Computacional", "regulares": ["102"], "aprobadas": []},
    "105": {"nombre": "Sistemas y Organizaciones", "regulares": [], "aprobadas": []},

    # --- SEGUNDO AÑO ---
    "201": {"nombre": "Paradigmas y Lenguajes", "regulares": ["103"], "aprobadas": ["101"]},
    "202": {"nombre": "Arquitectura y Organización de Computadoras", "regulares": ["104"], "aprobadas": ["101"]},
    "203": {"nombre": "Cálculo Diferencial e Integral", "regulares": ["104"], "aprobadas": ["102"]},
    "204": {"nombre": "Programación Orientada a Objetos", "regulares": ["201"], "aprobadas": ["103"]},
    "205": {"nombre": "Sistemas Operativos", "regulares": ["202"], "aprobadas": []},
    "206": {"nombre": "Bases de Datos I", "regulares": ["202"], "aprobadas": []},

    # --- TERCER AÑO ---
    "301": {"nombre": "Programación Web", "regulares": ["204"], "aprobadas": ["201"]},
    "302": {"nombre": "Comunicaciones de Datos", "regulares": ["205"], "aprobadas": ["202"]},
    "303": {"nombre": "Ingeniería de Software I", "regulares": ["204", "206"], "aprobadas": ["201"]},
    "304": {"nombre": "Probabilidad y Estadística", "regulares": ["203"], "aprobadas": ["104"]},
    "305": {"nombre": "Programación Avanzada", "regulares": ["301"], "aprobadas": []},
    "306": {"nombre": "Ingeniería de Software II", "regulares": ["303"], "aprobadas": ["206"]},

    # --- CUARTO AÑO ---
    "401": {"nombre": "Inteligencia Artificial", "regulares": ["304"], "aprobadas": ["203"]},
    "402": {"nombre": "Teoría de la Computación", "regulares": ["304"], "aprobadas": ["203"]},
    "403": {"nombre": "Redes de Datos", "regulares": ["302"], "aprobadas": ["205"]},
    "404": {"nombre": "Ingeniería de Software III", "regulares": ["306"], "aprobadas": ["303"]},
    "405": {"nombre": "Bases de Datos II", "regulares": ["304"], "aprobadas": ["206"]},
    "406": {"nombre": "Métodos Computacionales", "regulares": ["304"], "aprobadas": ["203"]},
    "407": {"nombre": "Análisis de Organizaciones y Procesos", "regulares": ["306"], "aprobadas": ["105"]},

    # --- QUINTO AÑO ---
    "501": {"nombre": "Auditoría y Seguridad Informática", "regulares": ["401"], "aprobadas": ["304"]},
    "502": {"nombre": "Emprendedorismo y Modelos de Negocios", "regulares": ["306"], "aprobadas": ["303"]},
    
    # Optativa I requiere tener todo 3er año regularizado para cursar
    "503": {"nombre": "Optativa I", "regulares": ["301", "302", "303", "304", "305", "306"], "aprobadas": []},
    
    "504": {"nombre": "Introducción a la Ciencia de Datos", "regulares": ["404"], "aprobadas": ["403"]},
    "505": {"nombre": "Aspectos Profesionales y Sociales de la Informática", "regulares": ["502"], "aprobadas": ["306"]},
    
    # Optativa II requiere tener todo 3er año aprobado para cursar
    "506": {"nombre": "Optativa II", "regulares": [], "aprobadas": ["301", "302", "303", "304", "305", "306"]},
    
    "507": {"nombre": "Proyecto Integrador de Carrera", "regulares": ["403", "404", "405"], "aprobadas": ["305", "306"]}
}