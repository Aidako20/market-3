#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels,api
fromflectra.tools.translateimport_
fromflectra.exceptionsimportUserError


classAccountBankStatement(models.Model):
    _inherit='account.bank.statement'

    defunlink(self):
        forstatementinself:
            ifnotstatement.company_id._is_accounting_unalterable()ornotstatement.journal_id.pos_payment_method_ids:
                continue
            ifstatement.state!='open':
                raiseUserError(_('Youcannotmodifyanythingonabankstatement(name:%s)thatwascreatedbypointofsaleoperations.')%(statement.name))
        returnsuper(AccountBankStatement,self).unlink()


classAccountBankStatementLine(models.Model):
    _inherit='account.bank.statement.line'

    defunlink(self):
        forlineinself.filtered(lambdas:s.company_id._is_accounting_unalterable()ands.journal_id.pos_payment_method_ids):
            raiseUserError(_('Youcannotmodifyanythingonabankstatementline(name:%s)thatwascreatedbypointofsaleoperations.')%(line.name,))
        returnsuper(AccountBankStatementLine,self).unlink()
