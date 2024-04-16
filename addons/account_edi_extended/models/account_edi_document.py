#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels,fields,_
importlogging

_logger=logging.getLogger(__name__)
DEFAULT_BLOCKING_LEVEL='warning' #Keeppreviousbehavior.TODO:whenaccount_edi_extendedismergedwithaccount_edi,shouldbe'error'(documentwillnotbeprocessedagainuntilforcedretryorresettodraft)


classAccountEdiDocument(models.Model):
    _inherit='account.edi.document'

    blocking_level=fields.Selection(selection=[('info','Info'),('warning','Warning'),('error','Error')],
                                     help="Blocksthedocumentcurrentoperationdependingontheerrorseverity:\n"
                                          " *Info:thedocumentisnotblockedandeverythingisworkingasitshould.\n"
                                          " *Warning:thereisanerrorthatdoesn'tpreventthecurrentElectronicInvoicingoperationtosucceed.\n"
                                          " *Error:thereisanerrorthatblocksthecurrentElectronicInvoicingoperation.")

