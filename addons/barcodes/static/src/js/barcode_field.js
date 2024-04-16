flectra.define('barcodes.field',function(require){
"usestrict";

varAbstractField=require('web.AbstractField');
varbasicFields=require('web.basic_fields');
varfieldRegistry=require('web.field_registry');
varBarcodeEvents=require('barcodes.BarcodeEvents').BarcodeEvents;

//Fieldinwhichtheusercanbothtypenormallyandscanbarcodes

varFieldFloatScannable=basicFields.FieldFloat.extend({
    events:_.extend({},basicFields.FieldFloat.prototype.events,{
        //Thebarcode_eventscomponentinterceptskeypressesandreleasesthemwhenit
        //appearstheyarenotpartofabarcode.Butsincereleasedkeypressesdon't
        //triggernativebehaviour(likecharactersinput),wemustsimulateit.
        keypress:'_onKeypress',
    }),

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     *@private
     */
    _renderEdit:function(){
        varself=this;
        returnPromise.resolve(this._super()).then(function(){
            self.$input.data('enableBarcode',true);
        });
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{KeyboardEvent}e
     */
    _onKeypress:function(e){
        /*onlysimulateakeypressifithasbeenpreviouslyprevented*/
        if(e.dispatched_by_barcode_reader!==true){
            if(!BarcodeEvents.is_special_key(e)){
                e.preventDefault();
            }
            return;
        }
        varcharacter=String.fromCharCode(e.which);
        varcurrent_str=e.target.value;
        varstr_before_carret=current_str.substring(0,e.target.selectionStart);
        varstr_after_carret=current_str.substring(e.target.selectionEnd);
        e.target.value=str_before_carret+character+str_after_carret;
        varnew_carret_index=str_before_carret.length+character.length;
        e.target.setSelectionRange(new_carret_index,new_carret_index);
        //triggeran'input'eventtonotifythewidgetthatit'svaluechanged
        $(e.target).trigger('input');
    },
});

//Fieldtousescanbarcodes
varFormViewBarcodeHandler=AbstractField.extend({
    /**
     *@override
     */
    init:function(){
        this._super.apply(this,arguments);

        this.trigger_up('activeBarcode',{
            name:this.name,
            commands:{
                barcode:'_barcodeAddX2MQuantity',
            }
        });
    },
});

fieldRegistry.add('field_float_scannable',FieldFloatScannable);
fieldRegistry.add('barcode_handler',FormViewBarcodeHandler);

return{
    FieldFloatScannable:FieldFloatScannable,
    FormViewBarcodeHandler:FormViewBarcodeHandler,
};

});
