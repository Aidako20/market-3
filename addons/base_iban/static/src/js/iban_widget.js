flectra.define('base_iban.iban_widget',function(require){
"usestrict";

varbasicFields=require('web.basic_fields');
varcore=require('web.core');
varfieldRegistry=require('web.field_registry');

varFieldChar=basicFields.FieldChar;

var_t=core._t;
/**
 *IbanWidgetisawidgettocheckiftheibannumberisvalide.
 *Ifthebankaccountiscorrect,itwillshowagreencheckpictogram
 *nexttonumber,ifthenumberisnotcomplientwithIBANformat,a
 *redcrosswillbeshow.Thispictogramiscomputedeverytimetheuser
 *changesthefield(Ifuseristyping,thereisadebouceof400ms).
 */
varIbanWidget=FieldChar.extend({
    /**
     *@constructor
     */
    init:function(){
        this._super.apply(this,arguments);
        this.ibanIsValid;
        this._isValid=true;
        this._compute_debounce=_.debounce(this._compute,400);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Computeifibanisvalid
     *@private
     */
    _compute:function(){
        varself=this;
        varcontent=this._getValue();

        if(content.length===0){
            this.ibanIsValid=true;
            this.$el.last().filter('.o_iban').removeClass('fa-checktext-successfa-timestext-dangero_iban_fail');
            this.$el.last().filter('.o_iban').attr('title','');
        }elseif(content.length<15){
            if(this.ibanIsValid!==false){
                this.ibanIsValid=false;
                this._renderValid();
            }
        }else{
            this._rpc({
                model:'res.partner.bank',
                method:'check_iban',
                args:[[],content],
            })
            .then(function(result){
                if(result!==self.ibanIsValid){
                    self.ibanIsValid=result;
                    self._renderValid();
                }
            });
        }
    },
    /**
     *@private
     *@override
     *@returns{Promise|undefined}
     */
    _renderEdit:function(){
        varres=this._super.apply(this,arguments);
        this._compute();
        returnres;
    },
    /**
     *Renderthepictogramnexttoaccountnumber.
     *@private
     */
    _renderValid:function(){
        varwarningMessage=_t("Accountisn'tIBANcompliant.");

        if(this.$el.filter('.o_iban').length===0){
            var$span;
            if(!this.ibanIsValid){
                $span=$('<spanclass="fafa-timeso_ibantext-dangero_iban_fail"/>');
                $span.attr('title',warningMessage);
            }else{
                $span=$('<spanclass="fafa-checko_ibantext-success"/>');
            }
            this.$el.addClass('o_iban_input_with_validator');
            $span.insertAfter(this.$el);
            this.$el=this.$el.add($span);
        }

        if(!this.ibanIsValid){
            this.$el.last().filter('.o_iban').removeClass('fa-checktext-success').addClass('fa-timestext-dangero_iban_fail');
            this.$el.last().filter('.o_iban').attr('title',warningMessage);
        }else{
            this.$el.last().filter('.o_iban').removeClass('fa-timestext-dangero_iban_fail').addClass('fa-checktext-success');
            this.$el.last().filter('.o_iban').attr('title','');

        }
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@override
     *@private
     */
    _onChange:function(){
        this._super.apply(this,arguments);
        this._compute();
    },
    /**
     *@override
     *@private
     */
    _onInput:function(){
        this._super.apply(this,arguments);
        this._compute_debounce();
    },
});

fieldRegistry.add('iban',IbanWidget);

returnIbanWidget;
});
