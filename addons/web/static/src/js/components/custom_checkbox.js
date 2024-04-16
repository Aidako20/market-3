flectra.define('web.CustomCheckbox',function(require){
    "usestrict";

    constutils=require('web.utils');

    const{Component}=owl;

    /**
     *Customcheckbox
     *
     *ComponentthatcanbeusedintemplatestorenderthecustomcheckboxofFlectra.
     *
     *<CustomCheckbox
     *    value="boolean"
     *    disabled="boolean"
     *    text="'Changethelabeltext'"
     *    t-on-change="_onValueChange"
     *    />
     *
     *@extendsComponent
     */
    classCustomCheckboxextendsComponent{
        /**
         *@param{Object}[props]
         *@param{string|number|null}[props.id]
         *@param{boolean}[props.value=false]
         *@param{boolean}[props.disabled=false]
         *@param{string}[props.text]
         */
        constructor(){
            super(...arguments);
            this._id=`checkbox-comp-${utils.generateID()}`;
        }
    }

    CustomCheckbox.props={
        id:{
            type:[String,Number],
            optional:1,
        },
        disabled:{
            type:Boolean,
            optional:1,
        },
        value:{
            type:Boolean,
            optional:1,
        },
        text:{
            type:String,
            optional:1,
        },
    };

    CustomCheckbox.template='web.CustomCheckbox';

    returnCustomCheckbox;
});
