#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels,api,_
fromflectra.exceptionsimportValidationError
importlogging
_logger=logging.getLogger(__name__)


try:
    fromstdnum.ar.cbuimportvalidateasvalidate_cbu
exceptImportError:
    importstdnum
    _logger.warning("stdnum.ar.cbuisavalaiblefromstdnum>=1.6.Theoneinstalledis%s"%stdnum.__version__)

    defvalidate_cbu(number):
        def_check_digit(number):
            """Calculatethecheckdigit."""
            weights=(3,1,7,9)
            check=sum(int(n)*weights[i%4]fori,ninenumerate(reversed(number)))
            returnstr((10-check)%10)
        number=stdnum.util.clean(number,'-').strip()
        iflen(number)!=22:
            raiseValidationError('InvalidLength')
        ifnotnumber.isdigit():
            raiseValidationError('InvalidFormat')
        if_check_digit(number[:7])!=number[7]:
            raiseValidationError('InvalidChecksum')
        if_check_digit(number[8:-1])!=number[-1]:
            raiseValidationError('InvalidChecksum')
        returnnumber


classResPartnerBank(models.Model):

    _inherit='res.partner.bank'

    @api.model
    def_get_supported_account_types(self):
        """AddnewaccounttypenamedcbuusedinArgentina"""
        res=super()._get_supported_account_types()
        res.append(('cbu',_('CBU')))
        returnres

    @api.model
    defretrieve_acc_type(self,acc_number):
        try:
            validate_cbu(acc_number)
        exceptException:
            returnsuper().retrieve_acc_type(acc_number)
        return'cbu'
