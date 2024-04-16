flectra.define('web.Pager',function(require){
    "usestrict";

    const{useAutofocus}=require('web.custom_hooks');

    const{Component,hooks}=owl;
    const{useState}=hooks;

    /**
     *Pager
     *
     *Thepagergoesfrom1tosize(included).
     *ThecurrentvalueiscurrentMinimumiflimit===1ortheinterval:
     *     [currentMinimum,currentMinimum+limit[iflimit>1].
     *Thevaluecanbemanuallychangedbyclickingonthepagervalueandgiving
     *aninputmatchingthepattern:min[,max](inwhichthecommacanbeadash
     *orasemicolon).
     *Thepageralsoprovidestwobuttonstoquicklychangethecurrentpage(next
     *orprevious).
     *@extendsComponent
     */
    classPagerextendsComponent{
        /**
         *@param{Object}[props]
         *@param{int}[props.size]thetotalnumberofelements
         *@param{int}[props.currentMinimum]thefirstelementofthecurrent_page
         *@param{int}[props.limit]thenumberofelementsperpage
         *@param{boolean}[props.editable]editablefeatureofthepager
         *@param{function}[props.validate]callbackreturningaPromiseto
         *  validatechanges
         *@param{boolean}[props.withAccessKey]canbedisabled,forexample,
         *  forx2mwidgets
         */
        constructor(){
            super(...arguments);

            this.state=useState({
                disabled:false,
                editing:false,
            });

            useAutofocus();
        }

        asyncwillUpdateProps(){
            this.state.editing=false;
            this.state.disabled=false;
        }

        //---------------------------------------------------------------------
        //Getters
        //---------------------------------------------------------------------

        /**
         *@returns{number}
         */
        getmaximum(){
            returnMath.min(this.props.currentMinimum+this.props.limit-1,this.props.size);
        }

        /**
         *@returns{boolean}trueiffthereisonlyonepage
         */
        getsinglePage(){
            return(1===this.props.currentMinimum)&&(this.maximum===this.props.size);
        }

        /**
         *@returns{number}
         */
        getvalue(){
            returnthis.props.currentMinimum+(this.props.limit>1?`-${this.maximum}`:'');
        }

        //---------------------------------------------------------------------
        //Private
        //---------------------------------------------------------------------

        /**
         *Updatethepager'sstateaccordingtoapageraction
         *@private
         *@param{number}[direction]theaction(previousornext)onthepager
         */
        async_changeSelection(direction){
            try{
                awaitthis.props.validate();
            }catch(err){
                return;
            }
            const{limit,size}=this.props;

            //ComputethenewcurrentMinimum
            letcurrentMinimum=(this.props.currentMinimum+limit*direction);
            if(currentMinimum>size){
                currentMinimum=1;
            }elseif((currentMinimum<1)&&(limit===1)){
                currentMinimum=size;
            }elseif((currentMinimum<1)&&(limit>1)){
                currentMinimum=size-((size%limit)||limit)+1;
            }

            //There-renderingofthepagermustbedonebeforethetriggerof
            //event'pager-changed'astherenderingmayenablethepager
            //(andacommonuseistodisablethepagerwhenthiseventis
            //triggered,andtore-enableitwhenthedatahavebeenreloaded).
            this._updateAndDisable(currentMinimum,limit);
        }

        /**
         *Savethestatefromthecontentoftheinput
         *@private
         *@param{string}valuethenewrawpagervalue
         *@returns{Promise}
         */
        async_saveValue(value){
            try{
                awaitthis.props.validate();
            }catch(err){
                return;
            }
            const[min,max]=value.trim().split(/\s*[\-\s,;]\s*/);

            letcurrentMinimum=Math.max(Math.min(parseInt(min,10),this.props.size),1);
            letmaximum=max?Math.max(Math.min(parseInt(max,10),this.props.size),1):min;

            if(
                !isNaN(currentMinimum)&&
                !isNaN(maximum)&&
                currentMinimum<=maximum
            ){
                constlimit=Math.max(maximum-currentMinimum)+1;
                this._updateAndDisable(currentMinimum,limit);
            }
        }

        /**
         *Commitsthecurrentinputvalue.Therearetwoscenarios:
         *-thevalueisthesame:thepagertogglesbacktoreadonly
         *-thevaluechanged:thepagerisdisabledtopreventfurtherchanges
         *Eitherwaythe"pager-changed"eventistriggeredtoreloadthe
         *view.
         *@private
         *@param{number}currentMinimum
         *@param{number}limit
         */
        _updateAndDisable(currentMinimum,limit){
            if(
                currentMinimum!==this.props.currentMinimum||
                limit!==this.props.limit
            ){
                this.state.disabled=true;
            }else{
                //Inthiscasewewanttotriggeranupdate,butsinceitwill
                //notre-renderthepager(currentprops===nextprops)we
                //havetodisabletheeditionmanuallyhere.
                this.state.editing=false;
            }
            this.trigger('pager-changed',{currentMinimum,limit});
        }

        //---------------------------------------------------------------------
        //Handlers
        //---------------------------------------------------------------------

        /**
         *@private
         */
        _onEdit(){
            if(
                this.props.editable&&//editable
                !this.state.editing&&//notalreadyediting
                !this.state.disabled//notbeingchangedalready
            ){
                this.state.editing=true;
            }
        }

        /**
         *@private
         *@param{InputEvent}ev
         */
        _onValueChange(ev){
            this._saveValue(ev.currentTarget.value);
            if(!this.state.disabled){
                ev.preventDefault();
            }
        }

        /**
         *@private
         *@param{KeyboardEvent}ev
         */
        _onValueKeydown(ev){
            switch(ev.key){
                case'Enter':
                    ev.preventDefault();
                    ev.stopPropagation();
                    this._saveValue(ev.currentTarget.value);
                    break;
                case'Escape':
                    ev.preventDefault();
                    ev.stopPropagation();
                    this.state.editing=false;
                    break;
            }
        }
    }

    Pager.defaultProps={
        editable:true,
        validate:async()=>{},
        withAccessKey:true,
    };
    Pager.props={
        currentMinimum:{type:Number,optional:1},
        editable:Boolean,
        limit:{validate:l=>!isNaN(l),optional:1},
        size:{type:Number,optional:1},
        validate:Function,
        withAccessKey:Boolean,
    };
    Pager.template='web.Pager';

    returnPager;
});
