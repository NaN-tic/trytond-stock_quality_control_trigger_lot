# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta, Pool
from trytond.model import fields
from trytond.modules.stock_quality_control_trigger_lot.quality import (
    CreateQualityTestsMixin)


__all__ = ['ShipmentIn', 'ShipmentOut', 'ShipmentInternal', 'Lot']


class ShipmentIn(CreateQualityTestsMixin, metaclass=PoolMeta):
    __name__ = 'stock.shipment.in'

    @classmethod
    def receive(cls, shipments):
        super().receive(shipments)
        cls.create_lot_quality_tests(shipments, 'shipment_in')

    def lots_for_quality_tests(self):
        return list(set(m.lot for m in self.incoming_moves if m.lot
            and m.state == 'done' and m.product.template.shipment_in_quality_template))


class ShipmentOut(CreateQualityTestsMixin, metaclass=PoolMeta):
    __name__ = 'stock.shipment.out'

    @classmethod
    def pack(cls, shipments):
        super().pack(shipments)
        cls.create_lot_quality_tests(shipments, 'shipment_out')

    def lots_for_quality_tests(self):
        return list(set(m.lot for m in self.outgoing_moves if m.lot
            and m.state == 'assigned' and m.product.template.shipment_out_quality_template))


class ShipmentInternal(CreateQualityTestsMixin, metaclass=PoolMeta):
    __name__ = 'stock.shipment.internal'

    @classmethod
    def assign(cls, shipments):
        super().assign(shipments)
        cls.create_lot_quality_tests(shipments, 'shipment_internal')

    def lots_for_quality_tests(self):
        return list(set(m.lot for m in self.moves if m.lot and m.state == 'assigned'
            and m.product.template.shipment_internal_quality_template))


class Lot(metaclass=PoolMeta):
    __name__ = 'stock.lot'
    quality_tests = fields.One2Many('quality.test', 'document', 'Tests',
        readonly=True)
