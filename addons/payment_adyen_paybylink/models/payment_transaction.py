#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportValidationError


_logger=logging.getLogger(__name__)


classPaymentTransaction(models.Model):
    _inherit='payment.transaction'

    @api.model
    defadyen_create(self,values):
        """
        Whenthecustomerlandsonthe`/payment/process`route,`/payment/process/poll`trytofind
        thetransactionwhose`date`fieldisbetweenyesterdayandnow.

        Sincethe`date`fieldisonlysetwhenthestateofthetransactionischanged,ifthe
        customercomesbackbeforethewebhook,hewillseea"transactionnotfound"pagebecause
        thevalueofthe`date`fieldwouldbe`False`.
        """
        returndict(date=fields.Datetime.now())

    #--------------------------------------------------
    #FORMRELATEDMETHODS
    #--------------------------------------------------

    @api.model
    def_adyen_form_get_tx_from_data(self,data):
        """Overrideof_adyen_form_get_tx_from_data"""
        reference,psp_reference=data.get('merchantReference'),data.get('pspReference')
        ifnotreferenceornotpsp_reference:
            error_msg=_(
                "Adyen:receiveddatawithmissingreference(%s)ormissingpspReference(%s)"
            )%(reference,psp_reference)
            _logger.info(error_msg)
            raiseValidationError(error_msg)

        tx=self.env['payment.transaction'].search([
            ('reference','=',reference),('provider','=','adyen')
        ])
        ifnottxorlen(tx)>1:
            error_msg=_("Adyen:receiveddataforreference%s")%reference
            ifnottx:
                error_msg+=_(";noorderfound")
            else:
                error_msg+=_(";multipleorderfound")
            _logger.info(error_msg)
            raiseValidationError(error_msg)

        returntx

    def_adyen_form_get_invalid_parameters(self,data):
        """Overrideof_adyen_form_get_invalid_parameterstodisablethismethod.

        Thepay-by-linkimplementationdoesn'tneedorwanttocheckforinvalidparameters.
        """
        return[]
