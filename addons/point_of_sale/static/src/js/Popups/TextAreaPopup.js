flectra.define('point_of_sale.TextAreaPopup',function(require){
    'usestrict';

    const{useState,useRef}=owl.hooks;
    constAbstractAwaitablePopup=require('point_of_sale.AbstractAwaitablePopup');
    constRegistries=require('point_of_sale.Registries');

    //formerlyTextAreaPopupWidget
    //IMPROVEMENT:ThiscodeisverysimilartoTextInputPopup.
    //     Combiningthemwouldreducethecode.
    classTextAreaPopupextendsAbstractAwaitablePopup{
        /**
         *@param{Object}props
         *@param{string}props.startingValue
         */
        constructor(){
            super(...arguments);
            this.state=useState({inputValue:this.props.startingValue});
            this.inputRef=useRef('input');
        }
        mounted(){
            this.inputRef.el.focus();
        }
        getPayload(){
            returnthis.state.inputValue;
        }
    }
    TextAreaPopup.template='TextAreaPopup';
    TextAreaPopup.defaultProps={
        confirmText:'Ok',
        cancelText:'Cancel',
        title:'',
        body:'',
    };

    Registries.Component.add(TextAreaPopup);

    returnTextAreaPopup;
});
