flectra.define('lunch.LunchControllerCommon',function(require){
"usestrict";

/**
 *ThisfiledefinesthecommoneventsandfunctionsusedbyControllersfortheLunchview.
 */

varsession=require('web.session');
varcore=require('web.core');
varLunchWidget=require('lunch.LunchWidget');
varLunchPaymentDialog=require('lunch.LunchPaymentDialog');

var_t=core._t;

varLunchControllerCommon={
    custom_events:{
        add_product:'_onAddProduct',
        change_location:'_onLocationChanged',
        change_user:'_onUserChanged',
        open_wizard:'_onOpenWizard',
        order_now:'_onOrderNow',
        remove_product:'_onRemoveProduct',
        unlink_order:'_onUnlinkOrder',
    },
    /**
     *@override
     */
    init:function(){
        this._super.apply(this,arguments);
        this.editMode=false;
        this.updated=false;
        this.widgetData=null;
        this.context=session.user_context;
        this.archiveEnabled=false;
    },
    /**
     *@override
     */
    start:function(){
        //createadivinsideo_contentthatwillbeusedtowrapthelunch
        //bannerandrenderer(thisisrequiredtogetthedesired
        //layoutwiththesearchPaneltotheleft)
        varself=this;
        this.$('.o_content').append($('<div>').addClass('o_lunch_content'));
        returnthis._super.apply(this,arguments).then(function(){
            self.$('.o_lunch_content').append(self.$('.o_lunch_view'));
        });
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    _fetchPaymentInfo:function(){
        returnthis._rpc({
            route:'/lunch/payment_message',
            params:{
                context:this.context,
            },
        });
    },
    _fetchWidgetData:asyncfunction(){
        this.widgetData=awaitthis._rpc({
            route:'/lunch/infos',
            params:{
                user_id:this.searchModel.get('userId'),
                context:this.context,
            },
        });
    },
    /**
     *Rendersandappendsthelunchbannerwidget.
     *
     *@private
     */
    _renderLunchWidget:function(){
        varself=this;
        varoldWidget=this.widget;
        this.widgetData.wallet=parseFloat(this.widgetData.wallet).toFixed(2);
        this.widget=newLunchWidget(this,_.extend(this.widgetData,{edit:this.editMode}));
        returnthis.widget.appendTo(document.createDocumentFragment()).then(function(){
            self.$('.o_lunch_content').prepend(self.widget.$el);
            if(oldWidget){
                oldWidget.destroy();
            }
        });
    },
    _showPaymentDialog:function(title){
        varself=this;

        title=title||'';

        this._fetchPaymentInfo().then(function(data){
            varpaymentDialog=newLunchPaymentDialog(self,_.extend(data,{title:title}));
            paymentDialog.open();
        });
    },
    /**
     *Overridetofetchanddisplaythelunchdata.Becauseofthepresenceof
     *thesearchPanel,alsowrapthelunchwidgetandtherendererinto
     *adiv,togetthedesiredlayout.
     *
     *@override
     *@private
     */
    _update:function(){
        vardef=this._fetchWidgetData().then(this._renderLunchWidget.bind(this));
        returnPromise.all([def,this._super.apply(this,arguments)]);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    _onAddProduct:function(ev){
        varself=this;
        ev.stopPropagation();

        this._rpc({
            model:'lunch.order',
            method:'update_quantity',
            args:[[ev.data.lineId],1],
        }).then(function(){
            self.reload();
        });
    },
    _onLocationChanged:function(ev){
        ev.stopPropagation();
        this.searchModel.dispatch('setLocationId',ev.data.locationId);
    },
    _onOpenWizard:function(ev){
        varself=this;
        ev.stopPropagation();

        varctx=this.searchModel.get('userId')?{default_user_id:this.searchModel.get('userId')}:{};

        varoptions={
            on_close:function(){
                self.reload();
            },
        };

        //YTITODOMaybedon'talwayspassthedefault_product_id
        varaction={
            res_model:'lunch.order',
            name:_t('ConfigureYourOrder'),
            type:'ir.actions.act_window',
            views:[[false,'form']],
            target:'new',
            context:_.extend(ctx,{default_product_id:ev.data.productId}),
        };

        if(ev.data.lineId){
            action=_.extend(action,{
                res_id:ev.data.lineId,
                context:_.extend(action.context,{
                    active_id:ev.data.lineId,
                }),
            });
        }

        this.do_action(action,options);
    },
    _onOrderNow:function(ev){
        varself=this;
        ev.stopPropagation();

        this._rpc({
            route:'/lunch/pay',
            params:{
                user_id:this.searchModel.get('userId'),
                context:this.context,
            },
        }).then(function(isPaid){
            if(isPaid){
                //TODO:feedback?
                self.reload();
            }else{
                self._showPaymentDialog(_t("Notenoughmoneyinyourwallet"));
                self.reload();
            }
        });
    },
    _onRemoveProduct:function(ev){
        varself=this;
        ev.stopPropagation();

        this._rpc({
            model:'lunch.order',
            method:'update_quantity',
            args:[[ev.data.lineId],-1],
        }).then(function(){
            self.reload();
        });
    },
    _onUserChanged:function(ev){
        ev.stopPropagation();
        this.searchModel.dispatch('updateUserId',ev.data.userId);
    },
    _onUnlinkOrder:function(ev){
        varself=this;
        ev.stopPropagation();

        this._rpc({
            route:'/lunch/trash',
            params:{
                user_id:this.searchModel.get('userId'),
                context:this.context,
            },
        }).then(function(){
            self.reload();
        });
    },
};

returnLunchControllerCommon;

});
