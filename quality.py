#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.model import fields, ModelView, Workflow
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval
from trytond.transaction import Transaction
from datetime import datetime

__all__ = ['QualityTest', 'CreateQualityTestsMixin']


class CreateQualityTestsMixin(object):

    @classmethod
    def create_lot_quality_tests(cls, shipments, template):
        QualityTest = Pool().get('quality.test')
        StockLot = Pool().get('stock.lot')
        new_tests = []
        to_save = []

        for shipment in shipments:
            lots = shipment.lots_for_quality_tests()

            if not lots:
                continue

            to_create = []
            today = datetime.today()
            for lot in lots:
                used_template = None
                lot.active = False
                to_save.append(lot)

                if (template == 'shipment_in' and
                        lot.product.template.shipment_in_quality_template):
                    used_template = lot.product.template.shipment_in_quality_template
                if (template == 'shipment_out' and
                        lot.product.template.shipment_out_quality_template):
                    used_template = lot.product.template.shipment_out_quality_template
                if (template == 'shipment_internal' and
                        lot.product.template.shipment_internal_quality_template):
                    used_template = lot.product.template.shipment_internal_quality_template
                if (template == 'production' and
                        lot.product.template.production_quality_template):
                    used_template = lot.product.template.production_quality_template

                if not template:
                    continue

                test_date = (datetime.combine(shipment.effective_date,
                        datetime.now().time())
                    if shipment.effective_date else today)
                to_create.append(QualityTest(
                    test_date=test_date,
                    templates=[used_template],
                    document='stock.lot,' + str(lot.id)))

            with Transaction().set_user(0, set_context=True):
                new_tests += QualityTest.create([x._save_values for x in
                    to_create])

        for test in new_tests:
            with Transaction().set_user(0, set_context=True):
                test.apply_template_values()
                test.save()

        StockLot.save(to_save)


class QualityTest(metaclass=PoolMeta):
    __name__ = 'quality.test'

    @classmethod
    @ModelView.button
    def manager_validate(cls, tests):
        super().manager_validate(tests)
        cls.lot_active(tests)

    @classmethod
    @ModelView.button
    @Workflow.transition('draft')
    def draft(cls, tests):
        super().draft(tests)
        cls.lot_active(tests)

    @staticmethod
    def lot_active(tests):
        StockLot = Pool().get('stock.lot')
        to_save = []

        for test in tests:
            if isinstance(test.document, StockLot):
                test.document.active = False
                if test.state == 'successful':
                    test.document.active = True
                to_save.append(test.document)

        StockLot.save(to_save)
