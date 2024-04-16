flectra.define('web.Dialog',function(require){
"usestrict";

varcore=require('web.core');
vardom=require('web.dom');
varWidget=require('web.Widget');
constOwlDialog=require('web.OwlDialog');

varQWeb=core.qweb;
var_t=core._t;

/**
 *Ausefulclasstohandledialogs.
 *Attributes:
 *
 *``$footer``
 *  AjQueryelementtargetingadompartwherebuttonscanbeadded.It
 *  alwaysexistsduringthelifecycleofthedialog.
 **/
varDialog=Widget.extend({
    tagName:'main',
    xmlDependencies:['/web/static/src/xml/dialog.xml'],
    custom_events:_.extend({},Widget.prototype.custom_events,{
        focus_control_button:'_onFocusControlButton',
        close_dialog:'_onCloseDialog',
    }),
    events:_.extend({},Widget.prototype.events,{
        'keydown.modal-footerbutton':'_onFooterButtonKeyDown',
    }),
    /**
     *@param{Widget}parent
     *@param{Object}[options]
     *@param{string}[options.title=Flectra]
     *@param{string}[options.subtitle]
     *@param{string}[options.size=large]-'extra-large','large','medium'
     *       or'small'
     *@param{boolean}[options.fullscreen=false]-whetherornotthedialog
     *       shouldbeopeninfullscreenmode(themainusecaseismobile)
     *@param{string}[options.dialogClass]-classtoaddtothemodal-body
     *@param{jQuery}[options.$content]
     *       Elementwhichwillbethe$el,replacethe.modal-bodyandgetthe
     *       modal-bodyclass
     *@param{Object[]}[options.buttons]
     *       Listofbuttondescriptions.Note:ifnobuttons,a"ok"primary
     *       buttonisaddedtoallowclosingthedialog
     *@param{string}[options.buttons[].text]
     *@param{string}[options.buttons[].classes]
     *       Defaultto'btn-primary'ifonlyonebutton,'btn-secondary'
     *       otherwise
     *@param{boolean}[options.buttons[].close=false]
     *@param{function}[options.buttons[].click]
     *@param{boolean}[options.buttons[].disabled]
     *@param{boolean}[options.technical=true]
     *       Ifsettofalse,themodalwillhavethestandardfrontendstyle
     *       (usethisfornon-editorfrontendfeatures)
     *@param{jQueryElement}[options.$parentNode]
     *       Elementinwhichdialogwillbeappended,bydefaultitwillbe
     *       inthebody
     *@param{boolean|string}[options.backdrop='static']
     *       Thekindofmodalbackdroptouse(seeBSdocumentation)
     *@param{boolean}[options.renderHeader=true]
     *       Whetherornotthedialogshouldberenderedwithheader
     *@param{boolean}[options.renderFooter=true]
     *       Whetherornotthedialogshouldberenderedwithfooter
     *@param{function}[options.onForceClose]
     *       Callbackthattriggerswhenthemodalisclosedbyothermeansthanwiththebuttons
     *       e.g.pressingESC
     */
    init:function(parent,options){
        varself=this;
        this._super(parent);
        this._opened=newPromise(function(resolve){
            self._openedResolver=resolve;
        });
        if(this.on_attach_callback){
            this._opened=this.opened(this.on_attach_callback);
        }
        options=_.defaults(options||{},{
            title:_t('Flectra'),subtitle:'',
            size:'large',
            fullscreen:false,
            dialogClass:'',
            $content:false,
            buttons:[{text:_t("Ok"),close:true}],
            technical:true,
            $parentNode:false,
            backdrop:'static',
            renderHeader:true,
            renderFooter:true,
            onForceClose:false,
        });

        this.$content=options.$content;
        this.title=options.title;
        this.subtitle=options.subtitle;
        this.fullscreen=options.fullscreen;
        this.dialogClass=options.dialogClass;
        this.size=options.size;
        this.buttons=options.buttons;
        this.technical=options.technical;
        this.$parentNode=options.$parentNode;
        this.backdrop=options.backdrop;
        this.renderHeader=options.renderHeader;
        this.renderFooter=options.renderFooter;
        this.onForceClose=options.onForceClose;

        core.bus.on('close_dialogs',this,this.destroy.bind(this));
    },
    /**
     *WaitforXMLdependenciesandinstantiatethemodalstructure(except
     *modal-body).
     *
     *@override
     */
    willStart:function(){
        varself=this;
        returnthis._super.apply(this,arguments).then(function(){
            //Rendermodaloncexmldependenciesareloaded
            self.$modal=$(QWeb.render('Dialog',{
                fullscreen:self.fullscreen,
                title:self.title,
                subtitle:self.subtitle,
                technical:self.technical,
                renderHeader:self.renderHeader,
                renderFooter:self.renderFooter,
            }));
            switch(self.size){
                case'extra-large':
                    self.$modal.find('.modal-dialog').addClass('modal-xl');
                    break;
                case'large':
                    self.$modal.find('.modal-dialog').addClass('modal-lg');
                    break;
                case'small':
                    self.$modal.find('.modal-dialog').addClass('modal-sm');
                    break;
            }
            if(self.renderFooter){
                self.$footer=self.$modal.find(".modal-footer");
                self.set_buttons(self.buttons);
            }
            self.$modal.on('hidden.bs.modal',_.bind(self.destroy,self));
        });
    },
    /**
     *@override
     */
    renderElement:function(){
        this._super();
        //Note:ideally,the$elwhichiscreated/sethereshouldusethe
        //'main'tag,wecannotenforcethisasitwouldrequiretore-create
        //thewholeelement.
        if(this.$content){
            this.setElement(this.$content);
        }
        this.$el.addClass('modal-body'+this.dialogClass);
    },
    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------
    /**
     *@param{Object[]}buttons-@seeinit
     */
    set_buttons:function(buttons){
        this._setButtonsTo(this.$footer,buttons);
    },

    set_title:function(title,subtitle){
        this.title=title||"";
        if(subtitle!==undefined){
            this.subtitle=subtitle||"";
        }

        var$title=this.$modal.find('.modal-title').first();
        var$subtitle=$title.find('.o_subtitle').detach();
        $title.html(this.title);
        $subtitle.html(this.subtitle).appendTo($title);

        returnthis;
    },

    opened:function(handler){
        return(handler)?this._opened.then(handler):this._opened;
    },

    /**
     *Showadialog
     *
     *@param{Object}options
     *@param{boolean}options.shouldFocusButtons iftrue,putthefocuson
     *thefirstbuttonprimarywhenthedialogopens
     */
    open:function(options){
        $('.tooltip').remove();//removeopentooltipifanytopreventthemstayingwhenmodalisopened

        varself=this;
        this.appendTo($('<div/>')).then(function(){
            if(self.isDestroyed()){
                return;
            }
            self.$modal.find(".modal-body").replaceWith(self.$el);
            self.$modal.attr('open',true);
            if(self.$parentNode){
                self.$modal.appendTo(self.$parentNode);
            }
            self.$modal.modal({
                show:true,
                backdrop:self.backdrop,
            });
            self._openedResolver();
            if(options&&options.shouldFocusButtons){
                self._onFocusControlButton();
            }

            //NotifiesOwlDialogtoadjustfocus/activepropertiesonowldialogs
            OwlDialog.display(self);
        });

        returnself;
    },

    close:function(){
        this.destroy();
    },

    /**
     *Closeanddestroythedialog.
     *
     *@param{Object}[options]
     *@param{Object}[options.infos]ifprovidedand`silent`isunset,the
     *  `on_close`handlerwillpassthisinformationrelatedtoclosingthis
     *  information.
     *@param{boolean}[options.silent=false]ifset,donotcallthe
     *  `on_close`handler.
     */
    destroy:function(options){
        //Needtotriggerbeforerealdestroybutif'closed'handlerdestroys
        //thewidgetagain,wewanttoavoidinfiniterecursion
        if(!this.__closed){
            this.__closed=true;
            this.trigger('closed',options);
        }

        if(this.isDestroyed()){
            return;
        }

        //NotifiesOwlDialogtoadjustfocus/activepropertiesonowldialogs.
        //Onlyhastobedoneifthedialoghasbeenopened(hasanel).
        if(this.el){
            OwlDialog.hide(this);
        }

        //TriggerstheonForceCloseeventifthecallbackisdefined
        if(this.onForceClose){
            this.onForceClose();
        }
        varisFocusSet=this._focusOnClose();

        this._super();

        $('.tooltip').remove();//removeopentooltipifanytopreventthemstayingwhenmodalhasdisappeared
        if(this.$modal){
            if(this.on_detach_callback){
                this.on_detach_callback();
            }
            this.$modal.modal('hide');
            this.$modal.remove();
        }

        constmodals=$('body.modal').filter(':visible');
        if(modals.length){
            if(!isFocusSet){
                modals.last().focus();
            }
            //Keepclassmodal-open(deletedbybootstraphidefnct)onbodytoallowscrollinginsidethemodal
            $('body').addClass('modal-open');
        }
    },
    /**
     *addsthekeydownbehaviortothedialogsafterexternalfilesmodifies
     *itsDOM.
     */
    rebindButtonBehavior:function(){
        this.$footer.on('keydown',this._onFooterButtonKeyDown);
    },
    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------
    /**
     *Managesthefocuswhenthedialogcloses.Thedefaultbehavioristosetthefocusonthetop-mostopenedpopup.
     *Thegoalofthisfunctionistobeoverriddenbyallchildrenofthedialogclass.
     *
     *@returns:boolean shouldreturntrueifthefocushasalreadybeensetelsefalse.
     */
    _focusOnClose:function(){
        returnfalse;
    },
    /**
     *Renderandsetthegivenbuttonsintoatargetelement
     *
     *@private
     *@param{jQueryElement}$targetThedestinationoftherenderedbuttons
     *@param{Array}buttonsThearrayofbuttonstorender
     */
    _setButtonsTo($target,buttons){
        varself=this;
        $target.empty();
        _.each(buttons,function(buttonData){
            var$button=dom.renderButton({
                attrs:{
                    class:buttonData.classes||(buttons.length>1?'btn-secondary':'btn-primary'),
                    disabled:buttonData.disabled,
                },
                icon:buttonData.icon,
                text:buttonData.text,
            });
            $button.on('click',function(e){
                vardef;
                if(buttonData.click){
                    def=buttonData.click.call(self,e);
                }
                if(buttonData.close){
                    self.onForceClose=false;
                    Promise.resolve(def).then(self.close.bind(self));
                }
            });
            if(self.technical){
                $target.append($button);
            }else{
                $target.prepend($button);
            }
        });
    },
    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------
    /**
     *@private
     */
    _onCloseDialog:function(ev){
        ev.stopPropagation();
        this.close();
    },
    /**
     *Movesthefocustothefirstbuttonprimaryinthefooterofthedialog
     *
     *@private
     *@param{flectraEvent}e
     */
    _onFocusControlButton:function(e){
        if(this.$footer){
            if(e){
                e.stopPropagation();
            }
            this.$footer.find('.btn-primary:visible:first()').focus();
        }
    },
    /**
     *ManagestheTABkeyonthebuttons.Ifyouthefocusisonaprimary
     *buttonandtheuserstriestotabtogotothenextbutton,display
     *atooltip
     *
     *@param{jQueryEvent}e
     *@private
     */
    _onFooterButtonKeyDown:function(e){
        switch(e.which){
            case$.ui.keyCode.TAB:
                if(!e.shiftKey&&e.target.classList.contains("btn-primary")){
                    e.preventDefault();
                    var$primaryButton=$(e.target);
                    $primaryButton.tooltip({
                        delay:{show:200,hide:0},
                        title:function(){
                            returnQWeb.render('FormButton.tooltip',{title:$primaryButton.text().toUpperCase()});
                        },
                        trigger:'manual',
                    });
                    $primaryButton.tooltip('show');
                }
                break;
        }
    }
});

//staticmethodtoopensimplealertdialog
Dialog.alert=function(owner,message,options){
    varbuttons=[{
        text:_t("Ok"),
        close:true,
        click:options&&options.confirm_callback,
    }];
    returnnewDialog(owner,_.extend({
        size:'medium',
        buttons:buttons,
        $content:$('<main/>',{
            role:'alert',
            text:message,
        }),
        title:_t("Alert"),
        onForceClose:options&&(options.onForceClose||options.confirm_callback),
    },options)).open({shouldFocusButtons:true});
};

//staticmethodtoopensimpleconfirmdialog
Dialog.confirm=function(owner,message,options){
    /**
     *Createsanimprovedcallbackfromthegivencallbackvalueatthegiven
     *keyfromtheparentfunction'soptionsparameter.Thisisimprovedto:
     *
     *-Preventcallinggivencallbacksonceonehasbeencalled.
     *
     *-Re-allowcallingcallbacksonceapreviouscallbackcall'sreturned
     *  Promiseisrejected.
     */
    letisBlocked=false;
    functionmakeCallback(key){
        constcallback=options&&options[key];
        returnfunction(){
            if(isBlocked){
                //Donot(re)callanycallbackandreturnarejectedPromise
                //topreventclosingtheDialog.
                returnPromise.reject();
            }
            isBlocked=true;
            constcallbackRes=callback&&callback.apply(this,arguments);
            Promise.resolve(callbackRes).guardedCatch(()=>{
                isBlocked=false;
            });
            returncallbackRes;
        };
    }
    varbuttons=[
        {
            text:_t("Ok"),
            classes:'btn-primary',
            close:true,
            click:makeCallback('confirm_callback'),
        },
        {
            text:_t("Cancel"),
            close:true,
            click:makeCallback('cancel_callback'),
        }
    ];
    returnnewDialog(owner,_.extend({
        size:'medium',
        buttons:buttons,
        $content:$('<main/>',{
            role:'alert',
            text:message,
        }),
        title:_t("Confirmation"),
        onForceClose:options&&(options.onForceClose||options.cancel_callback),
    },options)).open({shouldFocusButtons:true});
};

/**
 *Staticmethodtoopendoubleconfirmationdialog.
 *
 *@param{Widget}owner
 *@param{string}message
 *@param{Object}[options]@seeDialog.init@seeDialog.confirm
 *@param{string}[options.securityLevel="warning"]-bootstrapcolor
 *@param{string}[options.securityMessage="Iamsureaboutthis"]
 *@returns{Dialog}(open()isautomaticallycalled)
 */
Dialog.safeConfirm=function(owner,message,options){
    var$checkbox=dom.renderCheckbox({
        text:options&&options.securityMessage||_t("Iamsureaboutthis."),
    }).addClass('mb0');
    var$securityCheck=$('<div/>',{
        class:'alertalert-'+(options&&options.securityLevel||'warning')+'mt8mb0',
    }).prepend($checkbox);
    var$content;
    if(options&&options.$content){
        $content=options.$content;
        deleteoptions.$content;
    }else{
        $content=$('<div>',{
            text:message,
        });
    }
    $content=$('<main/>',{role:'alert'}).append($content,$securityCheck);

    varbuttons=[
        {
            text:_t("Ok"),
            classes:'btn-primaryo_safe_confirm_button',
            close:true,
            click:options&&options.confirm_callback,
            disabled:true,
        },
        {
            text:_t("Cancel"),
            close:true,
            click:options&&options.cancel_callback
        }
    ];
    vardialog=newDialog(owner,_.extend({
        size:'medium',
        buttons:buttons,
        $content:$content,
        title:_t("Confirmation"),
        onForceClose:options&&(options.onForceClose||options.cancel_callback),
    },options));
    dialog.opened(function(){
        var$button=dialog.$footer.find('.o_safe_confirm_button');
        $securityCheck.on('click','input[type="checkbox"]',function(ev){
            $button.prop('disabled',!$(ev.currentTarget).prop('checked'));
        });
    });
    returndialog.open();
};

returnDialog;

});
