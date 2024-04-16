#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importpsycopg2

fromflectraimportapi,fields,models,registry,SUPERUSER_ID,_

_logger=logging.getLogger(__name__)


classDeliveryCarrier(models.Model):
    _name='delivery.carrier'
    _description="ShippingMethods"
    _order='sequence,id'

    '''AShippingProvider

    Inordertoaddyourownexternalprovider,followthesesteps:

    1.CreateyourmodelMyProviderthat_inherit'delivery.carrier'
    2.Extendtheselectionofthefield"delivery_type"withapair
       ('<my_provider>','MyProvider')
    3.Addyourmethods:
       <my_provider>_rate_shipment
       <my_provider>_send_shipping
       <my_provider>_get_tracking_link
       <my_provider>_cancel_shipment
       _<my_provider>_get_default_custom_package_code
       (theyaredocumentedhereunder)
    '''

    #--------------------------------#
    #Internalsforshippingproviders#
    #--------------------------------#

    name=fields.Char('DeliveryMethod',required=True,translate=True)
    active=fields.Boolean(default=True)
    sequence=fields.Integer(help="Determinethedisplayorder",default=10)
    #Thisfieldwillbeoverwrittenbyinternalshippingprovidersbyaddingtheirowntype(ex:'fedex')
    delivery_type=fields.Selection([('fixed','FixedPrice')],string='Provider',default='fixed',required=True)
    integration_level=fields.Selection([('rate','GetRate'),('rate_and_ship','GetRateandCreateShipment')],string="IntegrationLevel",default='rate_and_ship',help="ActionwhilevalidatingDeliveryOrders")
    prod_environment=fields.Boolean("Environment",help="SettoTrueifyourcredentialsarecertifiedforproduction.")
    debug_logging=fields.Boolean('Debuglogging',help="Logrequestsinordertoeasedebugging")
    company_id=fields.Many2one('res.company',string='Company',related='product_id.company_id',store=True,readonly=False)
    product_id=fields.Many2one('product.product',string='DeliveryProduct',required=True,ondelete='restrict')

    invoice_policy=fields.Selection([
        ('estimated','Estimatedcost'),
        ('real','Realcost')
    ],string='InvoicingPolicy',default='estimated',required=True,
    help="EstimatedCost:thecustomerwillbeinvoicedtheestimatedcostoftheshipping.\nRealCost:thecustomerwillbeinvoicedtherealcostoftheshipping,thecostoftheshippingwillbeupdatedontheSOafterthedelivery.")

    country_ids=fields.Many2many('res.country','delivery_carrier_country_rel','carrier_id','country_id','Countries')
    state_ids=fields.Many2many('res.country.state','delivery_carrier_state_rel','carrier_id','state_id','States')
    zip_from=fields.Char('ZipFrom')
    zip_to=fields.Char('ZipTo')

    margin=fields.Float(help='Thispercentagewillbeaddedtotheshippingprice.')
    free_over=fields.Boolean('Freeiforderamountisabove',help="Iftheordertotalamount(shippingexcluded)isaboveorequaltothisvalue,thecustomerbenefitsfromafreeshipping",default=False)
    amount=fields.Float(string='Amount',help="Amountoftheordertobenefitfromafreeshipping,expressedinthecompanycurrency")

    can_generate_return=fields.Boolean(compute="_compute_can_generate_return")
    return_label_on_delivery=fields.Boolean(string="GenerateReturnLabel",help="Thereturnlabelisautomaticallygeneratedatthedelivery.")
    get_return_label_from_portal=fields.Boolean(string="ReturnLabelAccessiblefromCustomerPortal",help="Thereturnlabelcanbedownloadedbythecustomerfromthecustomerportal.")

    _sql_constraints=[
        ('margin_not_under_100_percent','CHECK(margin>=-100)','Margincannotbelowerthan-100%'),
    ]

    @api.depends('delivery_type')
    def_compute_can_generate_return(self):
        forcarrierinself:
            carrier.can_generate_return=False

    deftoggle_prod_environment(self):
        forcinself:
            c.prod_environment=notc.prod_environment

    deftoggle_debug(self):
        forcinself:
            c.debug_logging=notc.debug_logging

    definstall_more_provider(self):
        return{
            'name':'NewProviders',
            'view_mode':'kanban,form',
            'res_model':'ir.module.module',
            'domain':[['name','=like','delivery_%'],['name','!=','delivery_barcode']],
            'type':'ir.actions.act_window',
            'help':_('''<pclass="o_view_nocontent">
                    BuyFlectraEnterprisenowtogetmoreproviders.
                </p>'''),
        }

    defavailable_carriers(self,partner):
        returnself.filtered(lambdac:c._match_address(partner))

    def_match_address(self,partner):
        self.ensure_one()
        ifself.country_idsandpartner.country_idnotinself.country_ids:
            returnFalse
        ifself.state_idsandpartner.state_idnotinself.state_ids:
            returnFalse
        ifself.zip_fromand(partner.zipor'').upper()<self.zip_from.upper():
            returnFalse
        ifself.zip_toand(partner.zipor'').upper()>self.zip_to.upper():
            returnFalse
        returnTrue

    @api.onchange('integration_level')
    def_onchange_integration_level(self):
        ifself.integration_level=='rate':
            self.invoice_policy='estimated'

    @api.onchange('can_generate_return')
    def_onchange_can_generate_return(self):
        ifnotself.can_generate_return:
            self.return_label_on_delivery=False

    @api.onchange('return_label_on_delivery')
    def_onchange_return_label_on_delivery(self):
        ifnotself.return_label_on_delivery:
            self.get_return_label_from_portal=False

    @api.onchange('state_ids')
    defonchange_states(self):
        self.country_ids=[(6,0,self.country_ids.ids+self.state_ids.mapped('country_id.id'))]

    @api.onchange('country_ids')
    defonchange_countries(self):
        self.state_ids=[(6,0,self.state_ids.filtered(lambdastate:state.idinself.country_ids.mapped('state_ids').ids).ids)]

    def_get_delivery_type(self):
        """Returnthedeliverytype.

        Thismethodneedstobeoverriddenbyadeliverycarriermoduleifthedeliverytypeisnot
        storedonthefield`delivery_type`.
        """
        self.ensure_one()
        returnself.delivery_type
        
    #--------------------------#
    #APIforexternalproviders#
    #--------------------------#

    defrate_shipment(self,order):
        '''Computethepriceoftheordershipment

        :paramorder:recordofsale.order
        :returndict:{'success':boolean,
                       'price':afloat,
                       'error_message':astringcontaininganerrormessage,
                       'warning_message':astringcontainingawarningmessage}
                       #TODOmaybethecurrencycode?
        '''
        self.ensure_one()
        ifhasattr(self,'%s_rate_shipment'%self.delivery_type):
            res=getattr(self,'%s_rate_shipment'%self.delivery_type)(order)
            #applyfiscalposition
            company=self.company_idororder.company_idorself.env.company
            res['price']=self.product_id._get_tax_included_unit_price(
                company,
                company.currency_id,
                order.date_order,
                'sale',
                fiscal_position=order.fiscal_position_id,
                product_price_unit=res['price'],
                product_currency=company.currency_id
            )
            #applymarginoncomputedprice
            res['price']=float(res['price'])*(1.0+(self.margin/100.0))
            #savetherealpriceincaseafree_overruleoverideitto0
            res['carrier_price']=res['price']
            #freewhenorderislargeenough
            ifres['success']andself.free_overandorder._compute_amount_total_without_delivery()>=self.amount:
                res['warning_message']=_('Theshippingisfreesincetheorderamountexceeds%.2f.')%(self.amount)
                res['price']=0.0
            returnres

    defsend_shipping(self,pickings):
        '''Sendthepackagetotheserviceprovider

        :parampickings:Arecordsetofpickings
        :returnlist:Alistofdictionaries(oneperpicking)containingoftheform::
                         {'exact_price':price,
                           'tracking_number':number}
                           #TODOmissinglabelsperpackage
                           #TODOmissingcurrency
                           #TODOmissingsuccess,error,warnings
        '''
        self.ensure_one()
        ifhasattr(self,'%s_send_shipping'%self.delivery_type):
            returngetattr(self,'%s_send_shipping'%self.delivery_type)(pickings)

    defget_return_label(self,pickings,tracking_number=None,origin_date=None):
        self.ensure_one()
        ifself.can_generate_return:
            res=getattr(self,'%s_get_return_label'%self.delivery_type)(pickings,tracking_number,origin_date)
            ifself.get_return_label_from_portal:
                pickings.return_label_ids.generate_access_token()
            returnres

    defget_return_label_prefix(self):
        return'ReturnLabel-%s'%self.delivery_type

    defget_tracking_link(self,picking):
        '''Askthetrackinglinktotheserviceprovider

        :parampicking:recordofstock.picking
        :returnstr:anURLcontainingthetrackinglinkorFalse
        '''
        self.ensure_one()
        ifhasattr(self,'%s_get_tracking_link'%self.delivery_type):
            returngetattr(self,'%s_get_tracking_link'%self.delivery_type)(picking)

    defcancel_shipment(self,pickings):
        '''Cancelashipment

        :parampickings:Arecordsetofpickings
        '''
        self.ensure_one()
        ifhasattr(self,'%s_cancel_shipment'%self.delivery_type):
            returngetattr(self,'%s_cancel_shipment'%self.delivery_type)(pickings)

    deflog_xml(self,xml_string,func):
        self.ensure_one()

        ifself.debug_logging:
            self.flush()
            db_name=self._cr.dbname

            #Useanewcursortoavoidrollbackthatcouldbecausedbyanuppermethod
            try:
                db_registry=registry(db_name)
                withdb_registry.cursor()ascr:
                    env=api.Environment(cr,SUPERUSER_ID,{})
                    IrLogging=env['ir.logging']
                    IrLogging.sudo().create({'name':'delivery.carrier',
                              'type':'server',
                              'dbname':db_name,
                              'level':'DEBUG',
                              'message':xml_string,
                              'path':self.delivery_type,
                              'func':func,
                              'line':1})
            exceptpsycopg2.Error:
                pass

    def_get_default_custom_package_code(self):
        """Somedeliverycarriersrequireaprefixtobesentinordertousecustom
        packages(ienotofficialones).Thisoptionalmethodwillreturnitasastring.
        """
        self.ensure_one()
        ifhasattr(self,'_%s_get_default_custom_package_code'%self.delivery_type):
            returngetattr(self,'_%s_get_default_custom_package_code'%self.delivery_type)()
        else:
            returnFalse

    #------------------------------------------------#
    #Fixedpriceshipping,akaaverysimpleprovider#
    #------------------------------------------------#

    fixed_price=fields.Float(compute='_compute_fixed_price',inverse='_set_product_fixed_price',store=True,string='FixedPrice')

    @api.depends('product_id.list_price','product_id.product_tmpl_id.list_price')
    def_compute_fixed_price(self):
        forcarrierinself:
            carrier.fixed_price=carrier.product_id.list_price

    def_set_product_fixed_price(self):
        forcarrierinself:
            carrier.product_id.list_price=carrier.fixed_price

    deffixed_rate_shipment(self,order):
        carrier=self._match_address(order.partner_shipping_id)
        ifnotcarrier:
            return{'success':False,
                    'price':0.0,
                    'error_message':_('Error:thisdeliverymethodisnotavailableforthisaddress.'),
                    'warning_message':False}
        price=order.pricelist_id.get_product_price(self.product_id,1.0,order.partner_id)
        return{'success':True,
                'price':price,
                'error_message':False,
                'warning_message':False}

    deffixed_send_shipping(self,pickings):
        res=[]
        forpinpickings:
            res=res+[{'exact_price':p.carrier_id.fixed_price,
                          'tracking_number':False}]
        returnres

    deffixed_get_tracking_link(self,picking):
        returnFalse

    deffixed_cancel_shipment(self,pickings):
        raiseNotImplementedError()
