flectra.define('web.basic_fields_owl',function(require){
    "usestrict";

    constAbstractField=require('web.AbstractFieldOwl');
    constCustomCheckbox=require('web.CustomCheckbox');
    const{_lt}=require('web.translation');


    /**
     *FieldBadgedisplaysthefield'svalueinsideabootstrappillbadge.
     *Thesupportedfield'stypesare'char','selection'and'many2one'.
     *
     *Bydefault,thebackgroundcolorofthebadgeisalightgray,butitcan
     *becustomizedbysettinga'decoration-xxx'attributeonthefield.
     *Forinstance,
     *  <fieldname="some_field"widget="badge"decoration-danger="state=='cancel'"/>
     *rendersabadgewitharedbackgroundonrecordsmatchingthecondition.
     */
    classFieldBadgeextendsAbstractField{
        _getClassFromDecoration(decoration){
            return`bg-${decoration.split('-')[1]}-light`;
        }
    }
    FieldBadge.description=_lt("Badge");
    FieldBadge.supportedFieldTypes=['selection','many2one','char'];
    FieldBadge.template='web.FieldBadge';


    classFieldBooleanextendsAbstractField{
        patched(){
            super.patched();
            if(this.props.event&&this.props.event.target===this){
                this.activate();
            }
        }

        //----------------------------------------------------------------------
        //Public
        //----------------------------------------------------------------------

        /**
         *@override
         *@returns{HTMLElement|null}thefocusablecheckboxinput
         */
        getfocusableElement(){
            returnthis.mode==='readonly'?null:this.el.querySelector('input');
        }
        /**
         *Abooleanfieldisalwayssetsincefalseisavalidvalue.
         *
         *@override
         */
        getisSet(){
            returntrue;
        }
        /**
         *Togglethecheckboxifitisactivatedduetoaclickonitself.
         *
         *@override
         *@param{Object}[options]
         *@param{Event}[options.event]theeventwhichfiredthisactivation
         *@returns{boolean}trueifthecomponentwasactivated,falseifthe
         *                   focusableelementwasnotfoundorinvisible
         */
        activate(options){
            constactivated=super.activate(options);
            //Theeventmighthavebeenfiredonthenonfieldversionof
            //thisfield,wecanstilltestthepresenceofitscustomclass.
            if(activated&&options&&options.event&&options.event.target
                .closest('.custom-control.custom-checkbox')){
                this._setValue(!this.value); //Togglethecheckbox
            }
            returnactivated;
        }
        /**
         *Associatesthe'for'attributeoftheinternallabel.
         *
         *@override
         */
        setIdForLabel(id){
            super.setIdForLabel(id);
            this.el.querySelector('label').setAttribute('for',id);
        }

        //----------------------------------------------------------------------
        //Handlers
        //----------------------------------------------------------------------

        /**
         *Properlyupdatethevaluewhenthecheckboxis(un)tickedtotrigger
         *possibleonchanges.
         *
         *@private
         */
        _onChange(ev){
            this._setValue(ev.target.checked);
        }
        /**
         *Implementkeyboardmovements.Mostlyusefulforitsenvironment,such
         *asalistview.
         *
         *@override
         *@private
         *@param{KeyEvent}ev
         */
        _onKeydown(ev){
            switch(ev.which){
                case$.ui.keyCode.ENTER:
                    //preventsubsequent'click'event(see_onKeydownofAbstractField)
                    ev.preventDefault();
                    this._setValue(!this.value);
                    return;
                case$.ui.keyCode.UP:
                case$.ui.keyCode.RIGHT:
                case$.ui.keyCode.DOWN:
                case$.ui.keyCode.LEFT:
                    ev.preventDefault();
            }
            super._onKeydown(ev);
        }
    }
    FieldBoolean.components={CustomCheckbox};
    FieldBoolean.description=_lt("Checkbox");
    FieldBoolean.supportedFieldTypes=['boolean'];
    FieldBoolean.template='web.FieldBoolean';


    return{
        FieldBadge,
        FieldBoolean,
    };
});
