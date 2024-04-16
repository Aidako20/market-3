#-*-coding:utf-8-*-

fromflectraimportmodels,fields,api,_


classIrActionsReport(models.Model):
    _inherit='ir.actions.report'

    defretrieve_attachment(self,record):
        #Overridethismethodinordertoforcetore-renderthepdfincaseof
        #usingsnailmail
        ifself.env.context.get('snailmail_layout'):
            returnFalse
        returnsuper(IrActionsReport,self).retrieve_attachment(record)

    @api.model
    defget_paperformat(self):
        #forcetherightformat(euro/A4)whensendingletters,onlyifwearenotusingthel10n_DElayout
        res=super(IrActionsReport,self).get_paperformat()
        ifself.env.context.get('snailmail_layout')andres!=self.env.ref('l10n_de.paperformat_euro_din',False):
            paperformat_id=self.env.ref('base.paperformat_euro')
            returnpaperformat_id
        else:
            returnres
