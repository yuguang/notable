"""Alternative version of the ToDo RESTful server implemented using the
Flask-RESTful extension."""

from flask import Flask, jsonify, abort, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal

app = Flask(__name__, static_url_path="")
api = Api(app)

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



doctor_fields = {
  'title': fields.String,
  'description': fields.String,
  'done': fields.Boolean,
  'uri': fields.Url('doctor')
}

appointment_fields = {
  'first_name': fields.String,
  'last_name': fields.String,
  'time': fields.DateTime(dt_format='rfc822'),
  'kind': fields.String
}

class DoctorListAPI(Resource):

  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('title', type=str, required=True,
                               help='No doctor title provided',
                               location='json')
    self.reqparse.add_argument('description', type=str, default="",
                               location='json')
    super(DoctorListAPI, self).__init__()

  def get(self):
    return {'doctors': [marshal(doctor, doctor_fields) for doctor in doctors]}

  def post(self):
    args = self.reqparse.parse_args()
    doctor = {
      'id': doctors[-1]['id'] + 1,
      'title': args['title'],
      'description': args['description'],
      'done': False
    }
    doctors.append(doctor)
    return {'doctor': marshal(doctor, doctor_fields)}, 201


class AppointmentAPI(Resource):

  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('title', type=str, location='json')
    self.reqparse.add_argument('description', type=str, location='json')
    self.reqparse.add_argument('done', type=bool, location='json')
    super(DoctorAPI, self).__init__()

  def get(self, id):
    return {'appointments': [marshal(appointment, appointment_fields) for appointment in appointments]}


class DoctorAPI(Resource):

  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('title', type=str, location='json')
    self.reqparse.add_argument('description', type=str, location='json')
    self.reqparse.add_argument('done', type=bool, location='json')
    super(DoctorAPI, self).__init__()

  def get(self, id):
    doctor = [doctor for doctor in doctors if doctor['id'] == id]
    if len(doctor) == 0:
      abort(404)
    return {'doctor': marshal(doctor[0], doctor_fields)}

  def put(self, id):
    doctor = [doctor for doctor in doctors if doctor['id'] == id]
    if len(doctor) == 0:
      abort(404)
    doctor = doctor[0]
    args = self.reqparse.parse_args()
    for k, v in args.items():
      if v is not None:
        doctor[k] = v
    return {'doctor': marshal(doctor, doctor_fields)}

  def delete(self, id):
    doctor = [doctor for doctor in doctors if doctor['id'] == id]
    if len(doctor) == 0:
      abort(404)
    doctors.remove(doctor[0])
    return {'result': True}


api.add_resource(DoctorListAPI, '/appointment/api/v1.0/doctors', endpoint='doctors')
api.add_resource(DoctorAPI, '/appointment/api/v1.0/doctors/<int:id>', endpoint='doctor')

if __name__ == '__main__':
  app.run(debug=True)
