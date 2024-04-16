#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classPosConfig(models.Model):
    _inherit='pos.config'

    iface_splitbill=fields.Boolean(string='BillSplitting',help='EnablesBillSplittinginthePointofSale.')
    iface_printbill=fields.Boolean(string='BillPrinting',help='AllowstoprinttheBillbeforepayment.')
    iface_orderline_notes=fields.Boolean(string='Notes',help='AllowcustomnotesonOrderlines.')
    floor_ids=fields.One2many('restaurant.floor','pos_config_id',string='RestaurantFloors',help='Therestaurantfloorsservedbythispointofsale.')
    printer_ids=fields.Many2many('restaurant.printer','pos_config_printer_rel','config_id','printer_id',string='OrderPrinters')
    is_table_management=fields.Boolean('Floors&Tables')
    is_order_printer=fields.Boolean('OrderPrinter')
    set_tip_after_payment=fields.Boolean('SetTipAfterPayment',help="Adjusttheamountauthorizedbypaymentterminalstoaddatipafterthecustomersleftorattheendoftheday.")
    module_pos_restaurant=fields.Boolean(default=True)

    @api.onchange('module_pos_restaurant')
    def_onchange_module_pos_restaurant(self):
        ifnotself.module_pos_restaurant:
            self.update({'iface_printbill':False,
            'iface_splitbill':False,
            'is_order_printer':False,
            'is_table_management':False,
            'iface_orderline_notes':False})

    @api.onchange('iface_tipproduct')
    def_onchange_iface_tipproduct(self):
        ifnotself.iface_tipproduct:
            self.set_tip_after_payment=False

    def_force_http(self):
        enforce_https=self.env['ir.config_parameter'].sudo().get_param('point_of_sale.enforce_https')
        ifnotenforce_httpsandself.printer_ids.filtered(lambdapt:pt.printer_type=='epson_epos'):
            returnTrue
        returnsuper(PosConfig,self)._force_http()

    defget_tables_order_count(self):
        """        """
        self.ensure_one()
        tables=self.env['restaurant.table'].search([('floor_id.pos_config_id','in',self.ids)])
        domain=[('state','=','draft'),('table_id','in',tables.ids)]

        order_stats=self.env['pos.order'].read_group(domain,['table_id'],'table_id')
        orders_map=dict((s['table_id'][0],s['table_id_count'])forsinorder_stats)

        result=[]
        fortableintables:
            result.append({'id':table.id,'orders':orders_map.get(table.id,0)})
        returnresult

    def_get_forbidden_change_fields(self):
        forbidden_keys=super(PosConfig,self)._get_forbidden_change_fields()
        forbidden_keys.append('is_table_management')
        forbidden_keys.append('floor_ids')
        returnforbidden_keys

    defwrite(self,vals):
        if('is_table_management'invalsandvals['is_table_management']==False):
            vals['floor_ids']=[(5,0,0)]
        if('is_order_printer'invalsandvals['is_order_printer']==False):
            vals['printer_ids']=[(5,0,0)]
        returnsuper(PosConfig,self).write(vals)
