flectra.define('mrp.should_consume',function(require){
"usestrict";

constBasicFields=require('web.basic_fields');
constFieldFloat=BasicFields.FieldFloat;
constfieldRegistry=require('web.field_registry');
constfield_utils=require('web.field_utils');

/**
 *Thiswidgetisusedtodisplayalongsidethetotalquantitytoconsumeofaproductionorder,
 *theexactquantitythattheworkershouldconsumedependingontheBoM.Ex:
 *2componentstomake1finishedproduct.
 *Theproductionorderiscreatedtomake5finishedproductandthequantityproducingissetto3.
 *Thewidgetwillbe'3.000/5.000'.
 */
constMrpShouldConsume=FieldFloat.extend({
    /**
     *@override
     */
    init:function(parent,name,params){
        this._super.apply(this,arguments);
        this.displayShouldConsume=!['done','draft','cancel'].includes(params.data.state);
        this.should_consume_qty=field_utils.format.float(params.data.should_consume_qty,params.fields.should_consume_qty,this.nodeOptions);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Prefixtheclassicfloatfield(this.$el)byastaticvalue.
     *
     *@private
     *@param{float}[value]quantitytodisplaybeforetheinput`el`
     *@param{bool}[edit]whetherthefieldwillbeeditableorreadonly
     */
    _addShouldConsume:function(value,edit=false){
        const$to_consume_container=$('<spanclass="o_should_consume"/>');
        if(edit){
            $to_consume_container.addClass('o_row');
        }
        $to_consume_container.text(value+'/');
        this.setElement(this.$el.wrap($to_consume_container).parent());
    },

    /**
     *@private
     *@override
     */
    _renderEdit:function(){
        if(this.displayShouldConsume){
            if(!this.$el.text().includes('/')){
                this.$input=this.$el;
                this._addShouldConsume(this.should_consume_qty,true);
            }
            this._prepareInput(this.$input);
        }else{
            this._super.apply(this);
        }
    },
    /**
     *Resetsthecontenttotheformatedvalueinreadonlymode.
     *
     *@override
     *@private
     */
    _renderReadonly:function(){
        this.$el.text(this._formatValue(this.value));
        if(this.displayShouldConsume){
            this._addShouldConsume(this.should_consume_qty);
        }
    },
});

fieldRegistry.add('mrp_should_consume',MrpShouldConsume);

return{
    MrpShouldConsume:MrpShouldConsume,
};

});
