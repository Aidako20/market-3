flectra.define('pos_restaurant.floors',function(require){
"usestrict";

varmodels=require('point_of_sale.models');
const{Gui}=require('point_of_sale.Gui');
const{posbus}=require('point_of_sale.utils');

//AtPOSStartup,loadthefloors,andaddthemtotheposmodel
models.load_models({
    model:'restaurant.floor',
    fields:['name','background_color','table_ids','sequence'],
    domain:function(self){return[['pos_config_id','=',self.config.id]];},
    loaded:function(self,floors){
        self.floors=floors;
        self.floors_by_id={};
        for(vari=0;i<floors.length;i++){
            floors[i].tables=[];
            self.floors_by_id[floors[i].id]=floors[i];
        }

        //Makesuretheydisplayinthecorrectorder
        self.floors=self.floors.sort(function(a,b){returna.sequence-b.sequence;});

        //Ignorefloorplanfeaturesifnofloorspecified.
        self.config.iface_floorplan=!!self.floors.length;
    },
});

//AtPOSStartup,afterthefloorsareloaded,loadthetables,andassociate
//themwiththeirfloor.
models.load_models({
    model:'restaurant.table',
    fields:['name','width','height','position_h','position_v','shape','floor_id','color','seats'],
    loaded:function(self,tables){
        self.tables_by_id={};
        for(vari=0;i<tables.length;i++){
            self.tables_by_id[tables[i].id]=tables[i];
            varfloor=self.floors_by_id[tables[i].floor_id[0]];
            if(floor){
                floor.tables.push(tables[i]);
                tables[i].floor=floor;
            }
        }
    },
});

//Newordersarenowassociatedwiththecurrenttable,ifany.
var_super_order=models.Order.prototype;
models.Order=models.Order.extend({
    initialize:function(attr,options){
        _super_order.initialize.apply(this,arguments);
        if(!this.table&&!options.json){
            this.table=this.pos.table;
        }
        this.customer_count=this.customer_count||1;
        this.save_to_db();
    },
    export_as_JSON:function(){
        varjson=_super_order.export_as_JSON.apply(this,arguments);
        json.table    =this.table?this.table.name:undefined;
        json.table_id =this.table?this.table.id:false;
        json.floor    =this.table?this.table.floor.name:false;
        json.floor_id =this.table?this.table.floor.id:false;
        json.customer_count=this.customer_count;
        returnjson;
    },
    init_from_JSON:function(json){
        _super_order.init_from_JSON.apply(this,arguments);
        this.table=this.pos.tables_by_id[json.table_id];
        this.floor=this.table?this.pos.floors_by_id[json.floor_id]:undefined;
        this.customer_count=json.customer_count||1;
    },
    export_for_printing:function(){
        varjson=_super_order.export_for_printing.apply(this,arguments);
        json.table=this.table?this.table.name:undefined;
        json.floor=this.table?this.table.floor.name:undefined;
        json.customer_count=this.get_customer_count();
        returnjson;
    },
    get_customer_count:function(){
        returnthis.customer_count;
    },
    set_customer_count:function(count){
        this.customer_count=Math.max(count,0);
        this.trigger('change');
    },
});

//WeneedtochangethewaytheregularUIseestheorders,it
//needstoonlyseetheordersassociatedwiththecurrenttable,
//andwhenanorderisvalidated,itneedstogobacktothefloormap.
//
//Andwhenwechangethetable,wemustcreateanorderforthattable
//ifthereisnone.
var_super_posmodel=models.PosModel.prototype;
models.PosModel=models.PosModel.extend({
    after_load_server_data:asyncfunction(){
        varres=await_super_posmodel.after_load_server_data.call(this);
        if(this.config.iface_floorplan){
            this.table=null;
        }
        returnres;
    },

    transfer_order_to_different_table:function(){
        this.order_to_transfer_to_different_table=this.get_order();

        //goto'floors'screen,thiswillsettheordertonulland
        //eventuallythiswillcausetheguitogotoits
        //default_screen,whichis'floors'
        this.set_table(null);
    },

    remove_from_server_and_set_sync_state:function(ids_to_remove){
        varself=this;
        this.set_synch('connecting',ids_to_remove.length);
        returnself._remove_from_server(ids_to_remove)
            .then(function(server_ids){
                self.set_synch('connected');
            }).catch(function(reason){
                self.set_synch('error');
                throwreason;
            });
    },

    /**
     *Requesttheordersofthetablewithgivenid.
     *@param{number}table_id.
     *@param{dict}options.
     *@param{number}options.timeoutoptionaltimeoutparameterfortherpccall.
     *@return{Promise}
     */
    _get_from_server:function(table_id,options){
        options=options||{};
        vartimeout=typeofoptions.timeout==='number'?options.timeout:7500;
        returnthis.rpc({
                model:'pos.order',
                method:'get_table_draft_orders',
                args:[table_id],
                kwargs:{context:this.session.user_context},
            },{
                timeout:timeout,
                shadow:false,
            })
    },

    transfer_order_to_table:function(table){
        this.order_to_transfer_to_different_table.table=table;
        this.order_to_transfer_to_different_table.save_to_db();
    },

    push_order_for_transfer:function(order_ids,table_orders){
        order_ids.push(this.order_to_transfer_to_different_table.uid);
        table_orders.push(this.order_to_transfer_to_different_table);
    },

    clean_table_transfer:function(table){
        if(this.order_to_transfer_to_different_table&&table){
            this.order_to_transfer_to_different_table=null;
            this.set_table(table);
        }
    },

    sync_from_server:function(table,table_orders,order_ids){
        varself=this;
        varids_to_remove=this.db.get_ids_to_remove_from_server();
        varorders_to_sync=this.db.get_unpaid_orders_to_sync(order_ids);
        if(orders_to_sync.length){
            this.set_synch('connecting',orders_to_sync.length);
            this._save_to_server(orders_to_sync,{'draft':true}).then(function(server_ids){
                server_ids.forEach(server_id=>self.update_table_order(server_id,table_orders));
                if(!ids_to_remove.length){
                    self.set_synch('connected');
                }else{
                    self.remove_from_server_and_set_sync_state(ids_to_remove);
                }
            }).catch(function(reason){
                self.set_synch('error');
            }).finally(function(){
                self.clean_table_transfer(table);
            });
        }else{
            if(ids_to_remove.length){
                self.remove_from_server_and_set_sync_state(ids_to_remove);
            }
            self.clean_table_transfer(table);
        }
    },

    update_table_order:function(server_id,table_orders){
        constorder=table_orders.find(o=>o.name===server_id.pos_reference);
        if(order){
            order.server_id=server_id.id;
            order.save_to_db();
        }
        returnorder;
    },

    /**
     *@param{models.Order}orderordertoset
     */
    set_order_on_table:function(order){
        varorders=this.get_order_list();
        if(orders.length){
            order=order?orders.find((o)=>o.uid===order.uid):null;
            if(order){
                this.set_order(order);
            }else{
                //donotmindlesslysetthefirstorderinthelist.
                orders=orders.filter(order=>!order.finalized);
                if(orders.length){
                    this.set_order(orders[0]);
                }else{
                    this.add_new_order();
                }
            }
        }else{
            this.add_new_order(); //orcreateaneworderwiththecurrenttable
        }
    },

    sync_to_server:function(table,order){
        varself=this;
        varids_to_remove=this.db.get_ids_to_remove_from_server();

        this.set_synch('connecting',1);
        this._get_from_server(table.id).then(function(server_orders){
            varorders=self.get_order_list();
            self._replace_orders(orders,server_orders);
            if(!ids_to_remove.length){
                self.set_synch('connected');
            }else{
                self.remove_from_server_and_set_sync_state(ids_to_remove);
            }
        }).catch(function(reason){
            self.set_synch('error');
        }).finally(function(){
            self.set_order_on_table(order);
        });
    },
    _replace_orders:function(orders_to_replace,new_orders){
        varself=this;
        orders_to_replace.forEach(function(order){
            //Wedon'tremovethevalidatedordersbecausewestillwanttoseethem
            //intheticketscreen.Ordersin'ReceiptScreen'or'TipScreen'arevalidated
            //orders.
            if(order.server_id&&!order.finalized){
                self.get("orders").remove(order);
                order.destroy();
            }
        });
        new_orders.forEach(function(server_order){
            varnew_order=newmodels.Order({},{pos:self,json:server_order});
            self.get("orders").add(new_order);
            new_order.save_to_db();
        });
    },
    //@throwerror
    replace_table_orders_from_server:asyncfunction(table){
        constserver_orders=awaitthis._get_from_server(table.id);
        constorders=this.get_table_orders(table);
        this._replace_orders(orders,server_orders);
    },
    get_order_with_uid:function(){
        varorder_ids=[];
        this.get_order_list().forEach(function(o){
            order_ids.push(o.uid);
        });

        returnorder_ids;
    },

    /**
     *Changesthecurrenttable.
     *
     *Switchtableandmakesureallnececerysyncingtasksaredone.
     *@param{object}table.
     *@param{models.Order|undefined}orderifprovided,settothisorder
     */
    set_table:function(table,order){
        if(!table){
            this.sync_from_server(table,this.get_order_list(),this.get_order_with_uid());
            this.set_order(null);
            this.table=null;
        }elseif(this.order_to_transfer_to_different_table){
            varorder_ids=this.get_order_with_uid();

            this.transfer_order_to_table(table);
            this.push_order_for_transfer(order_ids,this.get_order_list());

            this.sync_from_server(table,this.get_order_list(),order_ids);
            this.set_order(null);
        }else{
            this.table=table;
            this.sync_to_server(table,order);
        }
        posbus.trigger('table-set');
    },

    //ifwehavetables,wedonotloadadefaultorder,asthedefaultorderwillbe
    //setwhentheuserselectsatable.
    set_start_order:function(){
        if(!this.config.iface_floorplan){
            _super_posmodel.set_start_order.apply(this,arguments);
        }
    },

    //weneedtopreventthecreationoforderswhenthereisno
    //tableselected.
    add_new_order:function(){
        if(this.config.iface_floorplan){
            if(this.table){
                return_super_posmodel.add_new_order.apply(this,arguments);
            }else{
                Gui.showPopup('ConfirmPopup',{
                    title:'Unabletocreateorder',
                    body:'Orderscannotbecreatedwhenthereisnoactivetableinrestaurantmode',
                });
                returnundefined;
            }
        }else{
            return_super_posmodel.add_new_order.apply(this,arguments);
        }
    },


    //getthelistofunpaidorders(associatedtothecurrenttable)
    get_order_list:function(){
        varorders=_super_posmodel.get_order_list.call(this);
        if(!(this.config&&this.config.iface_floorplan)){
            returnorders;
        }elseif(!this.table){
            return[];
        }else{
            vart_orders=[];
            for(vari=0;i<orders.length;i++){
                if(orders[i].table===this.table){
                    t_orders.push(orders[i]);
                }
            }
            returnt_orders;
        }
    },

    //getthelistofordersassociatedtoatable.FIXME:shouldbeO(1)
    get_table_orders:function(table){
        varorders  =_super_posmodel.get_order_list.call(this);
        vart_orders=[];
        for(vari=0;i<orders.length;i++){
            if(orders[i].table===table){
                t_orders.push(orders[i]);
            }
        }
        returnt_orders;
    },

    //getcustomercountattable
    get_customer_count:function(table){
        varorders=this.get_table_orders(table).filter(order=>!order.finalized);
        varcount =0;
        for(vari=0;i<orders.length;i++){
            count+=orders[i].get_customer_count();
        }
        returncount;
    },

    //Whenwevalidateanorderwegobacktothefloorplan.
    //Whenwecancelanorderandthereismultipleorders
    //onthetable,stayonthetable.
    on_removed_order:function(removed_order,index,reason){
        if(this.config.iface_floorplan){
            varorder_list=this.get_order_list();
            if(reason==='abandon'){
                this.db.set_order_to_remove_from_server(removed_order);
            }
            if((reason==='abandon'||removed_order.temporary)&&order_list.length>0){
                this.set_order(order_list[index]||order_list[order_list.length-1],{silent:true});
            }elseif(order_list.length===0){
                this.table?this.set_order(null):this.set_table(null);
            }
        }else{
            _super_posmodel.on_removed_order.apply(this,arguments);
        }
    },


});


var_super_paymentline=models.Paymentline.prototype;
models.Paymentline=models.Paymentline.extend({
    /**
     *Overridethismethodtobeabletoshowthe'AdjustAuthorisation'button
     *onavalidatedpayment_lineandtoshowthetipscreenwhichallow
     *tippingevenafterpayment.Bydefault,thisreturnstrueforall
     *non-cashpayment.
     */
    canBeAdjusted:function(){
        if(this.payment_method.payment_terminal){
            returnthis.payment_method.payment_terminal.canBeAdjusted(this.cid);
        }
        return!this.payment_method.is_cash_count;
    },
});

});
