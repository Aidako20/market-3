flectra.define('web.ActionMixin',function(require){
    "usestrict";

    /**
     *WedefineheretheActionMixin,thegenericnotionofaction(fromthepoint
     *ofviewofthewebclient). Inshort,anactionisawidgetwhichcontrols
     *themainpartofthescreen(everythingbelowthenavbar).
     *
     *Moreprecisely,theactionmanageristhecomponentthatcoordinatesastack
     *ofactions. Whenevertheusernavigatesintheinterface,switchesviews,
     *opendifferentmenus,theactionmanagercreates/updates/destroysspecial
     *widgetswhichimplementstheActionMixin. Theseactionsneedtoanswertoa
     *standardisedAPI,whichisthereasonforthismixin.
     *
     *Inpractice,mostactionsareviewcontrollers(comingfroman
     *ir.action.act_window). However,someactionsare'clientactions'. They
     *alsoneedtoimplementtheActionMixinforabettercooperationwiththe
     *actionmanager.
     *
     *@moduleweb.ActionMixin
     *@extendsWidgetAdapterMixin
     */

    constcore=require('web.core');
    const{WidgetAdapterMixin}=require('web.OwlCompatibility');

    constActionMixin=Object.assign({},WidgetAdapterMixin,{
        template:'Action',

        /**
         *Theactionmixinassumesthatitisrenderedwiththe'Action'template.
         *Thistemplatehasaspecialzone('.o_content')wherethecontentshould
         *beadded. Actionsthatwanttoautomaticallyrenderatemplatethere
         *shoulddefinethecontentTemplatekey. Inshort,clientactionsshould
         *probablydefineacontentTemplatekey,andnotatemplatekey.
         */
        contentTemplate:null,

        /**
         *EventsbuiltbyandmanagedbyFlectraFramework
         *
         *ItisexpectedthatanyWidgetClassimplementingthismixin
         *willalsoimplementtheParentedMixinwhichactuallymanagesthose
         */
        custom_events:{
            get_controller_query_params:'_onGetOwnedQueryParams',
        },

        /**
         *Ifanactionwantstouseacontrolpanel,itwillbecreatedand
         *registeredinthis_controlPanelkey(thewidget). Thewaythiscontrol
         *paneliscreatedisuptotheimplementation(so,viewcontrollersor
         *clientactionsmayhavedifferentneeds).
         *
         *Notethatmostofthetime,thiskeyshouldbesetbytheframework,not
         *bythecodeoftheclientaction.
         */
        _controlPanel:null,

        /**
         *Stringcontainingthetitleoftheclientaction(whichmaybeneededto
         *displayinthebreadcrumbszoneofthecontrolpanel).
         *
         *@see_setTitle
         */
        _title:'',

        /**
         *@override
         */
        renderElement:function(){
            this._super.apply(this,arguments);
            if(this.contentTemplate){
                constcontent=core.qweb.render(this.contentTemplate,{widget:this});
                this.$('.o_content').append(content);
            }
        },

        /**
         *Calledbytheactionmanagerwhenactionisrestored(typically,when
         *theuserclicksontheactioninthebreadcrumb)
         *
         *@returns{Promise|undefined}
         */
        willRestore:function(){},

        //---------------------------------------------------------------------
        //Public
        //---------------------------------------------------------------------

        /**
         *Insomesituations,weneedconfirmationfromthecontrollerthatthe
         *currentstatecanbedestroyedwithoutprejudicetotheuser. For
         *example,iftheuserhaseditedaform,maybeweshouldaskhimifwe
         *candiscardallhischangeswhenweswitchtoanotheraction. Inthat
         *case,theactionmanagerwillcallthismethod. Ifthereturned
         *promiseissuccessfullyresolved,thenwecandestroythecurrentaction,
         *otherwise,weneedtostop.
         *
         *@returns{Promise}resolvediftheactioncanberemoved,rejected
         *  otherwise
         */
        canBeRemoved:function(){
            returnPromise.resolve();
        },

        /**
         *Thisfunctioniscalledwhenthecurrentstateoftheaction
         *shouldbeknown.Forinstance,iftheactionisaviewcontroller,
         *thismaybeusefultoreinstantiateaviewinthesamestate.
         *
         *Typicallythestatecan(andshould)beencodedinaqueryobjectof
         *theform::
         *
         *    {
         *         context:{...},
         *         groupBy:[...],
         *         domain=[...],
         *         orderedBy=[...],
         *    }
         *
         *wherethecontextkeycancontainmanyinformation.
         *Thismethodismainlycalledduringthecreationofacustomfilter.
         *
         *@returns{Object}
         */
        getOwnedQueryParams:function(){
            return{};
        },

        /**
         *ReturnsaserializablestatethatwillbepushedintheURLby
         *theactionmanager,allowingtheactiontoberestartedcorrectly
         *uponrefresh.Thisfunctionshouldbeoverridentoaddextrainformation.
         *Notethatsomekeysarereservedbytheframeworkandwillthusbe
         *ignored('action','active_id','active_ids'and'title',forall
         *actions,and'model'and'view_type'foract_windowactions).
         *
         *@returns{Object}
         */
        getState:function(){
            return{};
        },

        /**
         *Returnsatitlethatmaybedisplayedinthebreadcrumbarea. For
         *example,thenameoftherecord(foraformview).Thisisactually
         *importantfortheactionmanager:thisisthewayitisabletogive
         *thepropertitlesforotheractions.
         *
         *@returns{string}
         */
        getTitle:function(){
            returnthis._title;
        },

        /**
         *Rendersthebuttonstoappend,inmostcases,tothecontrolpanel(in
         *thebottomleftcorner).Whentheactionisrenderedinadialog,those
         *buttonsmightbemovedtothedialog'sfooter.
         *
         *@param{jQueryNode}$node
         */
        renderButtons:function($node){},

        /**
         *Methodusedtoupdatethewidgetbuttonsstate.
         */
        updateButtons:function(){},

        /**
         *TheparameternewPropsisusedtoupdatethepropsof
         *thecontrolPanelWrapperbeforerenderit.Thekey'cp_content'
         *isnotapropofthecontrolpanelitself.Oneshouldifpossibleuse
         *theslotmechanism.
         *
         *@param{Object}[newProps={}]
         *@returns{Promise}
         */
        updateControlPanel:asyncfunction(newProps={}){
            if(!this.withControlPanel&&!this.hasControlPanel){
                return;
            }
            constprops=Object.assign({},newProps);//Workwithacleannewobject
            if('title'inprops){
                this._setTitle(props.title);
                this.controlPanelProps.title=this.getTitle();
                deleteprops.title;
            }
            if('cp_content'inprops){
                //cp_contenthasbeenupdated:refreshit.
                this.controlPanelProps.cp_content=Object.assign({},
                    this.controlPanelProps.cp_content,
                    props.cp_content,
                );
                deleteprops.cp_content;
            }
            //Updatepropsstate
            Object.assign(this.controlPanelProps,props);
            returnthis._controlPanelWrapper.update(this.controlPanelProps);
        },

        //---------------------------------------------------------------------
        //Private
        //---------------------------------------------------------------------

        /**
         *@private
         *@param{string}title
         */
        _setTitle:function(title){
            this._title=title;
        },

        //---------------------------------------------------------------------
        //Handlers
        //---------------------------------------------------------------------

        /**
         *FIXME:thislogicshouldberethought
         *
         *Handlesacontextrequest:providestothecallerthestateofthe
         *currentcontroller.
         *
         *@private
         *@param{function}callbackusedtosendtherequestedstate
         */
        _onGetOwnedQueryParams:function(callback){
            conststate=this.getOwnedQueryParams();
            callback(state||{});
        },
    });

    returnActionMixin;
});
