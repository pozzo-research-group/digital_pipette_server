from flask import Flask, request, Response
from flask.json import jsonify
import logging


app = Flask(__name__)

logger = logging.getLogger(__name__)

logging.basicConfig(filename = 'digital_syringe_logs.log', level = logging.DEBUG)

import digital_pipette

logger.info('Initializing digital pipette flask app')

pipette_10cc_1 = digital_pipette.DigitalPipette.from_config('/home/bgpelkie/digital_pipette_server/10_cc_1_config.json')
logger.info('Instantiated pipette_10cc_1')
pipette_1cc_1 = digital_pipette.DigitalPipette.from_config('/home/bgpelkie/digital_pipette_server/1_cc_1_config.json')
logger.info('Instantiated pipette 1cc_1')
pipette_1cc_2 = digital_pipette.DigitalPipette.from_config('/home/bgpelkie/digital_pipette_server/1_cc_2_config.json')
logger.info('Instantiated pipette 1cc_2')
pipette_1cc_3 = digital_pipette.DigitalPipette.from_config('/home/bgpelkie/digital_pipette_server/1_cc_3_config.json')
logger.info('Instantiated pipette 1cc_3')
pipette_1cc_3_hamilton = digital_pipette.DigitalPipette.from_config('/home/bgpelkie/digital_pipette_server/1_cc_3_hamilton_config.json')
logger.info('Instantiated pipette 1cc_3_hamilton')
pipette_10cc_1_glass = digital_pipette.DigitalPipette.from_config('/home/bgpelkie/digital_pipette_server/10_cc_1_glass_config.json')
logger.info('Instantiated pipette 10cc_1_glass')

#assert (0 <= wiper_val) and wiper_val <= 128, 'Wiper val must be integer between 0 and 127'
pipettes = {'10cc_1':pipette_10cc_1, '1cc_1':pipette_1cc_1, '1cc_2':pipette_1cc_2, '1cc_3':pipette_1cc_3, '1cc_3_hamilton':pipette_1cc_3_hamilton, '10cc_1_glass':pipette_10cc_1_glass}


@app.route('/get_config', methods = ['POST'])
def get_config():

    data = request.json
    name = data['name']
    pipette = pipettes[name]

    config = {}
    config['capacity'] = pipette.capacity
    config['name'] = pipette.name
    config['full_position'] = pipette.full_position
    config['empty_position'] = pipette.empty_position

    logger.info(f'Served syringe config for {name}')

    return jsonify(config)

@app.route('/get_status', methods = ['POST'])
def get_status():

    data = request.json
    name = data['name']
    pipette = pipettes[name]


    status = {}
    status['remaining_volume'] = pipette.remaining_volume
    status['syringe_loaded'] = pipette.syringe_loaded

    logger.info(f'Served syringe status for {name}')

    return jsonify(status)

@app.route('/load_syringe', methods = ['POST'])
def load_syringe():
    data = request.json
    name = data['name']
    pipette = pipettes[name]

    volume = data['volume']
    pulsewidth = data['pulsewidth']

    pipette.load_syringe(volume, pulsewidth)

    logger.info(f'Loaded syringe {name} with volume {volume} uL and pulsewidth position {pulsewidth} us')

    return 'loaded_syringe'


@app.route('/dispense', methods = ['POST'])
def dispense():
    data = request.json
    name = data['name']
    pipette = pipettes[name]
    volume = data['volume']
    s = data['speed']

    assert volume <= pipette.remaining_volume, f'Volume {volume} uL is greater than remaining volume ({pipette.remaining_volume} uL)'

    pipette.dispense(volume, s = s)

    logger.info(f'Syringe {name} dispensed {volume} uL')

    return 'dispensed'


@app.route('/aspirate', methods = ['POST'])
def aspirate():
    data = request.json
    volume = data['volume']
    name = data['name']
    pipette = pipettes[name]
    s = data['speed']

    assert volume + pipette.remaining_volume <= pipette.capacity, f'Volume {volume} is greater than remaining pipette capacity ({pipette.capacity})'


    pipette.aspirate(volume, s = s)

    logging.info(f'Syringe {name} aspirated {volume} uL')

    return 'aspirated'


@app.route('/set_pulsewidth', methods = ['POST'])
def set_pulsewidth():
    data = request.json
    pulsewidth = data['pulsewidth']
    name = data['name']
    pipette = pipettes[name]
    s = data['speed']
    logging.debug(f'pulsewidth: {pulsewidth}')
    logging.debug(f'full position: {pipette.full_position}')
    assert ((pulsewidth < pipette.empty_position) and (pulsewidth > pipette.full_position)), 'Pulsewidth must be between 1000 and 2000'

    pipette.set_pulsewidth_speed(pulsewidth, s)
           
    logging.info(f'Syringe {name} pulsewidth set to {pulsewidth}')

    return 'set_pulsewidth'


if __name__ == "__main__":
    app.run(host = "0.0.0.0", debug = False)
