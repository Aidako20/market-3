#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
#Copyright(C)2004-2008PCSolutions(<http://pcsol.be>).AllRightsReserved
fromflectraimportfields,models,api,_
fromflectra.exceptionsimportUserError


classAccountBankStatement(models.Model):
    _inherit='account.bank.statement'

    pos_session_id=fields.Many2one('pos.session',string="Session",copy=False)
    account_id=fields.Many2one('account.account',related='journal_id.default_account_id',readonly=True)

    defbutton_validate_or_action(self):
        #OVERRIDEtochecktheconsistencyofthestatement'sstateregardingthesession'sstate.
        forstatementinself:
            ifstatement.pos_session_id.state in('opened','closing_control')andstatement.state=='open':
                raiseUserError(_("Youcan'tvalidateabankstatementthatisusedinanopenedSessionofaPointofSale."))
        returnsuper(AccountBankStatement,self).button_validate_or_action()

    defunlink(self):
        forbsinself:
            ifbs.pos_session_id:
                raiseUserError(_("YoucannotdeleteabankstatementlinkedtoPointofSalesession."))
        returnsuper(AccountBankStatement,self).unlink()

classAccountBankStatementLine(models.Model):
    _inherit='account.bank.statement.line'

    pos_statement_id=fields.Many2one('pos.order',string="POSstatement",ondelete='cascade')
