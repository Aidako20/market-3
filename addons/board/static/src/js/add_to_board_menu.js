flectra.define('board.AddToBoardMenu',function(require){
    "usestrict";

    constContext=require('web.Context');
    constDomain=require('web.Domain');
    constDropdownMenuItem=require('web.DropdownMenuItem');
    constFavoriteMenu=require('web.FavoriteMenu');
    const{sprintf}=require('web.utils');
    const{useAutofocus}=require('web.custom_hooks');

    const{useState}=owl.hooks;

    /**
     *'Addtoboard'menu
     *
     *Componentconsisitingofatogglebutton,atextinputandan'Add'button.
     *Thefirstbuttonissimplyusedtotogglethecomponentandwilldetermine
     *whethertheotherelementsshouldberendered.
     *Theinputwillbegiventhename(ortitle)oftheviewthatwillbeadded.
     *Finally,thelastbuttonwillsendthenameaswellassomeoftheaction
     *propertiestotheservertoaddthecurrentview(anditscontext)tothe
     *user'sdashboard.
     *Thiscomponentisonlyavailableinactionsoftype'ir.actions.act_window'.
     *@extendsDropdownMenuItem
     */
    classAddToBoardMenuextendsDropdownMenuItem{
        constructor(){
            super(...arguments);

            this.interactive=true;
            this.state=useState({
                name:this.env.action.name||"",
                open:false,
            });

            useAutofocus();
        }

        //---------------------------------------------------------------------
        //Private
        //---------------------------------------------------------------------

        /**
         *Thisisthemainfunctionforactuallysavingthedashboard. Thismethod
         *issupposedtocalltheroute/board/add_to_dashboardwithproper
         *information.
         *@private
         */
        async_addToBoard(){
            constsearchQuery=this.env.searchModel.get('query');
            constcontext=newContext(this.env.action.context);
            context.add(searchQuery.context);
            context.add({
                group_by:searchQuery.groupBy,
                orderedBy:searchQuery.orderedBy,
            });
            if(searchQuery.timeRanges&&searchQuery.timeRanges.hasOwnProperty('fieldName')){
                context.add({
                    comparison:searchQuery.timeRanges,
                });
            }
            letcontrollerQueryParams;
            this.env.searchModel.trigger('get-controller-query-params',params=>{
                controllerQueryParams=params||{};
            });
            controllerQueryParams.context=controllerQueryParams.context||{};
            constqueryContext=controllerQueryParams.context;
            deletecontrollerQueryParams.context;
            context.add(Object.assign(controllerQueryParams,queryContext));

            constdomainArray=newDomain(this.env.action.domain||[]);
            constdomain=Domain.prototype.normalizeArray(domainArray.toArray().concat(searchQuery.domain));

            constevalutatedContext=context.eval();
            for(constkeyinevalutatedContext){
                if(evalutatedContext.hasOwnProperty(key)&&/^search_default_/.test(key)){
                    deleteevalutatedContext[key];
                }
            }
            evalutatedContext.dashboard_merge_domains_contexts=false;

            Object.assign(this.state,{
                name:$(".o_input").val()||"",
                open:false,
            });

            constresult=awaitthis.rpc({
                route:'/board/add_to_dashboard',
                params:{
                    action_id:this.env.action.id||false,
                    context_to_save:evalutatedContext,
                    domain:domain,
                    view_mode:this.env.view.type,
                    name:this.state.name,
                },
            });
            if(result){
                this.env.services.notification.notify({
                    title:sprintf(this.env._t("'%s'addedtodashboard"),this.state.name),
                    message:this.env._t("Pleaserefreshyourbrowserforthechangestotakeeffect."),
                    type:'warning',
                });
            }else{
                this.env.services.notification.notify({
                    message:this.env._t("Couldnotaddfiltertodashboard"),
                    type:'danger',
                });
            }
        }

        //---------------------------------------------------------------------
        //Handlers
        //---------------------------------------------------------------------

        /**
         *@private
         *@param{KeyboardEvent}ev
         */
        _onInputKeydown(ev){
            switch(ev.key){
                case'Enter':
                    ev.preventDefault();
                    this._addToBoard();
                    break;
                case'Escape':
                    //Givesthefocusbacktothecomponent.
                    ev.preventDefault();
                    ev.target.blur();
                    break;
            }
        }

        //---------------------------------------------------------------------
        //Static
        //---------------------------------------------------------------------

        /**
         *@param{Object}env
         *@returns{boolean}
         */
        staticshouldBeDisplayed(env){
            returnenv.action.type==='ir.actions.act_window';
        }
    }

    AddToBoardMenu.props={};
    AddToBoardMenu.template='AddToBoardMenu';

    FavoriteMenu.registry.add('add-to-board-menu',AddToBoardMenu,10);

    returnAddToBoardMenu;
});
