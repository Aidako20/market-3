#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classAccountMove(models.Model):
    _inherit="account.move"

    amount_total_words=fields.Char("Total(InWords)",compute="_compute_amount_total_words")
    l10n_in_gst_treatment=fields.Selection([
            ('regular','RegisteredBusiness-Regular'),
            ('composition','RegisteredBusiness-Composition'),
            ('unregistered','UnregisteredBusiness'),
            ('consumer','Consumer'),
            ('overseas','Overseas'),
            ('special_economic_zone','SpecialEconomicZone'),
            ('deemed_export','DeemedExport')
        ],string="GSTTreatment",compute="_compute_l10n_in_gst_treatment",store=True,readonly=False)
    l10n_in_state_id=fields.Many2one('res.country.state',string="Locationofsupply")
    l10n_in_company_country_code=fields.Char(related='company_id.country_id.code',string="Countrycode")
    l10n_in_gstin=fields.Char(string="GSTIN")
    #ForExportinvoicethisdataisneedinGSTRreport
    l10n_in_shipping_bill_number=fields.Char('Shippingbillnumber',readonly=True,states={'draft':[('readonly',False)]})
    l10n_in_shipping_bill_date=fields.Date('Shippingbilldate',readonly=True,states={'draft':[('readonly',False)]})
    l10n_in_shipping_port_code_id=fields.Many2one('l10n_in.port.code','Portcode',states={'draft':[('readonly',False)]})
    l10n_in_reseller_partner_id=fields.Many2one('res.partner','Reseller',domain=[('vat','!=',False)],help="OnlyRegisteredReseller",readonly=True,states={'draft':[('readonly',False)]})

    @api.depends('amount_total')
    def_compute_amount_total_words(self):
        forinvoiceinself:
            invoice.amount_total_words=invoice.currency_id.amount_to_text(invoice.amount_total)

    @api.depends('partner_id')
    def_compute_l10n_in_gst_treatment(self):
        forrecordinself:
            record.l10n_in_gst_treatment=record.partner_id.l10n_in_gst_treatment

    @api.model
    def_l10n_in_get_indian_state(self,partner):
        """Intaxreturnfiling,IfcustomerisnotIndianinthatcaseplaceofsupplyismustsettoOtherTerritory.
        SowesetOtherTerritoryinl10n_in_state_idwhencustomer(partner)isnotIndian
        AlsoweraiseifstateisnotsetinIndiancustomer.
        StateisbigroleunderGSTbecausetaxtypeisdependon.formoreinformationcheckthishttps://www.cbic.gov.in/resources//htdocs-cbec/gst/Integrated%20goods%20&%20Services.pdf"""
        ifpartner.country_idandpartner.country_id.code=='IN'andnotpartner.state_id:
            raiseValidationError(_("Stateismissingfromaddressin'%s'.Firstsetstateafterpostthisinvoiceagain.",partner.name))
        elifpartner.country_idandpartner.country_id.code!='IN':
            returnself.env.ref('l10n_in.state_in_ot')
        returnpartner.state_id


    @api.model
    def_get_tax_grouping_key_from_tax_line(self,tax_line):
        #OVERRIDEtogrouptaxesalsobyproduct.
        res=super()._get_tax_grouping_key_from_tax_line(tax_line)
        iftax_line.move_id.journal_id.company_id.country_id.code=='IN':
            res['product_id']=tax_line.product_id.id
            res['product_uom_id']=tax_line.product_uom_id.id
        returnres

    @api.model
    def_get_tax_grouping_key_from_base_line(self,base_line,tax_vals):
        #OVERRIDEtogrouptaxesalsobyproduct.
        res=super()._get_tax_grouping_key_from_base_line(base_line,tax_vals)
        ifbase_line.move_id.journal_id.company_id.country_id.code=='IN':
            res['product_id']=base_line.product_id.id
            res['product_uom_id']=base_line.product_uom_id.id
        returnres

    @api.model
    def_get_tax_key_for_group_add_base(self,line):
        #DEPRECATED:TOBEREMOVEDINMASTER
        tax_key=super(AccountMove,self)._get_tax_key_for_group_add_base(line)

        tax_key+=[
            line.product_id.id,
            line.product_uom_id.id,
        ]
        returntax_key

    def_l10n_in_get_shipping_partner(self):
        """Overwriteinsale"""
        self.ensure_one()
        returnself.partner_id

    @api.model
    def_l10n_in_get_shipping_partner_gstin(self,shipping_partner):
        """Overwriteinsale"""
        returnshipping_partner.vat

    def_post(self,soft=True):
        """UsejournaltypetodefinedocumenttypebecausenotmissstateinanyentryincludingPOSentry"""
        posted=super()._post(soft)
        gst_treatment_name_mapping={k:vfork,vin
                             self._fields['l10n_in_gst_treatment']._description_selection(self.env)}
        formoveinposted.filtered(lambdam:m.l10n_in_company_country_code=='IN'):
            """Checkstateissetincompany/sub-unit"""
            company_unit_partner=move.journal_id.l10n_in_gstin_partner_idormove.journal_id.company_id
            ifnotcompany_unit_partner.state_id:
                raiseValidationError(_(
                    "Stateismissingfromyourcompany/unit%(company_name)s(%(company_id)s).\nFirstsetstateinyourcompany/unit.",
                    company_name=company_unit_partner.name,
                    company_id=company_unit_partner.id
                ))
            elifmove.journal_id.type=='purchase':
                move.l10n_in_state_id=company_unit_partner.state_id

            shipping_partner=move._l10n_in_get_shipping_partner()
            #IncaseofshippingaddressdoesnothaveGSTNthenalsocheckcustomer(partner_id)GSTN
            #ThishappenswhenBill-toShip-totransactionwhereshipping(Ship-to)addressisunregisteredandcustomer(Bill-to)isregistred.
            move.l10n_in_gstin=move._l10n_in_get_shipping_partner_gstin(shipping_partner)ormove.partner_id.vat
            ifnotmove.l10n_in_gstinandmove.l10n_in_gst_treatmentin['regular','composition','special_economic_zone','deemed_export']:
                raiseValidationError(_(
                    "Partner%(partner_name)s(%(partner_id)s)GSTINisrequiredunderGSTTreatment%(name)s",
                    partner_name=shipping_partner.name,
                    partner_id=shipping_partner.id,
                    name=gst_treatment_name_mapping.get(move.l10n_in_gst_treatment)
                ))
            ifmove.journal_id.type=='sale':
                move.l10n_in_state_id=self._l10n_in_get_indian_state(shipping_partner)
                ifnotmove.l10n_in_state_id:
                    move.l10n_in_state_id=self._l10n_in_get_indian_state(move.partner_id)
                #stillstateisnotsetthenassumedthattransactionislocallikePoSsosetstateofcompanyunit
                ifnotmove.l10n_in_state_id:
                    move.l10n_in_state_id=company_unit_partner.state_id
        returnposted
