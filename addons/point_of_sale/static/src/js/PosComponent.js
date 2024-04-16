flectra.define('point_of_sale.PosComponent',function(require){
    'usestrict';

    const{Component}=owl;

    classPosComponentextendsComponent{
        /**
         *ThisfunctionisavailabletoallComponentsthatinheritthisclass.
         *Thegoalofthisfunctionistoshowanawaitabledialog(popup)that
         *returnsaresponseafteruserinteraction.Seethefollowingforquick
         *demonstration:
         *
         *```
         *asyncgetUserName(){
         *  constuserResponse=awaitthis.showPopup(
         *    'TextInputPopup',
         *    {title:'Whatisyourname?'}
         *  );
         *  //atthispoint,theTextInputPopupisdisplayed.Dependingonhowthepopupisdefined,
         *  //saytheinputcontainsthename,theresultoftheinteractionwiththeuseris
         *  //savedin`userResponse`.
         *  console.log(userResponse);//logs{confirmed:true,payload:<name>}
         *}
         *```
         *
         *@param{String}nameNameofthepopupcomponent
         *@param{Object}propsObjectthatwillbeusedtorendertopopup
         */
        showPopup(name,props){
            returnnewPromise((resolve)=>{
                this.trigger('show-popup',{name,props,resolve});
            });
        }
        showTempScreen(name,props){
            returnnewPromise((resolve)=>{
                this.trigger('show-temp-screen',{name,props,resolve});
            });
        }
        showScreen(name,props){
            this.trigger('show-main-screen',{name,props});
        }
        /**
         *@param{String}name'bell'|'error'
         */
        playSound(name){
            this.trigger('play-sound',name);
        }
        /**
         *ControltheSyncNotificationcomponent.
         *@param{String}status'connected'|'connecting'|'disconnected'|'error'
         *@param{String}pendingnumberofpendingorderstosync
         */
        setSyncStatus(status,pending){
            this.trigger('set-sync-status',{status,pending});
        }
    }

    returnPosComponent;
});
