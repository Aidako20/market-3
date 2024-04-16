#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api,_
fromflectra.addons.l10n_ch.models.res_bankimport_is_l10n_ch_postal

classAccountBankStatementLine(models.Model):

    _inherit="account.bank.statement.line"

    def_find_or_create_bank_account(self):
        ifself.company_id.country_id.codein('CH','LI')and_is_l10n_ch_postal(self.account_number):
            bank_account=self.env['res.partner.bank'].search(
                [('company_id','=',self.company_id.id),
                 ('sanitized_acc_number','like',self.account_number+'%'),
                 ('partner_id','=',self.partner_id.id)])
            ifnotbank_account:
                bank_account=self.env['res.partner.bank'].create({
                    'company_id':self.company_id.id,
                    'acc_number':self.account_number+""+self.partner_id.name,
                    'partner_id':self.partner_id.id
                })
            returnbank_account
        else:
            super(AccountBankStatementLine,self)._find_or_create_bank_account()