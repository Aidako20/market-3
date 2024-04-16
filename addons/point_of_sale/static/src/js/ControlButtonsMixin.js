flectra.define('point_of_sale.ControlButtonsMixin',function(require){
    'usestrict';

    constRegistries=require('point_of_sale.Registries');

    /**
     *Componentthathasthismixinallowstheuseof`addControlButton`.
     *Alladdedcontrolbuttonsthatsatisfiestheconditioncanbeaccessed
     *thruthe`controlButtons`fieldoftheComponent'sinstance.These
     *controlbuttonscanthenberenderedintheComponent.
     *@param{Function}xsuperclass
     */
    constControlButtonsMixin=(x)=>{
        classExtendedextendsx{
            getcontrolButtons(){
                returnthis.constructor.controlButtons
                    .filter((cb)=>{
                        returncb.condition.bind(this)();
                    })
                    .map((cb)=>
                        Object.assign({},cb,{component:Registries.Component.get(cb.component)})
                    );
            }
        }
        Extended.controlButtons=[];
        /**
         *@param{Object}controlButton
         *@param{Function}controlButton.component
         *     BaseclassthatisaddedintheRegistries.Component.
         *@param{Function}controlButton.conditionzeroargumentfunctionthatisbound
         *     totheinstanceofProductScreen,suchthat`this.env.pos`canbeused
         *     insidethefunction.
         *@param{Array}[controlButton.position]arrayoftwoelements
         *     [locator,relativeTo]
         *     locator:string->anyof('before','after','replace')
         *     relativeTo:string->othercontrolButtonscomponentname
         */
        Extended.addControlButton=function(controlButton){
            //Wesetthenamefirst.
            if(!controlButton.name){
                controlButton.name=controlButton.component.name;
            }

            //Ifnopositionisset,wejustpushittothearray.
            if(!controlButton.position){
                this.controlButtons.push(controlButton);
            }else{
                //FindwheretoputthenewcontrolButton.
                const[locator,relativeTo]=controlButton.position;
                letwhereIndex=-1;
                for(leti=0;i<this.controlButtons.length;i++){
                    if(this.controlButtons[i].name===relativeTo){
                        if(['before','replace'].includes(locator)){
                            whereIndex=i;
                        }elseif(locator==='after'){
                            whereIndex=i+1;
                        }
                        break;
                    }
                }

                //Iffoundwheretoput,thenperformthenecessarymutationof
                //thebuttonsarray.
                //Else,wejustpushthiscontrolButtontothearray.
                if(whereIndex>-1){
                    this.controlButtons.splice(
                        whereIndex,
                        locator==='replace'?1:0,
                        controlButton
                    );
                }else{
                    letwarningMessage=
                        `'${controlButton.name}'hasinvalid'position'([${locator},${relativeTo}]).`+
                        'ItispushedtothecontrolButtonsstackinstead.';
                    console.warn(warningMessage);
                    this.controlButtons.push(controlButton);
                }
            }
        };
        returnExtended;
    };

    returnControlButtonsMixin;
});
