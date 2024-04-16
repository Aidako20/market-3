flectra.define('point_of_sale.models',function(require){
"usestrict";

const{Context}=owl;
varBarcodeParser=require('barcodes.BarcodeParser');
varBarcodeReader=require('point_of_sale.BarcodeReader');
varPosDB=require('point_of_sale.DB');
vardevices=require('point_of_sale.devices');
varconcurrency=require('web.concurrency');
varconfig=require('web.config');
varcore=require('web.core');
varfield_utils=require('web.field_utils');
vartime=require('web.time');
varutils=require('web.utils');

varQWeb=core.qweb;
var_t=core._t;
varMutex=concurrency.Mutex;
varround_di=utils.round_decimals;
varround_pr=utils.round_precision;

varexports={};

//ThePosModelcontainsthePointOfSale'srepresentationofthebackend.
//SincethePoSmustworkinstandalone(Withoutconnectiontotheserver)
//itmustcontainsarepresentationoftheserver'sPoSbackend.
//(taxes,productlist,configurationoptions,etc.) thisrepresentation
//isfetchedandstoredbythePosModelattheinitialisation.
//thisisdoneasynchronously,areadydeferredalowstheGUItowaitinteractively
//fortheloadingtobecompleted
//ThereisasingleinstanceofthePosModelforeachFront-Endinstance,itisusuallycalled
//'pos'andisavailabletoallwidgetsextendingPosWidget.

exports.PosModel=Backbone.Model.extend({
    initialize:function(attributes){
        Backbone.Model.prototype.initialize.call(this,attributes);
        var self=this;
        this.flush_mutex=newMutex();                  //usedtomakesuretheordersaresenttotheserveronceattime

        this.env=this.get('env');
        this.rpc=this.get('rpc');
        this.session=this.get('session');
        this.do_action=this.get('do_action');
        this.setLoadingMessage=this.get('setLoadingMessage');
        this.setLoadingProgress=this.get('setLoadingProgress');
        this.showLoadingSkip=this.get('showLoadingSkip');

        this.proxy=newdevices.ProxyDevice(this);             //usedtocommunicatetothehardwaredevicesviaalocalproxy
        this.barcode_reader=newBarcodeReader({'pos':this,proxy:this.proxy});

        this.proxy_queue=newdevices.JobQueue();          //usedtopreventparallelscommunicationstotheproxy
        this.db=newPosDB();                      //alocaldatabaseusedtosearchtroughproductsandcategories&storependingorders
        this.debug=config.isDebug();//debugmode

        //Businessdata;loadedfromtheserveratlaunch
        this.company_logo=null;
        this.company_logo_base64='';
        this.currency=null;
        this.company=null;
        this.user=null;
        this.users=[];
        this.employee={name:null,id:null,barcode:null,user_id:null,pin:null};
        this.employees=[];
        this.partners=[];
        this.taxes=[];
        this.pos_session=null;
        this.config=null;
        this.units=[];
        this.units_by_id={};
        this.uom_unit_id=null;
        this.default_pricelist=null;
        this.order_sequence=1;
        window.posmodel=this;

        //Objectmappingtheorder'sname(whichcontainstheuid)toit'sserver_idafter
        //validation(orderpaidthensenttothebackend).
        this.validated_orders_name_server_id_map={};

        //Extracttheconfigidfromtheurl.
        vargiven_config=newRegExp('[\?&]config_id=([^&#]*)').exec(window.location.href);
        this.config_id=given_config&&given_config[1]&&parseInt(given_config[1])||false;

        //thesedynamicattributescanbewatchedforchangebyothermodelsorwidgets
        this.set({
            'synch':           {status:'connected',pending:0},
            'orders':          newOrderCollection(),
            'selectedOrder':   null,
            'selectedClient':  null,
            'cashier':         null,
            'selectedCategoryId':null,
        });

        this.get('orders').on('remove',function(order,_unused_,options){
            self.on_removed_order(order,options.index,options.reason);
        });

        //Forwardthe'client'attributeontheselectedorderto'selectedClient'
        functionupdate_client(){
            varorder=self.get_order();
            this.set('selectedClient',order?order.get_client():null);
        }
        this.get('orders').on('addremovechange',update_client,this);
        this.on('change:selectedOrder',update_client,this);

        //Wefetchthebackenddataontheserverasynchronously.thisisdoneonlywhentheposuserinterfaceislaunched,
        //Anychangeonthisdatamadeontheserveristhusnotreflectedonthepointofsaleuntilitisrelaunched.
        //whenallthedatahasloaded,wecomputesomestuff,anddeclarethePosreadytobeused.
        this.ready=this.load_server_data().then(function(){
            returnself.after_load_server_data();
        });
    },
    after_load_server_data:function(){
        this.load_orders();
        this.set_start_order();
        if(this.config.use_proxy){
            if(this.config.iface_customer_facing_display){
                this.on('change:selectedOrder',this.send_current_order_to_customer_facing_display,this);
            }

            returnthis.connect_to_proxy();
        }
        returnPromise.resolve();
    },
    //releasesressourcesholdsbythemodelattheendoflifeoftheposmodel
    destroy:function(){
        //FIXME,shouldwaitforflushing,returnadeferredtoindicatesuccessfulldestruction
        //this.flush();
        this.proxy.disconnect();
        this.barcode_reader.disconnect_from_proxy();
    },

    connect_to_proxy:function(){
        varself=this;
        returnnewPromise(function(resolve,reject){
            self.barcode_reader.disconnect_from_proxy();
            self.setLoadingMessage(_t('ConnectingtotheIoTBox'),0);
            self.showLoadingSkip(function(){
                self.proxy.stop_searching();
            });
            self.proxy.autoconnect({
                force_ip:self.config.proxy_ip||undefined,
                progress:function(prog){
                    self.setLoadingProgress(prog);
                },
            }).then(
                function(){
                    if(self.config.iface_scan_via_proxy){
                        self.barcode_reader.connect_to_proxy();
                    }
                    resolve();
                },
                function(statusText,url){
                    //thisshouldrejectsothatitcanbecapturedwhenwewaitforpos.ready
                    //inthechromecomponent.
                    //then,ifitgotreallyrejected,wecanshowtheerror.
                    if(statusText=='error'&&window.location.protocol=='https:'){
                        reject({
                            title:_t('HTTPSconnectiontoIoTBoxfailed'),
                            body:_.str.sprintf(
                              _t('MakesureyouareusingIoTBoxv18.12orhigher.Navigateto%stoacceptthecertificateofyourIoTBox.'),
                              url
                            ),
                            popup:'alert',
                        });
                    }else{
                        resolve();
                    }
                }
            );
        });
    },

    //Serversidemodelloaders.Thisisthelistofthemodelsthatneedtobeloadedfrom
    //theserver.Themodelsareloadedonebyonebythislist'sorder.The'loaded'callback
    //isusedtostorethedataintheappropriateplaceonceithasbeenloaded.Thiscallback
    //canreturnapromisethatwillpausetheloadingofthenextmodule.
    //asharedtemporarydictionaryisavailableforloaderstocommunicateprivatevariables
    //usedduringloadingsuchasobjectids,etc.
    models:[
    {
        label: 'version',
        loaded:function(self){
            returnself.session.rpc('/web/webclient/version_info',{}).then(function(version){
                self.version=version;
            });
        },

    },{
        model: 'res.company',
        fields:['currency_id','email','website','company_registry','vat','name','phone','partner_id','country_id','state_id','tax_calculation_rounding_method'],
        ids:   function(self){return[self.session.user_context.allowed_company_ids[0]];},
        loaded:function(self,companies){self.company=companies[0];},
    },{
        model: 'decimal.precision',
        fields:['name','digits'],
        loaded:function(self,dps){
            self.dp ={};
            for(vari=0;i<dps.length;i++){
                self.dp[dps[i].name]=dps[i].digits;
            }
        },
    },{
        model: 'uom.uom',
        fields:[],
        domain:null,
        context:function(self){return{active_test:false};},
        loaded:function(self,units){
            self.units=units;
            _.each(units,function(unit){
                self.units_by_id[unit.id]=unit;
            });
        }
    },{
        model: 'ir.model.data',
        fields:['res_id'],
        domain:function(){return[['name','=','product_uom_unit']];},
        loaded:function(self,unit){
            self.uom_unit_id=unit[0].res_id;
        }
    },{
        model: 'res.partner',
        label:'load_partners',
        fields:['name','street','city','state_id','country_id','vat','lang',
                 'phone','zip','mobile','email','barcode','write_date',
                 'property_account_position_id','property_product_pricelist'],
        loaded:function(self,partners){
            self.partners=partners;
            self.db.add_partners(partners);
        },
    },{
        model: 'res.country.state',
        fields:['name','country_id'],
        loaded:function(self,states){
            self.states=states;
        },
    },{
        model: 'res.country',
        fields:['name','vat_label','code'],
        loaded:function(self,countries){
            self.countries=countries;
            self.company.country=null;
            for(vari=0;i<countries.length;i++){
                if(countries[i].id===self.company.country_id[0]){
                    self.company.country=countries[i];
                }
            }
        },
    },{
        model: 'res.lang',
        fields:['name','code'],
        loaded:function(self,langs){
            self.langs=langs;
        },
    },{
        model: 'account.tax',
        fields:['name','amount','price_include','include_base_amount','amount_type','children_tax_ids'],
        domain:function(self){return[['company_id','=',self.company&&self.company.id||false]]},
        loaded:function(self,taxes){
            self.taxes=taxes;
            self.taxes_by_id={};
            _.each(taxes,function(tax){
                self.taxes_by_id[tax.id]=tax;
            });
            _.each(self.taxes_by_id,function(tax){
                tax.children_tax_ids=_.map(tax.children_tax_ids,function(child_tax_id){
                    returnself.taxes_by_id[child_tax_id];
                });
            });
            returnnewPromise(function(resolve,reject){
              vartax_ids=_.pluck(self.taxes,'id');
              self.rpc({
                  model:'account.tax',
                  method:'get_real_tax_amount',
                  args:[tax_ids],
              }).then(function(taxes){
                  _.each(taxes,function(tax){
                      self.taxes_by_id[tax.id].amount=tax.amount;
                  });
                  resolve();
              });
            });
        },
    },{
        model: 'pos.session',
        fields:['id','name','user_id','config_id','start_at','stop_at','sequence_number','payment_method_ids','cash_register_id','state'],
        domain:function(self){
            vardomain=[
                ['state','in',['opening_control','opened']],
                ['rescue','=',false],
            ];
            if(self.config_id)domain.push(['config_id','=',self.config_id]);
            returndomain;
        },
        loaded:function(self,pos_sessions,tmp){
            self.pos_session=pos_sessions[0];
            self.pos_session.login_number=flectra.login_number;
            self.config_id=self.config_id||self.pos_session&&self.pos_session.config_id[0];
            tmp.payment_method_ids=pos_sessions[0].payment_method_ids;
        },
    },{
        model:'pos.config',
        fields:[],
        domain:function(self){return[['id','=',self.config_id]];},
        loaded:function(self,configs){
            self.config=configs[0];
            self.config.use_proxy=self.config.is_posbox&&(
                                    self.config.iface_electronic_scale||
                                    self.config.iface_print_via_proxy ||
                                    self.config.iface_scan_via_proxy  ||
                                    self.config.iface_customer_facing_display);

            self.db.set_uuid(self.config.uuid);
            self.set_cashier(self.get_cashier());
            //Weneedtodoithere,sinceonlythenthelocalstoragehasthecorrectuuid
            self.db.save('pos_session_id',self.pos_session.id);

            varorders=self.db.get_orders();
            for(vari=0;i<orders.length;i++){
                self.pos_session.sequence_number=Math.max(self.pos_session.sequence_number,orders[i].data.sequence_number+1);
            }
       },
    },{
      model:'stock.picking.type',
      fields:['use_create_lots','use_existing_lots'],
      domain:function(self){return[['id','=',self.config.picking_type_id[0]]];},
      loaded:function(self,picking_type){
          self.picking_type=picking_type[0];
      },
    },{
        model: 'res.users',
        fields:['name','company_id','id','groups_id','lang'],
        domain:function(self){return[['company_ids','in',self.config.company_id[0]],'|',['groups_id','=',self.config.group_pos_manager_id[0]],['groups_id','=',self.config.group_pos_user_id[0]]];},
        loaded:function(self,users){
            users.forEach(function(user){
                user.role='cashier';
                user.groups_id.some(function(group_id){
                    if(group_id===self.config.group_pos_manager_id[0]){
                        user.role='manager';
                        returntrue;
                    }
                });
                if(user.id===self.session.uid){
                    self.user=user;
                    self.employee.name=user.name;
                    self.employee.role=user.role;
                    self.employee.user_id=[user.id,user.name];
                }
            });
            self.users=users;
            self.employees=[self.employee];
            self.set_cashier(self.employee);
        },
    },{
        model: 'product.pricelist',
        fields:['name','display_name','discount_policy'],
        domain:function(self){
            if(self.config.use_pricelist){
                return[['id','in',self.config.available_pricelist_ids]];
            }else{
                return[['id','=',self.config.pricelist_id[0]]];
            }
        },
        loaded:function(self,pricelists){
            _.map(pricelists,function(pricelist){pricelist.items=[];});
            self.default_pricelist=_.findWhere(pricelists,{id:self.config.pricelist_id[0]});
            self.pricelists=pricelists;
        },
    },{
        model: 'account.bank.statement',
        fields:['id','balance_start'],
        domain:function(self){return[['id','=',self.pos_session.cash_register_id[0]]];},
        loaded:function(self,statement){
            self.bank_statement=statement[0];
        },
    },{
        model: 'product.pricelist.item',
        domain:function(self){return[['pricelist_id','in',_.pluck(self.pricelists,'id')]];},
        loaded:function(self,pricelist_items){
            varpricelist_by_id={};
            _.each(self.pricelists,function(pricelist){
                pricelist_by_id[pricelist.id]=pricelist;
            });

            _.each(pricelist_items,function(item){
                varpricelist=pricelist_by_id[item.pricelist_id[0]];
                pricelist.items.push(item);
                item.base_pricelist=pricelist_by_id[item.base_pricelist_id[0]];
            });
        },
    },{
        model: 'product.category',
        fields:['name','parent_id'],
        loaded:function(self,product_categories){
            varcategory_by_id={};
            _.each(product_categories,function(category){
                category_by_id[category.id]=category;
            });
            _.each(product_categories,function(category){
                category.parent=category_by_id[category.parent_id[0]];
            });

            self.product_categories=product_categories;
        },
    },{
        model:'res.currency',
        fields:['name','symbol','position','rounding','rate'],
        ids:   function(self){return[self.config.currency_id[0],self.company.currency_id[0]];},
        loaded:function(self,currencies){
            self.currency=currencies[0];
            if(self.currency.rounding>0&&self.currency.rounding<1){
                self.currency.decimals=Math.ceil(Math.log(1.0/self.currency.rounding)/Math.log(10));
            }else{
                self.currency.decimals=0;
            }

            self.company_currency=currencies[1];
        },
    },{
        model: 'pos.category',
        fields:['id','name','parent_id','child_id','write_date'],
        domain:function(self){
            returnself.config.limit_categories&&self.config.iface_available_categ_ids.length?[['id','in',self.config.iface_available_categ_ids]]:[];
        },
        loaded:function(self,categories){
            self.db.add_categories(categories);
        },
    },{
        model: 'product.product',
        fields:['display_name','lst_price','standard_price','categ_id','pos_categ_id','taxes_id',
                 'barcode','default_code','to_weight','uom_id','description_sale','description',
                 'product_tmpl_id','tracking','write_date','available_in_pos','attribute_line_ids','active'],
        order: _.map(['sequence','default_code','name'],function(name){return{name:name};}),
        domain:function(self){
            vardomain=['&','&',['sale_ok','=',true],['available_in_pos','=',true],'|',['company_id','=',self.config.company_id[0]],['company_id','=',false]];
            if(self.config.limit_categories&& self.config.iface_available_categ_ids.length){
                domain.unshift('&');
                domain.push(['pos_categ_id','in',self.config.iface_available_categ_ids]);
            }
            if(self.config.iface_tipproduct){
              domain.unshift(['id','=',self.config.tip_product_id[0]]);
              domain.unshift('|');
            }
            returndomain;
        },
        context:function(self){return{display_default_code:false};},
        loaded:function(self,products){
            varusing_company_currency=self.config.currency_id[0]===self.company.currency_id[0];
            varconversion_rate=self.currency.rate/self.company_currency.rate;
            self.db.add_products(_.map(products,function(product){
                if(!using_company_currency){
                    product.lst_price=round_pr(product.lst_price*conversion_rate,self.currency.rounding);
                }
                product.categ=_.findWhere(self.product_categories,{'id':product.categ_id[0]});
                product.pos=self;
                returnnewexports.Product({},product);
            }));
        },
    },{
        model:'product.attribute',
        fields:['name','display_type'],
        condition:function(self){returnself.config.product_configurator;},
        domain:function(){return[['create_variant','=','no_variant']];},
        loaded:function(self,product_attributes,tmp){
            tmp.product_attributes_by_id={};
            _.map(product_attributes,function(product_attribute){
                tmp.product_attributes_by_id[product_attribute.id]=product_attribute;
            });
        }
    },{
        model:'product.attribute.value',
        fields:['name','attribute_id','is_custom','html_color'],
        condition:function(self){returnself.config.product_configurator;},
        domain:function(self,tmp){return[['attribute_id','in',_.keys(tmp.product_attributes_by_id).map(parseFloat)]];},
        loaded:function(self,pavs,tmp){
            tmp.pav_by_id={};
            _.map(pavs,function(pav){
                tmp.pav_by_id[pav.id]=pav;
            });
        }
    },{
        model:'product.template.attribute.value',
        fields:['product_attribute_value_id','attribute_id','attribute_line_id','price_extra'],
        condition:function(self){returnself.config.product_configurator;},
        domain:function(self,tmp){return[['attribute_id','in',_.keys(tmp.product_attributes_by_id).map(parseFloat)]];},
        loaded:function(self,ptavs,tmp){
            self.attributes_by_ptal_id={};
            _.map(ptavs,function(ptav){
                if(!self.attributes_by_ptal_id[ptav.attribute_line_id[0]]){
                    self.attributes_by_ptal_id[ptav.attribute_line_id[0]]={
                        id:ptav.attribute_line_id[0],
                        name:tmp.product_attributes_by_id[ptav.attribute_id[0]].name,
                        display_type:tmp.product_attributes_by_id[ptav.attribute_id[0]].display_type,
                        values:[],
                    };
                }
                self.attributes_by_ptal_id[ptav.attribute_line_id[0]].values.push({
                    id:ptav.product_attribute_value_id[0],
                    name:tmp.pav_by_id[ptav.product_attribute_value_id[0]].name,
                    is_custom:tmp.pav_by_id[ptav.product_attribute_value_id[0]].is_custom,
                    html_color:tmp.pav_by_id[ptav.product_attribute_value_id[0]].html_color,
                    price_extra:ptav.price_extra,
                });
            });
        }
    },{
        model:'account.cash.rounding',
        fields:['name','rounding','rounding_method'],
        domain:function(self){return[['id','=',self.config.rounding_method[0]]];},
        loaded:function(self,cash_rounding){
            self.cash_rounding=cash_rounding;
        }
    },{
        model: 'pos.payment.method',
        fields:['name','is_cash_count','use_payment_terminal'],
        domain:function(self){return['|',['active','=',false],['active','=',true]];},
        loaded:function(self,payment_methods){
            self.payment_methods=payment_methods.sort(function(a,b){
                //prefercashpayment_methodtobefirstinthelist
                if(a.is_cash_count&&!b.is_cash_count){
                    return-1;
                }elseif(!a.is_cash_count&&b.is_cash_count){
                    return1;
                }else{
                    returna.id-b.id;
                }
            });
            self.payment_methods_by_id={};
            _.each(self.payment_methods,function(payment_method){
                self.payment_methods_by_id[payment_method.id]=payment_method;

                varPaymentInterface=self.electronic_payment_interfaces[payment_method.use_payment_terminal];
                if(PaymentInterface){
                    payment_method.payment_terminal=newPaymentInterface(self,payment_method);
                }
            });
        }
    },{
        model: 'account.fiscal.position',
        fields:[],
        domain:function(self){return[['id','in',self.config.fiscal_position_ids]];},
        loaded:function(self,fiscal_positions){
            self.fiscal_positions=fiscal_positions;
        }
    },{
        model: 'account.fiscal.position.tax',
        fields:[],
        domain:function(self){
            varfiscal_position_tax_ids=[];

            self.fiscal_positions.forEach(function(fiscal_position){
                fiscal_position.tax_ids.forEach(function(tax_id){
                    fiscal_position_tax_ids.push(tax_id);
                });
            });

            return[['id','in',fiscal_position_tax_ids]];
        },
        loaded:function(self,fiscal_position_taxes){
            self.fiscal_position_taxes=fiscal_position_taxes;
            self.fiscal_positions.forEach(function(fiscal_position){
                fiscal_position.fiscal_position_taxes_by_id={};
                fiscal_position.tax_ids.forEach(function(tax_id){
                    varfiscal_position_tax=_.find(fiscal_position_taxes,function(fiscal_position_tax){
                        returnfiscal_position_tax.id===tax_id;
                    });

                    fiscal_position.fiscal_position_taxes_by_id[fiscal_position_tax.id]=fiscal_position_tax;
                });
            });
        }
    }, {
        label:'fonts',
        loaded:function(){
            returnnewPromise(function(resolve,reject){
                //Waitingforfontstobeloadedtopreventreceiptprinting
                //fromprintingemptyreceiptwhileloadingInconsolata
                //(Thefontusedforthereceipt)
                waitForWebfonts(['Lato','Inconsolata'],function(){
                    resolve();
                });
                //TheJSusedtodetectfontloadingisnot100%robust,so
                //donotwaitmorethan5sec
                setTimeout(resolve,5000);
            });
        },
    },{
        label:'pictures',
        loaded:function(self){
            self.company_logo=newImage();
            returnnewPromise(function(resolve,reject){
                self.company_logo.onload=function(){
                    varimg=self.company_logo;
                    varratio=1;
                    vartargetwidth=300;
                    varmaxheight=150;
                    if(img.width!==targetwidth){
                        ratio=targetwidth/img.width;
                    }
                    if(img.height*ratio>maxheight){
                        ratio=maxheight/img.height;
                    }
                    varwidth =Math.floor(img.width*ratio);
                    varheight=Math.floor(img.height*ratio);
                    varc=document.createElement('canvas');
                    c.width =width;
                    c.height=height;
                    varctx=c.getContext('2d');
                    ctx.drawImage(self.company_logo,0,0,width,height);

                    self.company_logo_base64=c.toDataURL();
                    resolve();
                };
                self.company_logo.onerror=function(){
                    reject();
                };
                self.company_logo.crossOrigin="anonymous";
                self.company_logo.src=`/web/image?model=res.company&id=${self.company.id}&field=logo`;
            });
        },
    },{
        label:'barcodes',
        loaded:function(self){
            varbarcode_parser=newBarcodeParser({'nomenclature_id':self.config.barcode_nomenclature_id});
            self.barcode_reader.set_barcode_parser(barcode_parser);
            returnbarcode_parser.is_loaded();
        },
    },
    ],

    //loadsalltheneededdataonthesever.returnsapromiseindicatingwhenallthedatahasloaded.
    load_server_data:function(){
        varself=this;
        varprogress=0;
        varprogress_step=1.0/self.models.length;
        vartmp={};//thisisusedtoshareatemporarystatebetweenmodelsloaders

        varloaded=newPromise(function(resolve,reject){
            functionload_model(index){
                if(index>=self.models.length){
                    resolve();
                }else{
                    varmodel=self.models[index];
                    self.setLoadingMessage(_t('Loading')+''+(model.label||model.model||''),progress);

                    varcond=typeofmodel.condition==='function' ?model.condition(self,tmp):true;
                    if(!cond){
                        load_model(index+1);
                        return;
                    }

                    varfields= typeofmodel.fields==='function' ?model.fields(self,tmp) :model.fields;
                    vardomain= typeofmodel.domain==='function' ?model.domain(self,tmp) :model.domain;
                    varcontext=typeofmodel.context==='function'?model.context(self,tmp):model.context||{};
                    varids    =typeofmodel.ids==='function'    ?model.ids(self,tmp):model.ids;
                    varorder  =typeofmodel.order==='function'  ?model.order(self,tmp):   model.order;
                    progress+=progress_step;

                    if(model.model){
                        varparams={
                            model:model.model,
                            context:_.extend(context,self.session.user_context||{}),
                        };

                        if(model.ids){
                            params.method='read';
                            params.args=[ids,fields];
                        }else{
                            params.method='search_read';
                            params.domain=domain;
                            params.fields=fields;
                            params.orderBy=order;
                        }

                        self.rpc(params).then(function(result){
                            try{//catchingexceptionsinmodel.loaded(...)
                                Promise.resolve(model.loaded(self,result,tmp))
                                    .then(function(){load_model(index+1);},
                                        function(err){reject(err);});
                            }catch(err){
                                console.error(err.message,err.stack);
                                reject(err);
                            }
                        },function(err){
                            reject(err);
                        });
                    }elseif(model.loaded){
                        try{//catchingexceptionsinmodel.loaded(...)
                            Promise.resolve(model.loaded(self,tmp))
                                .then(function(){load_model(index+1);},
                                    function(err){reject(err);});
                        }catch(err){
                            reject(err);
                        }
                    }else{
                        load_model(index+1);
                    }
                }
            }

            try{
                returnload_model(0);
            }catch(err){
                returnPromise.reject(err);
            }
        });

        returnloaded;
    },

    prepare_new_partners_domain:function(){
        return[['write_date','>',this.db.get_partner_write_date()]];
    },

    //reloadthelistofpartner,returnsasapromisethatresolvesiftherewere
    //updatedpartners,andfailsifnot
    load_new_partners:function(){
        varself=this;
        returnnewPromise(function(resolve,reject){
            varfields=_.find(self.models,function(model){returnmodel.label==='load_partners';}).fields;
            vardomain=self.prepare_new_partners_domain();
            self.rpc({
                model:'res.partner',
                method:'search_read',
                args:[domain,fields],
            },{
                timeout:3000,
                shadow:true,
            })
            .then(function(partners){
                if(self.db.add_partners(partners)){  //checkifthepartnerswegotwererealupdates
                    resolve();
                }else{
                    reject(newError('Failedinupdatingpartners.'));
                }
            },function(type,err){reject();});
        });
    },

    //thisiscalledwhenanorderisremovedfromtheordercollection.Itensuresthatthereisalwaysanexisting
    //orderandavalidselectedorder
    on_removed_order:function(removed_order,index,reason){
        varorder_list=this.get_order_list();
        if((reason==='abandon'||removed_order.temporary)&&order_list.length>0){
            //whenweintentionallyremoveanunfinishedorder,andthereisanotherexistingone
            this.set_order(order_list[index]||order_list[order_list.length-1],{silent:true});
        }else{
            //whentheorderwasautomaticallyremovedaftercompletion,
            //orwhenweintentionallydeletetheonlyconcurrentorder
            this.add_new_order({silent:true});
        }
    },

    //returnstheuserwhoiscurrentlythecashierforthispointofsale
    get_cashier:function(){
        //resetthecashiertothecurrentuserifsessionisnew
        if(this.db.load('pos_session_id')!==this.pos_session.id){
            this.set_cashier(this.employee);
        }
        returnthis.db.get_cashier()||this.get('cashier')||this.employee;
    },
    //changesthecurrentcashier
    set_cashier:function(employee){
        this.set('cashier',employee);
        this.db.set_cashier(this.get('cashier'));
    },
    //createsanewemptyorderandsetsitasthecurrentorder
    add_new_order:function(options){
        varorder=newexports.Order({},{pos:this});
        this.get('orders').add(order);
        this.set('selectedOrder',order,options);
        returnorder;
    },
    /**
     *LoadthelocallysavedunpaidordersforthisPoSConfig.
     *
     *Firstloadallordersbelongingtothecurrentsession.
     *Secondloadallordersbelongingtothesameconfigbutfromothersessions,
     *Onlyifthoorderhasorderlines.
     */
    load_orders:asyncfunction(){
        varjsons=this.db.get_unpaid_orders();
        awaitthis._loadMissingProducts(jsons);
        varorders=[];

        for(vari=0;i<jsons.length;i++){
            varjson=jsons[i];
            if(json.pos_session_id===this.pos_session.id){
                orders.push(newexports.Order({},{
                    pos: this,
                    json:json,
                }));
            }
        }
        for(vari=0;i<jsons.length;i++){
            varjson=jsons[i];
            if(json.pos_session_id!==this.pos_session.id&&(json.lines.length>0||json.statement_ids.length>0)){
                orders.push(newexports.Order({},{
                    pos: this,
                    json:json,
                }));
            }elseif(json.pos_session_id!==this.pos_session.id){
                this.db.remove_unpaid_order(jsons[i]);
            }
        }

        orders=orders.sort(function(a,b){
            returna.sequence_number-b.sequence_number;
        });

        if(orders.length){
            this.get('orders').add(orders);
        }
    },
    async_loadMissingProducts(orders){
        constmissingProductIds=newSet([]);
        for(constorderoforders){
            for(constlineoforder.lines){
                constproductId=line[2].product_id;
                if(missingProductIds.has(productId))continue;
                if(!this.db.get_product_by_id(productId)){
                    missingProductIds.add(productId);
                }
            }
        }
        constproductModel=_.find(this.models,function(model){returnmodel.model==='product.product';});
        constfields=productModel.fields;
        constproducts=awaitthis.rpc({
            model:'product.product',
            method:'read',
            args:[[...missingProductIds],fields],
            context:Object.assign(this.session.user_context,{display_default_code:false}),
        });
        productModel.loaded(this,products);
    },
    set_start_order:function(){
        varorders=this.get('orders').models;

        if(orders.length&&!this.get('selectedOrder')){
            this.set('selectedOrder',orders[0]);
        }else{
            this.add_new_order();
        }
    },

    //returnthecurrentorder
    get_order:function(){
        returnthis.get('selectedOrder');
    },

    get_client:function(){
        varorder=this.get_order();
        if(order){
            returnorder.get_client();
        }
        returnnull;
    },

    //changethecurrentorder
    set_order:function(order,options){
        this.set({selectedOrder:order},options);
    },

    //returnthelistofunpaidorders
    get_order_list:function(){
        returnthis.get('orders').models;
    },

    //removesthecurrentorder
    delete_current_order:function(){
        varorder=this.get_order();
        if(order){
            order.destroy({'reason':'abandon'});
        }
    },

    _convert_product_img_to_base64:function(product,url){
        returnnewPromise(function(resolve,reject){
            varimg=newImage();

            img.onload=function(){
                varcanvas=document.createElement('CANVAS');
                varctx=canvas.getContext('2d');

                canvas.height=this.height;
                canvas.width=this.width;
                ctx.drawImage(this,0,0);

                vardataURL=canvas.toDataURL('image/jpeg');
                product.image_base64=dataURL;
                canvas=null;

                resolve();
            };
            img.crossOrigin='use-credentials';
            img.src=url;
        });
    },

    send_current_order_to_customer_facing_display:function(){
        varself=this;
        this.render_html_for_customer_facing_display().then(function(rendered_html){
            self.proxy.update_customer_facing_display(rendered_html);
        });
    },

    /**
     *@returns{Promise<string>}
     */
    render_html_for_customer_facing_display:function(){
        varself=this;
        varorder=this.get_order();
        varrendered_html=this.config.customer_facing_display_html;

        //Ifwe'reusinganexternaldeviceliketheIoTBox,we
        //cannotget/web/image?model=product.productbecausethe
        //IoTBoxisnotloggedinandthusdoesn'thavetheaccess
        //rightstoaccessproduct.product.Soinsteadwe'llbase64
        //encodeitandembeditintheHTML.
        varget_image_promises=[];

        if(order){
            order.get_orderlines().forEach(function(orderline){
                varproduct=orderline.product;
                varimage_url=`/web/image?model=product.product&field=image_128&id=${product.id}&write_date=${product.write_date}&unique=1`;

                //onlydownloadandconvertimageifwehaven'tdoneitbefore
                if(!product.image_base64){
                    get_image_promises.push(self._convert_product_img_to_base64(product,image_url));
                }
            });
        }

        //whenallimagesareloadedinproduct.image_base64
        returnPromise.all(get_image_promises).then(function(){
            varrendered_order_lines="";
            varrendered_payment_lines="";
            varorder_total_with_tax=self.format_currency(0);

            if(order){
                rendered_order_lines=QWeb.render('CustomerFacingDisplayOrderLines',{
                    'orderlines':order.get_orderlines(),
                    'pos':self,
                });
                rendered_payment_lines=QWeb.render('CustomerFacingDisplayPaymentLines',{
                    'order':order,
                    'pos':self,
                });
                order_total_with_tax=self.format_currency(order.get_total_with_tax());
            }

            var$rendered_html=$(rendered_html);
            $rendered_html.find('.pos_orderlines_list').html(rendered_order_lines);
            $rendered_html.find('.pos-total').find('.pos_total-amount').html(order_total_with_tax);
            varpos_change_title=$rendered_html.find('.pos-change_title').text();
            $rendered_html.find('.pos-paymentlines').html(rendered_payment_lines);
            $rendered_html.find('.pos-change_title').text(pos_change_title);

            //proponlyusesthefirstelementinasetofelements,
            //andthere'snoguaranteethat
            //customer_facing_display_htmliswrappedinasingle
            //rootelement.
            rendered_html=_.reduce($rendered_html,function(memory,current_element){
                returnmemory+$(current_element).prop('outerHTML');
            },"");//initialmemoryof""

            rendered_html=QWeb.render('CustomerFacingDisplayHead',{
                origin:window.location.origin
            })+rendered_html;
            returnrendered_html;
        });
    },

    //savestheorderlocallyandtrytosendittothebackend.
    //itreturnsapromisethatsucceedsafterhavingtriedtosendtheorderandalltheotherpendingorders.
    push_orders:function(order,opts){
        opts=opts||{};
        varself=this;

        if(order){
            this.db.add_order(order.export_as_JSON());
        }

        returnnewPromise(function(resolve,reject){
            self.flush_mutex.exec(function(){
                varflushed=self._flush_orders(self.db.get_orders(),opts);

                flushed.then(resolve,reject);

                returnflushed;
            });
        });
    },

    push_single_order:function(order,opts){
        opts=opts||{};
        constself=this;
        constorder_id=self.db.add_order(order.export_as_JSON());

        returnnewPromise(function(resolve,reject){
            self.flush_mutex.exec(function(){
                varorder=self.db.get_order(order_id);
                if(order){
                    varflushed=self._flush_orders([order],opts);
                }else{
                    varflushed=Promise.resolve([]);
                }
                flushed.then(resolve,reject);

                returnflushed;
            });
        });
    },

    //savestheorderlocallyandtrytosendittothebackendandmakeaninvoice
    //returnsapromisethatsucceedswhentheorderhasbeenpostedandsuccessfullygenerated
    //aninvoice.Thismethodcanfailinvariousways:
    //error-no-client:theordermusthaveanassociatedpartner_id.Youcanretrytomakeaninvoiceonce
    //    thiserrorissolved
    //error-transfer:therewasaconnectionerrorduringthetransfer.Youcanretrytomaketheinvoiceonce
    //    thenetworkconnectionisup

    push_and_invoice_order:function(order){
        varself=this;
        varinvoiced=newPromise(function(resolveInvoiced,rejectInvoiced){
            if(!order.get_client()){
                rejectInvoiced({code:400,message:'MissingCustomer',data:{}});
            }
            else{
                varorder_id=self.db.add_order(order.export_as_JSON());

                self.flush_mutex.exec(function(){
                    vardone= newPromise(function(resolveDone,rejectDone){
                        //sendtheordertotheserver
                        //wehavea30secondstimeoutonthispush.
                        //FIXME:iftheservertakesmorethan30secondstoaccepttheorder,
                        //theclientwillbelieveitwasn'tsuccessfullysent,andverybad
                        //thingswillhappenasaduplicatewillbesentnexttime
                        //sowemustmakesuretheserverdetectsandignoresduplicatedorders

                        vartransfer=self._flush_orders([self.db.get_order(order_id)],{timeout:30000,to_invoice:true});

                        transfer.catch(function(error){
                            rejectInvoiced(error);
                            rejectDone();
                        });

                        //onsuccess,gettheorderidgeneratedbytheserver
                        transfer.then(function(order_server_id){
                            //generatethepdfanddownloadit
                            if(order_server_id.length){
                                self.do_action('point_of_sale.pos_invoice_report',{additional_context:{
                                    active_ids:order_server_id,
                                }}).then(function(){
                                    resolveInvoiced(order_server_id);
                                    resolveDone();
                                }).guardedCatch(function(error){
                                    rejectInvoiced({code:401,message:'BackendInvoice',data:{order:order}});
                                    rejectDone();
                                });
                            }elseif(order_server_id.length){
                                resolveInvoiced(order_server_id);
                                resolveDone();
                            }else{
                                //Theorderhasbeenpushedseparatelyinbatchwhen
                                //theconnectioncameback.
                                //Theuserhastogotothebackendtoprinttheinvoice
                                rejectInvoiced({code:401,message:'BackendInvoice',data:{order:order}});
                                rejectDone();
                            }
                        });
                        returndone;
                    });
                });
            }
        });

        returninvoiced;
    },

    //wrapperaroundthe_save_to_serverthatupdatesthesynchstatuswidget
    //Resolvestothebackendidsofthesyncedorders.
    _flush_orders:function(orders,options){
        varself=this;
        this.set_synch('connecting',orders.length);

        returnthis._save_to_server(orders,options).then(function(server_ids){
            self.set_synch('connected');
            for(leti=0;i<server_ids.length;i++){
                self.validated_orders_name_server_id_map[server_ids[i].pos_reference]=server_ids[i].id;
            }
            return_.pluck(server_ids,'id');
        }).catch(function(error){
            self.set_synch(self.get('failed')?'error':'disconnected');
            returnPromise.reject(error);
        });
    },

    set_synch:function(status,pending){
        if(['connected','connecting','error','disconnected'].indexOf(status)===-1){
            console.error(status,'isnotaknownconnectionstate.');
        }
        pending=pending||this.db.get_orders().length+this.db.get_ids_to_remove_from_server().length;
        this.set('synch',{status,pending});
    },

    //sendanarrayoforderstotheserver
    //availableoptions:
    //-timeout:timeoutfortherpccallinms
    //returnsapromisethatresolveswiththelistof
    //servergeneratedidsforthesentorders
    _save_to_server:function(orders,options){
        if(!orders||!orders.length){
            returnPromise.resolve([]);
        }

        options=options||{};

        varself=this;
        vartimeout=typeofoptions.timeout==='number'?options.timeout:30000*orders.length;

        //Keeptheorderidsthatareabouttobesenttothe
        //backend.Inbetweencreate_from_uiandthesuccesscallback
        //newordersmayhavebeenaddedtoit.
        varorder_ids_to_sync=_.pluck(orders,'id');

        //wetrytosendtheorder.shadowpreventsaspinnerifittakestoolong.(unlesswearesendinganinvoice,
        //thenwewanttonotifytheuserthatwearewaitingonsomething)
        varargs=[_.map(orders,function(order){
                order.to_invoice=options.to_invoice||false;
                returnorder;
            })];
        args.push(options.draft||false);
        returnthis.rpc({
                model:'pos.order',
                method:'create_from_ui',
                args:args,
                kwargs:{context:this.session.user_context},
            },{
                timeout:timeout,
                shadow:!options.to_invoice
            })
            .then(function(server_ids){
                _.each(order_ids_to_sync,function(order_id){
                    self.db.remove_order(order_id);
                });
                self.set('failed',false);
                returnserver_ids;
            }).catch(function(reason){
                varerror=reason.message;
                console.warn('Failedtosendorders:',orders);
                if(error.code===200){   //BusinessLogicError,notaconnectionproblem
                    //Hideerrorifalreadyshownbefore...
                    if((!self.get('failed')||options.show_error)&&!options.to_invoice){
                        self.set('failed',error);
                        throwerror;
                    }
                }
                throwerror;
            });
    },

    /**
     *Removeorderswithgivenidsfromthedatabase.
     *@param{array<number>}server_idsidsoftheorderstoberemoved.
     *@param{dict}options.
     *@param{number}options.timeoutoptionaltimeoutparameterfortherpccall.
     *@return{Promise<array<number>>}returnsapromiseoftheidssuccessfullyremoved.
     */
    _remove_from_server:function(server_ids,options){
        options=options||{};
        if(!server_ids||!server_ids.length){
            returnPromise.resolve([]);
        }

        varself=this;
        vartimeout=typeofoptions.timeout==='number'?options.timeout:7500*server_ids.length;

        returnthis.rpc({
                model:'pos.order',
                method:'remove_from_ui',
                args:[server_ids],
                kwargs:{context:this.session.user_context},
            },{
                timeout:timeout,
                shadow:true,
            })
            .then(function(data){
                returnself._post_remove_from_server(server_ids,data)
            }).catch(function(reason){
                varerror=reason.message;
                if(error.code===200){   //BusinessLogicError,notaconnectionproblem
                    //ifwarningdonotneedtodisplaytraceback!!
                    if(error.data.exception_type=='warning'){
                        deleteerror.data.debug;
                    }
                }
                //importanttothrowerrorhereandlettherenderingcomponenthandlethe
                //error
                console.warn('Failedtoremoveorders:',server_ids);
                throwerror;
            });
    },

    //tooverride
    _post_remove_from_server(server_ids,data){
        this.db.set_ids_removed_from_server(server_ids);
        returnserver_ids;
    },

    scan_product:function(parsed_code){
        varselectedOrder=this.get_order();
        varproduct=this.db.get_product_by_barcode(parsed_code.base_code);

        if(!product){
            returnfalse;
        }

        if(parsed_code.type==='price'){
            selectedOrder.add_product(product,{price:parsed_code.value,extras:{price_manually_set:true}});
        }elseif(parsed_code.type==='weight'){
            selectedOrder.add_product(product,{quantity:parsed_code.value,merge:false});
        }elseif(parsed_code.type==='discount'){
            selectedOrder.add_product(product,{discount:parsed_code.value,merge:false});
        }else{
            selectedOrder.add_product(product);
        }
        returntrue;
    },

    //Exportsthepaidorders(theoneswaitingforinternetconnection)
    export_paid_orders:function(){
        returnJSON.stringify({
            'paid_orders': this.db.get_orders(),
            'session':     this.pos_session.name,
            'session_id':   this.pos_session.id,
            'date':        (newDate()).toUTCString(),
            'version':     this.version.server_version_info,
        },null,2);
    },

    //Exportstheunpaidorders(thetabs)
    export_unpaid_orders:function(){
        returnJSON.stringify({
            'unpaid_orders':this.db.get_unpaid_orders(),
            'session':      this.pos_session.name,
            'session_id':   this.pos_session.id,
            'date':         (newDate()).toUTCString(),
            'version':      this.version.server_version_info,
        },null,2);
    },

    //Thisimportspaidorunpaidordersfromajsonfilewhose
    //contentsareprovidedasthestringstr.
    //Itreturnsareportofwhatcouldandwhatcouldnotbe
    //imported.
    import_orders:function(str){
        varjson=JSON.parse(str);
        varreport={
            //Numberofpaidordersthatwereimported
            paid:0,
            //Numberofunpaidordersthatwereimported
            unpaid:0,
            //Ordersthatwerenotimportedbecausetheyalreadyexist(uidconflict)
            unpaid_skipped_existing:0,
            //Ordersthatwerenotimportedbecausetheybelongtoanothersession
            unpaid_skipped_session: 0,
            //Thelistofsessionidstowhichskippedordersbelong.
            unpaid_skipped_sessions:[],
        };

        if(json.paid_orders){
            for(vari=0;i<json.paid_orders.length;i++){
                this.db.add_order(json.paid_orders[i].data);
            }
            report.paid=json.paid_orders.length;
            this.push_orders();
        }

        if(json.unpaid_orders){

            varorders =[];
            varexisting=this.get_order_list();
            varexisting_uids={};
            varskipped_sessions={};

            for(vari=0;i<existing.length;i++){
                existing_uids[existing[i].uid]=true;
            }

            for(vari=0;i<json.unpaid_orders.length;i++){
                varorder=json.unpaid_orders[i];
                if(order.pos_session_id!==this.pos_session.id){
                    report.unpaid_skipped_session+=1;
                    skipped_sessions[order.pos_session_id]=true;
                }elseif(existing_uids[order.uid]){
                    report.unpaid_skipped_existing+=1;
                }else{
                    orders.push(newexports.Order({},{
                        pos:this,
                        json:order,
                    }));
                }
            }

            orders=orders.sort(function(a,b){
                returna.sequence_number-b.sequence_number;
            });

            if(orders.length){
                report.unpaid=orders.length;
                this.get('orders').add(orders);
            }

            report.unpaid_skipped_sessions=_.keys(skipped_sessions);
        }

        returnreport;
    },

    _load_orders:function(){
        varjsons=this.db.get_unpaid_orders();
        varorders=[];
        varnot_loaded_count=0;

        for(vari=0;i<jsons.length;i++){
            varjson=jsons[i];
            if(json.pos_session_id===this.pos_session.id){
                orders.push(newexports.Order({},{
                    pos: this,
                    json:json,
                }));
            }else{
                not_loaded_count+=1;
            }
        }

        if(not_loaded_count){
            console.info('Thereare'+not_loaded_count+'locallysavedunpaidordersbelongingtoanothersession');
        }

        orders=orders.sort(function(a,b){
            returna.sequence_number-b.sequence_number;
        });

        if(orders.length){
            this.get('orders').add(orders);
        }
    },
    /**
     *MirrorJSmethodof:
     *_compute_amountinaddons/account/models/account.py
     */
    _compute_all:function(tax,base_amount,quantity,price_exclude){
        if(price_exclude===undefined)
            varprice_include=tax.price_include;
        else
            varprice_include=!price_exclude;
        if(tax.amount_type==='fixed'){
            varsign_base_amount=Math.sign(base_amount)||1;
            //Sincebaseamounthasbeencomputedwithquantity
            //wetaketheabsofquantity
            //Samelogicasbb72dea98de4dae8f59e397f232a0636411d37ce
            returntax.amount*sign_base_amount*Math.abs(quantity);
        }
        if(tax.amount_type==='percent'&&!price_include){
            returnbase_amount*tax.amount/100;
        }
        if(tax.amount_type==='percent'&&price_include){
            returnbase_amount-(base_amount/(1+tax.amount/100));
        }
        if(tax.amount_type==='division'&&!price_include){
            returnbase_amount/(1-tax.amount/100)-base_amount;
        }
        if(tax.amount_type==='division'&&price_include){
            returnbase_amount-(base_amount*(tax.amount/100));
        }
        returnfalse;
    },
    /**
     *MirrorJSmethodof:
     *compute_allinaddons/account/models/account.py
     *
     *Readcommentsinthepythonsidemethodformoredetailsabouteachsub-methods.
     */
    compute_all:function(taxes,price_unit,quantity,currency_rounding,handle_price_include=true){
        varself=this;

        //1)Flattenthetaxes.

        var_collect_taxes=function(taxes,all_taxes){
            taxes.sort(function(tax1,tax2){
                returntax1.sequence-tax2.sequence;
            });
            _(taxes).each(function(tax){
                if(tax.amount_type==='group')
                    all_taxes=_collect_taxes(tax.children_tax_ids,all_taxes);
                else
                    all_taxes.push(tax);
            });
            returnall_taxes;
        }
        varcollect_taxes=function(taxes){
            return_collect_taxes(taxes,[]);
        }

        taxes=collect_taxes(taxes);

        //2)Dealwiththeroundingmethods

        varround_tax=this.company.tax_calculation_rounding_method!='round_globally';

        varinitial_currency_rounding=currency_rounding;
        if(!round_tax)
            currency_rounding=currency_rounding*0.00001;

        //3)Iteratethetaxesinthereversedsequenceordertoretrievetheinitialbaseofthecomputation.
        varrecompute_base=function(base_amount,fixed_amount,percent_amount,division_amount){
             return(base_amount-fixed_amount)/(1.0+percent_amount/100.0)*(100-division_amount)/100;
        }

        varbase=round_pr(price_unit*quantity,initial_currency_rounding);

        varsign=1;
        if(base<0){
            base=-base;
            sign=-1;
        }elseif(utils.float_is_zero(base,this.currency.decimals)&&quantity<0){
            sign=-1
        }

        vartotal_included_checkpoints={};
        vari=taxes.length-1;
        varstore_included_tax_total=true;

        varincl_fixed_amount=0.0;
        varincl_percent_amount=0.0;
        varincl_division_amount=0.0;

        varcached_tax_amounts={};
        if(handle_price_include){
            _(taxes.reverse()).each(function(tax){
                if(tax.include_base_amount){
                    base=recompute_base(base,incl_fixed_amount,incl_percent_amount,incl_division_amount);
                    incl_fixed_amount=0.0;
                    incl_percent_amount=0.0;
                    incl_division_amount=0.0;
                    store_included_tax_total=true;
                }
                if(tax.price_include){
                    if(tax.amount_type==='percent')
                        incl_percent_amount+=tax.amount;
                    elseif(tax.amount_type==='division')
                        incl_division_amount+=tax.amount;
                    elseif(tax.amount_type==='fixed')
                        incl_fixed_amount+=Math.abs(quantity)*tax.amount
                    else{
                        vartax_amount=self._compute_all(tax,base,quantity);
                        incl_fixed_amount+=tax_amount;
                        cached_tax_amounts[i]=tax_amount;
                    }
                    if(store_included_tax_total){
                        total_included_checkpoints[i]=base;
                        store_included_tax_total=false;
                    }
                }
                i-=1;
            });
        }

        vartotal_excluded=round_pr(recompute_base(base,incl_fixed_amount,incl_percent_amount,incl_division_amount),initial_currency_rounding);
        vartotal_included=total_excluded;

        //4)Iteratethetaxesinthesequenceordertofillmissingbase/amountvalues.

        base=total_excluded;

        varskip_checkpoint=false;

        vartaxes_vals=[];
        i=0;
        varcumulated_tax_included_amount=0;
        _(taxes.reverse()).each(function(tax){
            if(!skip_checkpoint&&tax.price_include&&total_included_checkpoints[i]!==undefined){
                vartax_amount=total_included_checkpoints[i]-(base+cumulated_tax_included_amount);
                cumulated_tax_included_amount=0;
            }else
                vartax_amount=self._compute_all(tax,base,quantity,true);

            tax_amount=round_pr(tax_amount,currency_rounding);

            if(tax.price_include&&total_included_checkpoints[i]===undefined)
                cumulated_tax_included_amount+=tax_amount;

            taxes_vals.push({
                'id':tax.id,
                'name':tax.name,
                'amount':sign*tax_amount,
                'base':sign*round_pr(base,currency_rounding),
            });

            if(tax.include_base_amount){
                base+=tax_amount;
                if(!tax.price_include)
                    skip_checkpoint=true;
            }

            total_included+=tax_amount;
            i+=1;
        });

        return{
            'taxes':taxes_vals,
            'total_excluded':sign*round_pr(total_excluded,this.currency.rounding),
            'total_included':sign*round_pr(total_included,this.currency.rounding),
        }
    },

    _map_tax_fiscal_position:function(tax,order=false){
        varself=this;
        varcurrent_order=order||this.get_order();
        varorder_fiscal_position=current_order&&current_order.fiscal_position;
        vartaxes=[];

        if(order_fiscal_position){
            vartax_mappings=_.filter(order_fiscal_position.fiscal_position_taxes_by_id,function(fiscal_position_tax){
                returnfiscal_position_tax.tax_src_id[0]===tax.id;
            });

            if(tax_mappings&&tax_mappings.length){
                _.each(tax_mappings,function(tm){
                    if(tm.tax_dest_id){
                        vartaxe=self.taxes_by_id[tm.tax_dest_id[0]];
                        if(taxe){
                            taxes.push(taxe);
                        }
                    }
                });
            }else{
                taxes.push(tax);
            }
        }else{
            taxes.push(tax);
        }

        returntaxes;
    },

    get_taxes_after_fp:function(taxes_ids,order=false){
        varself=this;
        vartaxes= this.taxes;
        varproduct_taxes=[];
        _(taxes_ids).each(function(el){
            vartax=_.detect(taxes,function(t){
                returnt.id===el;
            });
            product_taxes.push.apply(product_taxes,self._map_tax_fiscal_position(tax,order));
        });
        product_taxes=_.uniq(product_taxes,function(tax){returntax.id;});
        returnproduct_taxes;
      },

    /**
     *Directlycallstherequestedservice,insteadoftriggeringa
     *'call_service'eventup,whichwouldn'tworkasserviceshavenoparent
     *
     *@param{FlectraEvent}ev
     */
    _trigger_up:function(ev){
        if(ev.is_stopped()){
            return;
        }
        constpayload=ev.data;
        if(ev.name==='call_service'){
            letargs=payload.args||[];
            if(payload.service==='ajax'&&payload.method==='rpc'){
                //ajaxserviceusesanextra'target'argumentforrpc
                args=args.concat(ev.target);
            }
            constservice=this.env.services[payload.service];
            constresult=service[payload.method].apply(service,args);
            payload.callback(result);
        }
    },

    electronic_payment_interfaces:{},

    format_currency:function(amount,precision){
        varcurrency=
            this&&this.currency
                ?this.currency
                :{symbol:'$',position:'after',rounding:0.01,decimals:2};

        amount=this.format_currency_no_symbol(amount,precision,currency);

        if(currency.position==='after'){
            returnamount+''+(currency.symbol||'');
        }else{
            return(currency.symbol||'')+''+amount;
        }
    },

    format_currency_no_symbol:function(amount,precision,currency){
        if(!currency){
            currency=
                this&&this.currency
                    ?this.currency
                    :{symbol:'$',position:'after',rounding:0.01,decimals:2};
        }
        vardecimals=currency.decimals;

        if(precision&&this.dp[precision]!==undefined){
            decimals=this.dp[precision];
        }

        if(typeofamount==='number'){
            amount=round_di(amount,decimals).toFixed(decimals);
            amount=field_utils.format.float(round_di(amount,decimals),{
                digits:[69,decimals],
            });
        }

        returnamount;
    },

    format_pr:function(value,precision){
        vardecimals=
            precision>0
                ?Math.max(0,Math.ceil(Math.log(1.0/precision)/Math.log(10)))
                :0;
        returnvalue.toFixed(decimals);
    },

    /**
     *(value=1.0000,decimals=2)=>'1'
     *(value=1.1234,decimals=2)=>'1.12'
     *@param{number}valueamounttoformat
     */
    formatFixed:function(value){
        constcurrency=this.currency||{decimals:2};
        return`${Number(value.toFixed(currency.decimals||0))}`;
    },

    disallowLineQuantityChange(){
        returnfalse;
    },

    getCurrencySymbol(){
        returnthis.currency?this.currency.symbol:'$';
    },

    htmlToImgLetterRendering(){
        returnfalse;
    },
});

/**
 *CallthisfunctiontomapyourPaymentInterfaceimplementationto
 *theuse_payment_terminalfield.WhenthePOSloadsitwilltake
 *careofinstantiatingyourinterfaceandsettingitontheright
 *paymentmethods.
 *
 *@param{string}use_payment_terminal-valueusedinthe
 *use_payment_terminalselectionfield
 *
 *@param{Object}ImplementedPaymentInterface-implemented
 *PaymentInterface
 */
exports.register_payment_method=function(use_payment_terminal,ImplementedPaymentInterface){
    exports.PosModel.prototype.electronic_payment_interfaces[use_payment_terminal]=ImplementedPaymentInterface;
};

//Addfieldstothelistofreadfieldswhenamodelisloaded
//bythepointofsale.
//e.g:module.load_fields("product.product",['price','category'])

exports.load_fields=function(model_name,fields){
    if(!(fieldsinstanceofArray)){
        fields=[fields];
    }

    varmodels=exports.PosModel.prototype.models;
    for(vari=0;i<models.length;i++){
        varmodel=models[i];
        if(model.model===model_name){
            //if'fields'isemptyallfieldsareloaded,sowedonotneed
            //tomodifythearray
            if((model.fieldsinstanceofArray)&&model.fields.length>0){
                model.fields=model.fields.concat(fields||[]);
            }
        }
    }
};

//Loadsopenerpmodelsatthepointofsalestartup.
//load_modelstakeanarrayofmodelloaderdeclarations.
//-Themodelswillbeloadedinthearrayorder.
//-Ifnoopenerpmodelnameisprovided,noserverdata
//  willbeloaded,butthesystemcanbeusedtopreprocess
//  databeforeload.
//-loaderargumentscanbefunctionsthatreturnadynamic
//  value.ThefunctiontakesthePosModelasthefirstargument
//  andatemporaryobjectthatissharedbyallmodels,andcan
//  beusedtostoretransientinformationbetweenmodelloads.
//-Thereisnodependencymanagement.Themodelsmustbeloaded
//  intherightorder.Newlyaddedmodelsareloadedattheend
//  buttheafter/beforeoptionscanbeusedtoloaddirectly
//  before/afteranothermodel.
//
//models:[{
// model:[string]thenameoftheopenerpmodeltoload.
// label:[string]Thelabeldisplayedduringload.
// fields:[[string]|function]thelistoffieldstobeloaded.
//         EmptyArray/Nullloadsallfields.
// order: [[string]|function]themodelswillbeorderedby
//         theprovidedfields
// domain:[domain|function]thedomainthatdetermineswhat
//         modelsneedtobeloaded.Nullloadseverything
// ids:   [[id]|function]theidlistofthemodelsthatmust
//         beloaded.Overridesdomain.
// context:[Dict|function]theopenerpcontextforthemodelread
// condition:[function]donotloadthemodelsifitevaluatesto
//            false.
// loaded:[function(self,model)]thisfunctioniscalledoncethe
//         modelshavebeenloaded,withthedataassecondargument
//         ifthefunctionreturnsapromise,thenextmodelwill
//         waituntilitresolvesbeforeloading.
//}]
//
//options:
//  before:[string]Themodelwillbeloadedbeforethenamedmodels
//          (appliestobothmodelnameandlabel)
//  after: [string]Themodelwillbeloadedafterthe(lastloaded)
//          namedmodel.(appliestobothmodelnameandlabel)
//
exports.load_models=function(models,options){
    options=options||{};
    if(!(modelsinstanceofArray)){
        models=[models];
    }

    varpmodels=exports.PosModel.prototype.models;
    varindex=pmodels.length;
    if(options.before){
        for(vari=0;i<pmodels.length;i++){
            if(   pmodels[i].model===options.before||
                    pmodels[i].label===options.before){
                index=i;
                break;
            }
        }
    }elseif(options.after){
        for(vari=0;i<pmodels.length;i++){
            if(   pmodels[i].model===options.after||
                    pmodels[i].label===options.after){
                index=i+1;
            }
        }
    }
    pmodels.splice.apply(pmodels,[index,0].concat(models));
};

exports.Product=Backbone.Model.extend({
    initialize:function(attr,options){
        _.extend(this,options);
    },
    isAllowOnlyOneLot:function(){
        constproductUnit=this.get_unit();
        returnthis.tracking==='lot'||!productUnit||!productUnit.is_pos_groupable;
    },
    get_unit:function(){
        varunit_id=this.uom_id;
        if(!unit_id){
            returnundefined;
        }
        unit_id=unit_id[0];
        if(!this.pos){
            returnundefined;
        }
        returnthis.pos.units_by_id[unit_id];
    },
    //Portofget_product_priceonproduct.pricelist.
    //
    //AnythingrelatedtoUOMcanbeignored,thePOSwillalwaysuse
    //thedefaultUOMsetontheproductandtheusercannotchange
    //it.
    //
    //Pricelistitemsdonothavetobesorted.All
    //product.pricelist.itemrecordsareloadedwithasearch_read
    //andwereautomaticallysortedbasedontheir_orderbythe
    //ORM.Afterthattheyareaddedinthisordertothepricelists.
    get_price:function(pricelist,quantity,price_extra){
        varself=this;
        vardate=moment();

        //Incaseofnestedpricelists,itisnecessarythatallpricelistsaremadeavailablein
        //thePOS.Displayabasicalerttotheuserinthiscase.
        if(pricelist===undefined){
            alert(_t(
                'Anerroroccurredwhenloadingproductprices.'+
                'MakesureallpricelistsareavailableinthePOS.'
            ));
        }

        varcategory_ids=[];
        varcategory=this.categ;
        while(category){
            category_ids.push(category.id);
            category=category.parent;
        }

        varpricelist_items=_.filter(pricelist.items,function(item){
            return(!item.product_tmpl_id||item.product_tmpl_id[0]===self.product_tmpl_id)&&
                   (!item.product_id||item.product_id[0]===self.id)&&
                   (!item.categ_id||_.contains(category_ids,item.categ_id[0]))&&
                   (!item.date_start||moment.utc(item.date_start).isSameOrBefore(date))&&
                   (!item.date_end||moment.utc(item.date_end).isSameOrAfter(date));
        });

        varprice=self.lst_price;
        if(price_extra){
            price+=price_extra;
        }
        _.find(pricelist_items,function(rule){
            if(rule.min_quantity&&quantity<rule.min_quantity){
                returnfalse;
            }

            if(rule.base==='pricelist'){
                price=self.get_price(rule.base_pricelist,quantity);
            }elseif(rule.base==='standard_price'){
                price=self.standard_price;
            }

            if(rule.compute_price==='fixed'){
                price=rule.fixed_price;
                returntrue;
            }elseif(rule.compute_price==='percentage'){
                price=price-(price*(rule.percent_price/100));
                returntrue;
            }else{
                varprice_limit=price;
                price=price-(price*(rule.price_discount/100));
                if(rule.price_round){
                    price=round_pr(price,rule.price_round);
                }
                if(rule.price_surcharge){
                    price+=rule.price_surcharge;
                }
                if(rule.price_min_margin){
                    price=Math.max(price,price_limit+rule.price_min_margin);
                }
                if(rule.price_max_margin){
                    price=Math.min(price,price_limit+rule.price_max_margin);
                }
                returntrue;
            }

            returnfalse;
        });

        //Thisreturnvaluehastoberoundedwithround_dibefore
        //beingusedfurther.Notethatthiscannothappenhere,
        //becauseitwouldcauseinconsistencieswiththebackendfor
        //pricelistthathavebase=='pricelist'.
        returnprice;
    },

    get_display_price:function(pricelist,quantity){
        if(this.pos.config.iface_tax_included==='total'){
            consttaxes=this.pos.get_taxes_after_fp(this.taxes_id);
            constallPrices=this.pos.compute_all(taxes,this.get_price(pricelist,quantity),1,this.pos.currency.rounding);
            returnallPrices.total_included;
        }else{
            returnthis.get_price(pricelist,quantity);
        }
    }
});

varorderline_id=1;

//Anorderlinerepresentoneelementofthecontentofaclient'sshoppingcart.
//Anorderlinecontainsaproduct,itsquantity,itsprice,discount.etc.
//AnOrdercontainszeroormoreOrderlines.
exports.Orderline=Backbone.Model.extend({
    initialize:function(attr,options){
        this.pos  =options.pos;
        this.order=options.order;
        if(options.json){
            try{
                this.init_from_JSON(options.json);
            }catch(error){
                console.error('ERROR:attemptingtorecoverproductID',options.json.product_id,
                    'notavailableinthepointofsale.Correcttheproductorcleanthebrowsercache.');
            }
            return;
        }
        this.product=options.product;
        this.set_product_lot(this.product);
        this.set_quantity(1);
        this.discount=0;
        this.discountStr='0';
        this.selected=false;
        this.description='';
        this.price_extra=0;
        this.full_product_name='';
        this.id=orderline_id++;
        this.price_manually_set=false;

        if(options.price){
            this.set_unit_price(options.price);
        }else{
            this.set_unit_price(this.product.get_price(this.order.pricelist,this.get_quantity()));
        }
    },
    init_from_JSON:function(json){
        this.product=this.pos.db.get_product_by_id(json.product_id);
        this.set_product_lot(this.product);
        this.price=json.price_unit;
        this.set_discount(json.discount);
        this.set_quantity(json.qty,'donotrecomputeunitprice');
        this.set_description(json.description);
        this.set_price_extra(json.price_extra);
        this.set_full_product_name(json.full_product_name);
        this.id=json.id?json.id:orderline_id++;
        orderline_id=Math.max(this.id+1,orderline_id);
        varpack_lot_lines=json.pack_lot_ids;
        for(vari=0;i<pack_lot_lines.length;i++){
            varpacklotline=pack_lot_lines[i][2];
            varpack_lot_line=newexports.Packlotline({},{'json':_.extend({...packlotline},{'order_line':this})});
            this.pack_lot_lines.add(pack_lot_line);
        }
    },
    clone:function(){
        varorderline=newexports.Orderline({},{
            pos:this.pos,
            order:this.order,
            product:this.product,
            price:this.price,
        });
        orderline.order=null;
        orderline.quantity=this.quantity;
        orderline.quantityStr=this.quantityStr;
        orderline.discount=this.discount;
        orderline.price=this.price;
        orderline.selected=false;
        orderline.price_manually_set=this.price_manually_set;
        returnorderline;
    },
    getPackLotLinesToEdit:function(isAllowOnlyOneLot){
        constcurrentPackLotLines=this.pack_lot_lines.models;
        letnExtraLines=Math.abs(this.quantity)-currentPackLotLines.length;
        nExtraLines=Math.ceil(nExtraLines);
        nExtraLines=nExtraLines>0?nExtraLines:1;
        consttempLines=currentPackLotLines
            .map(lotLine=>({
                id:lotLine.cid,
                text:lotLine.get('lot_name'),
            }))
            .concat(
                Array.from(Array(nExtraLines)).map(_=>({
                    text:'',
                }))
            );
        returnisAllowOnlyOneLot?[tempLines[0]]:tempLines;
    },
    /**
     *@param{modifiedPackLotLines,newPackLotLines}
     *   @param{Object}modifiedPackLotLineskey-valuepairofString(thecid)&String(thenewlot_name)
     *   @param{Array}newPackLotLinesarrayof{lot_name:String}
     */
    setPackLotLines:function({modifiedPackLotLines,newPackLotLines}){
        //Setthenewvaluesformodifiedlotlines.
        letlotLinesToRemove=[];
        for(letlotLineofthis.pack_lot_lines.models){
            constmodifiedLotName=modifiedPackLotLines[lotLine.cid];
            if(modifiedLotName){
                lotLine.set({lot_name:modifiedLotName});
            }else{
                //WeshouldnotcalllotLine.remove()herebecause
                //wedon'twanttomutatethearraywhileloopingthruit.
                lotLinesToRemove.push(lotLine);
            }
        }

        //Removethosethatneededtoberemoved.
        for(letlotLineoflotLinesToRemove){
            lotLine.remove();
        }

        //Createnewpacklotlines.
        letnewPackLotLine;
        for(letnewLotLineofnewPackLotLines){
            newPackLotLine=newexports.Packlotline({},{order_line:this});
            newPackLotLine.set({lot_name:newLotLine.lot_name});
            this.pack_lot_lines.add(newPackLotLine);
        }

        //Setthequantityofthelinebasedonnumberofpacklots.
        if(!this.product.to_weight){
            this.pack_lot_lines.set_quantity_by_lot();
        }
    },
    set_product_lot:function(product){
        this.has_product_lot=product.tracking!=='none';
        this.pack_lot_lines =this.has_product_lot&&newPacklotlineCollection(null,{'order_line':this});
    },
    //setsadiscount[0,100]%
    set_discount:function(discount){
        varparsed_discount=typeof(discount)==='number'?discount:isNaN(parseFloat(discount))?0:field_utils.parse.float(''+discount);
        vardisc=Math.min(Math.max(parsed_discount||0,0),100);
        this.discount=disc;
        this.discountStr=''+disc;
        this.trigger('change',this);
    },
    //returnsthediscount[0,100]%
    get_discount:function(){
        returnthis.discount;
    },
    get_discount_str:function(){
        returnthis.discountStr;
    },
    set_description:function(description){
        this.description=description||'';
    },
    set_price_extra:function(price_extra){
        this.price_extra=parseFloat(price_extra)||0.0;
    },
    set_full_product_name:function(full_product_name){
        this.full_product_name=full_product_name||'';
    },
    get_price_extra:function(){
        returnthis.price_extra;
    },
    //setsthequantityoftheproduct.Thequantitywillberoundedaccordingtothe
    //product'sunityofmeasureproperties.Quantitiesgreaterthanzerowillnotget
    //roundedtozero
    set_quantity:function(quantity,keep_price){
        this.order.assert_editable();
        if(quantity==='remove'){
            this.order.remove_orderline(this);
            return;
        }else{
            varquant=typeof(quantity)==='number'?quantity:(field_utils.parse.float(''+quantity)||0);
            varunit=this.get_unit();
            if(unit){
                if(unit.rounding){
                    vardecimals=this.pos.dp['ProductUnitofMeasure'];
                    varrounding=Math.max(unit.rounding,Math.pow(10,-decimals));
                    this.quantity   =round_pr(quant,rounding);
                    this.quantityStr=field_utils.format.float(this.quantity,{digits:[69,decimals]});
                }else{
                    this.quantity   =round_pr(quant,1);
                    this.quantityStr=this.quantity.toFixed(0);
                }
            }else{
                this.quantity   =quant;
                this.quantityStr=''+this.quantity;
            }
        }

        //justlikeinsale.orderchangingthequantitywillrecomputetheunitprice
        if(!keep_price&&!this.price_manually_set&&!(
            this.pos.config.product_configurator&&_.some(this.product.attribute_line_ids,(id)=>idinthis.pos.attributes_by_ptal_id))){
            this.set_unit_price(this.product.get_price(this.order.pricelist,this.get_quantity(),this.get_price_extra()));
            this.order.fix_tax_included_price(this);
        }
        this.trigger('change',this);
    },
    //returnthequantityofproduct
    get_quantity:function(){
        returnthis.quantity;
    },
    get_quantity_str:function(){
        returnthis.quantityStr;
    },
    get_quantity_str_with_unit:function(){
        varunit=this.get_unit();
        if(unit&&!unit.is_pos_groupable){
            returnthis.quantityStr+''+unit.name;
        }else{
            returnthis.quantityStr;
        }
    },

    get_lot_lines:function(){
        returnthis.pack_lot_lines.models;
    },

    get_required_number_of_lots:function(){
        varlots_required=1;

        if(this.product.tracking=='serial'){
            lots_required=Math.abs(this.quantity);
        }

        returnlots_required;
    },

    has_valid_product_lot:function(){
        if(!this.has_product_lot){
            returntrue;
        }
        varvalid_product_lot=this.pack_lot_lines.get_valid_lots();
        returnthis.get_required_number_of_lots()===valid_product_lot.length;
    },

    //returntheunitofmeasureoftheproduct
    get_unit:function(){
        returnthis.product.get_unit();
    },
    //returntheproductofthisorderline
    get_product:function(){
        returnthis.product;
    },
    get_full_product_name:function(){
        if(this.full_product_name){
            returnthis.full_product_name
        }
        varfull_name=this.product.display_name;
        if(this.description){
            full_name+=`(${this.description})`;
        }
        returnfull_name;
    },
    //selectsordeselectsthisorderline
    set_selected:function(selected){
        this.selected=selected;
        //thistriggeralsotriggersthechangeeventofthecollection.
        this.trigger('change',this);
        this.trigger('new-orderline-selected');
    },
    //returnstrueifthisorderlineisselected
    is_selected:function(){
        returnthis.selected;
    },
    //whenweaddanneworderlinewewanttomergeitwiththelastlinetoseereducethenumberofitems
    //intheorderline.Thisreturnstrueifitmakessensetomergethetwo
    can_be_merged_with:function(orderline){
        varprice=parseFloat(round_di(this.price||0,this.pos.dp['ProductPrice']).toFixed(this.pos.dp['ProductPrice']));
        varorder_line_price=orderline.get_product().get_price(orderline.order.pricelist,this.get_quantity());
        order_line_price=round_di(orderline.compute_fixed_price(order_line_price),this.pos.currency.decimals);
        if(this.get_product().id!==orderline.get_product().id){   //onlyorderlineofthesameproductcanbemerged
            returnfalse;
        }elseif(!this.get_unit()||!this.get_unit().is_pos_groupable){
            returnfalse;
        }elseif(this.get_discount()>0){            //wedon'tmergediscountedorderlines
            returnfalse;
        }elseif(!utils.float_is_zero(price-order_line_price-orderline.get_price_extra(),
                    this.pos.currency.decimals)){
            returnfalse;
        }elseif(this.product.tracking=='lot'&&(this.pos.picking_type.use_create_lots||this.pos.picking_type.use_existing_lots)){
            returnfalse;
        }elseif(this.description!==orderline.description){
            returnfalse;
        }else{
            returntrue;
        }
    },
    merge:function(orderline){
        this.order.assert_editable();
        this.set_quantity(this.get_quantity()+orderline.get_quantity());
    },
    export_as_JSON:function(){
        varpack_lot_ids=[];
        if(this.has_product_lot){
            this.pack_lot_lines.each(_.bind(function(item){
                returnpack_lot_ids.push([0,0,item.export_as_JSON()]);
            },this));
        }
        return{
            qty:this.get_quantity(),
            price_unit:this.get_unit_price(),
            price_subtotal:this.get_price_without_tax(),
            price_subtotal_incl:this.get_price_with_tax(),
            discount:this.get_discount(),
            product_id:this.get_product().id,
            tax_ids:[[6,false,_.map(this.get_applicable_taxes(),function(tax){returntax.id;})]],
            id:this.id,
            pack_lot_ids:pack_lot_ids,
            description:this.description,
            full_product_name:this.get_full_product_name(),
            price_extra:this.get_price_extra(),
        };
    },
    //usedtocreateajsonoftheticket,tobesenttotheprinter
    export_for_printing:function(){
        return{
            id:this.id,
            quantity:          this.get_quantity(),
            unit_name:         this.get_unit().name,
            is_in_unit:        this.get_unit().id==this.pos.uom_unit_id,
            price:             this.get_unit_display_price(),
            discount:          this.get_discount(),
            product_name:      this.get_product().display_name,
            product_name_wrapped:this.generate_wrapped_product_name(),
            price_lst:         this.get_lst_price(),
            display_discount_policy:   this.display_discount_policy(),
            price_display_one: this.get_display_price_one(),
            price_display:    this.get_display_price(),
            price_with_tax:   this.get_price_with_tax(),
            price_without_tax: this.get_price_without_tax(),
            price_with_tax_before_discount: this.get_price_with_tax_before_discount(),
            tax:               this.get_tax(),
            product_description:     this.get_product().description,
            product_description_sale:this.get_product().description_sale,
            pack_lot_lines:     this.get_lot_lines()
        };
    },
    generate_wrapped_product_name:function(){
        varMAX_LENGTH=24;//40*lineratioof.6
        varwrapped=[];
        varname=this.get_full_product_name();
        varcurrent_line="";

        while(name.length>0){
            varspace_index=name.indexOf("");

            if(space_index===-1){
                space_index=name.length;
            }

            if(current_line.length+space_index>MAX_LENGTH){
                if(current_line.length){
                    wrapped.push(current_line);
                }
                current_line="";
            }

            current_line+=name.slice(0,space_index+1);
            name=name.slice(space_index+1);
        }

        if(current_line.length){
            wrapped.push(current_line);
        }

        returnwrapped;
    },
    //changesthebasepriceoftheproductforthisorderline
    set_unit_price:function(price){
        this.order.assert_editable();
        varparsed_price=!isNaN(price)?
            price:
            isNaN(parseFloat(price))?0:field_utils.parse.float(''+price)
        this.price=round_di(parsed_price||0,this.pos.dp['ProductPrice']);
        this.trigger('change',this);
    },
    get_unit_price:function(){
        vardigits=this.pos.dp['ProductPrice'];
        //roundandtruncatetomimic_symbol_setbehavior
        returnparseFloat(round_di(this.price||0,digits).toFixed(digits));
    },
    get_unit_display_price:function(){
        if(this.pos.config.iface_tax_included==='total'){
            varquantity=this.quantity;
            this.quantity=1.0;
            varprice=this.get_all_prices().priceWithTax;
            this.quantity=quantity;
            returnprice;
        }else{
            returnthis.get_unit_price();
        }
    },
    get_base_price:   function(){
        varrounding=this.pos.currency.rounding;
        returnround_pr(this.get_unit_price()*this.get_quantity()*(1-this.get_discount()/100),rounding);
    },
    get_taxes_after_fp:function(taxes_ids){
        returnthis.pos.get_taxes_after_fp(taxes_ids,this.order);
    },
    get_display_price_one:function(){
        varrounding=this.pos.currency.rounding;
        varprice_unit=this.get_unit_price();
        if(this.pos.config.iface_tax_included!=='total'){
            returnround_pr(price_unit*(1.0-(this.get_discount()/100.0)),rounding);
        }else{
            varproduct= this.get_product();
            vartaxes_ids=product.taxes_id;
            varproduct_taxes=this.get_taxes_after_fp(taxes_ids);
            varall_taxes=this.compute_all(product_taxes,price_unit,1,this.pos.currency.rounding);

            returnround_pr(all_taxes.total_included*(1-this.get_discount()/100),rounding);
        }
    },
    get_display_price:function(){
        if(this.pos.config.iface_tax_included==='total'){
            returnthis.get_price_with_tax();
        }else{
            returnthis.get_base_price();
        }
    },
    get_taxed_lst_unit_price:function(){
        varlst_price=this.compute_fixed_price(this.get_lst_price());
        if(this.pos.config.iface_tax_included==='total'){
            varproduct= this.get_product();
            vartaxes_ids=product.taxes_id;
            varproduct_taxes=this.get_taxes_after_fp(taxes_ids);
            returnthis.compute_all(product_taxes,lst_price,1,this.pos.currency.rounding).total_included;
        }
        returnlst_price;
    },
    get_price_without_tax:function(){
        returnthis.get_all_prices().priceWithoutTax;
    },
    get_price_with_tax:function(){
        returnthis.get_all_prices().priceWithTax;
    },
    get_price_with_tax_before_discount:function(){
        returnthis.get_all_prices().priceWithTaxBeforeDiscount;
    },
    get_tax:function(){
        returnthis.get_all_prices().tax;
    },
    get_applicable_taxes:function(){
        vari;
        //Shenaningansbecauseweneed
        //tokeepthetaxesordering.
        varptaxes_ids=this.get_product().taxes_id;
        varptaxes_set={};
        for(i=0;i<ptaxes_ids.length;i++){
            ptaxes_set[ptaxes_ids[i]]=true;
        }
        vartaxes=[];
        for(i=0;i<this.pos.taxes.length;i++){
            if(ptaxes_set[this.pos.taxes[i].id]){
                taxes.push(this.pos.taxes[i]);
            }
        }
        returntaxes;
    },
    get_tax_details:function(){
        returnthis.get_all_prices().taxDetails;
    },
    get_taxes:function(){
        vartaxes_ids=this.get_product().taxes_id;
        vartaxes=[];
        for(vari=0;i<taxes_ids.length;i++){
            if(this.pos.taxes_by_id[taxes_ids[i]]){
                taxes.push(this.pos.taxes_by_id[taxes_ids[i]]);
            }
        }
        returntaxes;
    },
    _map_tax_fiscal_position:function(tax,order=false){
        returnthis.pos._map_tax_fiscal_position(tax,order);
    },
    /**
     *MirrorJSmethodof:
     *_compute_amountinaddons/account/models/account.py
     */
    _compute_all:function(tax,base_amount,quantity,price_exclude){
        returnthis.pos._compute_all(tax,base_amount,quantity,price_exclude)
    },
    /**
     *MirrorJSmethodof:
     *compute_allinaddons/account/models/account.py
     *
     *Readcommentsinthepythonsidemethodformoredetailsabouteachsub-methods.
     */
    compute_all:function(taxes,price_unit,quantity,currency_rounding,handle_price_include=true){
        returnthis.pos.compute_all(taxes,price_unit,quantity,currency_rounding,handle_price_include)

    },
    get_all_prices:function(){

        varprice_unit=this.get_unit_price()*(1.0-(this.get_discount()/100.0));
        vartaxtotal=0;

        varproduct= this.get_product();
        vartaxes_ids=_.filter(product.taxes_id,t=>tinthis.pos.taxes_by_id);
        vartaxdetail={};
        varproduct_taxes=this.get_taxes_after_fp(taxes_ids);

        varall_taxes=this.compute_all(product_taxes,price_unit,this.get_quantity(),this.pos.currency.rounding);
        varall_taxes_before_discount=this.compute_all(product_taxes,this.get_unit_price(),this.get_quantity(),this.pos.currency.rounding);
        _(all_taxes.taxes).each(function(tax){
            taxtotal+=tax.amount;
            taxdetail[tax.id]=tax.amount;
        });

        return{
            "priceWithTax":all_taxes.total_included,
            "priceWithoutTax":all_taxes.total_excluded,
            "priceSumTaxVoid":all_taxes.total_void,
            "priceWithTaxBeforeDiscount":all_taxes_before_discount.total_included,
            "tax":taxtotal,
            "taxDetails":taxdetail,
        };
    },
    display_discount_policy:function(){
        returnthis.order.pricelist.discount_policy;
    },
    compute_fixed_price:function(price){
        varorder=this.order;
        if(order.fiscal_position){
            vartaxes=this.get_taxes();
            varmapped_included_taxes=[];
            varnew_included_taxes=[];
            varself=this;
            _(taxes).each(function(tax){
                varline_taxes=self._map_tax_fiscal_position(tax,order);
                if(line_taxes.length&&line_taxes[0].price_include){
                    new_included_taxes=new_included_taxes.concat(line_taxes);
                }
                if(tax.price_include&&!_.contains(line_taxes,tax)){
                    mapped_included_taxes.push(tax);
                }
            });

            if(mapped_included_taxes.length>0){
                if(new_included_taxes.length>0){
                    varprice_without_taxes=this.compute_all(mapped_included_taxes,price,1,order.pos.currency.rounding,true).total_excluded
                    returnthis.compute_all(new_included_taxes,price_without_taxes,1,order.pos.currency.rounding,false).total_included
                }
                else{
                    returnthis.compute_all(mapped_included_taxes,price,1,order.pos.currency.rounding,true).total_excluded;
                }
            }
        }
        returnprice;
    },
    get_fixed_lst_price:function(){
        returnthis.compute_fixed_price(this.get_lst_price());
    },
    get_lst_price:function(){
        returnthis.product.get_price(this.pos.default_pricelist,1,0)
    },
    set_lst_price:function(price){
      this.order.assert_editable();
      this.product.lst_price=round_di(parseFloat(price)||0,this.pos.dp['ProductPrice']);
      this.trigger('change',this);
    },
    is_last_line:function(){
        varorder=this.pos.get_order();
        varlast_id=Object.keys(order.orderlines._byId)[Object.keys(order.orderlines._byId).length-1];
        varselectedLine=order?order.selected_orderline:null;

        return!selectedLine?false:last_id===selectedLine.cid;
    },
});

varOrderlineCollection=Backbone.Collection.extend({
    model:exports.Orderline,
});

exports.Packlotline=Backbone.Model.extend({
    defaults:{
        lot_name:null
    },
    initialize:function(attributes,options){
        this.order_line=options.order_line;
        if(options.json){
            this.init_from_JSON(options.json);
            return;
        }
    },

    init_from_JSON:function(json){
        this.order_line=json.order_line;
        this.set_lot_name(json.lot_name);
    },

    set_lot_name:function(name){
        this.set({lot_name:_.str.trim(name)||null});
    },

    get_lot_name:function(){
        returnthis.get('lot_name');
    },

    export_as_JSON:function(){
        return{
            lot_name:this.get_lot_name(),
        };
    },

    add:function(){
        varorder_line=this.order_line,
            index=this.collection.indexOf(this);
        varnew_lot_model=newexports.Packlotline({},{'order_line':this.order_line});
        this.collection.add(new_lot_model,{at:index+1});
        returnnew_lot_model;
    },

    remove:function(){
        this.collection.remove(this);
    }
});

varPacklotlineCollection=Backbone.Collection.extend({
    model:exports.Packlotline,
    initialize:function(models,options){
        this.order_line=options.order_line;
    },

    get_valid_lots:function(){
        returnthis.filter(function(model){
            returnmodel.get('lot_name');
        });
    },

    set_quantity_by_lot:function(){
        varvalid_lots_quantity=this.get_valid_lots().length;
        if(this.order_line.quantity<0){
            valid_lots_quantity=-valid_lots_quantity;
        }
        this.order_line.set_quantity(valid_lots_quantity);
    }
});

//EveryPaymentlinecontainsacashregisterandanamountofmoney.
exports.Paymentline=Backbone.Model.extend({
    initialize:function(attributes,options){
        this.pos=options.pos;
        this.order=options.order;
        this.amount=0;
        this.selected=false;
        this.cashier_receipt='';
        this.ticket='';
        this.payment_status='';
        this.card_type='';
        this.cardholder_name='';
        this.transaction_id='';

        if(options.json){
            this.init_from_JSON(options.json);
            return;
        }
        this.payment_method=options.payment_method;
        if(this.payment_method===undefined){
            thrownewError(_t('PleaseconfigureapaymentmethodinyourPOS.'));
        }
        this.name=this.payment_method.name;
    },
    init_from_JSON:function(json){
        this.amount=json.amount;
        this.payment_method=this.pos.payment_methods_by_id[json.payment_method_id];
        this.can_be_reversed=json.can_be_reversed;
        this.name=this.payment_method.name;
        this.payment_status=json.payment_status;
        this.ticket=json.ticket;
        this.card_type=json.card_type;
        this.cardholder_name=json.cardholder_name;
        this.transaction_id=json.transaction_id;
        this.is_change=json.is_change;
    },
    //setstheamountofmoneyonthispaymentline
    set_amount:function(value){
        this.order.assert_editable();
        this.amount=round_di(parseFloat(value)||0,this.pos.currency.decimals);
        if(this.pos.config.iface_customer_facing_display)this.pos.send_current_order_to_customer_facing_display();
        this.trigger('change',this);
    },
    //returnstheamountofmoneyonthispaymentline
    get_amount:function(){
        returnthis.amount;
    },
    get_amount_str:function(){
        returnfield_utils.format.float(this.amount,{digits:[69,this.pos.currency.decimals]});
    },
    set_selected:function(selected){
        if(this.selected!==selected){
            this.selected=selected;
            this.trigger('change',this);
        }
    },
    /**
     *returns{string}paymentstatus.
     */
    get_payment_status:function(){
        returnthis.payment_status;
    },

    /**
     *Setthenewpaymentstatus.
     *
     *@param{string}value-newstatus.
     */
    set_payment_status:function(value){
        this.payment_status=value;
        this.trigger('change',this);
    },

    /**
     *Checkifpaymentlineisdone.
     *Paymentlineisdoneifthereisnopaymentstatusorthepaymentstatusisdone.
     */
    is_done:function(){
        returnthis.get_payment_status()?this.get_payment_status()==='done'||this.get_payment_status()==='reversed':true;
    },

    /**
    *Setinfotobeprintedonthecashierreceipt.valueshould
    *becompatiblewithboththeQWebandESC/POSreceipts.
    *
    *@param{string}value-receiptinfo
    */
    set_cashier_receipt:function(value){
        this.cashier_receipt=value;
        this.trigger('change',this);
    },

    /**
     *Setadditionalinfotobeprintedonthereceipts.valueshould
     *becompatiblewithboththeQWebandESC/POSreceipts.
     *
     *@param{string}value-receiptinfo
     */
    set_receipt_info:function(value){
        this.ticket+=value;
        this.trigger('change',this);
    },

    //returnstheassociatedcashregister
    //exportsasJSONforservercommunication
    export_as_JSON:function(){
        return{
            name:time.datetime_to_str(newDate()),
            payment_method_id:this.payment_method.id,
            amount:this.get_amount(),
            payment_status:this.payment_status,
            can_be_reversed:this.can_be_resersed,
            ticket:this.ticket,
            card_type:this.card_type,
            cardholder_name:this.cardholder_name,
            transaction_id:this.transaction_id,
        };
    },
    //exportsasJSONforreceiptprinting
    export_for_printing:function(){
        return{
            cid:this.cid,
            amount:this.get_amount(),
            name:this.name,
            ticket:this.ticket,
        };
    },
    //Ifpaymentstatusisanon-emptystring,thenitisanelectronicpayment.
    //TODO:Therehastobealessconfusingwaytodistinguishsimplepayments
    //fromelectronictransactions.Perhapsuseaflag?
    is_electronic:function(){
        returnBoolean(this.get_payment_status());
    },
});

varPaymentlineCollection=Backbone.Collection.extend({
    model:exports.Paymentline,
});

//Anordermoreorlessrepresentsthecontentofaclient'sshoppingcart(theOrderLines)
//plustheassociatedpaymentinformation(thePaymentlines)
//thereisalwaysanactive('selected')orderinthePos,anewoneiscreated
//automaticalyonceanorderiscompletedandsenttotheserver.
exports.Order=Backbone.Model.extend({
    initialize:function(attributes,options){
        Backbone.Model.prototype.initialize.apply(this,arguments);
        varself=this;
        options =options||{};

        this.locked        =false;
        this.pos           =options.pos;
        this.selected_orderline  =undefined;
        this.selected_paymentline=undefined;
        this.screen_data   ={}; //seeGui
        this.temporary     =options.temporary||false;
        this.creation_date =newDate();
        this.to_invoice    =false;
        this.orderlines    =newOrderlineCollection();
        this.paymentlines  =newPaymentlineCollection();
        this.pos_session_id=this.pos.pos_session.id;
        this.employee      =this.pos.employee;
        this.finalized     =false;//iftrue,cannotbemodified.
        this.set_pricelist(this.pos.default_pricelist);

        this.set({client:null});

        this.uiState={
            ReceiptScreen:newContext({
                inputEmail:'',
                //ifnull:notyettriedtosend
                //iffalse/true:triedsendingemail
                emailSuccessful:null,
                emailNotice:'',
            }),
            TipScreen:newContext({
                inputTipAmount:'',
            })
        };

        if(options.json){
            this.init_from_JSON(options.json);
        }else{
            this.sequence_number=this.pos.pos_session.sequence_number++;
            this.uid =this.generate_unique_id();
            this.name=_.str.sprintf(_t("Order%s"),this.uid);
            this.validation_date=undefined;
            this.fiscal_position=_.find(this.pos.fiscal_positions,function(fp){
                returnfp.id===self.pos.config.default_fiscal_position_id[0];
            });
        }

        this.on('change',             function(){this.save_to_db("order:change");},this);
        this.orderlines.on('change',  function(){this.save_to_db("orderline:change");},this);
        this.orderlines.on('add',     function(){this.save_to_db("orderline:add");},this);
        this.orderlines.on('remove',  function(){this.save_to_db("orderline:remove");},this);
        this.paymentlines.on('change',function(){this.save_to_db("paymentline:change");},this);
        this.paymentlines.on('add',   function(){this.save_to_db("paymentline:add");},this);
        this.paymentlines.on('remove',function(){this.save_to_db("paymentline:rem");},this);

        if(this.pos.config.iface_customer_facing_display){
            this.paymentlines.on('add',this.pos.send_current_order_to_customer_facing_display,this.pos);
            this.paymentlines.on('remove',this.pos.send_current_order_to_customer_facing_display,this.pos);
        }

        this.save_to_db();

        returnthis;
    },
    save_to_db:function(){
        if(!this.temporary&&!this.locked){
            this.assert_editable();
            this.pos.db.save_unpaid_order(this);
        }
    },
    /**
     *InitializePoSorderfromaJSONstring.
     *
     *Iftheorderwascreatedinanothersession,thesequencenumbershouldbechangedsoitdoesn'tconflict
     *withordersinthecurrentsession.
     *Else,thesequencenumberofthesessionshouldfollowonthesequencenumberoftheloadedorder.
     *
     *@param{object}jsonJSONrepresentingonePoSorder.
     */
    init_from_JSON:function(json){
        varclient;
        if(json.pos_session_id!==this.pos.pos_session.id){
            this.sequence_number=this.pos.pos_session.sequence_number++;
        }else{
            this.sequence_number=json.sequence_number;
            this.pos.pos_session.sequence_number=Math.max(this.sequence_number+1,this.pos.pos_session.sequence_number);
        }
        this.session_id=this.pos.pos_session.id;
        this.uid=json.uid;
        this.name=_.str.sprintf(_t("Order%s"),this.uid);
        this.validation_date=json.creation_date;
        this.server_id=json.server_id?json.server_id:false;
        this.user_id=json.user_id;

        if(json.fiscal_position_id){
            varfiscal_position=_.find(this.pos.fiscal_positions,function(fp){
                returnfp.id===json.fiscal_position_id;
            });

            if(fiscal_position){
                this.fiscal_position=fiscal_position;
            }else{
                console.error('ERROR:tryingtoloadafiscalpositionnotavailableinthepos');
            }
        }

        if(json.pricelist_id){
            this.pricelist=_.find(this.pos.pricelists,function(pricelist){
                returnpricelist.id===json.pricelist_id;
            });
        }else{
            this.pricelist=this.pos.default_pricelist;
        }

        if(json.partner_id){
            client=this.pos.db.get_partner_by_id(json.partner_id);
            if(!client){
                console.error('ERROR:tryingtoloadapartnernotavailableinthepos');
            }
        }else{
            client=null;
        }
        this.set_client(client);

        this.temporary=false;    //FIXME
        this.to_invoice=false;   //FIXME

        varorderlines=json.lines;
        for(vari=0;i<orderlines.length;i++){
            varorderline=orderlines[i][2];
            if(this.pos.db.get_product_by_id(orderline.product_id)){
                this.add_orderline(newexports.Orderline({},{pos:this.pos,order:this,json:orderline}));
            }
        }

        varpaymentlines=json.statement_ids;
        for(vari=0;i<paymentlines.length;i++){
            varpaymentline=paymentlines[i][2];
            varnewpaymentline=newexports.Paymentline({},{pos:this.pos,order:this,json:paymentline});
            this.paymentlines.add(newpaymentline);

            if(i===paymentlines.length-1){
                this.select_paymentline(newpaymentline);
            }
        }

        //Tagthisorderas'locked'ifitisalreadypaid.
        this.locked=['paid','done','invoiced'].includes(json.state);
        this.state=json.state;
        this.amount_return=json.amount_return;
        this.account_move=json.account_move;
        this.backendId=json.id;
        this.isFromClosedSession=json.is_session_closed;
        this.is_tipped=json.is_tipped||false;
        this.tip_amount=json.tip_amount||0;
    },
    export_as_JSON:function(){
        varorderLines,paymentLines;
        orderLines=[];
        this.orderlines.each(_.bind(function(item){
            returnorderLines.push([0,0,item.export_as_JSON()]);
        },this));
        paymentLines=[];
        this.paymentlines.each(_.bind(function(item){
            returnpaymentLines.push([0,0,item.export_as_JSON()]);
        },this));
        varjson={
            name:this.get_name(),
            amount_paid:this.get_total_paid()-this.get_change(),
            amount_total:this.get_total_with_tax(),
            amount_tax:this.get_total_tax(),
            amount_return:this.get_change(),
            lines:orderLines,
            statement_ids:paymentLines,
            pos_session_id:this.pos_session_id,
            pricelist_id:this.pricelist?this.pricelist.id:false,
            partner_id:this.get_client()?this.get_client().id:false,
            user_id:this.pos.user.id,
            uid:this.uid,
            sequence_number:this.sequence_number,
            creation_date:this.validation_date||this.creation_date,//todo:renamecreation_dateinmaster
            fiscal_position_id:this.fiscal_position?this.fiscal_position.id:false,
            server_id:this.server_id?this.server_id:false,
            to_invoice:this.to_invoice?this.to_invoice:false,
            is_tipped:this.is_tipped||false,
            tip_amount:this.tip_amount||0,
        };
        if(!this.is_paid&&this.user_id){
            json.user_id=this.user_id;
        }
        returnjson;
    },
    export_for_printing:function(){
        varorderlines=[];
        varself=this;

        this.orderlines.each(function(orderline){
            orderlines.push(orderline.export_for_printing());
        });

        //Iforderislocked(paid),the'change'issavedasnegativepayment,
        //andisflaggedwithis_change=true.Areceiptthatisprintedfirst
        //timedoesn'tshowthisnegativepaymentsowefilteritout.
        varpaymentlines=this.paymentlines.models
            .filter(function(paymentline){
                return!paymentline.is_change;
            })
            .map(function(paymentline){
                returnpaymentline.export_for_printing();
            });
        varclient =this.get('client');
        varcashier=this.pos.get_cashier();
        varcompany=this.pos.company;
        vardate   =newDate();

        functionis_html(subreceipt){
            returnsubreceipt?(subreceipt.split('\n')[0].indexOf('<!DOCTYPEQWEB')>=0):false;
        }

        functionrender_html(subreceipt){
            if(!is_html(subreceipt)){
                returnsubreceipt;
            }else{
                subreceipt=subreceipt.split('\n').slice(1).join('\n');
                varqweb=newQWeb2.Engine();
                    qweb.debug=config.isDebug();
                    qweb.default_dict=_.clone(QWeb.default_dict);
                    qweb.add_template('<templates><tt-name="subreceipt">'+subreceipt+'</t></templates>');

                returnqweb.render('subreceipt',{'pos':self.pos,'order':self,'receipt':receipt});
            }
        }

        varreceipt={
            orderlines:orderlines,
            paymentlines:paymentlines,
            subtotal:this.get_subtotal(),
            total_with_tax:this.get_total_with_tax(),
            total_rounded:this.get_total_with_tax()+this.get_rounding_applied(),
            total_without_tax:this.get_total_without_tax(),
            total_tax:this.get_total_tax(),
            total_paid:this.get_total_paid(),
            total_discount:this.get_total_discount(),
            rounding_applied:this.get_rounding_applied(),
            tax_details:this.get_tax_details(),
            change:this.locked?this.amount_return:this.get_change(),
            name:this.get_name(),
            client:client?client:null,
            invoice_id:null,  //TODO
            cashier:cashier?cashier.name:null,
            precision:{
                price:2,
                money:2,
                quantity:3,
            },
            date:{
                year:date.getFullYear(),
                month:date.getMonth(),
                date:date.getDate(),      //dayofthemonth
                day:date.getDay(),        //dayoftheweek
                hour:date.getHours(),
                minute:date.getMinutes(),
                isostring:date.toISOString(),
                localestring:this.formatted_validation_date,
            },
            company:{
                email:company.email,
                website:company.website,
                company_registry:company.company_registry,
                contact_address:company.partner_id[1],
                vat:company.vat,
                vat_label:company.country&&company.country.vat_label||_t('TaxID'),
                name:company.name,
                phone:company.phone,
                logo: this.pos.company_logo_base64,
            },
            currency:this.pos.currency,
        };

        if(is_html(this.pos.config.receipt_header)){
            receipt.header='';
            receipt.header_html=render_html(this.pos.config.receipt_header);
        }else{
            receipt.header=this.pos.config.receipt_header||'';
        }

        if(is_html(this.pos.config.receipt_footer)){
            receipt.footer='';
            receipt.footer_html=render_html(this.pos.config.receipt_footer);
        }else{
            receipt.footer=this.pos.config.receipt_footer||'';
        }

        returnreceipt;
    },
    is_empty:function(){
        returnthis.orderlines.models.length===0;
    },
    generate_unique_id:function(){
        //Generatesapublicidentificationnumberfortheorder.
        //Thegeneratednumbermustbeuniqueandsequential.Theyaremade12digitlong
        //tofitintoEAN-13barcodes,shoulditbeneeded

        functionzero_pad(num,size){
            vars=""+num;
            while(s.length<size){
                s="0"+s;
            }
            returns;
        }
        returnzero_pad(this.pos.pos_session.id,5)+'-'+
               zero_pad(this.pos.pos_session.login_number,3)+'-'+
               zero_pad(this.sequence_number,4);
    },
    get_name:function(){
        returnthis.name;
    },
    assert_editable:function(){
        if(this.finalized){
            thrownewError('FinalizedOrdercannotbemodified');
        }
    },
    /*----OrderLines---*/
    add_orderline:function(line){
        this.assert_editable();
        if(line.order){
            line.order.remove_orderline(line);
        }
        line.order=this;
        this.orderlines.add(line);
        this.select_orderline(this.get_last_orderline());
    },
    get_orderline:function(id){
        varorderlines=this.orderlines.models;
        for(vari=0;i<orderlines.length;i++){
            if(orderlines[i].id===id){
                returnorderlines[i];
            }
        }
        returnnull;
    },
    get_orderlines:function(){
        returnthis.orderlines.models;
    },
    get_last_orderline:function(){
        returnthis.orderlines.at(this.orderlines.length-1);
    },
    get_tip:function(){
        vartip_product=this.pos.db.get_product_by_id(this.pos.config.tip_product_id[0]);
        varlines=this.get_orderlines();
        if(!tip_product){
            return0;
        }else{
            for(vari=0;i<lines.length;i++){
                if(lines[i].get_product()===tip_product){
                    returnlines[i].get_unit_price();
                }
            }
            return0;
        }
    },

    initialize_validation_date:function(){
        this.validation_date=newDate();
        this.formatted_validation_date=field_utils.format.datetime(
            moment(this.validation_date),{},{timezone:false});
    },

    set_tip:function(tip){
        vartip_product=this.pos.db.get_product_by_id(this.pos.config.tip_product_id[0]);
        varlines=this.get_orderlines();
        if(tip_product){
            for(vari=0;i<lines.length;i++){
                if(lines[i].get_product()===tip_product){
                    lines[i].set_unit_price(tip);
                    lines[i].set_lst_price(tip);
                    lines[i].price_manually_set=true;
                    lines[i].order.tip_amount=tip;
                    return;
                }
            }
            returnthis.add_product(tip_product,{
              is_tip:true,
              quantity:1,
              price:tip,
              lst_price:tip,
              extras:{price_manually_set:true},
            });
        }
    },
    set_pricelist:function(pricelist){
        varself=this;
        this.pricelist=pricelist;

        varlines_to_recompute=_.filter(this.get_orderlines(),function(line){
            return!line.price_manually_set;
        });
        _.each(lines_to_recompute,function(line){
            line.set_unit_price(line.product.get_price(self.pricelist,line.get_quantity(),line.get_price_extra()));
            self.fix_tax_included_price(line);
        });
        this.trigger('change');
    },
    remove_orderline:function(line){
        this.assert_editable();
        this.orderlines.remove(line);
        this.select_orderline(this.get_last_orderline());
    },

    fix_tax_included_price:function(line){
        line.set_unit_price(line.compute_fixed_price(line.price));
    },

    add_product:function(product,options){
        if(this._printed){
            this.destroy();
            returnthis.pos.get_order().add_product(product,options);
        }
        this.assert_editable();
        options=options||{};
        varline=newexports.Orderline({},{pos:this.pos,order:this,product:product});
        this.fix_tax_included_price(line);

        if(options.quantity!==undefined){
            line.set_quantity(options.quantity);
        }

        if(options.price_extra!==undefined){
            line.price_extra=options.price_extra;
            line.set_unit_price(line.product.get_price(this.pricelist,line.get_quantity(),options.price_extra));
            this.fix_tax_included_price(line);
        }

        if(options.price!==undefined){
            line.set_unit_price(options.price);
            this.fix_tax_included_price(line);
        }

        if(options.lst_price!==undefined){
            line.set_lst_price(options.lst_price);
        }

        if(options.discount!==undefined){
            line.set_discount(options.discount);
        }

        if(options.description!==undefined){
            line.description+=options.description;
        }

        if(options.extras!==undefined){
            for(varpropinoptions.extras){
                line[prop]=options.extras[prop];
            }
        }
        if(options.is_tip){
            this.is_tipped=true;
            this.tip_amount=options.price;
        }

        varto_merge_orderline;
        for(vari=0;i<this.orderlines.length;i++){
            if(this.orderlines.at(i).can_be_merged_with(line)&&options.merge!==false){
                to_merge_orderline=this.orderlines.at(i);
            }
        }
        if(to_merge_orderline){
            to_merge_orderline.merge(line);
            this.select_orderline(to_merge_orderline);
        }else{
            this.orderlines.add(line);
            this.select_orderline(this.get_last_orderline());
        }

        if(options.draftPackLotLines){
            this.selected_orderline.setPackLotLines(options.draftPackLotLines);
        }
        if(this.pos.config.iface_customer_facing_display){
            this.pos.send_current_order_to_customer_facing_display();
        }
    },
    get_selected_orderline:function(){
        returnthis.selected_orderline;
    },
    select_orderline:function(line){
        if(line){
            if(line!==this.selected_orderline){
                //ifline(newlinetoselect)isnotthesameastheold
                //selected_orderline,thenwesettheoldlinetofalse,
                //andsetthenewlinetotrue.Also,setthenewlineas
                //theselected_orderline.
                if(this.selected_orderline){
                    this.selected_orderline.set_selected(false);
                }
                this.selected_orderline=line;
                this.selected_orderline.set_selected(true);
            }
        }else{
            this.selected_orderline=undefined;
        }
    },
    deselect_orderline:function(){
        if(this.selected_orderline){
            this.selected_orderline.set_selected(false);
            this.selected_orderline=undefined;
        }
    },

    /*----PaymentLines---*/
    add_paymentline:function(payment_method){
        this.assert_editable();
        if(this.electronic_payment_in_progress()){
            returnfalse;
        }else{
            varnewPaymentline=newexports.Paymentline({},{order:this,payment_method:payment_method,pos:this.pos});
            newPaymentline.set_amount(this.get_due());
            this.paymentlines.add(newPaymentline);
            this.select_paymentline(newPaymentline);
            if(this.pos.config.cash_rounding){
              this.selected_paymentline.set_amount(0);
              this.selected_paymentline.set_amount(this.get_due());
            }

            if(payment_method.payment_terminal){
                newPaymentline.set_payment_status('pending');
            }
            returnnewPaymentline;
        }
    },
    get_paymentlines:function(){
        returnthis.paymentlines.models;
    },
    /**
     *Retrievethepaymentlinewiththespecifiedcid
     *
     *@param{String}cid
     */
    get_paymentline:function(cid){
        varlines=this.get_paymentlines();
        returnlines.find(function(line){
            returnline.cid===cid;
        });
    },
    remove_paymentline:function(line){
        this.assert_editable();
        if(this.selected_paymentline===line){
            this.select_paymentline(undefined);
        }
        this.paymentlines.remove(line);
    },
    clean_empty_paymentlines:function(){
        varlines=this.paymentlines.models;
        varempty=[];
        for(vari=0;i<lines.length;i++){
            if(!lines[i].get_amount()){
                empty.push(lines[i]);
            }
        }
        for(vari=0;i<empty.length;i++){
            this.remove_paymentline(empty[i]);
        }
    },
    select_paymentline:function(line){
        if(line!==this.selected_paymentline){
            if(this.selected_paymentline){
                this.selected_paymentline.set_selected(false);
            }
            this.selected_paymentline=line;
            if(this.selected_paymentline){
                this.selected_paymentline.set_selected(true);
            }
            this.trigger('change:selected_paymentline',this.selected_paymentline);
        }
    },
    electronic_payment_in_progress:function(){
        returnthis.get_paymentlines()
            .some(function(pl){
                if(pl.payment_status){
                    return!['done','reversed'].includes(pl.payment_status);
                }else{
                    returnfalse;
                }
            });
    },
    /**
     *Stopsapaymentontheterminalifoneisrunning
     */
    stop_electronic_payment:function(){
        varlines=this.get_paymentlines();
        varline=lines.find(function(line){
            varstatus=line.get_payment_status();
            returnstatus&&!['done','reversed','reversing','pending','retry'].includes(status);
        });
        if(line){
            line.set_payment_status('waitingCancel');
            line.payment_method.payment_terminal.send_payment_cancel(this,line.cid).finally(function(){
                line.set_payment_status('retry');
            });
        }
    },
    /*----PaymentStatus---*/
    get_subtotal:function(){
        returnround_pr(this.orderlines.reduce((function(sum,orderLine){
            returnsum+orderLine.get_display_price();
        }),0),this.pos.currency.rounding);
    },
    get_total_with_tax:function(){
        returnthis.get_total_without_tax()+this.get_total_tax();
    },
    get_total_without_tax:function(){
        returnround_pr(this.orderlines.reduce((function(sum,orderLine){
            returnsum+orderLine.get_price_without_tax();
        }),0),this.pos.currency.rounding);
    },
    get_total_discount:function(){
        returnround_pr(this.orderlines.reduce((function(sum,orderLine){
            sum+=(orderLine.get_unit_price()*(orderLine.get_discount()/100)*orderLine.get_quantity());
            if(orderLine.display_discount_policy()==='without_discount'){
                sum+=((orderLine.get_lst_price()-orderLine.get_unit_price())*orderLine.get_quantity());
            }
            returnsum;
        }),0),this.pos.currency.rounding);
    },
    get_total_tax:function(){
        if(this.pos.company.tax_calculation_rounding_method==="round_globally"){
            //Asalways,weneed:
            //1.Foreachtax,sumtheiramountacrossallorderlines
            //2.Roundthatresult
            //3.Sumallthoseroundedamounts
            vargroupTaxes={};
            this.orderlines.each(function(line){
                vartaxDetails=line.get_tax_details();
                vartaxIds=Object.keys(taxDetails);
                for(vart=0;t<taxIds.length;t++){
                    vartaxId=taxIds[t];
                    if(!(taxIdingroupTaxes)){
                        groupTaxes[taxId]=0;
                    }
                    groupTaxes[taxId]+=taxDetails[taxId];
                }
            });

            varsum=0;
            vartaxIds=Object.keys(groupTaxes);
            for(varj=0;j<taxIds.length;j++){
                vartaxAmount=groupTaxes[taxIds[j]];
                sum+=round_pr(taxAmount,this.pos.currency.rounding);
            }
            returnsum;
        }else{
            returnround_pr(this.orderlines.reduce((function(sum,orderLine){
                returnsum+orderLine.get_tax();
            }),0),this.pos.currency.rounding);
        }
    },
    get_total_paid:function(){
        returnround_pr(this.paymentlines.reduce((function(sum,paymentLine){
            if(paymentLine.is_done()){
                sum+=paymentLine.get_amount();
            }
            returnsum;
        }),0),this.pos.currency.rounding);
    },
    get_tax_details:function(){
        vardetails={};
        varfulldetails=[];

        this.orderlines.each(function(line){
            varldetails=line.get_tax_details();
            for(varidinldetails){
                if(ldetails.hasOwnProperty(id)){
                    details[id]=(details[id]||0)+ldetails[id];
                }
            }
        });

        for(varidindetails){
            if(details.hasOwnProperty(id)){
                fulldetails.push({amount:details[id],tax:this.pos.taxes_by_id[id],name:this.pos.taxes_by_id[id].name});
            }
        }

        returnfulldetails;
    },
    //Returnsatotalonlyfortheorderlineswithproductsbelongingtothecategory
    get_total_for_category_with_tax:function(categ_id){
        vartotal=0;
        varself=this;

        if(categ_idinstanceofArray){
            for(vari=0;i<categ_id.length;i++){
                total+=this.get_total_for_category_with_tax(categ_id[i]);
            }
            returntotal;
        }

        this.orderlines.each(function(line){
            if(self.pos.db.category_contains(categ_id,line.product.id)){
                total+=line.get_price_with_tax();
            }
        });

        returntotal;
    },
    get_total_for_taxes:function(tax_id){
        vartotal=0;

        if(!(tax_idinstanceofArray)){
            tax_id=[tax_id];
        }

        vartax_set={};

        for(vari=0;i<tax_id.length;i++){
            tax_set[tax_id[i]]=true;
        }

        this.orderlines.each(function(line){
            vartaxes_ids=line.get_product().taxes_id;
            for(vari=0;i<taxes_ids.length;i++){
                if(tax_set[taxes_ids[i]]){
                    total+=line.get_price_with_tax();
                    return;
                }
            }
        });

        returntotal;
    },
    get_change:function(paymentline){
        if(!paymentline){
            varchange=this.get_total_paid()-this.get_total_with_tax()-this.get_rounding_applied();
        }else{
            varchange=-this.get_total_with_tax();
            varlines =this.paymentlines.models;
            for(vari=0;i<lines.length;i++){
                change+=lines[i].get_amount();
                if(lines[i]===paymentline){
                    break;
                }
            }
        }
        returnround_pr(Math.max(0,change),this.pos.currency.rounding);
    },
    get_due:function(paymentline){
        if(!paymentline){
            vardue=this.get_total_with_tax()-this.get_total_paid()+this.get_rounding_applied();
        }else{
            vardue=this.get_total_with_tax();
            varlines=this.paymentlines.models;
            for(vari=0;i<lines.length;i++){
                if(lines[i]===paymentline){
                    break;
                }else{
                    due-=lines[i].get_amount();
                }
            }
        }
        returnround_pr(due,this.pos.currency.rounding);
    },
    get_rounding_applied:function(){
        if(this.pos.config.cash_rounding){
            constonly_cash=this.pos.config.only_round_cash_method;
            constpaymentlines=this.get_paymentlines();
            constlast_line=paymentlines?paymentlines[paymentlines.length-1]:false;
            constlast_line_is_cash=last_line?last_line.payment_method.is_cash_count==true:false;
            if(!only_cash||(only_cash&&last_line_is_cash)){
                varremaining=this.get_total_with_tax()-this.get_total_paid();
                vartotal=round_pr(remaining,this.pos.cash_rounding[0].rounding);
                varsign=remaining>0?1.0:-1.0;

                varrounding_applied=total-remaining;
                rounding_applied*=sign;
                //becausefloorandceildoesn'tincludedecimalsincalculation,wereusethevalueofthehalf-upandadaptit.
                if(utils.float_is_zero(rounding_applied,this.pos.currency.decimals)){
                    //https://xkcd.com/217/
                    return0;
                }elseif(Math.abs(this.get_total_with_tax())<this.pos.cash_rounding[0].rounding){
                    return0;
                }elseif(this.pos.cash_rounding[0].rounding_method==="UP"&&rounding_applied<0&&remaining>0){
                    rounding_applied+=this.pos.cash_rounding[0].rounding;
                }
                elseif(this.pos.cash_rounding[0].rounding_method==="UP"&&rounding_applied>0&&remaining<0){
                    rounding_applied-=this.pos.cash_rounding[0].rounding;
                }
                elseif(this.pos.cash_rounding[0].rounding_method==="DOWN"&&rounding_applied>0&&remaining>0){
                    rounding_applied-=this.pos.cash_rounding[0].rounding;
                }
                elseif(this.pos.cash_rounding[0].rounding_method==="DOWN"&&rounding_applied<0&&remaining<0){
                    rounding_applied+=this.pos.cash_rounding[0].rounding;
                }
                returnsign*rounding_applied;
            }
            else{
                return0;
            }
        }
        return0;
    },
    has_not_valid_rounding:function(){
        if(!this.pos.config.cash_rounding||this.get_total_with_tax()<this.pos.cash_rounding[0].rounding)
            returnfalse;

        constonly_cash=this.pos.config.only_round_cash_method;
        varlines=this.paymentlines.models;

        for(vari=0;i<lines.length;i++){
            varline=lines[i];
            if(only_cash&&!line.payment_method.is_cash_count)
                continue;

            if(!utils.float_is_zero(line.amount-round_pr(line.amount,this.pos.cash_rounding[0].rounding),6))
                returnline;
        }
        returnfalse;
    },
    is_paid:function(){
        returnthis.get_due()<=0&&this.check_paymentlines_rounding();
    },
    is_paid_with_cash:function(){
        return!!this.paymentlines.find(function(pl){
            returnpl.payment_method.is_cash_count;
        });
    },
    check_paymentlines_rounding:function(){
        if(this.pos.config.cash_rounding){
            varcash_rounding=this.pos.cash_rounding[0].rounding;
            vardefault_rounding=this.pos.currency.rounding;
            for(varidinthis.get_paymentlines()){
                varline=this.get_paymentlines()[id];
                vardiff=round_pr(round_pr(line.amount,cash_rounding)-round_pr(line.amount,default_rounding),default_rounding);
                if(this.get_total_with_tax()<this.pos.cash_rounding[0].rounding)
                    returntrue;
                if(diff&&line.payment_method.is_cash_count){
                    returnfalse;
                }elseif(!this.pos.config.only_round_cash_method&&diff){
                    returnfalse;
                }
            }
            returntrue;
        }
        returntrue;
    },
    finalize:function(){
        this.destroy();
    },
    destroy:function(){
        Backbone.Model.prototype.destroy.apply(this,arguments);
        this.pos.db.remove_unpaid_order(this);
    },
    /*----Invoice---*/
    set_to_invoice:function(to_invoice){
        this.assert_editable();
        this.to_invoice=to_invoice;
    },
    is_to_invoice:function(){
        returnthis.to_invoice;
    },
    /*----Client/Customer---*/
    //theclientrelatedtothecurrentorder.
    set_client:function(client){
        this.assert_editable();
        this.set('client',client);
    },
    get_client:function(){
        returnthis.get('client');
    },
    get_client_name:function(){
        varclient=this.get('client');
        returnclient?client.name:"";
    },
    get_cardholder_name:function(){
        varcard_payment_line=this.paymentlines.find(pl=>pl.cardholder_name);
        returncard_payment_line?card_payment_line.cardholder_name:"";
    },
    /*----ScreenStatus---*/
    //theorderalsostoresthescreenstatus,asthePoSsupports
    //differentactivescreensperorder.Thismethodisusedto
    //storethescreenstatus.
    set_screen_data:function(value){
        this.screen_data['value']=value;
    },
    //seeset_screen_data
    get_screen_data:function(){
        constscreen=this.screen_data['value'];
        //Ifnoscreendataissaved
        //  nopaymentline->productscreen
        //  withpaymentline->paymentscreen
        if(!screen){
            if(this.get_paymentlines().length>0)return{name:'PaymentScreen'};
            return{name:'ProductScreen'};
        }
        if(!this.finalized&&this.get_paymentlines().length>0){
            return{name:'PaymentScreen'};
        }
        returnscreen;
    },
    wait_for_push_order:function(){
        returnfalse;
    },
    /**
     *@returns{Object}objecttouseaspropsforinstantiatingOrderReceipt.
     */
    getOrderReceiptEnv:function(){
        //Formerlyget_receipt_render_envdefinedinScreenWidget.
        return{
            order:this,
            receipt:this.export_for_printing(),
            orderlines:this.get_orderlines(),
            paymentlines:this.get_paymentlines(),
        };
    },
    updatePricelist:function(newClient){
        letnewClientPricelist,newClientFiscalPosition;
        constdefaultFiscalPosition=this.pos.fiscal_positions.find(
            (position)=>position.id===this.pos.config.default_fiscal_position_id[0]
        );
        if(newClient){
            newClientFiscalPosition=newClient.property_account_position_id
                ?this.pos.fiscal_positions.find(
                      (position)=>position.id===newClient.property_account_position_id[0]
                  )
                :defaultFiscalPosition;
            newClientPricelist=
                this.pos.pricelists.find(
                    (pricelist)=>pricelist.id===newClient.property_product_pricelist[0]
                )||this.pos.default_pricelist;
        }else{
            newClientFiscalPosition=defaultFiscalPosition;
            newClientPricelist=this.pos.default_pricelist;
        }
        this.fiscal_position=newClientFiscalPosition;
        this.set_pricelist(newClientPricelist);
    }
});

varOrderCollection=Backbone.Collection.extend({
    model:exports.Order,
});

//exports={
//    PosModel:PosModel,
//    load_fields:load_fields,
//    load_models:load_models,
//    Orderline:Orderline,
//    Order:Order,
//};
returnexports;

});
