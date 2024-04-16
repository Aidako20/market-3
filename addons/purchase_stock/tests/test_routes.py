fromflectra.tests.commonimportTransactionCase,Form


classTestRoutes(TransactionCase):

    deftest_allow_rule_creation_for_route_without_company(self):
        self.env['res.config.settings'].write({
            'group_stock_adv_location':True,
            'group_stock_multi_locations':True,
        })

        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.company.id)],limit=1)

        location_1=self.env['stock.location'].create({
            'name':'loc1',
            'location_id':warehouse.id
        })

        location_2=self.env['stock.location'].create({
            'name':'loc2',
            'location_id':warehouse.id
        })

        receipt_1=self.env['stock.picking.type'].create({
            'name':'Receiptsfromloc1',
            'sequence_code':'IN1',
            'code':'incoming',
            'warehouse_id':warehouse.id,
            'default_location_dest_id':location_1.id,
        })

        receipt_2=self.env['stock.picking.type'].create({
            'name':'Receiptsfromloc2',
            'sequence_code':'IN2',
            'code':'incoming',
            'warehouse_id':warehouse.id,
            'default_location_dest_id':location_2.id,
        })

        route=self.env['stock.location.route'].create({
            'name':'Buy',
            'company_id':False
        })

        withForm(route)asr:
            withr.rule_ids.new()asline:
                line.name='firstrule'
                line.action='buy'
                line.picking_type_id=receipt_1
            withr.rule_ids.new()asline:
                line.name='secondrule'
                line.action='buy'
                line.picking_type_id=receipt_2
