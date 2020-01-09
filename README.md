## About
SIAKNG.ics is used to generate calendar data file (.ics) from course schedule (Universitas Indonesia).

## Usage

1. `pip install -r requirements.txt`
2. `python app.py`
3. Login to [SIAKNG](https://academic.ui.ac.id/)
4. Copy your [schedule table](https://academic.ui.ac.id/main/CoursePlan/CoursePlanViewClass/)
5. Paste it to http://localhost:5000/
6. Choose:
    - `Membuat`: events creation
    - `Menghapus`: events deletion (mark events created by `Membuat` as `CANCELLED`)
7. Download the generated file and import it to your calendar
