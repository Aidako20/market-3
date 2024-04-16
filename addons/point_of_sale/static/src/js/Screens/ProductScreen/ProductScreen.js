flectra.define('point_of_sale.ProductScreen',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constControlButtonsMixin=require('point_of_sale.ControlButtonsMixin');
    constNumberBuffer=require('point_of_sale.NumberBuffer');
    const{useListener}=require('web.custom_hooks');
    constRegistries=require('point_of_sale.Registries');
    const{onChangeOrder,useBarcodeReader}=require('point_of_sale.custom_hooks');
    const{useState}=owl.hooks;
    const{parse}=require('web.field_utils');

    classProductScreenextendsControlButtonsMixin(PosComponent){
        constructor(){
            super(...arguments);
            useListener('update-selected-orderline',this._updateSelectedOrderline);
            useListener('new-orderline-selected',this._newOrderlineSelected);
            useListener('set-numpad-mode',this._setNumpadMode);
            useListener('click-product',this._clickProduct);
            useListener('click-customer',this._onClickCustomer);
            useListener('click-pay',this._onClickPay);
            useBarcodeReader({
                product:this._barcodeProductAction,
                quantity:this._barcodeProductAction,
                weight:this._barcodeProductAction,
                price:this._barcodeProductAction,
                client:this._barcodeClientAction,
                discount:this._barcodeDiscountAction,
                error:this._barcodeErrorAction,
            })
            onChangeOrder(null,(newOrder)=>newOrder&&this.render());
            NumberBuffer.use({
                nonKeyboardInputEvent:'numpad-click-input',
                triggerAtInput:'update-selected-orderline',
                useWithBarcode:true,
            });
            letstatus=this.showCashBoxOpening()
            this.state=useState({cashControl:status,numpadMode:'quantity'});
            this.mobile_pane=this.props.mobile_pane||'right';
        }
        mounted(){
            this.env.pos.on('change:selectedClient',this.render,this);
        }
        willUnmount(){
            this.env.pos.off('change:selectedClient',null,this);
        }
        /**
         *Tobeoverriddenbymodulesthatchecksavailabilityof
         *connectedscale.
         *@see_onScaleNotAvailable
         */
        getisScaleAvailable(){
            returntrue;
        }
        getclient(){
            returnthis.env.pos.get_client();
        }
        getcurrentOrder(){
            returnthis.env.pos.get_order();
        }
        showCashBoxOpening(){
            if(this.env.pos.config.cash_control&&this.env.pos.pos_session.state=='opening_control')
                returntrue;
            returnfalse;
        }
        async_getAddProductOptions(product){
            letprice_extra=0.0;
            letdraftPackLotLines,weight,description,packLotLinesToEdit;

            if(this.env.pos.config.product_configurator&&_.some(product.attribute_line_ids,(id)=>idinthis.env.pos.attributes_by_ptal_id)){
                letattributes=_.map(product.attribute_line_ids,(id)=>this.env.pos.attributes_by_ptal_id[id])
                                  .filter((attr)=>attr!==undefined);
                let{confirmed,payload}=awaitthis.showPopup('ProductConfiguratorPopup',{
                    product:product,
                    attributes:attributes,
                });

                if(confirmed){
                    description=payload.selected_attributes.join(',');
                    price_extra+=payload.price_extra;
                }else{
                    return;
                }
            }

            //Gatherlotinformationifrequired.
            if(['serial','lot'].includes(product.tracking)&&(this.env.pos.picking_type.use_create_lots||this.env.pos.picking_type.use_existing_lots)){
                constisAllowOnlyOneLot=product.isAllowOnlyOneLot();
                if(isAllowOnlyOneLot){
                    packLotLinesToEdit=[];
                }else{
                    constorderline=this.currentOrder
                        .get_orderlines()
                        .filter(line=>!line.get_discount())
                        .find(line=>line.product.id===product.id);
                    if(orderline){
                        packLotLinesToEdit=orderline.getPackLotLinesToEdit();
                    }else{
                        packLotLinesToEdit=[];
                    }
                }
                const{confirmed,payload}=awaitthis.showPopup('EditListPopup',{
                    title:this.env._t('Lot/SerialNumber(s)Required'),
                    isSingleItem:isAllowOnlyOneLot,
                    array:packLotLinesToEdit,
                });
                if(confirmed){
                    //Segregatetheoldandnewpacklotlines
                    constmodifiedPackLotLines=Object.fromEntries(
                        payload.newArray.filter(item=>item.id).map(item=>[item.id,item.text])
                    );
                    constnewPackLotLines=payload.newArray
                        .filter(item=>!item.id)
                        .map(item=>({lot_name:item.text}));

                    draftPackLotLines={modifiedPackLotLines,newPackLotLines};
                }else{
                    //Wedon'tproceedonaddingproduct.
                    return;
                }
            }

            //Taketheweightifnecessary.
            if(product.to_weight&&this.env.pos.config.iface_electronic_scale){
                //ShowtheScaleScreentoweightheproduct.
                if(this.isScaleAvailable){
                    const{confirmed,payload}=awaitthis.showTempScreen('ScaleScreen',{
                        product,
                    });
                    if(confirmed){
                        weight=payload.weight;
                    }else{
                        //donotaddtheproduct;
                        return;
                    }
                }else{
                    awaitthis._onScaleNotAvailable();
                }
            }

            return{draftPackLotLines,quantity:weight,description,price_extra};
        }
        async_clickProduct(event){
            if(!this.currentOrder){
                this.env.pos.add_new_order();
            }
            constproduct=event.detail;
            constoptions=awaitthis._getAddProductOptions(product);
            //Donotaddproductifoptionsisundefined.
            if(!options)return;
            //Addtheproductafterhavingtheextrainformation.
            this.currentOrder.add_product(product,options);
            NumberBuffer.reset();
        }
        _setNumpadMode(event){
            const{mode}=event.detail;
            NumberBuffer.capture();
            NumberBuffer.reset();
            this.state.numpadMode=mode;
        }
        async_updateSelectedOrderline(event){
            if(this.state.numpadMode==='quantity'&&this.env.pos.disallowLineQuantityChange()){
                letorder=this.env.pos.get_order();
                letselectedLine=order.get_selected_orderline();
                letlastId=order.orderlines.last().cid;
                letcurrentQuantity=this.env.pos.get_order().get_selected_orderline().get_quantity();

                if(selectedLine.noDecrease){
                    this.showPopup('ErrorPopup',{
                        title:this.env._t('Invalidaction'),
                        body:this.env._t('Youarenotallowedtochangethisquantity'),
                    });
                    return;
                }
                constparsedInput=event.detail.buffer&&parse.float(event.detail.buffer)||0;
                if(lastId!=selectedLine.cid)
                    this._showDecreaseQuantityPopup();
                elseif(currentQuantity<parsedInput)
                    this._setValue(event.detail.buffer);
                elseif(parsedInput<currentQuantity)
                    this._showDecreaseQuantityPopup();
            }else{
                let{buffer}=event.detail;
                letval=buffer===null?'remove':buffer;
                this._setValue(val);
            }
        }
        async_newOrderlineSelected(){
            NumberBuffer.reset();
        }
        _setValue(val){
            if(this.currentOrder.get_selected_orderline()){
                if(this.state.numpadMode==='quantity'){
                    this.currentOrder.get_selected_orderline().set_quantity(val);
                }elseif(this.state.numpadMode==='discount'){
                    this.currentOrder.get_selected_orderline().set_discount(val);
                }elseif(this.state.numpadMode==='price'){
                    varselected_orderline=this.currentOrder.get_selected_orderline();
                    selected_orderline.price_manually_set=true;
                    selected_orderline.set_unit_price(val);
                }
                if(this.env.pos.config.iface_customer_facing_display){
                    this.env.pos.send_current_order_to_customer_facing_display();
                }
            }
        }
        async_barcodeProductAction(code){
            constproduct=this.env.pos.db.get_product_by_barcode(code.base_code)
            if(!product){
                returnthis._barcodeErrorAction(code);
            }
            constoptions=awaitthis._getAddProductOptions(product);
            //Donotproceedonaddingtheproductwhennooptionsisreturned.
            //Thisisconsistentwith_clickProduct.
            if(!options)return;

            //updatetheoptionsdependingonthetypeofthescannedcode
            if(code.type==='price'){
                Object.assign(options,{
                    price:code.value,
                    extras:{
                        price_manually_set:true,
                    },
                });
            }elseif(code.type==='weight'||code.type==='quantity'){
                Object.assign(options,{
                    quantity:code.value,
                    merge:false,
                });
            }elseif(code.type==='discount'){
                Object.assign(options,{
                    discount:code.value,
                    merge:false,
                });
            }
            this.currentOrder.add_product(product, options)
        }
        _barcodeClientAction(code){
            constpartner=this.env.pos.db.get_partner_by_barcode(code.code);
            if(partner){
                if(this.currentOrder.get_client()!==partner){
                    this.currentOrder.set_client(partner);
                    this.currentOrder.updatePricelist(partner);
                }
                returntrue;
            }
            this._barcodeErrorAction(code);
            returnfalse;
        }
        _barcodeDiscountAction(code){
            varlast_orderline=this.currentOrder.get_last_orderline();
            if(last_orderline){
                last_orderline.set_discount(code.value);
            }
        }
        //IMPROVEMENT:ThefollowingtwomethodsshouldbeinPosScreenComponent?
        //Why?Becauseoncewestartdeclaringbarcodeactionsindifferent
        //screens,thesemethodswillalsobedeclaredoverandover.
        _barcodeErrorAction(code){
            this.showPopup('ErrorBarcodePopup',{code:this._codeRepr(code)});
        }
        _codeRepr(code){
            if(code.code.length>32){
                returncode.code.substring(0,29)+'...';
            }else{
                returncode.code;
            }
        }
        /**
         *overridethismethodtoperformprocedureifthescaleisnotavailable.
         *@seeisScaleAvailable
         */
        async_onScaleNotAvailable(){}
        async_showDecreaseQuantityPopup(){
            const{confirmed,payload:inputNumber}=awaitthis.showPopup('NumberPopup',{
                startingValue:0,
                title:this.env._t('Setthenewquantity'),
            });
            if(!confirmed)
                return;
            letnewQuantity=parse.float(inputNumber);
            letorder=this.env.pos.get_order();
            letselectedLine=this.env.pos.get_order().get_selected_orderline();
            letcurrentQuantity=selectedLine.get_quantity()
            if(selectedLine.is_last_line()&&currentQuantity===1&&newQuantity<currentQuantity)
                selectedLine.set_quantity(newQuantity);
            elseif(newQuantity>=currentQuantity)
                selectedLine.set_quantity(newQuantity);
            else{
                letnewLine=selectedLine.clone();
                letdecreasedQuantity=currentQuantity-newQuantity
                newLine.order=order;

                newLine.set_quantity(-decreasedQuantity,true);
                order.add_orderline(newLine);
            }
        }
        async_onClickCustomer(){
            //IMPROVEMENT:ThiscodesnippetisverysimilartoselectClientofPaymentScreen.
            constcurrentClient=this.currentOrder.get_client();
            const{confirmed,payload:newClient}=awaitthis.showTempScreen(
                'ClientListScreen',
                {client:currentClient}
            );
            if(confirmed){
                this.currentOrder.set_client(newClient);
                this.currentOrder.updatePricelist(newClient);
            }
        }
        async_onClickPay(){
            if(this.env.pos.get_order().orderlines.any(line=>line.get_product().tracking!=='none'&&!line.has_valid_product_lot()&&(this.env.pos.picking_type.use_create_lots||this.env.pos.picking_type.use_existing_lots))){
                const{confirmed}=awaitthis.showPopup('ConfirmPopup',{
                    title:this.env._t('SomeSerial/LotNumbersaremissing'),
                    body:this.env._t('Youaretryingtosellproductswithserial/lotnumbers,butsomeofthemarenotset.\nWouldyouliketoproceedanyway?'),
                    confirmText:this.env._t('Yes'),
                    cancelText:this.env._t('No')
                });
                if(confirmed){
                    this.showScreen('PaymentScreen');
                }
            }else{
                this.showScreen('PaymentScreen');
            }
        }
        switchPane(){
            if(this.mobile_pane==="left"){
                this.mobile_pane="right";
                this.render();
            }
            else{
                this.mobile_pane="left";
                this.render();
            }
        }
    }
    ProductScreen.template='ProductScreen';

    Registries.Component.add(ProductScreen);

    returnProductScreen;
});
