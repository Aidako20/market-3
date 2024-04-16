flectra.define('web.StandaloneFieldManagerMixin',function(require){
"usestrict";


varFieldManagerMixin=require('web.FieldManagerMixin');

/**
 *TheStandaloneFieldManagerMixinisamixin,designedtobeusedbyawidget
 *thatinstanciatesitsownfieldwidgets.
 *
 *@mixin
 *@nameStandaloneFieldManagerMixin
 *@mixesFieldManagerMixin
 *@property{Function}_confirmChange
 *@property{Function}_registerWidget
 */
varStandaloneFieldManagerMixin=_.extend({},FieldManagerMixin,{

    /**
     *@override
     */
    init:function(){
        FieldManagerMixin.init.apply(this,arguments);

        //registeredWidgetsisadictofallfieldwidgetsusedbythewidget
        this.registeredWidgets={};
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Thismethodwillbecalledwheneverafieldvaluehaschanged(andhas
     *beenconfirmedbythemodel).
     *
     *@private
     *@param{string}idbasicModelIdforthechangedrecord
     *@param{string[]}fieldsthefields(names)thathavebeenchanged
     *@param{FlectraEvent}eventtheeventthattriggeredthechange
     *@returns{Promise}
     */
    _confirmChange:function(id,fields,event){
        varresult=FieldManagerMixin._confirmChange.apply(this,arguments);
        varrecord=this.model.get(id);
        _.each(this.registeredWidgets[id],function(widget,fieldName){
            if(_.contains(fields,fieldName)){
                widget.reset(record,event);
            }
        });
        returnresult;
    },

    _registerWidget:function(datapointID,fieldName,widget){
        if(!this.registeredWidgets[datapointID]){
            this.registeredWidgets[datapointID]={};
        }
        this.registeredWidgets[datapointID][fieldName]=widget;
    },
});

returnStandaloneFieldManagerMixin;

});
