import functions_framework
import folium
import json
from shapely.geometry import shape, Polygon, MultiPolygon, mapping
import openrouteservice
from flask import jsonify
import tempfile
import os
from flask import send_file

tkn = os.getenv("tkn")

client = openrouteservice.Client(key=os.getenv("apiKey"))

archivo_geojson = 'cadiz.json'

@functions_framework.http
def maps(request):
    if request.method != 'POST' and request.path == "/":
        return jsonify({"error": "Método no permitido"}), 405

    token = request.headers.get('Authorization')
    if token:
        token = token.split(" ")[1] if "Bearer " in token else token
        if not token or token != tkn:
            return "Unauthorized", 401

    request_json = request.get_json()
    if not request_json:
        return jsonify({"error": "Body no proporcionado"}), 400

    with open(archivo_geojson, 'r') as f:
        data = json.load(f)

    ruta = request_json.get('ruta').split("-")
    transiciones = ["A"+ruta[i]+"A"+ruta[i+1] for i in range(len(ruta)-1)]
    inicio = ruta[0]
    finP = ruta[-1]

    map_cadiz = folium.Map(location=[36.527061, -6.288596], zoom_start=13)

    zonas = []

    for feature in data['features']:
        if feature['geometry']['type'] == 'Polygon':
            if "Transicion" in feature['properties']:
                tr = feature['properties']['Transicion'].split("/")
                if tr[0] in transiciones or tr[1] in transiciones:
                    zonas.append(shape(feature['geometry']))
            if "Ciudad" in feature['properties']:
                ciudad = shape(feature['geometry'])
        elif feature['type'] == 'Feature':
            if "Lugar" in feature['properties']:
                if feature['properties']['Lugar'] == int(inicio):
                    ini = feature['geometry']['coordinates']
                    folium.Marker(
                        location=ini[::-1],
                        tooltip="Inicio"
                    ).add_to(map_cadiz)
                if feature['properties']['Lugar'] == int(finP):
                    fin = feature['geometry']['coordinates']
                    folium.Marker(
                        location=fin[::-1],
                        tooltip="Fin"
                    ).add_to(map_cadiz)
    
    for zona in zonas:
        ciudad = ciudad.difference(zona)

    feature['geometry'] = json.loads(json.dumps(ciudad.__geo_interface__))
    folium.GeoJson(
        feature,
        name="Ciudad",
        style_function=lambda x: {'fillColor': 'yellow'}
    ).add_to(map_cadiz)

    ciudad = mapping(ciudad)

    try:
        route = client.directions(
            coordinates=[ini, fin],
            profile='foot-walking',
            instructions=False,
            preference='shortest',
            options={
                'avoid_polygons': ciudad,
            },
            format='geojson'
        )
        folium.GeoJson(route, name='route').add_to(map_cadiz)
    except Exception as e:
        print(e)

    # Guardar el mapa en un archivo HTML temporal
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, 'map.html')
    map_cadiz.save(temp_path)

    return send_file(temp_path, mimetype='text/html', as_attachment=True, attachment_filename='map.html')
