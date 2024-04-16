flectra.define('point_of_sale.AbstractAwaitablePopup',function(require){
    'usestrict';

    const{useExternalListener}=owl.hooks;
    constPosComponent=require('point_of_sale.PosComponent');

    /**
     *Implementthisabstractclassbyextendingitlikeso:
     *```js
     *classConcretePopupextendsAbstractAwaitablePopup{
     *  asyncgetPayload(){
     *    return'result';
     *  }
     *}
     *ConcretePopup.template=owl.tags.xml`
     *  <div>
     *    <buttont-on-click="confirm">Okay</button>
     *    <buttont-on-click="cancel">Cancel</button>
     *  </div>
     *`
     *```
     *
     *Theconcretepopupcannowbeinstantiatedandbeawaitedfor
     *theuser'sresponselikeso:
     *```js
     *const{confirmed,payload}=awaitthis.showPopup('ConcretePopup');
     *//basedontheimplementationabove,
     *//ifconfirmed,payload='result'
     *//   otherwise,payload=null
     *```
     */
    classAbstractAwaitablePopupextendsPosComponent{
        constructor(){
            super(...arguments);
            useExternalListener(window,'keyup',this._cancelAtEscape);
        }
        asyncconfirm(){
            this.props.resolve({confirmed:true,payload:awaitthis.getPayload()});
            this.trigger('close-popup');
        }
        cancel(){
            this.props.resolve({confirmed:false,payload:null});
            this.trigger('close-popup');
        }
        _cancelAtEscape(event){
            if(event.key==='Escape'){
                this.cancel();
            }
        }
        /**
         *Overridethisintheconcretepopupimplementationtosetthe
         *payloadwhenthepopupisconfirmed.
         */
        asyncgetPayload(){
            returnnull;
        }
    }

    returnAbstractAwaitablePopup;
});
