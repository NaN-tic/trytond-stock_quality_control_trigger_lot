# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.modules.quality_control_trigger.quality import (
    QualityControlTriggerMixin)

__all__ = ['QualityTemplate', 'ShipmentIn', 'ShipmentOut', 'ShipmentInternal']


class QualityTemplate(metaclass=PoolMeta):
    __name__ = 'quality.template'

    @classmethod
    def _get_trigger_generation_models_by_trigger_models(cls):
        models = super(QualityTemplate,
            cls)._get_trigger_generation_models_by_trigger_models()
        for model_name in ('stock.shipment.in', 'stock.shipment.out',
                'stock.shipment.internal'):
            generated_models = models.setdefault(model_name, [])
            if 'stock.lot' not in generated_models:
                generated_models.append('stock.lot')
        return models


class ShipmentIn(QualityControlTriggerMixin, metaclass=PoolMeta):
    __name__ = 'stock.shipment.in'

    @classmethod
    def done(cls, shipments):
        super(ShipmentIn, cls).done(shipments)
        cls.create_quality_tests(shipments, 'stock.lot')

    def _get_quality_trigger_generation_instances(self, template):
        if template.trigger_generation_model != 'stock.lot':
            return super(ShipmentIn,
                self)._get_quality_trigger_generation_instances(template)
        return set(m.lot for m in self.inventory_moves
            if m.state == 'done' and m.product == template.document and m.lot)


class ShipmentOut(QualityControlTriggerMixin, metaclass=PoolMeta):
    __name__ = 'stock.shipment.out'

    @classmethod
    def done(cls, shipments):
        super(ShipmentOut, cls).done(shipments)
        cls.create_quality_tests(shipments, 'stock.lot')

    def _get_quality_trigger_generation_instances(self, template):
        if template.trigger_generation_model != 'stock.lot':
            return super(ShipmentOut,
                self)._get_quality_trigger_generation_instances(template)
        return set(m.lot for m in self.outgoing_moves
            if m.state == 'done' and m.product == template.document and m.lot)


class ShipmentInternal(QualityControlTriggerMixin, metaclass=PoolMeta):
    __name__ = 'stock.shipment.internal'

    @classmethod
    def done(cls, shipments):
        super(ShipmentInternal, cls).done(shipments)
        cls.create_quality_tests(shipments, 'stock.lot')

    def _get_quality_trigger_generation_instances(self, template):
        if template.trigger_generation_model != 'stock.lot':
            return super(ShipmentInternal,
                self)._get_quality_trigger_generation_instances(template)
        return set(m.lot for m in self.moves
            if m.state == 'done' and m.product == template.document and m.lot)
