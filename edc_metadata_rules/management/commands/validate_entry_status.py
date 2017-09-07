import sys

from tqdm import tqdm
from django.apps import apps as django_apps
from django.db.models import Count
from django.core.management.base import BaseCommand
from edc_metadata.models import RequisitionMetadata, CrfMetadata
from edc_metadata.constants import KEYED
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):

    help = 'Performs a `get_model` for each target models referenced'

    def handle(self, *args, **options):

        grouping = RequisitionMetadata.objects.distinct().values(
            'model').annotate(model_count=Count('model')).order_by()
        requisition_models = [grp.get('model') for grp in grouping]
        grouping = CrfMetadata.objects.values(
            'model').annotate(model_count=Count('model')).order_by()
        crf_models = [grp.get('model') for grp in grouping]

        for model in tqdm(requisition_models):
            model_cls = django_apps.get_model(model)
            exists = 0
            doesnotexist = 0
            keyed = 0
            qs = model_cls.objects.all()
            count = qs.count()
            for index, obj in enumerate(qs):
                opts = dict(
                    model=model,
                    subject_identifier=obj.subject_identifier,
                    visit_code=obj.visit.visit_code,
                    panel_name=obj.panel_name)
                try:
                    RequisitionMetadata.objects.get(**opts)
                except ObjectDoesNotExist:
                    doesnotexist += 1
                else:
                    exists += 1
                    opts.update(entry_status=KEYED)
                    try:
                        RequisitionMetadata.objects.get(**opts)
                    except ObjectDoesNotExist:
                        pass
                    else:
                        keyed += 1
                perc = round((index / count) * 100)
                sys.stdout.write(
                    f' ( ) {model} exists={exists}/{count}, keyed={keyed}/{count}, missing={doesnotexist}/{count}    {perc}% \r')
            sys.stdout.write(
                f' (*) {model} exists={exists}/{count}, keyed={keyed}/{count}, missing={doesnotexist}/{count}    {perc}% \n')

        for model in tqdm(crf_models):
            model_cls = django_apps.get_model(model)
            exists = 0
            doesnotexist = 0
            keyed = 0
            qs = model_cls.objects.all()
            count = qs.count()
            for index, obj in enumerate(qs):
                opts = dict(
                    model=model,
                    subject_identifier=obj.subject_identifier,
                    visit_code=obj.visit.visit_code)
                try:
                    CrfMetadata.objects.get(**opts)
                except ObjectDoesNotExist:
                    doesnotexist += 1
                else:
                    exists += 1
                    opts.update(entry_status=KEYED)
                    try:
                        CrfMetadata.objects.get(**opts)
                    except ObjectDoesNotExist:
                        pass
                    else:
                        keyed += 1
                perc = round((index / count) * 100)
                sys.stdout.write(
                    f' ( ) {model} exists={exists}/{count}, keyed={keyed}/{count}, missing={doesnotexist}/{count}    {perc}% \r')
            sys.stdout.write(
                f' (*) {model} exists={exists}/{count}, keyed={keyed}/{count}, missing={doesnotexist}/{count}    {perc}% \n')
