## Quick Start

## Docker

### Build container
```
make build
```
it also populates a DB with some sample data taken from `populate_data.py`

### Run in dev mode
```
make dev
```

## Local Development
```bash
source vent/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py
```

### Run tests
```
python -m pytest
```

## API Endpoints
- `GET /api/{model}/` - List all
- `POST /api/{model}/` - Create new
- `GET /api/{model}/{id}/` - Get by ID
- `PUT /api/{model}/{id}/` - Update by ID
- `DELETE /api/{model}/{id}/` - Delete by ID

### Special Endpoints
- `POST /api/patients/{id}/assign_procedure/` - Assign procedure to patient
- `GET /api/patients/by_procedure/?procedure_name=Surgery` - Get patients by procedure
- `GET /api/clinician-patient-counts/by_department/?department_id=1` - Patient count by department

### Search
- `GET /api/patients/?search=john` - Search patients by name/email
- `GET /api/departments/?search=cardio` - Search departments by name
- `GET /api/clinicians/?search=smith` - Search clinicians by name
