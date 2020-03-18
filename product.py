#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval

__all__ = ['Template']


class Template(metaclass=PoolMeta):
    __name__ = 'product.template'
    shipment_in_quality_template = fields.Many2One('quality.template',
        'Shipment In Quality Template')
    shipment_out_quality_template = fields.Many2One('quality.template',
        'Shipment Out Quality Template')
    shipment_internal_quality_template = fields.Many2One('quality.template',
        'Shipment Internal Quality Template')
    production_quality_template = fields.Many2One('quality.template',
        'Production Quality Template')
