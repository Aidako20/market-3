#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importdatetime
fromflectraimportapi,fields,models,SUPERUSER_ID,_


classStockProductionLot(models.Model):
    _inherit='stock.production.lot'

    use_expiration_date=fields.Boolean(
        string='UseExpirationDate',related='product_id.use_expiration_date')
    expiration_date=fields.Datetime(string='ExpirationDate',
        help='ThisisthedateonwhichthegoodswiththisSerialNumbermaybecomedangerousandmustnotbeconsumed.')
    use_date=fields.Datetime(string='BestbeforeDate',
        help='ThisisthedateonwhichthegoodswiththisSerialNumberstartdeteriorating,withoutbeingdangerousyet.')
    removal_date=fields.Datetime(string='RemovalDate',
        help='ThisisthedateonwhichthegoodswiththisSerialNumbershouldberemovedfromthestock.ThisdatewillbeusedinFEFOremovalstrategy.')
    alert_date=fields.Datetime(string='AlertDate',
        help='Datetodeterminetheexpiredlotsandserialnumbersusingthefilter"ExpirationAlerts".')
    product_expiry_alert=fields.Boolean(compute='_compute_product_expiry_alert',help="TheExpirationDatehasbeenreached.")
    product_expiry_reminded=fields.Boolean(string="Expiryhasbeenreminded")

    @api.depends('expiration_date')
    def_compute_product_expiry_alert(self):
        current_date=fields.Datetime.now()
        forlotinself:
            iflot.expiration_date:
                lot.product_expiry_alert=lot.expiration_date<=current_date
            else:
                lot.product_expiry_alert=False

    def_get_dates(self,product_id=None):
        """Returnsdatesbasedonnumberofdaysconfiguredincurrentlot'sproduct."""
        mapped_fields={
            'expiration_date':'expiration_time',
            'use_date':'use_time',
            'removal_date':'removal_time',
            'alert_date':'alert_time'
        }
        res=dict.fromkeys(mapped_fields,False)
        product=self.env['product.product'].browse(product_id)orself.product_id
        ifproduct:
            forfieldinmapped_fields:
                duration=getattr(product,mapped_fields[field])
                ifduration:
                    date=datetime.datetime.now()+datetime.timedelta(days=duration)
                    res[field]=fields.Datetime.to_string(date)
        returnres

    #Assigndatesaccordingtoproductsdata
    @api.model_create_multi
    defcreate(self,vals_list):
        forvalsinvals_list:
            dates=self._get_dates(vals.get('product_id')orself.env.context.get('default_product_id'))
            fordindates:
                ifnotvals.get(d):
                    vals[d]=dates[d]
        returnsuper().create(vals_list)

    @api.onchange('expiration_date')
    def_onchange_expiration_date(self):
        ifnotself._originornot(self.expiration_dateandself._origin.expiration_date):
            return
        time_delta=self.expiration_date-self._origin.expiration_date
        #Aswecompareexpiration_datewith_origin.expiration_date,weneedto
        #use`_get_date_values`with_origintokeepastabilityinthevalues.
        #Otherwiseitwillrecomputefromtheupdatedvaluesiftheusercalls
        #thisonchangemultipletimeswithoutsavebetweeneachonchange.
        vals=self._origin._get_date_values(time_delta,self.expiration_date)
        self.update(vals)

    @api.onchange('product_id')
    def_onchange_product(self):
        dates_dict=self._get_dates()
        forfield,valueindates_dict.items():
            setattr(self,field,value)

    @api.model
    def_alert_date_exceeded(self):
        """Loganactivityoninternallystoredlotswhosealert_datehasbeenreached.

        Nofurtheractivitywillbegeneratedonlotswhosealert_date
        hasalreadybeenreached(evenifthealert_dateischanged).
        """
        alert_lots=self.env['stock.production.lot'].search([
            ('alert_date','<=',fields.Date.today()),
            ('product_expiry_reminded','=',False)])

        lot_stock_quants=self.env['stock.quant'].search([
            ('lot_id','in',alert_lots.ids),
            ('quantity','>',0),
            ('location_id.usage','=','internal')])
        alert_lots=lot_stock_quants.mapped('lot_id')

        forlotinalert_lots:
            lot.activity_schedule(
                'product_expiry.mail_activity_type_alert_date_reached',
                user_id=lot.product_id.with_company(lot.company_id).responsible_id.idorlot.product_id.responsible_id.idorSUPERUSER_ID,
                note=_("Thealertdatehasbeenreachedforthislot/serialnumber")
            )
        alert_lots.write({
            'product_expiry_reminded':True
        })

    def_update_date_values(self,new_date):
        ifnew_date:
            time_delta=new_date-(self.expiration_dateorfields.Datetime.now())
            vals=self._get_date_values(time_delta,new_date)
            vals['expiration_date']=new_date
            self.write(vals)

    def_get_date_values(self,time_delta,new_date=False):
        '''Returnadictwithdifferentdatevaluesupdateddependingofthe
        time_delta.Usedintheonchangeof`expiration_date`andwhenuser
        definesadateatthereceipt.'''
        vals={
            'use_date':self.use_dateand(self.use_date+time_delta)ornew_date,
            'removal_date':self.removal_dateand(self.removal_date+time_delta)ornew_date,
            'alert_date':self.alert_dateand(self.alert_date+time_delta)ornew_date,
        }
        returnvals


classProcurementGroup(models.Model):
    _inherit='procurement.group'

    @api.model
    def_run_scheduler_tasks(self,use_new_cursor=False,company_id=False):
        super(ProcurementGroup,self)._run_scheduler_tasks(use_new_cursor=use_new_cursor,company_id=company_id)
        self.env['stock.production.lot']._alert_date_exceeded()
        ifuse_new_cursor:
            self.env.cr.commit()
