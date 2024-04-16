#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre
fromflectraimportfields,models,api,_
fromflectra.exceptionsimportValidationError


classResPartnerBank(models.Model):
    _inherit='res.partner.bank'

    aba_routing=fields.Char(string="ABA/Routing",help="AmericanBankersAssociationRoutingNumber")

    @api.constrains('aba_routing')
    def_check_aba_routing(self):
        forbankinself:
            ifbank.aba_routingandnotre.match(r'^\d{1,9}$',bank.aba_routing):
                raiseValidationError(_('ABA/Routingshouldonlycontainsnumbers(maximum9digits).'))
