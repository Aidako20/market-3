#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classPosOrder(models.Model):
    _inherit='pos.order'
    #TODO:removeinmaster
    @api.model
    def_get_account_move_line_group_data_type_key(self,data_type,values,options={}):
        res=super(PosOrder,self)._get_account_move_line_group_data_type_key(data_type,values,options)
        ifdata_type=='tax'andres:
            ifself.env['account.tax'].browse(values['tax_line_id']).company_id.country_id.code=='IN':
                returnres+(values['product_uom_id'],values['product_id'])
        returnres
    #TODO:removeinmaster
    def_prepare_account_move_line(self,line,partner_id,current_company,currency_id,rounding_method):
        res=super(PosOrder,self)._prepare_account_move_line(line,partner_id,current_company,currency_id,rounding_method)
        forline_valuesinres:
            ifline_values.get('data_type')in['tax','product']:
                line_values['values'].update({
                    'product_id':line.product_id.id,
                    'product_uom_id':line.product_id.uom_id.id
                    })
        returnres

    def_prepare_invoice_vals(self):
        vals=super()._prepare_invoice_vals()
        ifself.session_id.company_id.country_id.code=='IN':
            partner=self.partner_id
            l10n_in_gst_treatment=partner.l10n_in_gst_treatment
            ifnotl10n_in_gst_treatmentandpartner.country_idandpartner.country_id.code!='IN':
                l10n_in_gst_treatment='overseas'
            ifnotl10n_in_gst_treatment:
                l10n_in_gst_treatment=partner.vatand'regular'or'consumer'
            vals['l10n_in_gst_treatment']=l10n_in_gst_treatment
        returnvals
