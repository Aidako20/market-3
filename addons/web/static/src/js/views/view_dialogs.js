flectra.define('web.view_dialogs',function(require){
"usestrict";

varconfig=require('web.config');
varcore=require('web.core');
varDialog=require('web.Dialog');
vardom=require('web.dom');
varview_registry=require('web.view_registry');
varselect_create_controllers_registry=require('web.select_create_controllers_registry');

var_t=core._t;

/**
 *ClasswitheverythingwhichiscommonbetweenFormViewDialogand
 *SelectCreateDialog.
 */
varViewDialog=Dialog.extend({
    custom_events:_.extend({},Dialog.prototype.custom_events,{
        push_state:'_onPushState',
    }),
    /**
     *@constructor
     *@param{Widget}parent
     *@param{options}[options]
     *@param{string}[options.dialogClass=o_act_window]
     *@param{string}[options.res_model]themodeloftherecord(s)toopen
     *@param{any[]}[options.domain]
     *@param{Object}[options.context]
     */
    init:function(parent,options){
        options=options||{};
        options.fullscreen=config.device.isMobile;
        options.dialogClass=options.dialogClass||''+'o_act_window';

        this._super(parent,$.extend(true,{},options));

        this.res_model=options.res_model||null;
        this.domain=options.domain||[];
        this.context=options.context||{};
        this.options=_.extend(this.options||{},options||{});
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Westopallpush_stateeventsfrombubblingup. Itwouldbeweirdto
     *changetheurlbecauseadialogopened.
     *
     *@param{FlectraEvent}event
     */
    _onPushState:function(event){
        event.stopPropagation();
    },
});

/**
 *Createandeditdialog(displaysaformviewrecordandleaveoncesaved)
 */
varFormViewDialog=ViewDialog.extend({
    /**
     *@param{Widget}parent
     *@param{Object}[options]
     *@param{string}[options.parentID]theidoftheparentrecord.Itis
     *  usefulforsituationssuchasaone2manyopenedinaformviewdialog.
     *  Inthatcase,wewanttobeabletoproperlyevaluatedomainswiththe
     *  'parent'key.
     *@param{integer}[options.res_id]theidoftherecordtoopen
     *@param{Object}[options.form_view_options]dictofoptionstopassto
     *  theFormView@todo:makeitwork
     *@param{Object}[options.fields_view]optionalformfields_view
     *@param{boolean}[options.readonly=false]onlyapplicablewhennotin
     *  creationmode
     *@param{boolean}[options.deletable=false]whetherornottherecordcan
     *  bedeleted
     *@param{boolean}[options.disable_multiple_selection=false]settotrue
     *  toremovethepossibilitytocreateseveralrecordsinarow
     *@param{function}[options.on_saved]callbackexecutedaftersavinga
     *  record. Itwillbecalledwiththerecorddata,andabooleanwhich
     *  indicatesifsomethingwaschanged
     *@param{function}[options.on_remove]callbackexecutedwhentheuser
     *  clicksonthe'Remove'button
     *@param{BasicModel}[options.model]ifgiven,itwillbeusedinsteadof
     * anewformviewmodel
     *@param{string}[options.recordID]ifgiven,themodelhastobegivenas
     *  well,andinthatcase,itwillbeusedwithoutloadinganything.
     *@param{boolean}[options.shouldSaveLocally]iftrue,theviewdialog
     *  willsavelocallyinsteadofactuallysaving(usefulforone2manys)
     *@param{function}[options._createContext]functiontogetcontextfornamefield
     *  usefulformany2many_tagswidgetwherewewanttoremoveddefault_namefield
     *  context.
     */
    init:function(parent,options){
        varself=this;
        options=options||{};

        this.res_id=options.res_id||null;
        this.on_saved=options.on_saved||(function(){});
        this.on_remove=options.on_remove||(function(){});
        this.context=options.context;
        this._createContext=options._createContext;
        this.model=options.model;
        this.parentID=options.parentID;
        this.recordID=options.recordID;
        this.shouldSaveLocally=options.shouldSaveLocally;
        this.readonly=options.readonly;
        this.deletable=options.deletable;
        this.disable_multiple_selection=options.disable_multiple_selection;
        varoBtnRemove='o_btn_remove';

        varmulti_select=!_.isNumber(options.res_id)&&!options.disable_multiple_selection;
        varreadonly=_.isNumber(options.res_id)&&options.readonly;

        if(!options.buttons){
            options.buttons=[{
                text:options.close_text||(readonly?_t("Close"):_t("Discard")),
                classes:"btn-secondaryo_form_button_cancel",
                close:true,
                click:function(){
                    if(!readonly){
                        self.form_view.model.discardChanges(self.form_view.handle,{
                            rollback:self.shouldSaveLocally,
                        });
                    }
                },
            }];

            if(!readonly){
                options.buttons.unshift({
                    text:options.save_text||(multi_select?_t("Save&Close"):_t("Save")),
                    classes:"btn-primary",
                    click:function(){
                        self._save().then(self.close.bind(self));
                    }
                });

                if(multi_select){
                    options.buttons.splice(1,0,{
                        text:_t("Save&New"),
                        classes:"btn-primary",
                        click:function(){
                            self._save()
                                .then(function(){
                                    //resetdefaultnamefieldfromcontextwhenSave&Newisclicked,passadditional
                                    //contextsothatwhengetContextiscalledadditionalcontextresetsit
                                    constadditionalContext=self._createContext&&self._createContext(false);
                                    self.form_view.createRecord(self.parentID,additionalContext);
                                })
                                .then(function(){
                                    if(!self.deletable){
                                        return;
                                    }
                                    self.deletable=false;
                                    self.buttons=self.buttons.filter(function(button){
                                        returnbutton.classes.split('').indexOf(oBtnRemove)<0;
                                    });
                                    self.set_buttons(self.buttons);
                                    self.set_title(_t("Create")+_.str.strRight(self.title,_t("Open:")));
                                });
                        },
                    });
                }

                varmulti=options.disable_multiple_selection;
                if(!multi&&this.deletable){
                    this._setRemoveButtonOption(options,oBtnRemove);
                }
            }
        }
        this._super(parent,options);
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Opentheformviewdialog. Itisnecessarilyasynchronous,butthis
     *methodreturnsimmediately.
     *
     *@returns{FormViewDialog}thisinstance
     */
    open:function(){
        varself=this;
        var_super=this._super.bind(this);
        varFormView=view_registry.get('form');
        varfields_view_def;
        if(this.options.fields_view){
            fields_view_def=Promise.resolve(this.options.fields_view);
        }else{
            fields_view_def=this.loadFieldView(this.res_model,this.context,this.options.view_id,'form');
        }

        fields_view_def.then(function(viewInfo){
            varrefinedContext=_.pick(self.context,function(value,key){
                returnkey.indexOf('_view_ref')===-1;
            });
            varformview=newFormView(viewInfo,{
                modelName:self.res_model,
                context:refinedContext,
                ids:self.res_id?[self.res_id]:[],
                currentId:self.res_id||undefined,
                index:0,
                mode:self.res_id&&self.options.readonly?'readonly':'edit',
                footerToButtons:true,
                default_buttons:false,
                withControlPanel:false,
                model:self.model,
                parentID:self.parentID,
                recordID:self.recordID,
                isFromFormViewDialog:true,
            });
            returnformview.getController(self);
        }).then(function(formView){
            self.form_view=formView;
            varfragment=document.createDocumentFragment();
            if(self.recordID&&self.shouldSaveLocally){
                self.model.save(self.recordID,{savePoint:true});
            }
            returnself.form_view.appendTo(fragment)
                .then(function(){
                    self.opened().then(function(){
                        var$buttons=$('<div>');
                        self.form_view.renderButtons($buttons);
                        if($buttons.children().length){
                            self.$footer.empty().append($buttons.contents());
                        }
                        dom.append(self.$el,fragment,{
                            callbacks:[{widget:self.form_view}],
                            in_DOM:true,
                        });
                        self.form_view.updateButtons();
                    });
                    return_super();
                });
        });

        returnthis;
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _focusOnClose:function(){
        varisFocusSet=false;
        this.trigger_up('form_dialog_discarded',{
            callback:function(isFocused){
                isFocusSet=isFocused;
            },
        });
        returnisFocusSet;
    },

    /**
     *@private
     */
    _remove:function(){
        returnPromise.resolve(this.on_remove());
    },

    /**
     *@private
     *@returns{Promise}
     */
    _save:function(){
        varself=this;
        returnthis.form_view.saveRecord(this.form_view.handle,{
            stayInEdit:true,
            reload:false,
            savePoint:this.shouldSaveLocally,
            viewType:'form',
        }).then(function(changedFields){
            //recordmighthavebeenchangedbythesave(e.g.ifthiswasanewrecord,ithasan
            //idnow),sodon'tre-usethecopyobtainedbeforethesave
            varrecord=self.form_view.model.get(self.form_view.handle);
            returnself.on_saved(record,!!changedFields.length);
        });
    },

    /**
     *Setthe"remove"buttonintotheoptions'buttonslist
     *
     *@private
     *@param{Object}optionsTheoptionsobjecttomodify
     *@param{string}btnClassesTheclassesfortheremovebutton
     */
    _setRemoveButtonOption(options,btnClasses){
        constself=this;
        options.buttons.push({
            text:_t("Remove"),
            classes:'btn-secondary'+btnClasses,
            click:function(){
                self._remove().then(self.close.bind(self));
            }
        });
    },
});

/**
 *Searchdialog(displaysalistofrecordsandpermitstocreateanewonebyswitchingtoaformview)
 */
varSelectCreateDialog=ViewDialog.extend({
    custom_events:_.extend({},ViewDialog.prototype.custom_events,{
        select_record:function(event){
            if(!this.options.readonly){
                this.on_selected([event.data]);
                this.close();
            }
        },
        selection_changed:function(event){
            event.stopPropagation();
            this.$footer.find(".o_select_button").prop('disabled',!event.data.selection.length);
        },
    }),

    /**
     *options:
     *-initial_ids
     *-initial_view:formorsearch(defaultsearch)
     *-list_view_options:dictofoptionstopasstotheListView
     *-on_selected:optionalcallbacktoexecutewhenrecordsareselected
     *-disable_multiple_selection:truetoallowcreate/selectmultiplerecords
     *-dynamicFilters:filterstoaddtothesearchview
     */
    init:function(){
        this._super.apply(this,arguments);
        _.defaults(this.options,{initial_view:'search'});
        this.on_selected=this.options.on_selected||(function(){});
        this.on_closed=this.options.on_closed||(function(){});
        this.initialIDs=this.options.initial_ids;
        this.viewType='list';
    },

    open:function(){
        if(this.options.initial_view!=="search"){
            returnthis.create_edit_record();
        }
        varself=this;
        var_super=this._super.bind(this);
        varviewRefID=this.viewType==='kanban'?
            (this.options.kanban_view_ref&&JSON.parse(this.options.kanban_view_ref)||false):false;
        returnthis.loadViews(this.res_model,this.context,[[viewRefID,this.viewType],[false,'search']],{load_filters:true})
            .then(this.setup.bind(this))
            .then(function(fragment){
                self.opened().then(function(){
                    dom.append(self.$el,fragment,{
                        callbacks:[{widget:self.viewController}],
                        in_DOM:true,
                    });
                    self.set_buttons(self.__buttons);
                });
                return_super();
            });
    },

    setup:function(fieldsViews){
        varself=this;
        varfragment=document.createDocumentFragment();

        vardomain=this.domain;
        if(this.initialIDs){
            domain=domain.concat([['id','in',this.initialIDs]]);
        }
        varViewClass=view_registry.get(this.viewType);
        varviewOptions={};
        varselectCreateController;
        if(this.viewType==='list'){//addlistviewspecificoptions
            _.extend(viewOptions,{
                hasSelectors:!this.options.disable_multiple_selection,
                readonly:true,

            },this.options.list_view_options);
            selectCreateController=select_create_controllers_registry.SelectCreateListController;
        }
        if(this.viewType==='kanban'){
            _.extend(viewOptions,{
                noDefaultGroupby:true,
                selectionMode:this.options.selectionMode||false,
            });
            selectCreateController=select_create_controllers_registry.SelectCreateKanbanController;
        }
        varview=newViewClass(fieldsViews[this.viewType],_.extend(viewOptions,{
            action:{
                controlPanelFieldsView:fieldsViews.search,
                help:_.str.sprintf("<p>%s</p>",_t("Norecordsfound!")),
            },
            action_buttons:false,
            dynamicFilters:this.options.dynamicFilters,
            context:this.context,
            domain:domain,
            modelName:this.res_model,
            withBreadcrumbs:false,
            withSearchPanel:false,
        }));
        view.setController(selectCreateController);
        returnview.getController(this).then(function(controller){
            self.viewController=controller;
            //renderthefooterbuttons
            self._prepareButtons();
            returnself.viewController.appendTo(fragment);
        }).then(function(){
            returnfragment;
        });
    },
    close:function(){
        this._super.apply(this,arguments);
        this.on_closed();
    },
    create_edit_record:function(){
        varself=this;
        vardialog=newFormViewDialog(this,_.extend({},this.options,{
            on_saved:function(record){
                varvalues=[{
                    id:record.res_id,
                    display_name:record.data.display_name||record.data.name,
                }];
                self.on_selected(values);
            },
        })).open();
        dialog.on('closed',this,this.close);
        returndialog;
    },
    /**
     *@override
     */
    _focusOnClose:function(){
        varisFocusSet=false;
        this.trigger_up('form_dialog_discarded',{
            callback:function(isFocused){
                isFocusSet=isFocused;
            },
        });
        returnisFocusSet;
    },
    /**
     *preparebuttonsfordialogfooterbasedonoptions
     *
     *@private
     */
    _prepareButtons:function(){
        this.__buttons=[{
            text:_t("Cancel"),
            classes:'btn-secondaryo_form_button_cancel',
            close:true,
        }];
        if(!this.options.no_create){
            this.__buttons.unshift({
                text:_t("Create"),
                classes:'btn-primary',
                click:this.create_edit_record.bind(this)
            });
        }
        if(!this.options.disable_multiple_selection){
            this.__buttons.unshift({
                text:_t("Select"),
                classes:'btn-primaryo_select_button',
                disabled:true,
                close:true,
                click:async()=>{
                    constvalues=awaitthis.viewController.getSelectedRecordsWithDomain();
                    this.on_selected(values);
                },
            });
        }
    },
});

return{
    FormViewDialog:FormViewDialog,
    SelectCreateDialog:SelectCreateDialog,
};

});
