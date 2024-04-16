////////////////////////////////////////////////////////////////////////////////
///!\DEPRECATED
//
//LegacyFieldWidgetsareaddedinthisfilewhentheyareconvertedinto
//OwlComponent.
////////////////////////////////////////////////////////////////////////////////

flectra.define('web.basic_fields.deprecated',function(require){
"usestrict";

/**
 *Thismodulecontainsmostofthebasic(meaning:nonrelational)field
 *widgets.Fieldwidgetsaresupposedtobeusedinviewsinheritingfrom
 *BasicView,so,theycanworkwiththerecordsobtainedfromaBasicModel.
 */

varAbstractField=require('web.AbstractField');
varcore=require('web.core');

var_lt=core._lt;

varFieldBoolean=AbstractField.extend({
    className:'o_field_boolean',
    description:_lt("Checkbox"),
    events:_.extend({},AbstractField.prototype.events,{
        change:'_onChange',
    }),
    supportedFieldTypes:['boolean'],

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Togglethecheckboxifitisactivatedduetoaclickonitself.
     *
     *@override
     */
    activate:function(options){
        varactivated=this._super.apply(this,arguments);
        //TheformatValueofbooleanfieldsrendersHTMLelementssimilarto
        //theonerenderedbythewidgetitself.Eventhoughtheeventmight
        //havebeenfiredonthenon-widgetversionofthisfield,wecanstill
        //testthepresenceofitscustomclass.
        if(activated&&options&&options.event&&$(options.event.target).closest('.custom-control.custom-checkbox').length){
            this._setValue(!this.value); //Togglethecheckbox
        }
        returnactivated;
    },

    /**
     *@override
     *@returns{jQuery}thefocusablecheckboxinput
     */
    getFocusableElement:function(){
        returnthis.mode==='readonly'?$():this.$input;
    },
    /**
     *Abooleanfieldisalwayssetsincefalseisavalidvalue.
     *
     *@override
     */
    isSet:function(){
        returntrue;
    },
    /**
     *Whenthecheckboxisrerendered,weneedtocheckifitwastheactual
     *originofthereset.Ifitis,weneedtoactivateitbacksoitlooks
     *likeitwasnotrerenderedbutisstillthesameinput.
     *
     *@override
     */
    reset:function(record,event){
        varrendered=this._super.apply(this,arguments);
        if(event&&event.target.name===this.name){
            this.activate();
        }
        returnrendered;
    },
    /**
     *Associatesthe'for'attributeoftheinternallabel.
     *
     *@override
     */
    setIDForLabel:function(id){
        this._super.apply(this,arguments);
        this.$('.custom-control-label').attr('for',id);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Theactualcheckboxisdesignedincsstohavefullcontroloverits
     *appearance,asopposedtolettingthebrowserandtheosdecidehow
     *acheckboxshouldlook.Theactualinputisdisabledandhidden.In
     *readonlymode,thecheckboxisdisabled.
     *
     *@override
     *@private
     */
    _render:function(){
        var$checkbox=this._formatValue(this.value);
        this.$input=$checkbox.find('input');
        this.$input.prop('disabled',this.mode==='readonly');
        this.$el.addClass($checkbox.attr('class'));
        this.$el.empty().append($checkbox.contents());
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Properlyupdatethevaluewhenthecheckboxis(un)tickedtotrigger
     *possibleonchanges.
     *
     *@private
     */
    _onChange:function(){
        this._setValue(this.$input[0].checked);
    },
    /**
     *Implementkeyboardmovements. Mostlyusefulforitsenvironment,such
     *asalistview.
     *
     *@override
     *@private
     *@param{KeyEvent}ev
     */
    _onKeydown:function(ev){
        switch(ev.which){
            case$.ui.keyCode.ENTER:
                //preventsubsequent'click'event(see_onKeydownofAbstractField)
                ev.preventDefault();
                this.$input.prop('checked',!this.value);
                this._setValue(!this.value);
                return;
            case$.ui.keyCode.UP:
            case$.ui.keyCode.RIGHT:
            case$.ui.keyCode.DOWN:
            case$.ui.keyCode.LEFT:
                ev.preventDefault();
        }
        this._super.apply(this,arguments);
    },
});

return{
    FieldBoolean:FieldBoolean,
};

});
