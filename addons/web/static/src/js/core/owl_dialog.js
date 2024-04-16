flectra.define('web.OwlDialog',function(require){
    "usestrict";

    constpatchMixin=require('web.patchMixin');

    const{Component,hooks,misc}=owl;
    const{Portal}=misc;
    const{useExternalListener,useRef}=hooks;
    constSIZE_CLASSES={
        'extra-large':'modal-xl',
        'large':'modal-lg',
        'small':'modal-sm',
    };

    /**
     *Dialog(owlversion)
     *
     *Representsabootstrap-styleddialoghandledwithpureJS.Itsimplementation
     *isroughlythesameasthelegacydialog,theonlyexceptionbeingthebuttons.
     *@extendsComponent
     **/
    classDialogextendsComponent{
        /**
         *@param{Object}[props]
         *@param{(boolean|string)}[props.backdrop='static']Thekindofmodalbackdrop
         *     touse(seeBootstrapdocumentation).
         *@param{string}[props.contentClass]Classtoaddtothedialog
         *@param{boolean}[props.fullscreen=false]Whetherthedialogshouldbe
         *     openinfullscreenmode(themainusecaseismobile).
         *@param{boolean}[props.renderFooter=true]Whetherthedialogfooter
         *     shouldberendered.
         *@param{boolean}[props.renderHeader=true]Whetherthedialogheader
         *     shouldberendered.
         *@param{string}[props.size='large']'extra-large','large','medium'
         *     or'small'.
         *@param{string}[props.stopClicks=true]whetherthedialogshouldstop
         *     theclickspropagationoutsideofitself.
         *@param{string}[props.subtitle='']
         *@param{string}[props.title='Flectra']
         *@param{boolean}[props.technical=true]Ifsettofalse,themodalwillhave
         *     thestandardfrontendstyle(usethisfornon-editorfrontendfeatures).
         */
        constructor(){
            super(...arguments);

            this.modalRef=useRef('modal');
            this.footerRef=useRef('modal-footer');

            useExternalListener(window,'keydown',this._onKeydown);
        }

        mounted(){
            this.constructor.display(this);

            this.env.bus.on('close_dialogs',this,this._close);

            if(this.props.renderFooter){
                //Setupmainbutton:willfirstlookforanelementwiththe
                //'btn-primary'class,thena'btn'class,thenthefirstbutton
                //element.
                letmainButton=this.footerRef.el.querySelector('.btn.btn-primary');
                if(!mainButton){
                    mainButton=this.footerRef.el.querySelector('.btn');
                }
                if(!mainButton){
                    mainButton=this.footerRef.el.querySelector('button');
                }
                if(mainButton){
                    this.mainButton=mainButton;
                    this.mainButton.addEventListener('keydown',this._onMainButtonKeydown.bind(this));
                    this.mainButton.focus();
                }
            }

            this._removeTooltips();
        }

        willUnmount(){
            this.env.bus.off('close_dialogs',this,this._close);

            this._removeTooltips();

            this.constructor.hide(this);
        }

        //--------------------------------------------------------------------------
        //Getters
        //--------------------------------------------------------------------------

        /**
         *@returns{string}
         */
        getsize(){
            returnSIZE_CLASSES[this.props.size];
        }

        //--------------------------------------------------------------------------
        //Private
        //--------------------------------------------------------------------------

        /**
         *Sendaneventsignalingthatthedialogmustbeclosed.
         *@private
         */
        _close(){
            this.trigger('dialog-closed');
        }

        /**
         *RemoveanyexistingtooltippresentintheDOM.
         *@private
         */
        _removeTooltips(){
            for(consttooltipofdocument.querySelectorAll('.tooltip')){
                tooltip.remove();//removeopentooltipifanytopreventthemstayingwhenmodalisopened
            }
        }

        //--------------------------------------------------------------------------
        //Handlers
        //--------------------------------------------------------------------------

        /**
         *@private
         *@param{MouseEvent}ev
         */
        _onBackdropClick(ev){
            if(!this.props.backdrop||ev.target!==ev.currentTarget){
                return;
            }
            if(this.props.backdrop==='static'){
                if(this.mainButton){
                    this.mainButton.focus();
                }
            }else{
                this._close();
            }
        }

        /**
         *@private
         *@param{MouseEvent}ev
         */
        _onClick(ev){
            if(this.props.stopClicks){
                ev.stopPropagation();
            }
        }

        /**
         *@private
         */
        _onFocus(){
            if(this.mainButton){
                this.mainButton.focus();
            }
        }

        /**
         *ManagetheTABkeyonthemainbutton.Ifthefocusisonaprimary
         *buttonandtheusertriestotabtogotothenextbutton:atooltip
         *willbedisplayed.
         *@private
         *@param{KeyboardEvent}ev
         */
        _onMainButtonKeydown(ev){
            if(ev.key==='Tab'&&!ev.shiftKey){
                ev.preventDefault();
                $(this.mainButton)
                    .tooltip({
                        delay:{show:200,hide:0},
                        title:()=>this.env.qweb.renderToString('web.DialogButton.tooltip',{
                            title:this.mainButton.innerText.toUpperCase(),
                        }),
                        trigger:'manual',
                    })
                    .tooltip('show');
            }
        }

        /**
         *@private
         *@param{KeyboardEvent}ev
         */
        _onKeydown(ev){
            if(
                ev.key==='Escape'&&
                !['INPUT','TEXTAREA'].includes(ev.target.tagName)&&
                this.constructor.displayed[this.constructor.displayed.length-1]===this
            ){
                ev.preventDefault();
                ev.stopImmediatePropagation();
                ev.stopPropagation();
                this._close();
            }
        }

        //--------------------------------------------------------------------------
        //Static
        //--------------------------------------------------------------------------

        /**
         *Pushthegivendialogattheendofthedisplayedlistthensetitas
         *activeandalltheothersaspassive.
         *@param{(LegacyDialog|OwlDialog)}dialog
         */
        staticdisplay(dialog){
            constactiveDialog=this.displayed[this.displayed.length-1];
            if(activeDialog){
                //Deactivatepreviousdialog
                constactiveDialogEl=activeDialoginstanceofthis?
                    //Owldialog
                    activeDialog.modalRef.el:
                    //Legacydialog
                    activeDialog.$modal[0];
                activeDialogEl.classList.add('o_inactive_modal');
            }
            //Pushdialog
            this.displayed.push(dialog);
            //Updatebodyclass
            document.body.classList.add('modal-open');
        }

        /**
         *Setthegivendisplayeddialogaspassiveandthelastaddeddisplayeddialog
         *asactive,thenremoveitfromthedisplayedlist.
         *@param{(LegacyDialog|OwlDialog)}dialog
         */
        statichide(dialog){
            //Removegivendialogfromthelist
            this.displayed.splice(this.displayed.indexOf(dialog),1);
            //Activatelastdialogandupdatebodyclass
            constlastDialog=this.displayed[this.displayed.length-1];
            if(lastDialog){
                lastDialog.el.focus();
                constmodalEl=lastDialoginstanceofthis?
                    //Owldialog
                    lastDialog.modalRef.el:
                    //Legacydialog
                    lastDialog.$modal[0];
                modalEl.classList.remove('o_inactive_modal');
            }else{
                document.body.classList.remove('modal-open');
            }
        }
    }

    Dialog.displayed=[];

    Dialog.components={Portal};
    Dialog.defaultProps={
        backdrop:'static',
        renderFooter:true,
        renderHeader:true,
        size:'large',
        stopClicks:true,
        technical:true,
        title:"Flectra",
    };
    Dialog.props={
        backdrop:{validate:b=>['static',true,false].includes(b)},
        contentClass:{type:String,optional:1},
        fullscreen:{type:Boolean,optional:1},
        renderFooter:Boolean,
        renderHeader:Boolean,
        size:{validate:s=>['extra-large','large','medium','small'].includes(s)},
        stopClicks:Boolean,
        subtitle:{type:String,optional:1},
        technical:Boolean,
        title:String,
    };
    Dialog.template='web.OwlDialog';

    returnpatchMixin(Dialog);
});
