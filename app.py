"""Alternative version of the ToDo RESTful server implemented using the
Flask-RESTful extension."""
import dateutil.parser
import pytz

utc=pytz.UTC
from flask import Flask, jsonify, abort, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal
from datetime import datetime, timedelta

app = Flask(__name__, static_url_path="")
api = Api(app)

# constants
NEW_PATIENT = 'New Patient'
FOLLOW_UP = 'Follow-up'
VISIT_KIND = [NEW_PATIENT, FOLLOW_UP]

doctors = [
  {
    'id': 1,
    'first_name': 'Julius',
    'last_name': 'Hilbert'
  },
  {
    'id': 2,
    'first_name': 'John',
    'last_name': 'Smith'
  }
]


appointments = [
  {
    'id': 1,
    'first_name': 'Sterling',
    'last_name': 'Archer',
    'time': datetime.now().replace(tzinfo=utc),
    'kind': NEW_PATIENT,
    'doctor': 1
  },
  {
    'id': 2,
    'first_name': 'Pam',
    'last_name': 'Kane',
    'time': datetime.now().replace(tzinfo=utc),
    'kind': NEW_PATIENT,
    'doctor': 2
  }
]


doctor_fields = {
  'id': fields.Integer,
  'first_name': fields.String,
  'last_name': fields.String,
}

appointment_fields = {
  'id': fields.Integer,
  'first_name': fields.String,
  'last_name': fields.String,
  'time': fields.DateTime(dt_format='rfc822'),
  'kind': fields.String
}

class DoctorListAPI(Resource):

  def __init__(self):
    super(DoctorListAPI, self).__init__()

  def get(self):
    return {'doctors': [marshal(doctor, doctor_fields) for doctor in doctors]}



class AppointmentListAPI(Resource):

  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('first_name', type=str, location='json')
    self.reqparse.add_argument('last_name', type=str, location='json')
    self.reqparse.add_argument('time', type=str, location='json')
    self.reqparse.add_argument('kind', type=int, location='json')
    super(AppointmentListAPI, self).__init__()

  def get(self, doctor_id, day):
    try:
      date = datetime.strptime(day, '%Y%m%d').replace(tzinfo=utc)
    except:
      return {'error': 'Invalid date format'}, 400
    ret = []
    for appointment in appointments:
      # get the doctor's appointments and check if the time for the appointment falls on the day
      if (appointment['id'] == doctor_id and
          appointment['time'] > date and
          appointment['time'] <= date + timedelta(days=1)):
        ret.append(marshal(appointment, appointment_fields))

    return {'appointments': ret}

  def post(self, doctor_id):
    args = self.reqparse.parse_args()
    # validate input
    if args['kind'] > len(VISIT_KIND):
      return {'error': 'Invalid kind index'}, 400
    try:
      date = dateutil.parser.parse(args['time'])
    except:
      return {'error': 'Invalid date format'}, 400
    # check doctor exists
    if not doctor_id in [d['id'] for d in doctors]:
      return {'error': 'Doctor does not exist'}, 400
    # check if starts at 15 minute intervals
    if not date.minute in [0, 15, 30, 45]:
      return {'error': 'New appointments can only start at 15 minute intervals'}, 400
    appointment = {
      'id': doctor_id,
      'first_name': args['first_name'],
      'last_name': args['last_name'],
      'time': date,
      'kind': VISIT_KIND[args['kind']],
    }
    appointments.append(appointment)
    return {'appointment': marshal(appointment, appointment_fields)}, 201


class AppointmentAPI(Resource):

  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('title', type=str, location='json')
    self.reqparse.add_argument('description', type=str, location='json')
    self.reqparse.add_argument('done', type=bool, location='json')
    super(AppointmentAPI, self).__init__()

  def get(self, id):
    appointment = [appointment for appointment in appointments if appointment['id'] == id]
    if len(appointment) == 0:
      abort(404)
    return {'appointment': marshal(appointment[0], appointment_fields)}

  def put(self, id):
    appointment = [appointment for appointment in appointments if appointment['id'] == id]
    if len(appointment) == 0:
      abort(404)
    appointment = appointment[0]
    args = self.reqparse.parse_args()
    for k, v in args.items():
      if v is not None:
        appointment[k] = v
    return {'appointment': marshal(appointment, appointment_fields)}

  def delete(self, id):
    appointment = [appointment for appointment in appointments if appointment['id'] == id]
    if len(appointment) == 0:
      abort(404)
    appointments.remove(appointment[0])
    return {'result': True}


api.add_resource(DoctorListAPI, '/appointment/api/v1.0/doctors', endpoint='doctors')
api.add_resource(AppointmentAPI, '/appointment/api/v1.0/appointment/<int:id>', endpoint='appointment')
api.add_resource(AppointmentListAPI, '/appointment/api/v1.0/doctor/<int:doctor_id>/date/<string:day>',
                 endpoint='doctor_day')
api.add_resource(AppointmentListAPI, '/appointment/api/v1.0/doctor/<int:doctor_id>',
                 endpoint='doctor')

if __name__ == '__main__':
  app.run(debug=True)
