import functions_framework
from flask import jsonify
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import os

tkn = os.getenv('tkn')

flood = ctrl.Antecedent(np.arange(0, 100, 1), 'flood')
objects = ctrl.Antecedent(np.arange(0, 10, 1), 'objects')
magnitude = ctrl.Antecedent(np.arange(54, 74, 1), 'magnitude')

path = ctrl.Consequent(np.arange(0, 11, 1), 'path')

flood['low'] = fuzz.trapmf(flood.universe, [0, 0, 10, 30])
flood['medium'] = fuzz.trimf(flood.universe, [10, 30, 50])
flood['high'] = fuzz.trapmf(flood.universe, [30, 50, 100, 100])

objects['small'] = fuzz.trapmf(objects.universe, [0, 0, 1, 3])
objects['medium'] = fuzz.trimf(objects.universe, [1, 3, 5])
objects['large'] = fuzz.trapmf(objects.universe, [3, 5, 10, 10])

magnitude['info'] = fuzz.trapmf(magnitude.universe, [54, 55, 59, 60])
magnitude['advisory'] = fuzz.trapmf(magnitude.universe, [59, 60, 64, 65])
magnitude['watch'] = fuzz.trapmf(magnitude.universe, [64, 65, 74, 75])

path['open'] = fuzz.trapmf(path.universe, [0, 0, 2, 3])
path['precaution'] = fuzz.trapmf(path.universe, [2, 3, 6, 7])
path['close'] = fuzz.trapmf(path.universe, [6, 7, 10, 10])

rules = [
    ctrl.Rule(flood['low'] & objects['small'] & ~magnitude['watch'], path['open']),
    ctrl.Rule(flood['high'] | objects['large'] | magnitude['watch'], path['close']),
    ctrl.Rule(~flood['high'] & objects['medium'] & ~magnitude['watch'], path['precaution']),
    ctrl.Rule(flood['medium'] & ~objects['large'] & ~magnitude['watch'], path['precaution'])
]

path_ctrl = ctrl.ControlSystem(rules)
path_simulation = ctrl.ControlSystemSimulation(path_ctrl)

@functions_framework.http
def fis_cadiz(request):

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
    
    res = {}

    for vals in request_json["paths"]:

        path_simulation.input['flood'] = vals['flood']
        path_simulation.input['objects'] = vals['objects']
        path_simulation.input['magnitude'] = vals['magnitude']

        path_simulation.compute()

        res[vals['path']] = path_simulation.output['path']

    return jsonify(res), 200

