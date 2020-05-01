# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta, Pool
from trytond.model import fields
from trytond.modules.stock_quality_control_trigger_lot.quality import (
    CreateQualityTestsMixin)


class Template(metaclass=PoolMeta):
    __name__ = 'product.template'
    production_quality_template = fields.Many2One('quality.template',
        'Production Quality Template')


class Production(CreateQualityTestsMixin, metaclass=PoolMeta):
    __name__ = 'production'

    @classmethod
    def done(cls, productions):
        super().done(productions)
        cls.create_lot_quality_tests(productions, 'production')

    def lots_for_quality_tests(self):
        return list(set(m.lot for m in self.outputs if m.lot
            and m.state == 'done' and m.product.production_quality_template))
