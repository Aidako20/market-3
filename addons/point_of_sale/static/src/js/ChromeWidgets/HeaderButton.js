flectra.define('point_of_sale.HeaderButton',function(require){
    'usestrict';

    const{useState}=owl;
    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    //PreviouslyHeaderButtonWidget
    //Thisistheclosesessionbutton
    classHeaderButtonextendsPosComponent{
        constructor(){
            super(...arguments);
            this.state=useState({label:'Close'});
            this.confirmed=null;
        }
        gettranslatedLabel(){
            returnthis.env._t(this.state.label);
        }
        onClick(){
            if(!this.confirmed){
                this.state.label='Confirm';
                this.confirmed=setTimeout(()=>{
                    this.state.label='Close';
                    this.confirmed=null;
                },2000);
            }else{
                this.trigger('close-pos');
            }
        }
    }
    HeaderButton.template='HeaderButton';

    Registries.Component.add(HeaderButton);

    returnHeaderButton;
});
