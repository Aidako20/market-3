flectra.define('web.DropdownMenu',function(require){
    "usestrict";

    constDropdownMenuItem=require('web.DropdownMenuItem');

    const{Component,hooks}=owl;
    const{useExternalListener,useRef,useState}=hooks;

    /**
     *Dropdownmenu
     *
     *Genericcomponentusedtogeneratealistofinteractiveitems.Itusessome
     *bootstrapclassesbutmostinteractionsarehandledinhereorinthedropdown
     *menuitemclassdefinition,includingsomekeyboardnavigationandescaping
     *system(clickoutsidetoclosethedropdown).
     *
     *Thelayoutofadropdownmenuisasfollowing:
     *>aButton(alwaysrendered)witha`title`andanoptional`icon`;
     *>aDropdown(renderedwhenopen)containingacollectionofgivenitems.
     *  Theseitemsmustbeobjectsandcanhavetwoshapes:
     *  1.item.Component&item.props>willinstantiatethegivenComponentwith
     *     thegivenprops.Anyadditionalkeywillbeuseless.
     *  2.anyothershape>willinstantiateaDropdownMenuItemwiththeitem
     *     objectbeingitsprops.Thereisnopropsvalidationasthisobject
     *     willbepassedas-iswhen`selected`andcancontainadditionalmeta-keys
     *     thatwillnotaffectthedisplayeditem.Formoreinformationregarding
     *     thebehaviouroftheseitems,@seeDropdownMenuItem.
     *@extendsComponent
     */
    classDropdownMenuextendsComponent{
        constructor(){
            super(...arguments);

            this.dropdownMenu=useRef('dropdown');
            this.state=useState({open:false});

            useExternalListener(window,'click',this._onWindowClick,true);
            useExternalListener(window,'keydown',this._onWindowKeydown);
        }

        //---------------------------------------------------------------------
        //Getters
        //---------------------------------------------------------------------

        /**
         *Indesktop,bydefault,wedonotdisplayacareticonnexttothe
         *dropdown.
         *@returns{boolean}
         */
        getdisplayCaret(){
            returnfalse;
        }

        /**
         *Inmobile,bydefault,wedisplayachevroniconnexttothedropdown
         *button.Notethatwhen'displayCaret'istrue,wedisplayacaret
         *insteadofachevron,nomatterthevalueof'displayChevron'.
         *@returns{boolean}
         */
        getdisplayChevron(){
            returnthis.env.device.isMobile;
        }

        /**
         *Canbeoverridentoforceanicononaninheritingclass.
         *@returns{string}FontAwesomeiconclass
         */
        geticon(){
            returnthis.props.icon;
        }

        /**
         *Meanttobeoverridentoprovidethelistofitemstodisplay.
         *@returns{Object[]}
         */
        getitems(){
            returnthis.props.items;
        }

        /**
         *@returns{string}
         */
        gettitle(){
            returnthis.props.title;
        }

        //---------------------------------------------------------------------
        //Handlers
        //---------------------------------------------------------------------

        /**
         *@private
         *@param{KeyboardEvent}ev
         */
        _onButtonKeydown(ev){
            switch(ev.key){
                case'ArrowLeft':
                case'ArrowRight':
                case'ArrowUp':
                case'ArrowDown':
                    constfirstItem=this.el.querySelector('.dropdown-item');
                    if(firstItem){
                        ev.preventDefault();
                        firstItem.focus();
                    }
            }
        }

        /**
         *@private
         *@param{OwlEvent}ev
         */
        _onItemSelected(/*ev*/){
            if(this.props.closeOnSelected){
                this.state.open=false;
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
                if(document.body.classList.contains("modal-open")){
                    //retrievetheactivemodalandcheckifthedropdownisachildofthismodal
                    constmodal=document.querySelector('body>.modal:not(.o_inactive_modal)');
                    if(modal&&!modal.contains(this.el)){
                        return;
                    }
                    constowlModal=document.querySelector('body>.o_dialog>.modal:not(.o_inactive_modal)');
                    if(owlModal&&!owlModal.contains(this.el)){
                        return;
                    }
                }
                //checkforanactiveopenbootstrapcalendarlikethefilterdropdowninsidethesearchpanel)
                if(document.querySelector('body>.bootstrap-datetimepicker-widget')){
                    return;
                }
                this.state.open=false;
            }
        }

        /**
         *@private
         *@param{KeyboardEvent}ev
         */
        _onWindowKeydown(ev){
            if(this.state.open&&ev.key==='Escape'){
                this.state.open=false;
            }
        }
    }

    DropdownMenu.components={DropdownMenuItem};
    DropdownMenu.defaultProps={items:[]};
    DropdownMenu.props={
        icon:{type:String,optional:1},
        items:{
            type:Array,
            element:Object,
            optional:1,
        },
        title:{type:String,optional:1},
        closeOnSelected:{type:Boolean,optional:1},
    };
    DropdownMenu.template='web.DropdownMenu';

    returnDropdownMenu;
});
