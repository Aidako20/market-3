#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields


classUsers(models.Model):
    _inherit=['res.users']

    property_warehouse_id=fields.Many2one('stock.warehouse',string='DefaultWarehouse',company_dependent=True,check_company=True)

    def_get_default_warehouse_id(self):
        ifself.property_warehouse_id:
            returnself.property_warehouse_id
        #!!!Anychangetothefollowingsearchdomainshouldprobably
        #bealsoappliedinsale_stock/models/sale_order.py/_init_column.
        returnself.env['stock.warehouse'].search([('company_id','=',self.env.company.id)],limit=1)

    def__init__(self,pool,cr):
        """Overrideof__init__toaddaccessrights.
            Accessrightsaredisabledbydefault,butallowed
            onsomespecificfieldsdefinedinself.SELF_{READ/WRITE}ABLE_FIELDS.
        """

        sale_stock_writeable_fields=[
            'property_warehouse_id',
        ]

        init_res=super().__init__(pool,cr)
        #duplicatelisttoavoidmodifyingtheoriginalreference
        pool[self._name].SELF_READABLE_FIELDS=pool[self._name].SELF_READABLE_FIELDS+sale_stock_writeable_fields
        pool[self._name].SELF_WRITEABLE_FIELDS=pool[self._name].SELF_WRITEABLE_FIELDS+sale_stock_writeable_fields
        returninit_res
