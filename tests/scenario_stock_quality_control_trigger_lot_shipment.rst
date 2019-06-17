====================================================
Quality Control Trigger by Lot on Shipments Scenario
====================================================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import config, Model
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> today = datetime.date.today()

Activate module::

    >>> config = activate_modules('stock_quality_control_trigger_lot')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create supplier and customer::

    >>> Party = Model.get('party.party')
    >>> supplier = Party(name='Supplier')
    >>> supplier.save()
    >>> customer = Party(name='Customer')
    >>> customer.save()

Create products::

    >>> ProductUom = Model.get('product.uom')
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> template1 = ProductTemplate()
    >>> template1.name = 'Product 1'
    >>> template1.default_uom = unit
    >>> template1.type = 'goods'
    >>> template1.list_price = Decimal('20')
    >>> template1.save()
    >>> product1, = template1.products
    >>> template2 = ProductTemplate()
    >>> template2.name = 'Product 2'
    >>> template2.default_uom = unit
    >>> template2.type = 'goods'
    >>> template2.list_price = Decimal('20')
    >>> template2.save()
    >>> product2, = template2.products

Create Quality Configuration::

    >>> Sequence = Model.get('ir.sequence')
    >>> Configuration = Model.get('quality.configuration')
    >>> ConfigLine = Model.get('quality.configuration.line')
    >>> IrModel = Model.get('ir.model')
    >>> sequence = Sequence.find([('code','=','quality.test')])[0]
    >>> product_model, = IrModel.find([('model','=','product.product')])
    >>> lot_model, = IrModel.find([('model','=','stock.lot')])
    >>> configuration = Configuration()
    >>> configuration.name = 'Configuration'
    >>> product_config_line = ConfigLine()
    >>> configuration.allowed_documents.append(product_config_line)
    >>> product_config_line.quality_sequence = sequence
    >>> product_config_line.document = product_model
    >>> lot_config_line = ConfigLine()
    >>> configuration.allowed_documents.append(lot_config_line)
    >>> lot_config_line.quality_sequence = sequence
    >>> lot_config_line.document = lot_model
    >>> configuration.save()

Create Templates related to Product 1 with Shipments as Trigger model and
Lot as generated model::

    >>> Template = Model.get('quality.template')
    >>> for model, name in (('stock.shipment.in', 'Shipment In'),
    ...         ('stock.shipment.out', 'Shipment Out'),
    ...         ('stock.shipment.internal', 'Shipment Internal')):
    ...     template = Template()
    ...     template.name = 'Template %s' % name
    ...     template.document = product1
    ...     template.internal_description='Quality Control on %s' % name
    ...     template.external_description='External description'
    ...     template.trigger_model = model
    ...     template.trigger_generation_model = 'stock.lot'
    ...     template.save()

Get stock locations and create new internal location::

    >>> Location = Model.get('stock.location')
    >>> warehouse_loc, = Location.find([('code', '=', 'WH')])
    >>> supplier_loc, = Location.find([('code', '=', 'SUP')])
    >>> customer_loc, = Location.find([('code', '=', 'CUS')])
    >>> input_loc, = Location.find([('code', '=', 'IN')])
    >>> output_loc, = Location.find([('code', '=', 'OUT')])
    >>> storage_loc, = Location.find([('code', '=', 'STO')])
    >>> internal_loc = Location()
    >>> internal_loc.name = 'Internal Location'
    >>> internal_loc.code = 'INT'
    >>> internal_loc.type = 'storage'
    >>> internal_loc.parent = storage_loc
    >>> internal_loc.save()

Create Shipment In::

    >>> ShipmentIn = Model.get('stock.shipment.in')
    >>> shipment_in = ShipmentIn()
    >>> shipment_in.planned_date = today
    >>> shipment_in.supplier = supplier
    >>> shipment_in.warehouse = warehouse_loc

Add three shipment lines of product 1 and one of product 2::

    >>> StockMove = Model.get('stock.move')
    >>> shipment_in.incoming_moves.extend([StockMove(), StockMove(),
    ...         StockMove()])
    >>> for move in shipment_in.incoming_moves:
    ...     move.product = product1
    ...     move.uom = unit
    ...     move.quantity = 1
    ...     move.from_location = supplier_loc
    ...     move.to_location = input_loc
    ...     move.unit_price = Decimal('1')
    >>> move = StockMove()
    >>> shipment_in.incoming_moves.append(move)
    >>> move.product = product2
    >>> move.uom = unit
    >>> move.quantity = 3
    >>> move.from_location = supplier_loc
    >>> move.to_location = input_loc
    >>> move.unit_price = Decimal('1')
    >>> shipment_in.save()

Create two Lots of Product 1 and set them to the shipment lines (two lines with
the same lot)::

    >>> Lot = Model.get('stock.lot')
    >>> move1, move2, move3 = [m for m in shipment_in.incoming_moves if
    ...     m.product == product1]
    >>> lot1 = Lot(number='1')
    >>> lot1.product = product1
    >>> lot1.save()
    >>> move1.lot = lot1
    >>> move1.save()
    >>> lot2 = Lot(number='2')
    >>> lot2.product = product1
    >>> lot2.save()
    >>> move2.lot = lot2
    >>> move2.save()
    >>> move3.lot = lot1
    >>> move3.save()

Create a Lot for Product 2 and set to the shipment line::

    >>> move4, = [m for m in shipment_in.incoming_moves
    ...     if m.product == product2]
    >>> lot3 = Lot(number='3')
    >>> lot3.product = product2
    >>> lot3.save()
    >>> move4.lot = lot3
    >>> move4.save()

Receive products and set the state as Done::

    >>> ShipmentIn.receive([shipment_in.id], config.context)
    >>> ShipmentIn.done([shipment_in.id], config.context)
    >>> shipment_in.reload()
    >>> shipment_in.state
    'done'
    >>> {m.state for m in shipment_in.inventory_moves}
    {'done'}

Check the created Quality Tests::

    >>> QualityTest = Model.get('quality.test')
    >>> tests_in = QualityTest.find([])
    >>> len(tests_in)
    2
    >>> tests_in[0].document in (lot1, lot2)
    True
    >>> tests_in[1].document in (lot1, lot2)
    True

Create Shipment Out::

    >>> ShipmentOut = Model.get('stock.shipment.out')
    >>> shipment_out = ShipmentOut()
    >>> shipment_out.planned_date = today
    >>> shipment_out.customer = customer
    >>> shipment_out.warehouse = warehouse_loc

Add one line of product 1 and one of product 2::

    >>> shipment_out.outgoing_moves.extend([StockMove(), StockMove()])
    >>> product_tmp = product1
    >>> lot_tmp = lot1
    >>> for move in shipment_out.outgoing_moves:
    ...     move.product = product_tmp
    ...     move.lot = lot_tmp
    ...     move.uom = unit
    ...     move.quantity = 1
    ...     move.from_location = output_loc
    ...     move.to_location = customer_loc
    ...     move.unit_price = Decimal('1')
    ...     product_tmp = product2
    ...     lot_tmp = lot3
    >>> shipment_out.save()

Set the shipment state to waiting and then assign and pack it::

    >>> ShipmentOut.wait([shipment_out.id], config.context)
    >>> ShipmentOut.assign_try([shipment_out.id], config.context)
    True
    >>> ShipmentOut.pack([shipment_out.id], config.context)
    >>> shipment_out.reload()
    >>> len(shipment_out.outgoing_moves)
    2
    >>> len(shipment_out.inventory_moves)
    2
    >>> {m.state for m in shipment_out.outgoing_moves}
    {'assigned'}

Set the state as Done::

    >>> ShipmentOut.done([shipment_out.id], config.context)
    >>> shipment_out.reload()
    >>> shipment_in.state
    'done'
    >>> {m.state for m in shipment_out.outgoing_moves}
    {'done'}

Check the created Quality Tests::

    >>> tests_out = QualityTest.find([
    ...         ('id', 'not in', [t.id for t in tests_in]),
    ...         ])
    >>> len(tests_out)
    1
    >>> tests_out[0].document == lot1
    True

Create Shipment Internal::

    >>> ShipmentInternal = Model.get('stock.shipment.internal')
    >>> shipment_internal = ShipmentInternal()
    >>> shipment_internal.planned_date = today
    >>> shipment_internal.from_location = storage_loc
    >>> shipment_internal.to_location = internal_loc

Add one line of product 1 and one of product 2::

    >>> shipment_internal.moves.extend([StockMove(), StockMove()])
    >>> product_tmp = product1
    >>> lot_tmp = lot2
    >>> for move in shipment_internal.moves:
    ...     move.product = product_tmp
    ...     move.lot = lot_tmp
    ...     move.uom = unit
    ...     move.quantity = 1
    ...     move.from_location = storage_loc
    ...     move.to_location = internal_loc
    ...     move.unit_price = Decimal('1')
    ...     product_tmp = product2
    ...     lot_tmp = lot3
    >>> shipment_internal.save()

Set the shipment state to waiting and then assign it::

    >>> ShipmentInternal.wait([shipment_internal.id], config.context)
    >>> ShipmentInternal.assign_try([shipment_internal.id], config.context)
    True
    >>> shipment_internal.reload()
    >>> {m.state for m in shipment_internal.moves}
    {'assigned'}

Set the state as Done::

    >>> ShipmentInternal.done([shipment_internal.id], config.context)
    >>> shipment_internal.reload()
    >>> shipment_in.state
    'done'
    >>> {m.state for m in shipment_internal.moves}
    {'done'}

Check the created Quality Tests::

    >>> prev_test_ids = [t.id for t in tests_in] + [t.id for t in tests_out]
    >>> tests_internal = QualityTest.find([('id', 'not in', prev_test_ids)])
    >>> len(tests_internal)
    1
    >>> tests_internal[0].document == lot2
    True
