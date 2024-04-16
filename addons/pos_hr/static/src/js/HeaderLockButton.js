flectra.define('point_of_sale.HeaderLockButton',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');
    const{useState}=owl;

    classHeaderLockButtonextendsPosComponent{
        constructor(){
            super(...arguments);
            this.state=useState({isUnlockIcon:true,title:'Unlocked'});
        }
        asyncshowLoginScreen(){
            awaitthis.showTempScreen('LoginScreen');
        }
        onMouseOver(isMouseOver){
            this.state.isUnlockIcon=!isMouseOver;
            this.state.title=isMouseOver?'Lock':'Unlocked';
        }
    }

    Registries.Component.add(HeaderLockButton);

    returnHeaderLockButton;
});
