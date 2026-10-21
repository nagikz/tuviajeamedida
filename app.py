import os
from flask import Flask, render_template, request, abort
from data.data_destinos import DESTINOS
from data.data_alojamientos import ALOJAMIENTOS
from data.data_actividades import ACTIVIDADES

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "clave-secreta-default")


# Auxiliares para búsqueda rápida por ID
def get_destino_by_id(destino_id):
    return next((d for d in DESTINOS if d["id"] == destino_id), None)


def get_alojamiento_by_id(alojamiento_id):
    return next((a for a in ALOJAMIENTOS if a["id"] == alojamiento_id), None)


def get_actividad_by_id(actividad_id):
    return next((act for act in ACTIVIDADES if act["id"] == actividad_id), None)


# --- 2. SECCIONES INSTITUCIONALES ---


@app.route("/")
def index():
    totales = {
        "destinos": len(DESTINOS),
        "alojamientos": len(ALOJAMIENTOS),
        "actividades": len(ACTIVIDADES),
    }
    return render_template("index.html", totales=totales)


@app.route("/acerca-de-nosotros")
def acerca():
    return render_template("acerca.html")


# --- 3. DIRECTORIOS GENERALES ---


@app.route("/destinos")
def listado_destinos():
    return render_template("directorios/destinos.html", destinos=DESTINOS)


@app.route("/alojamientos")
def listado_alojamientos():
    return render_template("directorios/alojamientos.html", alojamientos=ALOJAMIENTOS)


@app.route("/actividades")
def listado_actividades():
    # Asociamos el nombre del destino a cada actividad para mostrarlo según requisito
    actividades_con_destino = []
    for act in ACTIVIDADES:
        dest = get_destino_by_id(act["destino_id"])
        act_copy = act.copy()
        act_copy["destino_nombre"] = dest["nombre"] if dest else "Desconocido"
        actividades_con_destino.append(act_copy)
    return render_template(
        "directorios/actividades.html", actividades=actividades_con_destino
    )


# --- 4. HERRAMIENTAS DE BÚSQUEDA Y FILTRADO ---


@app.route("/explorador-destinos", methods=["GET"])
def explorador_destinos():
    entorno = request.args.get("entorno", "")
    sin_visado = request.args.get("sin_visado", "") == "1"

    resultados = DESTINOS
    if entorno:
        resultados = [d for d in resultados if d["entorno"] == entorno]
    if sin_visado:
        resultados = [d for d in resultados if not d["requiere_visado"]]

    return render_template(
        "busquedas/explorador_destinos.html",
        destinos=resultados,
        entorno=entorno,
        sin_visado=sin_visado,
    )


@app.route("/comparador-alojamientos", methods=["GET"])
def comparador_alojamientos():
    precio_max = request.args.get("precio_max", type=float)
    tipo = request.args.get("tipo", "")
    con_desayuno = request.args.get("con_desayuno", "") == "1"
    admite_mascotas = request.args.get("admite_mascotas", "") == "1"

    resultados = ALOJAMIENTOS
    if precio_max is not None:
        resultados = [a for a in resultados if a["precio_noche"] <= precio_max]
    if tipo:
        resultados = [a for a in resultados if a["tipo"] == tipo]
    if con_desayuno:
        resultados = [a for a in resultados if a["incluye_desayuno"]]
    if admite_mascotas:
        resultados = [a for a in resultados if a["admite_mascotas"]]

    return render_template(
        "busquedas/comparador_alojamientos.html",
        alojamientos=resultados,
        precio_max=precio_max,
        tipo=tipo,
        con_desayuno=con_desayuno,
        admite_mascotas=admite_mascotas,
    )


@app.route("/viaje-a-medida", methods=["GET"])
def viaje_a_medida():
    # Parámetros del Formulario Combinado
    entorno = request.args.get("entorno", "")
    sin_visado = request.args.get("sin_visado", "") == "1"
    tipo_alojamiento = request.args.get("tipo_alojamiento", "")
    precio_max = request.args.get("precio_max", type=float)
    con_desayuno = request.args.get("con_desayuno", "") == "1"

    busqueda_realizada = any(
        [entorno, sin_visado, tipo_alojamiento, precio_max is not None, con_desayuno]
    )
    combinaciones = []

    if busqueda_realizada:
        # 1. Filtrar Destinos
        destinos_validos = DESTINOS
        if entorno:
            destinos_validos = [d for d in destinos_validos if d["entorno"] == entorno]
        if sin_visado:
            destinos_validos = [d for d in destinos_validos if not d["requiere_visado"]]

        destinos_ids = [d["id"] for d in destinos_validos]

        # 2. Filtrar Alojamientos vinculados a destinos válidos
        alojamientos_validos = [
            a for a in ALOJAMIENTOS if a["destino_id"] in destinos_ids
        ]
        if tipo_alojamiento:
            alojamientos_validos = [
                a for a in alojamientos_validos if a["tipo"] == tipo_alojamiento
            ]
        if precio_max is not None:
            alojamientos_validos = [
                a for a in alojamientos_validos if a["precio_noche"] <= precio_max
            ]
        if con_desayuno:
            alojamientos_validos = [
                a for a in alojamientos_validos if a["incluye_desayuno"]
            ]

        # 3. Cruzar resultados (Combinaciones válidas Destino + Alojamiento)
        for aloj in alojamientos_validos:
            dest = get_destino_by_id(aloj["destino_id"])
            combinaciones.append({"destino": dest, "alojamiento": aloj})

    return render_template(
        "busquedas/viaje_a_medida.html",
        combinaciones=combinaciones,
        busqueda_realizada=busqueda_realizada,
        entorno=entorno,
        sin_visado=sin_visado,
        tipo_alojamiento=tipo_alojamiento,
        precio_max=precio_max,
        con_desayuno=con_desayuno,
    )


# --- 5. FICHAS DE DETALLE Y NAVEGACIÓN CONECTADA ---


@app.route("/destino/<destino_id>")
def destino_detalle(destino_id):
    destino = get_destino_by_id(destino_id)
    if not destino:
        abort(404)

    alojamientos_relacionados = [
        a for a in ALOJAMIENTOS if a["destino_id"] == destino_id
    ]
    actividades_relacionadas = [
        act for act in ACTIVIDADES if act["destino_id"] == destino_id
    ]

    return render_template(
        "detalles/destino_detalle.html",
        destino=destino,
        alojamientos=alojamientos_relacionados,
        actividades=actividades_relacionadas,
    )


@app.route("/alojamiento/<alojamiento_id>")
def alojamiento_detalle(alojamiento_id):
    alojamiento = get_alojamiento_by_id(alojamiento_id)
    if not alojamiento:
        abort(404)

    destino = get_destino_by_id(alojamiento["destino_id"])
    return render_template(
        "detalles/alojamiento_detalle.html", alojamiento=alojamiento, destino=destino
    )


@app.route("/actividad/<actividad_id>")
def actividad_detalle(actividad_id):
    actividad = get_actividad_by_id(actividad_id)
    if not actividad:
        abort(404)

    destino = get_destino_by_id(actividad["destino_id"])
    return render_template(
        "detalles/actividad_detalle.html", actividad=actividad, destino=destino
    )


# --- MANEJADOR DE ERROR 404 ---


@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
