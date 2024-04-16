#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,SUPERUSER_ID,_
fromflectra.exceptionsimportUserError


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    module_procurement_jit=fields.Selection([
        ('1','Immediatelyaftersalesorderconfirmation'),
        ('0','Manuallyorbasedonautomaticscheduler')
        ],"Reservation",default='0',
        help="Reservingproductsmanuallyindeliveryordersorbyrunningtheschedulerisadvisedtobettermanageprioritiesincaseoflongcustomerleadtimesor/andfrequentstock-outs.")
    module_product_expiry=fields.Boolean("ExpirationDates",
        help="Trackfollowingdatesonlots&serialnumbers:bestbefore,removal,endoflife,alert.\nSuchdatesaresetautomaticallyatlot/serialnumbercreationbasedonvaluessetontheproduct(indays).")
    group_stock_production_lot=fields.Boolean("Lots&SerialNumbers",
        implied_group='stock.group_production_lot')
    group_lot_on_delivery_slip=fields.Boolean("DisplayLots&SerialNumbersonDeliverySlips",
        implied_group='stock.group_lot_on_delivery_slip',group="base.group_user,base.group_portal")
    group_stock_tracking_lot=fields.Boolean("Packages",
        implied_group='stock.group_tracking_lot')
    group_stock_tracking_owner=fields.Boolean("Consignment",
        implied_group='stock.group_tracking_owner')
    group_stock_adv_location=fields.Boolean("Multi-StepRoutes",
        implied_group='stock.group_adv_location',
        help="Addandcustomizerouteoperationstoprocessproductmovesinyourwarehouse(s):e.g.unload>qualitycontrol>stockforincomingproducts,pick>pack>shipforoutgoingproducts.\nYoucanalsosetputawaystrategiesonwarehouselocationsinordertosendincomingproductsintospecificchildlocationsstraightaway(e.g.specificbins,racks).")
    group_warning_stock=fields.Boolean("WarningsforStock",implied_group='stock.group_warning_stock')
    group_stock_sign_delivery=fields.Boolean("Signature",implied_group='stock.group_stock_sign_delivery')
    module_stock_picking_batch=fields.Boolean("BatchPickings")
    module_stock_barcode=fields.Boolean("BarcodeScanner")
    stock_move_email_validation=fields.Boolean(related='company_id.stock_move_email_validation',readonly=False)
    stock_mail_confirmation_template_id=fields.Many2one(related='company_id.stock_mail_confirmation_template_id',readonly=False)
    module_stock_sms=fields.Boolean("SMSConfirmation")
    module_delivery=fields.Boolean("DeliveryMethods")
    module_delivery_dhl=fields.Boolean("DHLExpressConnector")
    module_delivery_fedex=fields.Boolean("FedExConnector")
    module_delivery_ups=fields.Boolean("UPSConnector")
    module_delivery_usps=fields.Boolean("USPSConnector")
    module_delivery_bpost=fields.Boolean("bpostConnector")
    module_delivery_easypost=fields.Boolean("EasypostConnector")
    group_stock_multi_locations=fields.Boolean('StorageLocations',implied_group='stock.group_stock_multi_locations',
        help="Storeproductsinspecificlocationsofyourwarehouse(e.g.bins,racks)andtotrackinventoryaccordingly.")

    @api.onchange('group_stock_multi_locations')
    def_onchange_group_stock_multi_locations(self):
        ifnotself.group_stock_multi_locations:
            self.group_stock_adv_location=False

    @api.onchange('group_stock_production_lot')
    def_onchange_group_stock_production_lot(self):
        ifnotself.group_stock_production_lot:
            self.group_lot_on_delivery_slip=False

    @api.onchange('group_stock_adv_location')
    defonchange_adv_location(self):
        ifself.group_stock_adv_locationandnotself.group_stock_multi_locations:
            self.group_stock_multi_locations=True

    defset_values(self):
        ifself.module_procurement_jit=='0':
            self.env['ir.config_parameter'].sudo().set_param('stock.picking_no_auto_reserve',True)
        else:
            self.env['ir.config_parameter'].sudo().set_param('stock.picking_no_auto_reserve',False)
        warehouse_grp=self.env.ref('stock.group_stock_multi_warehouses')
        location_grp=self.env.ref('stock.group_stock_multi_locations')
        base_user=self.env.ref('base.group_user')
        ifnotself.group_stock_multi_locationsandlocation_grpinbase_user.implied_idsandwarehouse_grpinbase_user.implied_ids:
            raiseUserError(_("Youcan'tdesactivatethemulti-locationifyouhavemorethanoncewarehousebycompany"))

        previous_group=self.default_get(['group_stock_multi_locations','group_stock_production_lot','group_stock_tracking_lot'])
        was_operations_showed=self.env['stock.picking.type'].with_user(SUPERUSER_ID)._default_show_operations()
        res=super(ResConfigSettings,self).set_values()

        ifnotself.user_has_groups('stock.group_stock_manager'):
            return

        """Ifwedisablemultiplelocations,wecandeactivatetheinternal
        operationtypesofthewarehouses,sotheywon'tappearinthedashboard.
        Otherwise,activatethem.
        """
        warehouse_obj=self.env['stock.warehouse']
        ifself.group_stock_multi_locationsandnotprevious_group.get('group_stock_multi_locations'):
            #overrideactive_testthatisfalseinset_values
            warehouse_obj.with_context(active_test=True).search([]).mapped('int_type_id').write({'active':True})
        elifnotself.group_stock_multi_locationsandprevious_group.get('group_stock_multi_locations'):
            warehouse_obj.search([
                ('reception_steps','=','one_step'),
                ('delivery_steps','=','ship_only')]
            ).mapped('int_type_id').write({'active':False})

        ifnotwas_operations_showedandself.env['stock.picking.type'].with_user(SUPERUSER_ID)._default_show_operations():
            picking_types=self.env['stock.picking.type'].with_context(active_test=False).search([
                ('code','!=','incoming'),
                ('show_operations','=',False)
            ])
            picking_types.sudo().write({'show_operations':True})
        returnres
