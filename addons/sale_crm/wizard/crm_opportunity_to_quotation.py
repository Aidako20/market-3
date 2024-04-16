#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classOpportunity2Quotation(models.TransientModel):
    _name='crm.quotation.partner'
    _description='CreateneworuseexistingCustomeronnewQuotation'

    @api.model
    defdefault_get(self,fields):
        result=super(Opportunity2Quotation,self).default_get(fields)

        active_model=self._context.get('active_model')
        ifactive_model!='crm.lead':
            raiseUserError(_('Youcanonlyapplythisactionfromalead.'))

        lead=False
        ifresult.get('lead_id'):
            lead=self.env['crm.lead'].browse(result['lead_id'])
        elif'lead_id'infieldsandself._context.get('active_id'):
            lead=self.env['crm.lead'].browse(self._context['active_id'])
        iflead:
            result['lead_id']=lead.id
            partner_id=result.get('partner_id')orlead._find_matching_partner().id
            if'action'infieldsandnotresult.get('action'):
                result['action']='exist'ifpartner_idelse'create'
            if'partner_id'infieldsandnotresult.get('partner_id'):
                result['partner_id']=partner_id

        returnresult

    action=fields.Selection([
        ('create','Createanewcustomer'),
        ('exist','Linktoanexistingcustomer'),
        ('nothing','Donotlinktoacustomer')
    ],string='QuotationCustomer',required=True)
    lead_id=fields.Many2one('crm.lead',"AssociatedLead",required=True)
    partner_id=fields.Many2one('res.partner','Customer')

    defaction_apply(self):
        """Convertleadtoopportunityormergeleadandopportunityandopen
            thefreshlycreatedopportunityview.
        """
        self.ensure_one()
        ifself.action=='create':
            self.lead_id.handle_partner_assignment(create_missing=True)
        elifself.action=='exist':
            self.lead_id.handle_partner_assignment(force_partner_id=self.partner_id.id,create_missing=False)
        returnself.lead_id.action_new_quotation()
