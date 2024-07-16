

from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import uuid
import awsgi
from datetime import datetime

app = Flask(__name__)

CORS(app)

# Static URLs for flight schedules and delays
FLIGHT_SCHEDULES_URL = "https://challenge.usecosmos.cloud/flight_schedules.json"
FLIGHT_DELAYS_URL = "https://challenge.usecosmos.cloud/flight_delays.json"

def fetch_json_data(url):
    # Function to fetch JSON data from a given URL
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

def parse_iso_datetime(iso_datetime_str):
    # Function to parse ISO format datetime strings
    if iso_datetime_str.endswith('Z'):
        iso_datetime_str = iso_datetime_str[:-1] + '+00:00'
    return datetime.fromisoformat(iso_datetime_str)

@app.route('/flights', methods=['GET'])
def get_flights():
    
    try:
        schedules_response = fetch_json_data(FLIGHT_SCHEDULES_URL)
        schedules_response = schedules_response['FlightStatusResource']["Flights"]["Flight"]
        delays_response = fetch_json_data(FLIGHT_DELAYS_URL)
        if not schedules_response or not delays_response:
            return jsonify({'error': 'Failed to fetch flight data'}), 500

        flights = {}
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

            date_key = parse_iso_datetime(actual_departure_at).date()
            key = (airline, destination, date_key)
            if key not in flights or parse_iso_datetime(actual_departure_at) > parse_iso_datetime(flights[key]['actual_departure_at']):
                flights[key] = {
                    'id': str(uuid.uuid4()),
                    'flight_number': flight_number,
                    'airline': airline,
                    'origin': origin,
                    'destination': destination,
                    'scheduled_departure_at': scheduled_departure_at,
                    'actual_departure_at': actual_departure_at,
                    'delays': delays
                }

        destination_param = request.args.get('destination')
        airlines_param = request.args.getlist('airlines')
        filtered_flights = []
        for flight in flights.values():
            if (not destination_param or flight['destination'] == destination_param) and \
               (not airlines_param or flight['airline'] in airlines_param):
                filtered_flights.append(flight)

        # Extract only the flight with the latest actual_departure_at
        latest_flight = min(filtered_flights, key=lambda x: parse_iso_datetime(x['actual_departure_at']))

        return jsonify(["latest_flight"])

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def lambda_handler(event, context):
    return awsgi.response(app, event, context, base64_content_types={"image/png"})

# if __name__ == '__main__':
#     app.run(debug=True)