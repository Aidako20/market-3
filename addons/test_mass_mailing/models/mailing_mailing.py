#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimportmodels

_logger=logging.getLogger(__name__)


classMailing(models.Model):
    _inherit='mailing.mailing'

    def_get_opt_out_list(self):
        """Returnsasetofemailsopted-outintargetmodel"""
        self.ensure_one()
        ifself.mailing_model_real=='mailing.test.optout':
            res_ids=self._get_recipients()
            opt_out_contacts=set(self.env['mailing.test.optout'].search([
                ('id','in',res_ids),
                ('opt_out','=',True)
            ]).mapped('email_normalized'))
            _logger.info(
                "Mass-mailing%stargets%s,optout:%semails",
                self,self.mailing_model_real,len(opt_out_contacts))
            returnopt_out_contacts
        returnsuper(Mailing,self)._get_opt_out_list()
