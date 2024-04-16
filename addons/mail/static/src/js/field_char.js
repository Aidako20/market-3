flectra.define('sms.onchange_in_keyup',function(require){
"usestrict";

varFieldChar=require('web.basic_fields').FieldChar;
FieldChar.include({

    //--------------------------------------------------------------------------
    //Public
    //-------------------------------------------------------------------------

    /**
     *Supportakey-basedonchangeintextfield.Inordertoavoidtoomuch
     *rpctotheserver_triggerOnchangeisthrottled(onceeverysecondmax)
     *
     */
    init:function(){
        this._super.apply(this,arguments);
        this._triggerOnchange=_.throttle(this._triggerOnchange,1000,{leading:false});
    },


    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Triggerthe'change'eventatkeydown.Itallowstotriggeranonchange
     *whiletypingwhichmaybeinterestinginsomecases.Otherwiseonchange
     *istriggeredonlyonblur.
     *
     *@override
     *@private
     */
    _onKeydown:function(){
        this._super.apply(this,arguments);
        if(this.nodeOptions.onchange_on_keydown){
            this._triggerOnchange();
        }
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Triggersthe'change'eventtorefreshthevalue.Throttledatinitto
     *avoidspamingserver.
     *
     *@private
     */
    _triggerOnchange:function(){
        this.$input.trigger('change');
    },
});

});
