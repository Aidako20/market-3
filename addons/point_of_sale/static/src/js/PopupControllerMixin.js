flectra.define('point_of_sale.PopupControllerMixin',function(require){
    'usestrict';

    const{useState}=owl;
    const{useListener}=require('web.custom_hooks');

    /**
     *Allowsthecomponentdeclaredwiththismixintheabilityshowpopupdynamically,
     *providedthefollowing:
     * 1.Thefollowingelementisdeclaredinthetemplate.ItiswherethePopupwillberendered.
     *    `<tt-if="popup.isShown"t-component="popup.component"t-props="popupProps"t-key="popup.name"/>`
     * 2.Thecomponentshouldtrigger`show-popup`eventtoshowthepopupand`close-popup`event
     *    toclose.InPosComponent,`showPopup`isconvenientlydeclaredtosatisfythisrequirement.
     *@param{Function}xclassdefinitiontomixwithduringextension
     */
    constPopupControllerMixin=x=>
        classextendsx{
            constructor(){
                super(...arguments);
                useListener('show-popup',this.__showPopup);
                useListener('close-popup',this.__closePopup);

                this.popup=useState({isShown:false,name:null,component:null});
                this.popupProps={};//WewanttoavoidmakingthepropstobecomeProxy!
            }
            __showPopup(event){
                const{name,props,resolve}=event.detail;
                constpopupConstructor=this.constructor.components[name];
                if(popupConstructor.dontShow){
                    resolve();
                    return;
                }
                this.popup.isShown=true;
                this.popup.name=name;
                this.popup.component=popupConstructor;
                this.popupProps=Object.assign({},props,{resolve});
            }
            __closePopup(){
                this.popup.isShown=false;
            }
        };

    returnPopupControllerMixin;
});
