flectra.define('web.WebClient',function(require){
"usestrict";

varAbstractWebClient=require('web.AbstractWebClient');
varconfig=require('web.config');
varcore=require('web.core');
vardata_manager=require('web.data_manager');
vardom=require('web.dom');
varMenu=require('web.Menu');
varsession=require('web.session');

returnAbstractWebClient.extend({
    custom_events:_.extend({},AbstractWebClient.prototype.custom_events,{
        app_clicked:'on_app_clicked',
        menu_clicked:'on_menu_clicked',
    }),
    start:function(){
        core.bus.on('change_menu_section',this,function(menuID){
            this.do_push_state(_.extend($.bbq.getState(),{
                menu_id:menuID,
            }));
        });

        returnthis._super.apply(this,arguments);
    },
    bind_events:function(){
        varself=this;
        this._super.apply(this,arguments);

        /*
            Smallpatchtoallowhavingalinkwithahreftowardsananchor.Sinceflectrausehashtag
            torepresentthecurrentstateoftheview,wecan'teasilydistinguishbetweenalink
            towardsananchorandalinktowardsanoterview/state.Ifwewanttonavigatetowardsan
            anchor,wemustnotchangethehashoftheurlotherwisewewillberedirectedtotheapp
            switcherinstead.
            Tocheckifwehaveananchor,firstcheckifwehaveanhrefattributesstartingwith#.
            TrytofindaelementintheDOMusingJQueryselector.
            Ifwehaveamatch,itmeansthatitisprobablyalinktoananchor,sowejumptothatanchor.
        */
        this.$el.on('click','a',function(ev){
            vardisable_anchor=ev.target.attributes.disable_anchor;
            if(disable_anchor&&disable_anchor.value==="true"){
                return;
            }

            varhref=ev.target.attributes.href;
            if(href){
                if(href.value[0]==='#'&&href.value.length>1){
                    if(self.$("[id='"+href.value.substr(1)+"']").length){
                        ev.preventDefault();
                        self.trigger_up('scrollTo',{'selector':href.value});
                    }
                }
            }
        });
    },
    load_menus:function(){
        return(flectra.loadMenusPromise||flectra.reloadMenus())
            .then(function(menuData){
                //Computeaction_idifnotdefinedonatopmenuitem
                for(vari=0;i<menuData.children.length;i++){
                    varchild=menuData.children[i];
                    if(child.action===false){
                        while(child.children&&child.children.length){
                            child=child.children[0];
                            if(child.action){
                                menuData.children[i].action=child.action;
                                break;
                            }
                        }
                    }
                }
                flectra.loadMenusPromise=null;
                returnmenuData;
            });
    },
    asyncshow_application(){
        this.set_title();

        awaitthis.menu_dp.add(this.instanciate_menu_widgets());
        $(window).bind('hashchange',this.on_hashchange);

        conststate=$.bbq.getState(true);
        if(!_.isEqual(_.keys(state),["cids"])){
            returnthis.on_hashchange();
        }

        const[data]=awaitthis.menu_dp.add(this._rpc({
            model:'res.users',
            method:'read',
            args:[session.uid,["action_id"]],
        }));
        if(data.action_id){
            awaitthis.do_action(data.action_id[0]);
            this.menu.change_menu_section(this.menu.action_id_to_primary_menu_id(data.action_id[0]));
            return;
        }

        if(!this.menu.openFirstApp()){
            this.trigger_up('webclient_started');
        }
    },

    instanciate_menu_widgets:function(){
        varself=this;
        varproms=[];
        returnthis.load_menus().then(function(menuData){
            self.menu_data=menuData;

            //Here,weinstanciateeverymenuwidgetsandweimmediatelyappendthemintodummy
            //documentfragments,sothattheir`start`methodareexecutedbeforeinsertingthem
            //intotheDOM.
            if(self.menu){
                self.menu.destroy();
            }
            self.menu=newMenu(self,menuData);
            proms.push(self.menu.prependTo(self.$el));
            returnPromise.all(proms);
        });
    },

    //--------------------------------------------------------------
    //URLstatehandling
    //--------------------------------------------------------------
    on_hashchange:function(event){
        if(this._ignore_hashchange){
            this._ignore_hashchange=false;
            returnPromise.resolve();
        }

        varself=this;
        returnthis.clear_uncommitted_changes().then(function(){
            varstringstate=$.bbq.getState(false);
            if(!_.isEqual(self._current_state,stringstate)){
                varstate=$.bbq.getState(true);
                if(state.action||(state.model&&(state.view_type||state.id))){
                    returnself.menu_dp.add(self.action_manager.loadState(state,!!self._current_state)).then(function(){
                        if(state.menu_id){
                            if(state.menu_id!==self.menu.current_primary_menu){
                                core.bus.trigger('change_menu_section',state.menu_id);
                            }
                        }else{
                            varaction=self.action_manager.getCurrentAction();
                            if(action){
                                varmenu_id=self.menu.action_id_to_primary_menu_id(action.id);
                                core.bus.trigger('change_menu_section',menu_id);
                            }
                        }
                    });
                }elseif(state.menu_id){
                    varaction_id=self.menu.menu_id_to_action_id(state.menu_id);
                    returnself.menu_dp.add(self.do_action(action_id,{clear_breadcrumbs:true})).then(function(){
                        core.bus.trigger('change_menu_section',state.menu_id);
                    });
                }else{
                    self.menu.openFirstApp();
                }
            }
            self._current_state=stringstate;
        },function(){
            if(event){
                self._ignore_hashchange=true;
                window.location=event.originalEvent.oldURL;
            }
        });
    },

    //--------------------------------------------------------------
    //Menuhandling
    //--------------------------------------------------------------
    on_app_clicked:function(ev){
        varself=this;
        returnthis.menu_dp.add(data_manager.load_action(ev.data.action_id))
            .then(function(result){
                returnself.action_mutex.exec(function(){
                    varcompleted=newPromise(function(resolve,reject){
                        varoptions=_.extend({},ev.data.options,{
                            clear_breadcrumbs:true,
                            action_menu_id:ev.data.menu_id,
                        });

                        Promise.resolve(self._openMenu(result,options))
                               .then(function(){
                                    self._on_app_clicked_done(ev)
                                        .then(resolve)
                                        .guardedCatch(reject);
                               }).guardedCatch(function(){
                                    resolve();
                               });
                        setTimeout(function(){
                                resolve();
                            },2000);
                    });
                    returncompleted;
                });
            });
    },
    _on_app_clicked_done:function(ev){
        core.bus.trigger('change_menu_section',ev.data.menu_id);
        returnPromise.resolve();
    },
    on_menu_clicked:function(ev){
        varself=this;
        returnthis.menu_dp.add(data_manager.load_action(ev.data.action_id))
            .then(function(result){
                self.$el.removeClass('o_mobile_menu_opened');

                returnself.action_mutex.exec(function(){
                    varcompleted=newPromise(function(resolve,reject){
                        Promise.resolve(self._openMenu(result,{
                            clear_breadcrumbs:true,
                        })).then(resolve).guardedCatch(reject);

                        setTimeout(function(){
                            resolve();
                        },2000);
                    });
                    returncompleted;
                });
            }).guardedCatch(function(){
                self.$el.removeClass('o_mobile_menu_opened');
            });
    },
    /**
     *Opentheactionlinkedtoamenu.
     *Thisfunctionismostlyusedtoallowoverrideinothermodules.
     *
     *@private
     *@param{Object}action
     *@param{Object}options
     *@returns{Promise}
     */
    _openMenu:function(action,options){
        returnthis.do_action(action,options);
    },
});

});
