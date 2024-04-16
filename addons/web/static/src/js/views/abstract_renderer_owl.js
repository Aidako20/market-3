flectra.define('web.AbstractRendererOwl',function(){
    "usestrict";

    //Renderersmaydisplaysampledatawhenthereisnorealdatatodisplay.In
    //thiscasethedataisdisplayedwithopacityandcan'tbeclicked.Moreover,
    //wealsowanttopreventtheuserfromaccessingDOMelementswithTAB
    //navigation.Thisisthelistofelementswewon'tallowtofocus.
    constFOCUSABLE_ELEMENTS=[
        //focusablebydefault
        'a','button','input','select','textarea',
        //manuallyset
        '[tabindex="0"]'
    ].map((sel)=>`:scope${sel}`).join(',');

    classAbstractRendererextendsowl.Component{

        constructor(){
            super(...arguments);
            //Definestheelementssuppressedwhenindemodata.Thismustbealist
            //ofDOMselectorsmatchingviewelementsthatwill:
            //1.receivethe'o_sample_data_disabled'class(greydout&nouserevents)
            //2.havethemselvesandanyoftheirfocusablechildrenremovedfromthe
            //   tabnavigation
            this.sampleDataTargets=[];
        }

        mounted(){
            this._suppressFocusableElements();
        }

        patched(){
            this._suppressFocusableElements();
        }

        /**
         *Suppresses'tabindex'propertyonanyfocusableelementlocatedinside
         *rootelementsdefinedinthe`this.sampleDataTargets`objectandassigns
         *the'o_sample_data_disabled'classtotheserootelements.
         *
         *@private
         *@seesampleDataTargets
         */
        _suppressFocusableElements(){
            if(!this.props.isSample||this.props.isEmbedded){
                constdisabledEls=this.el.querySelectorAll(`.o_sample_data_disabled`);
                disabledEls.forEach(el=>el.classList.remove('o_sample_data_disabled'));
                return;
            }
            constrootEls=[];
            for(constselectorofthis.sampleDataTargets){
                rootEls.push(...this.el.querySelectorAll(`:scope${selector}`));
            }
            constfocusableEls=newSet(rootEls);
            for(constrootElofrootEls){
                rootEl.classList.add('o_sample_data_disabled');
                for(constfocusableElofrootEl.querySelectorAll(FOCUSABLE_ELEMENTS)){
                    focusableEls.add(focusableEl);
                }
            }
            for(constfocusableEloffocusableEls){
                focusableEl.setAttribute('tabindex',-1);
                if(focusableEl.classList.contains('dropdown-item')){
                    //TellsBootstraptoignorethedropdowniteminkeynav
                    focusableEl.classList.add('disabled');
                }
            }
        }
    }

    returnAbstractRenderer;

});
