#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

from__future__importprint_function
importlogging
importmath
importos
importos.path
importsubprocess
importtime
importnetifacesasni
importtraceback

try:
    from..escposimport*
    from..escpos.exceptionsimport*
    from..escpos.printerimportUsb
exceptImportError:
    escpos=printer=None

fromqueueimportQueue
fromthreadingimportThread,Lock

try:
    importusb.core
exceptImportError:
    usb=None

fromflectraimporthttp,_
fromflectra.addons.hw_drivers.controllersimportproxy

_logger=logging.getLogger(__name__)

#workaroundhttps://bugs.launchpad.net/openobject-server/+bug/947231
#relatedtohttp://bugs.python.org/issue7980
fromdatetimeimportdatetime
datetime.strptime('2012-01-01','%Y-%m-%d')

classEscposDriver(Thread):
    def__init__(self):
        Thread.__init__(self)
        self.queue=Queue()
        self.lock =Lock()
        self.status={'status':'connecting','messages':[]}

    defconnected_usb_devices(self):
        connected=[]

        #printerscaneitherdefinebDeviceClass=7,ortheycandefineoneof
        #theirinterfaceswithbInterfaceClass=7.Thisclasschecksforboth.
        classFindUsbClass(object):
            def__init__(self,usb_class):
                self._class=usb_class
            def__call__(self,device):
                #first,let'scheckthedevice
                ifdevice.bDeviceClass==self._class:
                    returnTrue
                #transversealldevicesandlookthroughtheirinterfacesto
                #findamatchingclass
                forcfgindevice:
                    intf=usb.util.find_descriptor(cfg,bInterfaceClass=self._class)

                    ifintfisnotNone:
                        returnTrue

                returnFalse

        printers=usb.core.find(find_all=True,custom_match=FindUsbClass(7))

        #ifnoprintersarefoundafterthisstepwewilltakethe
        #firstepsonorstardevicewecanfind.
        #epson
        ifnotprinters:
            printers=usb.core.find(find_all=True,idVendor=0x04b8)
        #star
        ifnotprinters:
            printers=usb.core.find(find_all=True,idVendor=0x0519)

        forprinterinprinters:
            try:
                description=usb.util.get_string(printer,printer.iManufacturer)+""+usb.util.get_string(printer,printer.iProduct)
            exceptExceptionase:
                _logger.error("Cannotgetprinterdescription:%s"%e)
                description='Unknownprinter'
            connected.append({
                'vendor':printer.idVendor,
                'product':printer.idProduct,
                'name':description
            })

        returnconnected

    deflockedstart(self):
        withself.lock:
            ifnotself.is_alive():
                self.daemon=True
                self.start()
    
    defget_escpos_printer(self):
  
        printers=self.connected_usb_devices()
        iflen(printers)>0:
            try:
                print_dev=Usb(printers[0]['vendor'],printers[0]['product'])
            exceptHandleDeviceError:
                #EscposprintersarenowintegratedtoPrinterDriver,iftheIoTBoxisprinting
                #throughCupsatthesametime,wegetanUSBError(16,'Resourcebusy').Thismeans
                #thattheFlectrainstanceconnectedtothisIoTBoxisuptodateandnolongeruses
                #thisescposlibrary.
                returnNone
            self.set_status(
                'connected',
                "Connectedto%s(in=0x%02x,out=0x%02x)"%(printers[0]['name'],print_dev.in_ep,print_dev.out_ep)
            )
            returnprint_dev
        else:
            self.set_status('disconnected','PrinterNotFound')
            returnNone

    defget_status(self):
        self.push_task('status')
        returnself.status

    defopen_cashbox(self,printer):
        printer.cashdraw(2)
        printer.cashdraw(5)

    defset_status(self,status,message=None):
        _logger.info(status+':'+(messageor'nomessage'))
        ifstatus==self.status['status']:
            ifmessage!=Noneand(len(self.status['messages'])==0ormessage!=self.status['messages'][-1]):
                self.status['messages'].append(message)
        else:
            self.status['status']=status
            ifmessage:
                self.status['messages']=[message]
            else:
                self.status['messages']=[]

        ifstatus=='error'andmessage:
            _logger.error('ESC/POSError:%s',message)
        elifstatus=='disconnected'andmessage:
            _logger.warning('ESC/POSDeviceDisconnected:%s',message)

    defrun(self):
        printer=None
        ifnotescpos:
            _logger.error('ESC/POScannotinitialize,pleaseverifysystemdependencies.')
            return
        whileTrue:
            try:
                error=True
                timestamp,task,data=self.queue.get(True)

                printer=self.get_escpos_printer()

                ifprinter==None:
                    iftask!='status':
                        self.queue.put((timestamp,task,data))
                    error=False
                    time.sleep(5)
                    continue
                eliftask=='receipt':
                    iftimestamp>=time.time()-1*60*60:
                        self.print_receipt_body(printer,data)
                        printer.cut()
                eliftask=='xml_receipt':
                    iftimestamp>=time.time()-1*60*60:
                        printer.receipt(data)
                eliftask=='cashbox':
                    iftimestamp>=time.time()-12:
                        self.open_cashbox(printer)
                eliftask=='status':
                    pass
                error=False

            exceptNoDeviceErrorase:
                print("Nodevicefound%s"%e)
            exceptHandleDeviceErrorase:
                printer=None
                print("Impossibletohandlethedeviceduetopreviouserror%s"%e)
            exceptTicketNotPrintedase:
                print("Theticketdoesnotseemstohavebeenfullyprinted%s"%e)
            exceptNoStatusErrorase:
                print("Impossibletogetthestatusoftheprinter%s"%e)
            exceptExceptionase:
                self.set_status('error')
                _logger.exception(e)
            finally:
                iferror:
                    self.queue.put((timestamp,task,data))
                ifprinter:
                    printer.close()
                    printer=None

    defpush_task(self,task,data=None):
        self.lockedstart()
        self.queue.put((time.time(),task,data))

    defprint_receipt_body(self,eprint,receipt):

        defcheck(string):
            returnstring!=Trueandbool(string)andstring.strip()
        
        defprice(amount):
            return("{0:."+str(receipt['precision']['price'])+"f}").format(amount)
        
        defmoney(amount):
            return("{0:."+str(receipt['precision']['money'])+"f}").format(amount)

        defquantity(amount):
            ifmath.floor(amount)!=amount:
                return("{0:."+str(receipt['precision']['quantity'])+"f}").format(amount)
            else:
                returnstr(amount)

        defprintline(left,right='',width=40,ratio=0.5,indent=0):
            lwidth=int(width*ratio)
            rwidth=width-lwidth
            lwidth=lwidth-indent
            
            left=left[:lwidth]
            iflen(left)!=lwidth:
                left=left+''*(lwidth-len(left))

            right=right[-rwidth:]
            iflen(right)!=rwidth:
                right=''*(rwidth-len(right))+right

            return''*indent+left+right+'\n'
        
        defprint_taxes():
            taxes=receipt['tax_details']
            fortaxintaxes:
                eprint.text(printline(tax['tax']['name'],price(tax['amount']),width=40,ratio=0.6))

        #ReceiptHeader
        ifreceipt['company']['logo']:
            eprint.set(align='center')
            eprint.print_base64_image(receipt['company']['logo'])
            eprint.text('\n')
        else:
            eprint.set(align='center',type='b',height=2,width=2)
            eprint.text(receipt['company']['name']+'\n')

        eprint.set(align='center',type='b')
        ifcheck(receipt['company']['contact_address']):
            eprint.text(receipt['company']['contact_address']+'\n')
        ifcheck(receipt['company']['phone']):
            eprint.text('Tel:'+receipt['company']['phone']+'\n')
        ifcheck(receipt['company']['vat']):
            eprint.text('VAT:'+receipt['company']['vat']+'\n')
        ifcheck(receipt['company']['email']):
            eprint.text(receipt['company']['email']+'\n')
        ifcheck(receipt['company']['website']):
            eprint.text(receipt['company']['website']+'\n')
        ifcheck(receipt['header']):
            eprint.text(receipt['header']+'\n')
        ifcheck(receipt['cashier']):
            eprint.text('-'*32+'\n')
            eprint.text('Servedby'+receipt['cashier']+'\n')

        #Orderlines
        eprint.text('\n\n')
        eprint.set(align='center')
        forlineinreceipt['orderlines']:
            pricestr=price(line['price_display'])
            ifline['discount']==0andline['unit_name']=='Units'andline['quantity']==1:
                eprint.text(printline(line['product_name'],pricestr,ratio=0.6))
            else:
                eprint.text(printline(line['product_name'],ratio=0.6))
                ifline['discount']!=0:
                    eprint.text(printline('Discount:'+str(line['discount'])+'%',ratio=0.6,indent=2))
                ifline['unit_name']=='Units':
                    eprint.text(printline(quantity(line['quantity'])+'x'+price(line['price']),pricestr,ratio=0.6,indent=2))
                else:
                    eprint.text(printline(quantity(line['quantity'])+line['unit_name']+'x'+price(line['price']),pricestr,ratio=0.6,indent=2))

        #Subtotalifthetaxesarenotincluded
        taxincluded=True
        ifmoney(receipt['subtotal'])!=money(receipt['total_with_tax']):
            eprint.text(printline('','-------'));
            eprint.text(printline(_('Subtotal'),money(receipt['subtotal']),width=40,ratio=0.6))
            print_taxes()
            #eprint.text(printline(_('Taxes'),money(receipt['total_tax']),width=40,ratio=0.6))
            taxincluded=False


        #Total
        eprint.text(printline('','-------'));
        eprint.set(align='center',height=2)
        eprint.text(printline(_('        TOTAL'),money(receipt['total_with_tax']),width=40,ratio=0.6))
        eprint.text('\n\n');
        
        #Paymentlines
        eprint.set(align='center')
        forlineinreceipt['paymentlines']:
            eprint.text(printline(line['journal'],money(line['amount']),ratio=0.6))

        eprint.text('\n');
        eprint.set(align='center',height=2)
        eprint.text(printline(_('       CHANGE'),money(receipt['change']),width=40,ratio=0.6))
        eprint.set(align='center')
        eprint.text('\n');

        #ExtraPaymentinfo
        ifreceipt['total_discount']!=0:
            eprint.text(printline(_('Discounts'),money(receipt['total_discount']),width=40,ratio=0.6))
        iftaxincluded:
            print_taxes()
            #eprint.text(printline(_('Taxes'),money(receipt['total_tax']),width=40,ratio=0.6))

        #Footer
        ifcheck(receipt['footer']):
            eprint.text('\n'+receipt['footer']+'\n\n')
        eprint.text(receipt['name']+'\n')
        eprint.text(     str(receipt['date']['date']).zfill(2)
                    +'/'+str(receipt['date']['month']+1).zfill(2)
                    +'/'+str(receipt['date']['year']).zfill(4)
                    +''+str(receipt['date']['hour']).zfill(2)
                    +':'+str(receipt['date']['minute']).zfill(2))


driver=EscposDriver()

proxy.proxy_drivers['escpos']=driver


classEscposProxy(proxy.ProxyController):
    
    @http.route('/hw_proxy/open_cashbox',type='json',auth='none',cors='*')
    defopen_cashbox(self):
        _logger.info('ESC/POS:OPENCASHBOX')
        driver.push_task('cashbox')
        
    @http.route('/hw_proxy/print_receipt',type='json',auth='none',cors='*')
    defprint_receipt(self,receipt):
        _logger.info('ESC/POS:PRINTRECEIPT')
        driver.push_task('receipt',receipt)

    @http.route('/hw_proxy/print_xml_receipt',type='json',auth='none',cors='*')
    defprint_xml_receipt(self,receipt):
        _logger.info('ESC/POS:PRINTXMLRECEIPT')
        driver.push_task('xml_receipt',receipt)
