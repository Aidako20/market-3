"""ESC/POSExceptionsclasses"""


classError(Exception):
    """BaseclassforESC/POSerrors"""
    def__init__(self,msg,status=None):
        Exception.__init__(self)
        self.msg=msg
        self.resultcode=1
        ifstatusisnotNone:
            self.resultcode=status

    def__str__(self):
        returnself.msg

#Result/Exitcodes
#0 =success
#10=NoBarcodetypedefined
#20=Barcodesizevaluesareoutofrange
#30=Barcodetextnotsupplied
#40=Imageheightistoolarge
#50=Nostringsuppliedtobeprinted
#60=InvalidpintosendCashDrawerpulse


classBarcodeTypeError(Error):
    def__init__(self,msg=""):
        Error.__init__(self,msg)
        self.msg=msg
        self.resultcode=10

    def__str__(self):
        return"NoBarcodetypeisdefined"

classBarcodeSizeError(Error):
    def__init__(self,msg=""):
        Error.__init__(self,msg)
        self.msg=msg
        self.resultcode=20

    def__str__(self):
        return"Barcodesizeisoutofrange"

classBarcodeCodeError(Error):
    def__init__(self,msg=""):
        Error.__init__(self,msg)
        self.msg=msg
        self.resultcode=30

    def__str__(self):
        return"Codewasnotsupplied"

classImageSizeError(Error):
    def__init__(self,msg=""):
        Error.__init__(self,msg)
        self.msg=msg
        self.resultcode=40

    def__str__(self):
        return"Imageheightislongerthan255pxandcan'tbeprinted"

classTextError(Error):
    def__init__(self,msg=""):
        Error.__init__(self,msg)
        self.msg=msg
        self.resultcode=50

    def__str__(self):
        return"Textstringmustbesuppliedtothetext()method"


classCashDrawerError(Error):
    def__init__(self,msg=""):
        Error.__init__(self,msg)
        self.msg=msg
        self.resultcode=60

    def__str__(self):
        return"Validpinmustbesettosendpulse"

classNoStatusError(Error):
    def__init__(self,msg=""):
        Error.__init__(self,msg)
        self.msg=msg
        self.resultcode=70

    def__str__(self):
        return"Impossibletogetstatusfromtheprinter:"+str(self.msg)

classTicketNotPrinted(Error):
    def__init__(self,msg=""):
        Error.__init__(self,msg)
        self.msg=msg
        self.resultcode=80

    def__str__(self):
        return"Apartoftheticketwasnotbeenprinted:"+str(self.msg)

classNoDeviceError(Error):
    def__init__(self,msg=""):
        Error.__init__(self,msg)
        self.msg=msg
        self.resultcode=90

    def__str__(self):
        returnstr(self.msg)

classHandleDeviceError(Error):
    def__init__(self,msg=""):
        Error.__init__(self,msg)
        self.msg=msg
        self.resultcode=100

    def__str__(self):
        returnstr(self.msg)
