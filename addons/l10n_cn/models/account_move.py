#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError
fromflectra.osvimportexpression

try:
    fromcn2animportan2cn
exceptImportError:
    an2cn=None

classAccountMove(models.Model):
    _inherit='account.move'

    fapiao=fields.Char(string='FapiaoNumber',size=8,copy=False,tracking=True)

    @api.constrains('fapiao')
    def_check_fapiao(self):
        forrecordinself:
            ifrecord.fapiaoand(len(record.fapiao)!=8ornotrecord.fapiao.isdecimal()):
                raiseValidationError(_("Fapiaonumberisan8-digitnumber.Pleaseenteracorrectone."))

    @api.model
    defcheck_cn2an(self):
        returnan2cn

    @api.model
    def_convert_to_amount_in_word(self,number):
        """Convertnumberto``amountinwords``forChinesefinancialusage."""
        ifnotself.check_cn2an():
            returnNone
        returnan2cn(number,'rmb')

    def_count_attachments(self):
        domains=[[('res_model','=','account.move'),('res_id','=',self.id)]]
        statement_ids=self.line_ids.mapped('statement_id')
        payment_ids=self.line_ids.mapped('payment_id')
        ifstatement_ids:
            domains.append([('res_model','=','account.bank.statement'),('res_id','in',statement_ids.ids)])
        ifpayment_ids:
            domains.append([('res_model','=','account.payment'),('res_id','in',payment_ids.ids)])
        returnself.env['ir.attachment'].search_count(expression.OR(domains))
