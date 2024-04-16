#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api,_


classStockPicking(models.Model):
    _inherit="stock.picking"

    l10n_it_transport_reason=fields.Selection([('sale','Sale'),
                                                 ('outsourcing','Outsourcing'),
                                                 ('evaluation','Evaluation'),
                                                 ('gift','Gift'),
                                                 ('transfer','Transfer'),
                                                 ('substitution','Substitution'),
                                                 ('attemped_sale','AttemptedSale'),
                                                 ('loaned_use','LoanedforUse'),
                                                 ('repair','Repair')],default="sale",tracking=True,string='TransportReason')
    l10n_it_transport_method=fields.Selection([('sender','Sender'),('recipient','Recipient'),('courier','Courierservice')],
                                                default="sender",string='TransportMethod')
    l10n_it_transport_method_details=fields.Char('TransportNote')
    l10n_it_parcels=fields.Integer(string="Parcels",default=1)
    l10n_it_country_code=fields.Char(related="company_id.country_id.code")
    l10n_it_ddt_number=fields.Char('DDTNumber',readonly=True)
    l10n_it_show_print_ddt_button=fields.Boolean(compute="_compute_l10n_it_show_print_ddt_button")

    @api.depends('l10n_it_country_code',
                 'picking_type_code',
                 'state',
                 'is_locked',
                 'move_ids_without_package',
                 'move_ids_without_package.partner_id',
                 'location_id',
                 'location_dest_id')
    def_compute_l10n_it_show_print_ddt_button(self):
        #EnableprintingtheDDTfordoneoutgoingshipments
        #ordropshipping(pickinggoingfromsuppliertocustomer)
        forpickinginself:
            picking.l10n_it_show_print_ddt_button=(
                picking.l10n_it_country_code=='IT'
                andpicking.state=='done'
                andpicking.is_locked
                and(picking.picking_type_code=='outgoing'
                     or(
                         picking.move_ids_without_package
                         andpicking.move_ids_without_package[0].partner_id
                         andpicking.location_id.usage=='supplier'
                         andpicking.location_dest_id.usage=='customer'
                         )
                     )
                )

    def_action_done(self):
        super(StockPicking,self)._action_done()
        forpickinginself.filtered(lambdap:p.picking_type_id.l10n_it_ddt_sequence_id):
            picking.l10n_it_ddt_number=picking.picking_type_id.l10n_it_ddt_sequence_id.next_by_id()


classStockPickingType(models.Model):
    _inherit='stock.picking.type'

    l10n_it_ddt_sequence_id=fields.Many2one('ir.sequence')

    def_get_dtt_ir_seq_vals(self,warehouse_id,sequence_code):
        ifwarehouse_id:
            wh=self.env['stock.warehouse'].browse(warehouse_id)
            ir_seq_name=wh.name+''+_('Sequence')+''+sequence_code
            ir_seq_prefix=wh.code+'/'+sequence_code+'/DDT'
        else:
            ir_seq_name=_('Sequence')+''+sequence_code
            ir_seq_prefix=sequence_code+'/DDT'
        returnir_seq_name,ir_seq_prefix

    @api.model
    defcreate(self,vals):
        company=self.env['res.company'].browse(vals.get('company_id',False))orself.env.company
        ifcompany.country_id.code=='IT'andvals['code']=='outgoing'and('l10n_it_ddt_sequence_id'notinvalsornotvals['l10n_it_ddt_sequence_id']):
            ir_seq_name,ir_seq_prefix=self._get_dtt_ir_seq_vals(vals.get('warehouse_id'),vals['sequence_code'])
            vals['l10n_it_ddt_sequence_id']=self.env['ir.sequence'].create({
                    'name':ir_seq_name,
                    'prefix':ir_seq_prefix,
                    'padding':5,
                    'company_id':company.id,
                    'implementation':'no_gap',
                }).id
        returnsuper(StockPickingType,self).create(vals)

    defwrite(self,vals):
        if'sequence_code'invals:
            forpicking_typeinself.filtered(lambdap:p.l10n_it_ddt_sequence_id):
                warehouse=picking_type.warehouse_id.idif'warehouse_id'notinvalselsevals['warehouse_ids']
                ir_seq_name,ir_seq_prefix=self._get_dtt_ir_seq_vals(warehouse,vals['sequence_code'])
                picking_type.l10n_it_ddt_sequence_id.write({
                        'name':ir_seq_name,
                        'prefix':ir_seq_prefix,
                    })
        returnsuper(StockPickingType,self).write(vals)