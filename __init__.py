# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .stock import *


def register():
    Pool.register(
        QualityTemplate,
        ShipmentIn,
        ShipmentOut,
        ShipmentInternal,
        module='stock_quality_control_trigger_lot', type_='model')
