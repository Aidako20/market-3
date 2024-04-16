flectra.define('pos_restaurant.multiprint',function(require){
"usestrict";

varmodels=require('point_of_sale.models');
varcore=require('web.core');
varPrinter=require('point_of_sale.Printer').Printer;

varQWeb=core.qweb;

models.PosModel=models.PosModel.extend({
    create_printer:function(config){
        varurl=config.proxy_ip||'';
        if(url.indexOf('//')<0){
            url=window.location.protocol+'//'+url;
        }
        if(url.indexOf(':',url.indexOf('//')+2)<0&&window.location.protocol!=='https:'){
            url=url+':7073';
        }
        returnnewPrinter(url,this);
    },
});

models.load_models({
    model:'restaurant.printer',
    fields:['name','proxy_ip','product_categories_ids','printer_type'],
    domain:null,
    loaded:function(self,printers){
        varactive_printers={};
        for(vari=0;i<self.config.printer_ids.length;i++){
            active_printers[self.config.printer_ids[i]]=true;
        }

        self.printers=[];
        self.printers_categories={};//listofproductcategoriesthatbelongto
                                       //oneormoreorderprinter

        for(vari=0;i<printers.length;i++){
            if(active_printers[printers[i].id]){
                varprinter=self.create_printer(printers[i]);
                printer.config=printers[i];
                self.printers.push(printer);

                for(varj=0;j<printer.config.product_categories_ids.length;j++){
                    self.printers_categories[printer.config.product_categories_ids[j]]=true;
                }
            }
        }
        self.printers_categories=_.keys(self.printers_categories);
        self.config.iface_printers=!!self.printers.length;
    },
});

var_super_orderline=models.Orderline.prototype;

models.Orderline=models.Orderline.extend({
    initialize:function(){
        _super_orderline.initialize.apply(this,arguments);
        if(!this.pos.config.iface_printers){
            return;
        }
        if(typeofthis.mp_dirty==='undefined'){
            //mpdirtyistrueifthisorderlinehaschanged
            //sincethelastkitchenprint
            //it'sleftundefinediftheorderlinedoesnot
            //needtobeprintedtoaprinter.

            this.mp_dirty=this.printable()||undefined;
        }
        if(!this.mp_skip){
            //mp_skipistrueifthecashierwantthisorderline
            //nottobesenttothekitchen
            this.mp_skip =false;
        }
    },
    //canthisorderlinebepotentiallyprinted?
    printable:function(){
        returnthis.pos.db.is_product_in_category(this.pos.printers_categories,this.get_product().id);
    },
    init_from_JSON:function(json){
        _super_orderline.init_from_JSON.apply(this,arguments);
        this.mp_dirty=json.mp_dirty;
        this.mp_skip =json.mp_skip;
    },
    export_as_JSON:function(){
        varjson=_super_orderline.export_as_JSON.apply(this,arguments);
        json.mp_dirty=this.mp_dirty;
        json.mp_skip =this.mp_skip;
        returnjson;
    },
    set_quantity:function(quantity,keep_price){
        if(this.pos.config.iface_printers&&quantity!==this.quantity&&this.printable()){
            this.mp_dirty=true;
        }
        _super_orderline.set_quantity.apply(this,arguments);
    },
    can_be_merged_with:function(orderline){
        return(!this.mp_skip)&&
               (!orderline.mp_skip)&&
               _super_orderline.can_be_merged_with.apply(this,arguments);
    },
    set_skip:function(skip){
        if(this.mp_dirty&&skip&&!this.mp_skip){
            this.mp_skip=true;
            this.trigger('change',this);
        }
        if(this.mp_skip&&!skip){
            this.mp_dirty=true;
            this.mp_skip =false;
            this.trigger('change',this);
        }
    },
    set_dirty:function(dirty){
        if(this.mp_dirty!==dirty){
            this.mp_dirty=dirty;
            this.trigger('change',this);
        }
    },
    get_line_diff_hash:function(){
        if(this.get_note()){
            returnthis.id+'|'+this.get_note();
        }else{
            return''+this.id;
        }
    },
});

var_super_order=models.Order.prototype;
models.Order=models.Order.extend({
    build_line_resume:function(){
        varresume={};
        this.orderlines.each(function(line){
            if(line.mp_skip){
                return;
            }
            varqty =Number(line.get_quantity());
            varnote=line.get_note();
            varproduct_id=line.get_product().id;
            varproduct_name=line.get_full_product_name();
            varp_key=product_id+"-"+product_name;
            varproduct_resume=p_keyinresume?resume[p_key]:{
                pid:product_id,
                product_name_wrapped:line.generate_wrapped_product_name(),
                qties:{},
            };
            if(noteinproduct_resume['qties'])product_resume['qties'][note]+=qty;
            elseproduct_resume['qties'][note]=qty;
            resume[p_key]=product_resume;
        });
        returnresume;
    },
    saveChanges:function(){
        this.saved_resume=this.build_line_resume();
        this.orderlines.each(function(line){
            line.set_dirty(false);
        });
        this.trigger('change',this);
    },
    computeChanges:function(categories){
        varcurrent_res=this.build_line_resume();
        varold_res    =this.saved_resume||{};
        varjson       =this.export_as_JSON();
        varadd=[];
        varrem=[];
        varp_key,note;

        for(p_keyincurrent_res){
            for(noteincurrent_res[p_key]['qties']){
                varcurr=current_res[p_key];
                varold =old_res[p_key]||{};
                varpid=curr.pid;
                varfound=p_keyinold_res&&noteinold_res[p_key]['qties'];

                if(!found){
                    add.push({
                        'id':      pid,
                        'name':    this.pos.db.get_product_by_id(pid).display_name,
                        'name_wrapped':curr.product_name_wrapped,
                        'note':    note,
                        'qty':     curr['qties'][note],
                    });
                }elseif(old['qties'][note]<curr['qties'][note]){
                    add.push({
                        'id':      pid,
                        'name':    this.pos.db.get_product_by_id(pid).display_name,
                        'name_wrapped':curr.product_name_wrapped,
                        'note':    note,
                        'qty':     curr['qties'][note]-old['qties'][note],
                    });
                }elseif(old['qties'][note]>curr['qties'][note]){
                    rem.push({
                        'id':      pid,
                        'name':    this.pos.db.get_product_by_id(pid).display_name,
                        'name_wrapped':curr.product_name_wrapped,
                        'note':    note,
                        'qty':     old['qties'][note]-curr['qties'][note],
                    });
                }
            }
        }

        for(p_keyinold_res){
            for(noteinold_res[p_key]['qties']){
                varfound=p_keyincurrent_res&&noteincurrent_res[p_key]['qties'];
                if(!found){
                    varold=old_res[p_key];
                    varpid=old.pid;
                    rem.push({
                        'id':      pid,
                        'name':    this.pos.db.get_product_by_id(pid).display_name,
                        'name_wrapped':old.product_name_wrapped,
                        'note':    note,
                        'qty':     old['qties'][note],
                    });
                }
            }
        }

        if(categories&&categories.length>0){
            //filtertheaddedandremovedorderstoonlycontains
            //productsthatbelongtooneofthecategoriessuppliedasaparameter

            varself=this;

            var_add=[];
            var_rem=[];

            for(vari=0;i<add.length;i++){
                if(self.pos.db.is_product_in_category(categories,add[i].id)){
                    _add.push(add[i]);
                }
            }
            add=_add;

            for(vari=0;i<rem.length;i++){
                if(self.pos.db.is_product_in_category(categories,rem[i].id)){
                    _rem.push(rem[i]);
                }
            }
            rem=_rem;
        }

        vard=newDate();
        varhours  =''+d.getHours();
            hours  =hours.length<2?('0'+hours):hours;
        varminutes=''+d.getMinutes();
            minutes=minutes.length<2?('0'+minutes):minutes;

        return{
            'new':add,
            'cancelled':rem,
            'table':json.table||false,
            'floor':json.floor||false,
            'name':json.name ||'unknownorder',
            'time':{
                'hours':  hours,
                'minutes':minutes,
            },
        };

    },
    printChanges:asyncfunction(){
        varprinters=this.pos.printers;
        letisPrintSuccessful=true;
        for(vari=0;i<printers.length;i++){
            varchanges=this.computeChanges(printers[i].config.product_categories_ids);
            if(changes['new'].length>0||changes['cancelled'].length>0){
                varreceipt=QWeb.render('OrderChangeReceipt',{changes:changes,widget:this});
                constresult=awaitprinters[i].print_receipt(receipt);
                if(!result.successful){
                    isPrintSuccessful=false;
                }
            }
        }
        returnisPrintSuccessful;
    },
    hasChangesToPrint:function(){
        varprinters=this.pos.printers;
        for(vari=0;i<printers.length;i++){
            varchanges=this.computeChanges(printers[i].config.product_categories_ids);
            if(changes['new'].length>0||changes['cancelled'].length>0){
                returntrue;
            }
        }
        returnfalse;
    },
    hasSkippedChanges:function(){
        varorderlines=this.get_orderlines();
        for(vari=0;i<orderlines.length;i++){
            if(orderlines[i].mp_skip){
                returntrue;
            }
        }
        returnfalse;
    },
    export_as_JSON:function(){
        varjson=_super_order.export_as_JSON.apply(this,arguments);
        json.multiprint_resume=JSON.stringify(this.saved_resume);
        returnjson;
    },
    init_from_JSON:function(json){
        _super_order.init_from_JSON.apply(this,arguments);
        this.saved_resume=json.multiprint_resume&&JSON.parse(json.multiprint_resume);
    },
});


});
