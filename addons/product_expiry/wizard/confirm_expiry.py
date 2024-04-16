#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classConfirmExpiry(models.TransientModel):
    _name='expiry.picking.confirmation'
    _description='ConfirmExpiry'

    lot_ids=fields.Many2many('stock.production.lot',readonly=True,required=True)
    picking_ids=fields.Many2many('stock.picking',readonly=True)
    description=fields.Char('Description',compute='_compute_descriptive_fields')
    show_lots=fields.Boolean('ShowLots',compute='_compute_descriptive_fields')

    @api.depends('lot_ids')
    def_compute_descriptive_fields(self):
        #Showsexpiredlotsonlyifwearemorethanoneexpiredlot.
        self.show_lots=len(self.lot_ids)>1
        ifself.show_lots:
            #Formultipleexpiredlots,theyarelistedinthewizardview.
            self.description=_(
                "Youaregoingtodeliversomeproductexpiredlots."
                "\nDoyouconfirmyouwanttoproceed?"
            )
        else:
            #Foroneexpiredlot,itsnameiswritteninthewizardmessage.
            self.description=_(
                "Youaregoingtodelivertheproduct%(product_name)s,%(lot_name)swhichisexpired."
                "\nDoyouconfirmyouwanttoproceed?",
                product_name=self.lot_ids.product_id.display_name,
                lot_name=self.lot_ids.name
            )

    defprocess(self):
        picking_to_validate=self.env.context.get('button_validate_picking_ids')
        ifpicking_to_validate:
            picking_to_validate=self.env['stock.picking'].browse(picking_to_validate)
            ctx=dict(self.env.context,skip_expired=True)
            ctx.pop('default_lot_ids')
            returnpicking_to_validate.with_context(ctx).button_validate()
        returnTrue

    defprocess_no_expired(self):
        """Don'tprocessforconcernedpickings(oneswithexpiredlots),but
        processforallotherpickings(incaseofmulti)."""
        #Remove`self.pick_ids`from`button_validate_picking_ids`andcall
        #`button_validate`withthesubset(ifany).
        pickings_to_validate=self.env['stock.picking'].browse(self.env.context.get('button_validate_picking_ids'))
        pickings_to_validate=pickings_to_validate-self.picking_ids
        ifpickings_to_validate:
            returnpickings_to_validate.with_context(skip_expired=True).button_validate()
        returnTrue
