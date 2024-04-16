flectra.define('point_of_sale.devices',function(require){
"usestrict";

varcore=require('web.core');
varmixins=require('web.mixins');
varSession=require('web.Session');
varPrinter=require('point_of_sale.Printer').Printer;

//theJobQueueschedulesasequenceof'jobs'.eachjobis
//afunctionreturningapromise.Thequeuewaitsforeachjobtofinish
//beforelaunchingthenext.Eachjobcanalsobescheduledwithadelay.
//the isusedtopreventparallelrequeststotheproxy.

varJobQueue=function(){
    varqueue=[];
    varrunning=false;
    varscheduled_end_time=0;
    varend_of_queue=Promise.resolve();
    varstoprepeat=false;

    varrun=function(){
        varrunNextJob=function(){
            if(queue.length===0){
                running=false;
                scheduled_end_time=0;
                returnPromise.resolve();
            }
            running=true;
            varjob=queue[0];
            if(!job.opts.repeat||stoprepeat){
                queue.shift();
                stoprepeat=false;
            }

            //thetimescheduledforthisjob
            scheduled_end_time=(newDate()).getTime()+(job.opts.duration||0);

            //werunthejobandputinpromwhenitfinishes
            varprom=job.fun()||Promise.resolve();

            varalways=function(){
                //werunthenextjobafterthescheduled_end_time,evenifitfinishesbefore
                returnnewPromise(function(resolve,reject){
                    setTimeout(
                        resolve,
                        Math.max(0,scheduled_end_time-(newDate()).getTime())
                    );
                });
            };
            //wedon'tcareifajobfails...
            returnprom.then(always,always).then(runNextJob);
        };

        if(!running){
            end_of_queue=runNextJob();
        }
    };

    /**
     *Addsajobtotheschedule.
     *
     *@param{function}funmustreturnapromise
     *@param{object}[opts]
     *@param{number}[opts.duration]thejobisguaranteedtofinishnoquickerthanthis(milisec)
     *@param{boolean}[opts.repeat]iftrue,thejobwillbeendlesslyrepeated
     *@param{boolean}[opts.important]iftrue,thescheduledjobcannotbecanceledbyaqueue.clear()
     */
    this.schedule =function(fun,opts){
        queue.push({fun:fun,opts:opts||{}});
        if(!running){
            run();
        }
    };

    //removealljobsfromtheschedule(excepttheonesmarkedasimportant)
    this.clear=function(){
        queue=_.filter(queue,function(job){returnjob.opts.important===true;});
    };

    //endtherepetitionofthecurrentjob
    this.stoprepeat=function(){
        stoprepeat=true;
    };

    /**
     *Returnsapromisethatresolveswhenallscheduledjobshavebeenrun.
     *(jobsaddedafterthecalltothismethodareconsideredaswell)
     *
     *@returns{Promise}
     */
    this.finished=function(){
        returnend_of_queue;
    };

};


//thisobjectinterfaceswiththelocalproxytocommunicatetothevarioushardwaredevices
//connectedtothePointofSale.AsthecommunicationonlygoesfromthePOStotheproxy,
//methodsareusedbothtosignalanevent,andtofetchinformation.

varProxyDevice =core.Class.extend(mixins.PropertiesMixin,{
    init:function(parent,options){
        mixins.PropertiesMixin.init.call(this);
        varself=this;
        this.setParent(parent);
        options=options||{};

        this.pos=parent;

        this.weighing=false;
        this.debug_weight=0;
        this.use_debug_weight=false;

        this.paying=false;
        this.default_payment_status={
            status:'waiting',
            message:'',
            payment_method:undefined,
            receipt_client:undefined,
            receipt_shop:  undefined,
        };
        this.custom_payment_status=this.default_payment_status;

        this.notifications={};
        this.bypass_proxy=false;

        this.connection=null;
        this.host      ='';
        this.keptalive =false;

        this.set('status',{});

        this.set_connection_status('disconnected');

        this.on('change:status',this,function(eh,status){
            status=status.newValue;
            if(status.status==='connected'&&self.printer){
                self.printer.print_receipt();
            }
        });

        this.posbox_supports_display=true;

        window.hw_proxy=this;
    },
    set_connection_status:function(status,drivers,msg=''){
        varoldstatus=this.get('status');
        varnewstatus={};
        newstatus.status=status;
        newstatus.drivers=status==='disconnected'?{}:oldstatus.drivers;
        newstatus.drivers=drivers?drivers:newstatus.drivers;
        newstatus.msg=msg;
        this.set('status',newstatus);
    },
    disconnect:function(){
        if(this.get('status').status!=='disconnected'){
            this.connection.destroy();
            this.set_connection_status('disconnected');
        }
    },

    /**
     *Connectstothespecifiedurl.
     *
     *@param{string}url
     *@returns{Promise}
     */
    connect:function(url){
        varself=this;
        this.connection=newSession(undefined,url,{use_cors:true});
        this.host=url;
        if(this.pos.config.iface_print_via_proxy){
            this.connect_to_printer();
        }
        this.set_connection_status('connecting',{});

        returnthis.message('handshake').then(function(response){
                if(response){
                    self.set_connection_status('connected');
                    localStorage.hw_proxy_url=url;
                    self.keepalive();
                }else{
                    self.set_connection_status('disconnected');
                    console.error('ConnectionrefusedbytheProxy');
                }
            },function(){
                self.set_connection_status('disconnected');
                console.error('CouldnotconnecttotheProxy');
            });
    },

    connect_to_printer:function(){
        this.printer=newPrinter(this.host,this.pos);
    },

    /**
     *Findaproxyandconnectstoit.
     *
     *@param{Object}[options]
     *@param{string}[options.force_ip]onlytrytoconnecttothespecifiedip.
     *@param{string}[options.port]@seefind_proxy
     *@param{function}[options.progress]@seefind_proxy
     *@returns{Promise}
     */
    autoconnect:function(options){
        varself=this;
        this.set_connection_status('connecting',{});
        if(this.pos.config.iface_print_via_proxy){
            this.connect_to_printer();
        }
        varfound_url=newPromise(function(){});

        if(options.force_ip){
            //iftheipisforcedbyserverconfig,bailoutonfail
            found_url=this.try_hard_to_connect(options.force_ip,options);
        }elseif(localStorage.hw_proxy_url){
            //tryharderwhenwerememberagoodproxyurl
            found_url=this.try_hard_to_connect(localStorage.hw_proxy_url,options)
                .catch(function(){
                    if(window.location.protocol!='https:'){
                        returnself.find_proxy(options);
                    }
                });
        }else{
            //justfindsomethingquick
            if(window.location.protocol!='https:'){
                found_url=this.find_proxy(options);
            }
        }

        varsuccessProm=found_url.then(function(url){
            returnself.connect(url);
        });

        successProm.catch(function(){
            self.set_connection_status('disconnected');
        });

        returnsuccessProm;
    },

    //startsaloopthatupdatestheconnectionstatus
    keepalive:function(){
        varself=this;

        functionstatus(){
            varalways=function(){
                setTimeout(status,5000);
            };
            self.connection.rpc('/hw_proxy/status_json',{},{shadow:true,timeout:2500})
                .then(function(driver_status){
                    self.set_connection_status('connected',driver_status);
                },function(){
                    if(self.get('status').status!=='connecting'){
                        self.set_connection_status('disconnected');
                    }
                }).then(always,always);
        }

        if(!this.keptalive){
            this.keptalive=true;
            status();
        }
    },

    /**
     *@param{string}name
     *@param{Object}[params]
     *@returns{Promise}
     */
    message:function(name,params){
        varcallbacks=this.notifications[name]||[];
        for(vari=0;i<callbacks.length;i++){
            callbacks[i](params);
        }
        if(this.get('status').status!=='disconnected'){
            returnthis.connection.rpc('/hw_proxy/'+name,params||{},{shadow:true});
        }else{
            returnPromise.reject();
        }
    },

    /**
     *Triesseveraltimetoconnecttoaknownproxyurl.
     *
     *@param{*}url
     *@param{Object}[options]
     *@param{string}[options.port=7073]whatporttolistento
     *@returns{Promise<string|Array>}
     */
    try_hard_to_connect:function(url,options){
        options  =options||{};
        varprotocol=window.location.protocol;
        varport=(!options.port&&protocol=="https:")?':443':':'+(options.port||'7073');

        this.set_connection_status('connecting');

        if(url.indexOf('//')<0){
            url=protocol+'//'+url;
        }

        if(url.indexOf(':',5)<0){
            url=url+port;
        }

        //tryrealhardtoconnecttourl,witha1sectimeoutandupto'retries'retries
        functiontry_real_hard_to_connect(url,retries){
            returnPromise.resolve(
                $.ajax({
                    url:url+'/hw_proxy/hello',
                    method:'GET',
                    timeout:1000,
                })
                .then(function(){
                    returnPromise.resolve(url);
                },function(resp){
                    if(retries>0){
                        returntry_real_hard_to_connect(url,retries-1);
                    }else{
                        returnPromise.reject([resp.statusText,url]);
                    }
                })
            );
        }

        returntry_real_hard_to_connect(url,3);
    },

    /**
     *Returnsasapromiseavalidhosturlthatcanbeusedasproxy.
     *
     *@param{Object}[options]
     *@param{string}[options.port]whatporttolistento(default7073)
     *@param{function}[options.progress]callbackforsearchprogress(facin[0,1])
     *@returns{Promise<string>}willberesolvedwiththeproxyvalidurl
     */
    find_proxy:function(options){
        options=options||{};
        varself =this;
        varport =':'+(options.port||'7073');
        varurls =[];
        varfound=false;
        varparallel=8;
        varthreads =[];
        varprogress=0;


        urls.push('http://localhost'+port);
        for(vari=0;i<256;i++){
            urls.push('http://192.168.0.'+i+port);
            urls.push('http://192.168.1.'+i+port);
            urls.push('http://10.0.0.'+i+port);
        }

        varprog_inc=1/urls.length;

        functionupdate_progress(){
            progress=found?1:progress+prog_inc;
            if(options.progress){
                options.progress(progress);
            }
        }

        functionthread(){
            varurl=urls.shift();

            if(!url||found||!self.searching_for_proxy){
                returnPromise.resolve();
            }

            returnPromise.resolve(
                $.ajax({
                    url:url+'/hw_proxy/hello',
                    method:'GET',
                    timeout:400,
                }).then(function(){
                    found=true;
                    update_progress();
                    returnPromise.resolve(url);
                },function(){
                    update_progress();
                    returnthread();
                })
            );
        }

        this.searching_for_proxy=true;

        varlen =Math.min(parallel,urls.length);
        for(i=0;i<len;i++){
            threads.push(thread());
        }

        returnnewPromise(function(resolve,reject){
            Promise.all(threads).then(function(results){
                varurls=[];
                for(vari=0;i<results.length;i++){
                    if(results[i]){
                        urls.push(results[i]);
                    }
                }
                resolve(urls[0]);
            });
        });
    },

    stop_searching:function(){
        this.searching_for_proxy=false;
        this.set_connection_status('disconnected');
    },

    //thisallowstheclienttobenotifiedwhenaproxycallismade.Thenotification
    //callbackwillbeexecutedwiththesameargumentsastheproxycall
    add_notification:function(name,callback){
        if(!this.notifications[name]){
            this.notifications[name]=[];
        }
        this.notifications[name].push(callback);
    },

    /**
     *Returnstheweightonthescale.
     *
     *@returns{Promise<Object>}
     */
    scale_read:function(){
        varself=this;
        if(self.use_debug_weight){
            returnPromise.resolve({weight:this.debug_weight,unit:'Kg',info:'ok'});
        }
        returnnewPromise(function(resolve,reject){
            self.message('scale_read',{})
            .then(function(weight){
                resolve(weight);
            },function(){//failedtoreadweight
                resolve({weight:0.0,unit:'Kg',info:'ok'});
            });
        });
    },

    //setsacustomweight,ignoringtheproxyreturnedvalue.
    debug_set_weight:function(kg){
        this.use_debug_weight=true;
        this.debug_weight=kg;
    },

    //resetsthecustomweightandre-enablelisteningtotheproxyforweightvalues
    debug_reset_weight:function(){
        this.use_debug_weight=false;
        this.debug_weight=0;
    },

    update_customer_facing_display:function(html){
        if(this.posbox_supports_display){
            returnthis.message('customer_facing_display',
                {html:html},
                {timeout:5000});
        }
    },

    /**
     *@param{string}html
     *@returns{Promise}
     */
    take_ownership_over_client_screen:function(html){
        returnthis.message("take_control",{html:html});
    },

    /**
     *@returns{Promise}
     */
    test_ownership_of_client_screen:function(){
        if(this.connection){
            returnthis.message("test_ownership",{});
        }
        returnPromise.reject({abort:true});
    },

    //askstheproxytologsomeinformation,aswiththedebug.logyoucanprovideseveralarguments.
    log:function(){
        returnthis.message('log',{'arguments':_.toArray(arguments)});
    },

});

return{
    JobQueue:JobQueue,
    ProxyDevice:ProxyDevice,
};

});
