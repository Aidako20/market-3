#-*-coding:utf-8-*-

fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.addons.product.testsimportcommon


classTestStockCommon(common.TestProductCommon):

    def_create_move(self,product,src_location,dst_location,**values):
        #TDEFIXME:userasparameter
        Move=self.env['stock.move'].with_user(self.user_stock_manager)
        #simulatecreate+onchange
        move=Move.new({'product_id':product.id,'location_id':src_location.id,'location_dest_id':dst_location.id})
        move.onchange_product_id()
        move_values=move._convert_to_write(move._cache)
        move_values.update(**values)
        returnMove.create(move_values)

    @classmethod
    defsetUpClass(cls):
        super(TestStockCommon,cls).setUpClass()

        #UserData:stockuserandstockmanager
        cls.user_stock_user=mail_new_test_user(
            cls.env,
            name='PaulinePoivraisselle',
            login='pauline',
            email='p.p@example.com',
            notification_type='inbox',
            groups='stock.group_stock_user',
        )
        cls.user_stock_manager=mail_new_test_user(
            cls.env,
            name='JulieTablier',
            login='julie',
            email='j.j@example.com',
            notification_type='inbox',
            groups='stock.group_stock_manager',
        )

        #Warehouses
        cls.warehouse_1=cls.env['stock.warehouse'].create({
            'name':'BaseWarehouse',
            'reception_steps':'one_step',
            'delivery_steps':'ship_only',
            'code':'BWH'})

        #Locations
        cls.location_1=cls.env['stock.location'].create({
            'name':'TestLocation1',
            'posx':3,
            'location_id':cls.warehouse_1.lot_stock_id.id,
        })

        #Existingdata
        cls.existing_inventories=cls.env['stock.inventory'].search([])
        cls.existing_quants=cls.env['stock.quant'].search([])
