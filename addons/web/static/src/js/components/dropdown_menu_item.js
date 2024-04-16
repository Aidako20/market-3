flectra.define('web.DropdownMenuItem',function(require){
    "usestrict";

    const{useListener}=require('web.custom_hooks');

    const{Component,hooks}=owl;
    const{useExternalListener,useRef,useState}=hooks;

    /**
     *Dropdownmenuitem
     *
     *Genericcomponentinstantiatedbyadropdownmenu(@seeDropdownMenu)in
     *theabsenceof`Component`and`props`keysinagivenitemobject.
     *
     *Initssimplestform,adropdownmenuitemwillbegivenadescription(optional,
     *buthighlyrecommended)andwilltriggera'select-item'whenclickedon.
     *Additionalyitcanreceivethefollowingprops:
     *-isActive:willadda`checked`symbolontheleftsideoftheitem
     *-removable:willadda`remove`trashiconontherightsideoftheitem.
     *             whenclicked,willtriggera'remove-item'event.
     *-options:willchangethebehaviouroftheitem;insteadoftriggering
     *           anevent,theitemwillactasanesteddropdownmenuanddisplay
     *           itsgivenoptions.Thesewillhavethesamedefinitionasanother
     *           dropdownitembutcannothaveoptionsoftheirown.
     *
     *ItisrecommendedtoextendthisclasswhendefiningaComponentwhichwill
     *beputinsideofadropdownmenu(@seeCustomFilterItemasexample).
     *@extendsComponent
     */
    classDropdownMenuItemextendsComponent{
        constructor(){
            super(...arguments);

            this.canBeOpened=Boolean(this.props.options&&this.props.options.length);

            this.fallbackFocusRef=useRef('fallback-focus');
            this.state=useState({open:false});

            useExternalListener(window,'click',this._onWindowClick);
            useListener('keydown',this._onKeydown);
        }

        //---------------------------------------------------------------------
        //Handlers
        //---------------------------------------------------------------------

        /**
         *@private
         *@param{KeyboardEvent}ev
         */
        _onKeydown(ev){
            if(['INPUT','TEXTAREA'].includes(document.activeElement.tagName)){
                return;
            }
            switch(ev.key){
                case'ArrowLeft':
                    if(this.canBeOpened&&this.state.open){
                        ev.preventDefault();
                        if(this.fallbackFocusRef.el){
                            this.fallbackFocusRef.el.focus();
                        }
                        this.state.open=false;
                    }
                    break;
                case'ArrowRight':
                    if(this.canBeOpened&&!this.state.open){
                        ev.preventDefault();
                        this.state.open=true;
                    }
                    break;
                case'Escape':
                    ev.target.blur();
                    if(this.canBeOpened&&this.state.open){
                        ev.preventDefault();
                        ev.stopPropagation();
                        if(this.fallbackFocusRef.el){
                            this.fallbackFocusRef.el.focus();
                        }
                        this.state.open=false;
                    }
            }
        }

        /**
         *@private
         *@param{MouseEvent}ev
         */
        _onWindowClick(ev){
            if(
                this.state.open&&
                !this.el.contains(ev.target)&&
                !this.el.contains(document.activeElement)
            ){
                this.state.open=false;
            }
        }
    }

    DropdownMenuItem.template='web.DropdownMenuItem';

    returnDropdownMenuItem;
});
