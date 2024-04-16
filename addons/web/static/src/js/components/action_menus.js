flectra.define('web.ActionMenus',function(require){
    "usestrict";

    constContext=require('web.Context');
    constDropdownMenu=require('web.DropdownMenu');
    constRegistry=require('web.Registry');

    const{Component}=owl;

    letregistryActionId=1;

    /**
     *Actionmenus(orAction/Printbar,previouslycalled'Sidebar')
     *
     *Thesidebaristhegroupofdropdownmenuslocatedontheleftsideofthe
     *controlpanel.Itsroleistodisplayalistofitemsdependingontheview
     *typeandselectedrecordsandtoexecuteasetofactionsonactiverecords.
     *Itismadeoutof2dropdownmenus:PrintandAction.
     *
     *ThiscomponentalsoprovidesaregistrytousecustomcomponentsintheActionMenus's
     *Actionmenu.
     *@extendsComponent
     */
    classActionMenusextendsComponent{

        asyncwillStart(){
            this.actionItems=awaitthis._setActionItems(this.props);
            this.printItems=awaitthis._setPrintItems(this.props);
        }

        asyncwillUpdateProps(nextProps){
            this.actionItems=awaitthis._setActionItems(nextProps);
            this.printItems=awaitthis._setPrintItems(nextProps);
        }

        mounted(){
            this._addTooltips();
        }

        patched(){
            this._addTooltips();
        }

        //---------------------------------------------------------------------
        //Private
        //---------------------------------------------------------------------

        /**
         *Addthetooltipstotheitems
         *@private
         */
        _addTooltips(){
            $(this.el.querySelectorAll('[title]')).tooltip({
                delay:{show:500,hide:0}
            });
        }

        /**
         *@private
         *@param{Object}props
         *@returns{Promise<Object[]>}
         */
        async_setActionItems(props){
            //Callbackbasedactions
            constcallbackActions=(props.items.other||[]).map(
                action=>Object.assign({key:`action-${action.description}`},action)
            );
            //Actionbasedactions
            constactionActions=props.items.action||[];
            constrelateActions=props.items.relate||[];
            constformattedActions=[...actionActions,...relateActions].map(
                action=>({action,description:action.name,key:action.id})
            );
            //ActionMenusactionregistrycomponents
            constregistryActions=[];
            constrpc=this.rpc.bind(this);
            for(const{Component,getProps}ofthis.constructor.registry.values()){
                constitemProps=awaitgetProps(props,this.env,rpc);
                if(itemProps){
                    registryActions.push({
                        Component,
                        key:`registry-action-${registryActionId++}`,
                        props:itemProps,
                    });
                }
            }

            return[...callbackActions,...formattedActions,...registryActions];
        }

        /**
         *@private
         *@param{Object}props
         *@returns{Promise<Object[]>}
         */
        async_setPrintItems(props){
            constprintActions=props.items.print||[];
            constprintItems=printActions.map(
                action=>({action,description:action.name,key:action.id})
            );
            returnprintItems;
        }

        //---------------------------------------------------------------------
        //Handlers
        //---------------------------------------------------------------------

        /**
         *Performtheactionfortheitemclickedaftergettingthedata
         *necessarywithatrigger.
         *@private
         *@param{OwlEvent}ev
         */
        async_executeAction(action){
            letactiveIds=this.props.activeIds;
            if(this.props.isDomainSelected){
                activeIds=awaitthis.rpc({
                    model:this.env.action.res_model,
                    method:'search',
                    args:[this.props.domain],
                    kwargs:{
                        limit:this.env.session.active_ids_limit,
                    },
                });
            }
            constactiveIdsContext={
                active_id:activeIds[0],
                active_ids:activeIds,
                active_model:this.env.action.res_model,
            };
            if(this.props.domain){
                //keepactive_domainincontextforbackwardcompatibility
                //reasons,andtoallowactionstobypasstheactive_ids_limit
                activeIdsContext.active_domain=this.props.domain;
            }

            constcontext=newContext(this.props.context,activeIdsContext).eval();
            constresult=awaitthis.rpc({
                route:'/web/action/load',
                params:{action_id:action.id,context},
            });
            result.context=newContext(result.context||{},activeIdsContext)
                .set_eval_context(context);
            result.flags=result.flags||{};
            result.flags.new_window=true;
            this.trigger('do-action',{
                action:result,
                options:{
                    on_close:()=>this.trigger('reload'),
                },
            });
        }

        /**
         *Handlerusedtodeterminewhichwaymustbeusedtoexecuteaselected
         *action:itwillbeeither:
         *-acallback(functiongivenbytheviewcontroller);
         *-anactionID(string);
         *-anURL(string).
         *@private
         *@param{OwlEvent}ev
         */
        _onItemSelected(ev){
            ev.stopPropagation();
            const{item}=ev.detail;
            if(item.callback){
                item.callback([item]);
            }elseif(item.action){
                this._executeAction(item.action);
            }elseif(item.url){
                //Eventhasbeenpreventedatitssource:weneedtoredirectmanually.
                this.env.services.navigate(item.url);
            }
        }
    }

    ActionMenus.registry=newRegistry();

    ActionMenus.components={DropdownMenu};
    ActionMenus.props={
        activeIds:{type:Array,element:[Number,String]},//virtualIDsarestrings.
        context:Object,
        domain:{type:Array,optional:1},
        isDomainSelected:{type:Boolean,optional:1},
        items:{
            type:Object,
            shape:{
                action:{type:Array,optional:1},
                print:{type:Array,optional:1},
                other:{type:Array,optional:1},
            },
        },
    };
    ActionMenus.template='web.ActionMenus';

    returnActionMenus;
});
