flectra.define('point_of_sale.MobileOrderManagementScreen',function(require){
    constOrderManagementScreen=require('point_of_sale.OrderManagementScreen');
    constRegistries=require('point_of_sale.Registries');
    const{useListener}=require('web.custom_hooks');
    const{useState}=owl.hooks;

    constMobileOrderManagementScreen=(OrderManagementScreen)=>{
        classMobileOrderManagementScreenextendsOrderManagementScreen{
            constructor(){
                super(...arguments);
                useListener('click-order',this._onShowDetails)
                this.mobileState=useState({showDetails:false});
            }
            _onShowDetails(){
                this.mobileState.showDetails=true;
            }
        }
        MobileOrderManagementScreen.template='MobileOrderManagementScreen';
        returnMobileOrderManagementScreen;
    };

    Registries.Component.addByExtending(MobileOrderManagementScreen,OrderManagementScreen);

    returnMobileOrderManagementScreen;
});
