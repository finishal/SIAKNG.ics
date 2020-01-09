import datetime, pandas, icalendar, pytz, hashlib, uuid
from flask import Flask, Response, request, render_template
app = Flask(__name__)


onDay = lambda date, day: date + datetime.timedelta(days=(day-date.isoweekday()+7)%7)
prefix = '<table class="box"'
suffix = '</table>'
delimiter = 'SIAKNG.ics'
days_i = {'Minggu': 0, 'Senin': 1, 'Selasa': 2, 'Rabu': 3, 'Kamis': 4, 'Jumat': 5, 'Sabtu': 6,
          'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6}
status_s = {'1': 'CONFIRMED', '0': 'CANCELLED'}


@app.route('/', methods=['GET', 'POST'])
def siakng_ics():
    if request.method == 'GET':
        return render_template('index.html')

    try:
        raw = request.form.get('tabel-jadwal')
        raw = raw[raw.index(prefix) : raw.index(suffix) + len(suffix)]
        raw = raw.replace('<br>', delimiter)
        rows = pandas.read_html(raw)[0].to_dict('records')

        cal = icalendar.Calendar()
        cal.add('prodid', 'PRODID:-//faisalhanif.id//NONSGML SIAKNG.ics//ID')
        cal.add('version', '2.0')

        tzc = icalendar.Timezone()
        tzc.add('tzid', 'Asia/Jakarta')
        tzc.add('x-lic-location', 'Asia/Jakarta')

        tzs = icalendar.TimezoneStandard()
        tzs.add('tzname', 'WIB')
        tzs.add('dtstart', datetime.datetime(1970, 1, 1, 0, 0, 0))
        tzs.add('TZOFFSETFROM', datetime.timedelta(hours=7))
        tzs.add('TZOFFSETTO', datetime.timedelta(hours=7))

        tzc.add_component(tzs)
        cal.add_component(tzc)
        tz = pytz.timezone('Asia/Jakarta')

        for row in rows:
            row = list(row.values())
            periode_raw = row[4]
            kelas_raw = row[2]
            jadwal_raw = row[5]
            ruangan_raw = row[6]

            periodes = periode_raw.split(delimiter)
            kelas = kelas_raw[:kelas_raw.index(delimiter)]
            jadwals = jadwal_raw.split(delimiter)
            ruangans = ruangan_raw.split(delimiter)

            assert len(periodes) == len(jadwals) == len(ruangans)

            for periode, jadwal, ruangan in zip(periodes, jadwals, ruangans):
                event = icalendar.Event()

                jadwal_by, jadwal = jadwal.split(', ')
                periode_op, periode_ed = periode.split(' - ')

                op, ed = [
                    datetime.datetime.strptime(periode_op + ' ' + jam, '%d/%m/%Y %H.%M')
                    for jam in jadwal.split('-')
                ]
                op = onDay(op, days_i[jadwal_by])
                ed = onDay(ed, days_i[jadwal_by])
                true_ed = datetime.datetime.strptime(periode_ed + ' ' + '23.59.59', '%d/%m/%Y %H.%M.%S')

                event.add('dtstart', tz.localize(op))
                event.add('dtend', tz.localize(ed))
                event.add('dtstamp', tz.localize(datetime.datetime.today()))
                event.add('rrule', {'freq': 'weekly', 'until': true_ed})
                event.add('summary', kelas)
                event.add('location', ruangan)

                status = request.form.get('status')
                event.add('status', status_s[status])

                event_hash = hashlib.sha1((kelas + str(op)).encode()).hexdigest()
                event.add('uid', uuid.uuid5(uuid.NAMESPACE_URL, event_hash))

                cal.add_component(event)

        return Response(
            cal.to_ical(),
            mimetype='text/calendar',
            headers={'Content-disposition': 'attachment; filename=SIAKNG.ics'}
        )

    except:
        return Response(
            'ERROR',
            mimetype='text/plain',
            headers={'Content-disposition': 'attachment; filename=ERROR'}
        )


if __name__ == '__main__':
    app.run(host='0.0.0.0')
