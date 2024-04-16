flectra.define('stock.popover_widget',function(require){
'usestrict';

varAbstractField=require('web.AbstractField');
varcore=require('web.core');
varQWeb=core.qweb;
varContext=require('web.Context');
vardata_manager=require('web.data_manager');
varfieldRegistry=require('web.field_registry');

/**
 *WidgetPopoverforJSONfield(char),bydefaultrenderasimplehtmlmessage
 *{
 * 'msg':'<CONTENTOFTHEPOPOVER>',
 * 'icon':'<FONTAWESOMECLASS>'(optionnal),
 * 'color':'<COLORCLASSOFICON>'(optionnal),
 * 'title':'<TITLEOFPOPOVER>'(optionnal),
 * 'popoverTemplate':'<TEMPLATEOFTHETEMPLATE>'(optionnal)
 *}
 */
varPopoverWidgetField=AbstractField.extend({
    supportedFieldTypes:['char'],
    buttonTemplape:'stock.popoverButton',
    popoverTemplate:'stock.popoverContent',
    trigger:'focus',
    placement:'top',
    html:true,
    color:'text-primary',
    icon:'fa-info-circle',

    _render:function(){
        varvalue=JSON.parse(this.value);
        if(!value){
            this.$el.html('');
            return;
        }
        this.$el.css('max-width','17px');
        this.$el.html(QWeb.render(this.buttonTemplape,_.defaults(value,{color:this.color,icon:this.icon})));
        this.$el.find('a').prop('special_click',true);
        this.$popover=$(QWeb.render(value.popoverTemplate||this.popoverTemplate,value));
        this.$popover.on('click','.action_open_forecast',this._openForecast.bind(this));
        this.$el.find('a').popover({
            content:this.$popover,
            html:this.html,
            placement:this.placement,
            title:value.title||this.title.toString(),
            trigger:this.trigger,
            delay:{'show':0,'hide':100},
        });
    },

    /**
     *Redirecttotheproductforecastedreport.
     *
     *@private
     *@param{MouseEvent}event
     *@returns{Promise}actionloaded
     */
    async_openForecast(ev){
        ev.stopPropagation();
        constreportContext={
            active_model:'product.product',
            active_id:this.recordData.product_id.data.id,
        };
        constaction=awaitthis._rpc({
            model:reportContext.active_model,
            method:'action_product_forecast_report',
            args:[[reportContext.active_id]],
        });
        action.context=newContext(action.context,reportContext);
        returnthis.do_action(action);
    },

    destroy:function(){
        this.$el.find('a').popover('dispose');
        this._super.apply(this,arguments);
    },

});

fieldRegistry.add('popover_widget',PopoverWidgetField);

returnPopoverWidgetField;
});
