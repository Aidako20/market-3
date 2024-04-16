#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importsys


classExceptionLogger:
    """
    RedirectExceptionstotheloggertokeeptrackoftheminthelogfile.
    """

    def__init__(self):
        self.logger=logging.getLogger()

    defwrite(self,message):
        ifmessage!='\n':
            self.logger.error(message)

    defflush(self):
        pass

sys.stderr=ExceptionLogger()
