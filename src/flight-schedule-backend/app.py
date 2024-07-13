from flask import Flask, request, jsonify
import requests
from flask_cors import CORS 
import uuid 

app = Flask(__name__)

CORS(app)

# Static URLs for flight schedules and delays
FLIGHT_SCHEDULES_URL = "https://challenge.usecosmos.cloud/flight_schedules.json"
FLIGHT_DELAYS_URL = "https://challenge.usecosmos.cloud/flight_delays.json"

def fetch_json_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except ValueError as val_err:
        print(f"Value error occurred: {val_err}")
    return None

@app.route('/flights', methods=['GET'])
def get_flights():
    try:
       
        schedules_response = fetch_json_data(FLIGHT_SCHEDULES_URL)
        airlines_param = request.args.getlist('airlines')
        schedules_response=schedules_response['FlightStatusResource']["Flights"]["Flight"]
        delays_response = fetch_json_data(FLIGHT_DELAYS_URL)
        if not schedules_response or not delays_response:
            return jsonify({'error': 'Failed to fetch flight data'}), 500
        flights = []
        for schedule in schedules_response:
            flight_number = schedule['MarketingCarrier']['FlightNumber']
            airline = schedule['MarketingCarrier']['AirlineID']
            origin = schedule['Departure']['AirportCode']
            destination = schedule['Arrival']['AirportCode']
            scheduled_departure_at = schedule['Departure']['ScheduledTimeUTC']['DateTime']
            actual_departure_at = schedule['Departure']['ActualTimeUTC']['DateTime']
            delays = []
            for leg in delays_response:
                if leg['Flight']['OperatingFlight']['Number'] == flight_number and leg['Flight']['OperatingFlight']['Airline'] == airline:
                    for key, delay in leg["FlightLegs"][0]['Departure']['Delay'].items():
                        if delay:
                            delay_info = {
                                'code': delay['Code'],
                                'time_minutes': delay['DelayTime'],
                                'description': delay['Description']
                            }
                            delays.append(delay_info)

            flight_record = {
                'id': str(uuid.uuid4()), 
                'flight_number': flight_number,
                'airline': airline,
                'origin': origin,
                'destination': destination,
                'scheduled_departure_at': scheduled_departure_at,
                'actual_departure_at': actual_departure_at,
                'delays': delays
            }

            flights.append(flight_record)

        destination_param = request.args.get('destination')
        airlines_param = request.args.getlist('airlines')
        filtered_flights = []

        for flight in flights:
            if (not destination_param or flight['destination'] == destination_param) and \
               (not airlines_param or flight['airline'] in airlines_param):
                filtered_flights.append(flight)
       
        return jsonify(filtered_flights)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
