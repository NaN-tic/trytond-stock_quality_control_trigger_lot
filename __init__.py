# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import product
from . import production
from . import quality
from . import stock

module = 'stock_quality_control_trigger_lot'

def register():
    Pool.register(
        product.Template,
        quality.QualityTest,
        stock.Lot,
        stock.ShipmentIn,
        stock.ShipmentOut,
        stock.ShipmentInternal,
        module=module, type_='model')
    Pool.register(
        production.Template,
        production.Production,
        depends=['production'],
        module=module, type_='model')
