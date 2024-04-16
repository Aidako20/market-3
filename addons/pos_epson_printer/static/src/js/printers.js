
flectra.define('pos_epson_printer.Printer',function(require){
"usestrict";

const{Gui}=require('point_of_sale.Gui');
varcore=require('web.core');
varPrinterMixin=require('point_of_sale.Printer').PrinterMixin;

var_t=core._t;

varEpsonPrinter=core.Class.extend(PrinterMixin,{
    init:function(ip,pos){
        PrinterMixin.init.call(this,pos);
        this.ePOSDevice=newepson.ePOSDevice();
        varport=window.location.protocol==='http:'?'8008':'8043';
        this.ePOSDevice.connect(ip,port,this.callback_connect.bind(this),{eposprint:true});
    },

    callback_connect:function(resultConnect){
        vardeviceId='local_printer';
        varoptions={'crypto':false,'buffer':false};
        if((resultConnect=='OK')||(resultConnect=='SSL_CONNECT_OK')){
            this.ePOSDevice.createDevice(deviceId,this.ePOSDevice.DEVICE_TYPE_PRINTER,options,this.callback_createDevice.bind(this));
        }else{
            Gui.showPopup('ErrorPopup',{
                'title':_t('Connectiontotheprinterfailed'),
                'body':_t('Pleasecheckiftheprinterisstillconnected,iftheconfiguredIPaddressiscorrectandifyourprintersupportstheePOSprotocol.\n'+
                    'Somebrowsersdon\'tallowHTTPcallsfromwebsitestodevicesinthenetwork(forsecurityreasons).'+
                    'Ifitisthecase,youwillneedtofollowFlectra\'sdocumentationfor'+
                    '\'Self-signedcertificateforePOSprinters\'and\'Secureconnection(HTTPS)\'tosolvetheissue'
                ),
            });
        }
    },

    callback_createDevice:function(deviceObj,errorCode){
        if(deviceObj===null){
            Gui.showPopup('ErrorPopup',{
                'title':_t('Connectiontotheprinterfailed'),
                'body': _t('Pleasecheckiftheprinterisstillconnected.Errorcode:')+errorCode,
            });
            return;
        }
        this.printer=deviceObj;
        this.printer.onreceive=function(response){
            if(!response.success){
                Gui.showPopup('ErrorPopup',{
                    'title':_t('EpsonePOSError'),
                    'body': _t('Anerrorhappenedwhilesendingdatatotheprinter.Errorcode:')+response.code,
                });
            }
        };
    },

    /**
     *CreatetheprintrequestforwebPRNTfromacanvas
     *
     *@override
     */
    process_canvas:function(canvas){
        if(this.printer){
            this.printer.addTextAlign(this.printer.ALIGN_CENTER);
            this.printer.addImage(canvas.getContext('2d'),0,0,canvas.width,canvas.height);
            this.printer.addCut();
        }
    },

    /**
     *@override
     */
    open_cashbox:function(){
        if(this.printer){
            this.printer.addPulse();
            this.printer.send();
        }
    },

    /**
     *@override
     */
    send_printing_job:function(){
        if(this.printer){
            this.printer.send();
            return{
                result:true
            };
        }
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *NotapplicabletoEpsonePOS
     *@override
     */
    _onIoTActionFail:function(){},
    _onIoTActionResult:function(){},
});

returnEpsonPrinter;

});
