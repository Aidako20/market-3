flectra.define('point_of_sale.TextInputPopup',function(require){
    'usestrict';

    const{useState,useRef}=owl.hooks;
    constAbstractAwaitablePopup=require('point_of_sale.AbstractAwaitablePopup');
    constRegistries=require('point_of_sale.Registries');

    //formerlyTextInputPopupWidget
    classTextInputPopupextendsAbstractAwaitablePopup{
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
    TextInputPopup.template='TextInputPopup';
    TextInputPopup.defaultProps={
        confirmText:'Ok',
        cancelText:'Cancel',
        title:'',
        body:'',
        startingValue:'',
    };

    Registries.Component.add(TextInputPopup);

    returnTextInputPopup;
});
