from WindPy import w
from django.core.management.base import BaseCommand

from stocks import models


class Command(BaseCommand):
    help = """
        python manage.py stock_adjustment --s=000001.SZ
    """

    def add_arguments(self, parser):
        parser.add_argument('--s', type=str, help='root symbol')
        parser.add_argument('--t1', type=str, help='start datetime')
        parser.add_argument('--t2', type=str, help='end datetime')
        parser.add_argument('--type', type=int, default=0,
                            help='0=adjfactor, 1=dividends, 2=splits')

    def handle(self, *args, **kwargs):
        w.start()

        if kwargs['s']:
            codes = models.Code.objects.filter(wind_code=kwargs['s'])
        else:
            codes = models.Code.objects.filter(asset=0)  # stock

        if kwargs['type'] == 0:
            field = 'adjfactor'
        else:
            raise Exception('Not supported yet.')

        for code in codes:
            try:
                row = models.Adjustment.objects.filter(code=code)
                default_start = row.latest().datetime
            except models.Adjustment.DoesNotExist:
                default_start = code.start_date

            t1 = kwargs['t1'] or default_start
            t2 = kwargs['t2'] or ""

            status, df = w.wsd(
                code.wind_code, field,
                t1, t2,
                "Days=Alldays;Fill=Previous",
                usedf=True,
            )

            if status == -40522017:
                raise Exception('Reach data limit!')
            elif status != 0 or len(df) == 1:  # or only one bar returned
                continue

            df.drop_duplicates(inplace=True)
            df.columns = ['value']

            for dt, row in df.iterrows():
                cf, created = models.Adjustment.objects.update_or_create(
                    code=code,
                    datetime=dt,
                    type=kwargs['type'],
                    defaults={'value': row['value']}
                )

                if created:
                    self.stdout.write(f"{code}({dt}): created - {field}")
                else:
                    self.stdout.write(f"{code}({dt}): updated - {field}")

        w.close()
