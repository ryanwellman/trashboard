import csv
from progressbar import ProgressBar

from apps.regional.models import Region

fn = '/home/alex/projects/work/agreement/dashboard/dashboard/apps/regional/us_postal.csv'
size = 79526

reader = csv.reader(open(fn, 'r'), delimiter=';', quotechar='"')

bar = ProgressBar(maxval=size).start()
i = 0

Region.objects.all().delete()

for row in reader:
    i += 1
    r = Region()
    r.zipcode = row[1]
    r.city = row[2]
    r.county = row[3]
    r.state = row[5]
    r.areacode = row[6]
    r.save()
    bar.update(i)

bar.finish()
print
