#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime

fromflectraimportapi,fields,models


classStockMoveLine(models.Model):
    _inherit="stock.move.line"

    expiration_date=fields.Datetime(
        string='ExpirationDate',compute='_compute_expiration_date',store=True,
        help='ThisisthedateonwhichthegoodswiththisSerialNumbermay'
        'becomedangerousandmustnotbeconsumed.')

    @api.depends('product_id','picking_type_use_create_lots','lot_id.expiration_date')
    def_compute_expiration_date(self):
        formove_lineinself:
            ifmove_line.lot_id.expiration_date:
                move_line.expiration_date=move_line.lot_id.expiration_date
            elifmove_line.picking_type_use_create_lots:
                ifmove_line.product_id.use_expiration_date:
                    ifnotmove_line.expiration_date:
                        move_line.expiration_date=fields.Datetime.today()+datetime.timedelta(days=move_line.product_id.expiration_time)
                else:
                    move_line.expiration_date=False

    @api.onchange('lot_id')
    def_onchange_lot_id(self):
        ifnotself.picking_type_use_existing_lotsornotself.product_id.use_expiration_date:
            return
        ifself.lot_id:
            self.expiration_date=self.lot_id.expiration_date
        else:
            self.expiration_date=False

    @api.onchange('product_id','product_uom_id')
    def_onchange_product_id(self):
        res=super()._onchange_product_id()
        ifself.picking_type_use_create_lots:
            ifself.product_id.use_expiration_date:
                self.expiration_date=fields.Datetime.today()+datetime.timedelta(days=self.product_id.expiration_time)
            else:
                self.expiration_date=False
        returnres

    def_assign_production_lot(self,lot):
        super()._assign_production_lot(lot)
        self.lot_id._update_date_values(self[0].expiration_date)

    def_get_value_production_lot(self):
        res=super()._get_value_production_lot()
        ifself.expiration_date:
            res.update({
                'expiration_date':self.expiration_date,
                'use_date':self.product_id.use_timeandself.expiration_date-datetime.timedelta(days=(self.product_id.expiration_time-self.product_id.use_time)),
                'removal_date':self.product_id.removal_timeandself.expiration_date-datetime.timedelta(days=(self.product_id.expiration_time-self.product_id.removal_time)),
                'alert_date':self.product_id.alert_timeandself.expiration_date-datetime.timedelta(days=(self.product_id.expiration_time-self.product_id.alert_time))
            })
        returnres
