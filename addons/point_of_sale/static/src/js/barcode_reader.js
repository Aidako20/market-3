flectra.define('point_of_sale.BarcodeReader',function(require){
"usestrict";

varcore=require('web.core');

//thismoduleinterfaceswiththebarcodereader.Itassumesthebarcodereader
//isset-uptoactlike akeyboard.Useconnect()anddisconnect()toactivate
//anddeactivatethebarcodereader.Useset_action_callbackstotellit
//whattodowhenitreadsabarcode.
varBarcodeReader=core.Class.extend({
    actions:[
        'product',
        'cashier',
        'client',
    ],

    init:function(attributes){
        this.pos=attributes.pos;
        this.action_callbacks={};
        this.exclusive_callbacks={};
        this.proxy=attributes.proxy;
        this.remote_scanning=false;
        this.remote_active=0;

        this.barcode_parser=attributes.barcode_parser;

        this.action_callback_stack=[];

        core.bus.on('barcode_scanned',this,function(barcode){
            this.scan(barcode);
        });
    },

    set_barcode_parser:function(barcode_parser){
        this.barcode_parser=barcode_parser;
    },

    //whenabarcodeisscannedandparsed,thecallbackcorresponding
    //toitstypeiscalledwiththeparsed_barcodeasaparameter.
    //(parsed_barcodeistheresultofparse_barcode(barcode))
    //
    //callbacksisaMapof'actions':callback(parsed_barcode)
    //thatsetsthecallbackforeachaction.ifacallbackforthe
    //specifiedactionalreadyexists,itisreplaced.
    //
    //possibleactionsinclude:
    //'product'|'cashier'|'client'|'discount'
    set_action_callback:function(name,callback){
        if(this.action_callbacks[name]){
            this.action_callbacks[name].add(callback);
        }else{
            this.action_callbacks[name]=newSet([callback]);
        }
    },

    remove_action_callback:function(name,callback){
        if(!callback){
            deletethis.action_callbacks[name];
            return;
        }
        constcallbacks=this.action_callbacks[name];
        if(callbacks){
            callbacks.delete(callback);
            if(callbacks.size===0){
                deletethis.action_callbacks[name];
            }
        }
    },

    /**
     *Allowsettingofexclusivecallbacks.Ifthereareexclusivecallbacks,
     *thesecallbacksarecalledneglectingtheregularcallbacks.Thisis
     *usefulforrenderedComponentsthatwantstotakeexclusiveaccess
     *tothebarcodereader.
     *
     *@param{String}name
     *@param{Function}callbackfunctionthattakesparsedbarcode
     */
    set_exclusive_callback:function(name,callback){
        if(this.exclusive_callbacks[name]){
            this.exclusive_callbacks[name].add(callback);
        }else{
            this.exclusive_callbacks[name]=newSet([callback]);
        }
    },

    remove_exclusive_callback:function(name,callback){
        if(!callback){
            deletethis.exclusive_callbacks[name];
            return;
        }
        constcallbacks=this.exclusive_callbacks[name];
        if(callbacks){
            callbacks.delete(callback);
            if(callbacks.size===0){
                deletethis.exclusive_callbacks[name];
            }
        }
    },

    scan:function(code){
        if(!code)return;

        constcallbacks=Object.keys(this.exclusive_callbacks).length
            ?this.exclusive_callbacks
            :this.action_callbacks;

        constparsed_result=this.barcode_parser.parse_barcode(code);
        if(callbacks[parsed_result.type]){
            [...callbacks[parsed_result.type]].map((cb)=>cb(parsed_result));
        }elseif(callbacks.error){
            [...callbacks.error].map((cb)=>cb(parsed_result));
        }else{
            console.warn('IgnoredBarcodeScan:',parsed_result);
        }

    },

    //thebarcodescannerwilllistenonthehw_proxy/scannerinterfacefor
    //scaneventsuntildisconnect_from_proxyiscalled
    connect_to_proxy:function(){
        varself=this;
        this.remote_scanning=true;
        if(this.remote_active>=1){
            return;
        }
        this.remote_active=1;

        functionwaitforbarcode(){
            returnself.proxy.connection.rpc('/hw_proxy/scanner',{},{shadow:true,timeout:7500})
                .then(function(barcode){
                    if(!self.remote_scanning){
                        self.remote_active=0;
                        return;
                    }
                    self.scan(barcode);
                    waitforbarcode();
                },
                function(){
                    if(!self.remote_scanning){
                        self.remote_active=0;
                        return;
                    }
                    waitforbarcode();
                });
        }
        waitforbarcode();
    },

    //thebarcodescannerwillstoplisteningonthehw_proxy/scannerremoteinterface
    disconnect_from_proxy:function(){
        this.remote_scanning=false;
    },
});

returnBarcodeReader;

});
