flectra.define('web.AbstractField',function(require){
"usestrict";

/**
 *Thisisthebasicfieldwidgetusedbyalltheviewstorenderafieldinaview.
 *Thesefieldwidgetsaremostlycommontoallviews,inparticularformandlist
 *views.
 *
 *Theresponsabilitiesofafieldwidgetaremainly:
 *-renderavisualrepresentationofthecurrentvalueofafield
 *-thatrepresentationiseitherin'readonly'orin'edit'mode
 *-notifytherestofthesystemwhenthefieldhasbeenchangedby
 *  theuser(ineditmode)
 *
 *Notes
 *-thewidgetisnotsupposedtobeabletoswitchbetweenmodes. Ifanother
 *  modeisrequired,theviewwilltakecareofinstantiatinganotherwidget.
 *-notifythesystemwhenitsvaluehaschangedanditsmodeischangedto'readonly'
 *-notifythesystemwhensomeactionhastobetaken,suchasopeningarecord
 *-theFieldwidgetshouldnot,ever,underanycircumstance,beawareof
 *  itsparent. Thewayitcommunicateschangeswiththerestofthesystemisby
 *  triggeringevents(withtrigger_up). Theseeventsbubbleupandareinterpreted
 *  bythemostappropriateparent.
 *
 *Also,insomecases,itmaynotbepracticaltohavethesamewidgetforall
 *views.Inthatsituation,youcanhavea'viewspecificwidget'. Justregister
 *thewidgetintheregistryprefixedbytheviewtypeandadot. So,forexample,
 *aformspecificmany2onewidgetshouldberegisteredas'form.many2one'.
 *
 *@moduleweb.AbstractField
 */

varfield_utils=require('web.field_utils');
varWidget=require('web.Widget');

varAbstractField=Widget.extend({
    events:{
        'keydown':'_onKeydown',
    },
    custom_events:{
        navigation_move:'_onNavigationMove',
    },

    /**
    *Anobjectrepresentingfieldstobefetchedbythemodeleventhoughnotpresentintheview
    *Thisobjectcontains"fieldname"askeyandanobjectasvalue.
    *Thatvalueobjectmustcontainthekey"type"
    *seeFieldBinaryImageforanexample.
    */
    fieldDependencies:{},

    /**
     *Ifthisflagissettotrue,thefieldwidgetwillberesetonevery
     *changewhichismadeintheview(iftheviewsupportsit).Thisis
     *currentlyaformviewfeature.
     */
    resetOnAnyFieldChange:false,
    /**
     *Ifthisflagisgivenastring,therelatedBasicModelwillbeusedto
     *initializespecialDatathefieldmightneed.Thisdatawillbeavailable
     *throughthis.record.specialData[this.name].
     *
     *@seeBasicModel._fetchSpecialData
     */
    specialData:false,
    /**
     *tooverridetoindicatewhichfieldtypesaresupportedbythewidget
     *
     *@typeArray<String>
     */
    supportedFieldTypes:[],

    /**
     *Tooverridetogiveauserfriendlynametothewidget.
     *
     *@type<string>
     */
    description:"",
    /**
     *Currentlyonlyusedinlistview.
     *Ifthisflagissettotrue,thelistcolumnnamewillbeempty.
     */
    noLabel:false,
    /**
     *Currentlyonlyusedinlistview.
     *Ifset,thisvaluewillbedisplayedascolumnname.
     */
    label:'',
    /**
     *Abstractfieldclass
     *
     *@constructor
     *@param{Widget}parent
     *@param{string}nameThefieldnamedefinedinthemodel
     *@param{Object}recordArecordobject(resultofthegetmethodof
     *  abasicmodel)
     *@param{Object}[options]
     *@param{string}[options.mode=readonly]shouldbe'readonly'or'edit'
     */
    init:function(parent,name,record,options){
        this._super(parent);
        options=options||{};

        //'name'isthefieldnamedisplayedbythiswidget
        this.name=name;

        //thedatapointfetchedfromthemodel
        this.record=record;

        //the'field'propertyisadescriptionofallthevariousfieldproperties,
        //suchasthetype,thecomodel(relation),...
        this.field=record.fields[name];

        //the'viewType'isthetypeoftheviewinwhichthefieldwidgetis
        //instantiated.Forstandalonewidgets,a'default'viewTypeisset.
        this.viewType=options.viewType||'default';

        //the'attrs'propertycontainstheattributesofthexml'field'tag,
        //theinnerviews...
        varfieldsInfo=record.fieldsInfo[this.viewType];
        this.attrs=options.attrs||(fieldsInfo&&fieldsInfo[name])||{};

        //the'additionalContext'propertycontainstheattributestopassthroughthecontext.
        this.additionalContext=options.additionalContext||{};

        //thispropertytracksthecurrent(parsedifneeded)valueofthefield.
        //Notethatwedon'tuseaneventsystemanymore,usingthis.get('value')
        //isnolongervalid.
        this.value=record.data[name];

        //recordDatatracksthevaluesfortheotherfieldsforthesamerecord.
        //notethatitisexpectedtobemostlyareadonlyproperty,youcannot
        //usethistotrytochangeotherfieldsvalue,thisisnothowitis
        //supposedtowork.Also,donotusethis.recordData[this.name]toget
        //thecurrentvalue,thiscouldbeoutofsyncaftera_setValue.
        this.recordData=record.data;

        //the'string'propertyisahumanreadable(andtranslated)description
        //ofthefield.Mostlyusefultobedisplayedinvariousplacesinthe
        //UI,suchastooltipsorcreatedialogs.
        this.string=this.attrs.string||this.field.string||this.name;

        //Widgetcanoftenbeconfiguredinthe'options'attributeinthe
        //xml'field'tag. Theseoptionsaresaved(andevaled)innodeOptions
        this.nodeOptions=this.attrs.options||{};

        //dataPointIDistheidcorrespondingtothecurrentrecordinthemodel.
        //Itsintendeduseistobeabletotaganymessagesgoingupstream,
        //sotheviewknowswhichrecordswaschangedforexample.
        this.dataPointID=record.id;

        //thisistheres_idfortherecordindatabase. Obviously,itis
        //readonly. Also,whentheuseriscreatinganewrecord,thereis
        //nores_id. Whentherecordwillbecreated,thefieldwidgetwill
        //bedestroyed(whentheformviewswitchestoreadonlymode)andanew
        //widgetwithares_idinmodereadonlywillbecreated.
        this.res_id=record.res_id;

        //usefulmostlytotriggerrpcsonthecorrectmodel
        this.model=record.model;

        //awidgetcanbeintwomodes:'edit'or'readonly'. Thismodeshould
        //neverbechanged,ifaviewchangesitsmode,itwilldestroyand
        //recreateanewfieldwidget.
        this.mode=options.mode||"readonly";

        //thisflagtracksifthewidgetisinavalidstate,meaningthatthe
        //currentvaluerepresentedintheDOMisavaluethatcanbeparsed
        //andsaved. Forexample,afloatfieldcanonlyuseanumberandnot
        //astring.
        this._isValid=true;

        //thisisthelastvaluethatwassetbytheuser,unparsed. Thisis
        //usedtoavoidsettingthevaluetwiceinarowwiththeexactvalue.
        this.lastSetValue=undefined;

        //formatTypeisusedtodeterminewhichformat(andparse)functions
        //tocalltoformatthefield'svaluetoinsertintotheDOM(typically
        //putintoaspanoraninput),andtoparsethevaluefromtheinput
        //tosendittotheserver.Thesefunctionsarechosenaccordingto
        //the'widget'attrsifisisgiven,andifitisavalidkey,witha
        //fallbackonthefieldtype,ensuringthatthevalueisformattedand
        //displayedaccordingtothechosenwidget,ifany.
        this.formatType=this.attrs.widgetinfield_utils.format?
                            this.attrs.widget:
                            this.field.type;
        //formatOptions(resp.parseOptions)isadictofoptionspassedto
        //callstotheformat(resp.parse)function.
        this.formatOptions={};
        this.parseOptions={};

        //ifweadddecorations,weneedtoreevaluatethefieldwheneverany
        //valuefromtherecordischanged
        if(this.attrs.decorations){
            this.resetOnAnyFieldChange=true;
        }
    },
    /**
     *WhenafieldwidgetisappendedtotheDOM,itsstartmethodiscalled,
     *andwillautomaticallycallrender.Mostwidgetsshouldnotoverridethis.
     *
     *@returns{Promise}
     */
    start:function(){
        varself=this;
        returnthis._super.apply(this,arguments).then(function(){
            self.$el.attr('name',self.name);
            self.$el.addClass('o_field_widget');
            returnself._render();
        });
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Activatesthefieldwidget.Bydefault,activationmeansfocusingand
     *selecting(ifpossible)theassociatedfocusableelement.Theselecting
     *partcanbedisabled. Inthatcase,notethatthefocusedinput/textarea
     *willhavethecursorattheveryend.
     *
     *@param{Object}[options]
     *@param{boolean}[options.noselect=false]iffalseandtheinput
     *  isoftypetextortextarea,thecontentwillalsobeselected
     *@param{Event}[options.event]theeventwhichfiredthisactivation
     *@returns{boolean}trueifthewidgetwasactivated,falseifthe
     *                   focusableelementwasnotfoundorinvisible
     */
    activate:function(options){
        if(this.isFocusable()){
            var$focusable=this.getFocusableElement();
            $focusable.focus();
            if($focusable.is('input[type="text"],textarea')){
                $focusable[0].selectionStart=$focusable[0].selectionEnd=$focusable[0].value.length;
                if(options&&!options.noselect){
                    $focusable.select();
                }
            }
            returntrue;
        }
        returnfalse;
    },
    /**
     *Thisfunctionshouldbeimplementedbywidgetsthatarenotableto
     *notifytheirenvironmentwhentheirvaluechanges(maybebecausetheir
     *arenotawareofthechanges)orthatmayhaveavalueinatemporary
     *state(maybebecausesomeactionshouldbeperformedtovalidateit
     *beforenotifyingit).Thisistypicallycalledbeforetryingtosavethe
     *widget'svalue,soitshouldcall_setValue()tonotifytheenvironment
     *ifthevaluechangedbutwasnotnotified.
     *
     *@abstract
     *@returns{Promise|undefined}
     */
    commitChanges:function(){},
    /**
     *Returnsthemainfield'sDOMelement(jQueryform)whichcanbefocused
     *bythebrowser.
     *
     *@returns{jQuery}mainfocusableelementinsidethewidget
     */
    getFocusableElement:function(){
        return$();
    },
    /**
     *Returnswhetherornotthefieldisemptyandcanthusbehidden.This
     *methodistypicallycalledwhenthewidgetisinreadonly,tohideit
     *(anditslabel)ifitisempty.
     *
     *@returns{boolean}
     */
    isEmpty:function(){
        return!this.isSet();
    },
    /**
     *Returnstrueiffthewidgethasavisibleelementthatcantakethefocus
     *
     *@returns{boolean}
     */
    isFocusable:function(){
        var$focusable=this.getFocusableElement();
        return$focusable.length&&$focusable.is(':visible');
    },
    /**
     *thismethodisusedtodetermineifthefieldvalueissettoameaningful
     *value. Thisisusefultodetermineifafieldshouldbedisplayedasempty
     *
     *@returns{boolean}
     */
    isSet:function(){
        return!!this.value;
    },
    /**
     *Afieldwidgetisvalidifitwascheckedasvalidthelasttimeits
     *valuewaschangedbytheuser.Thisischeckedbeforesavingarecord,by
     *theview.
     *
     *Note:thisistheresponsibilityoftheviewtocheckthatrequired
     *fieldshaveasetvalue.
     *
     *@returns{boolean}true/falseifthewidgetisvalid
     */
    isValid:function(){
        returnthis._isValid;
    },
    /**
     *thismethodissupposedtobecalledfromtheoutsideoffieldwidgets.
     *Thetypicalusecaseiswhenanonchangehaschangedthewidgetvalue.
     *Itwillresetthewidgettothevaluesthatcouldhavechanged,thenwill
     *rerenderthewidget.
     *
     *@param{any}record
     *@param{FlectraEvent}[event]aneventthattriggeredtheresetaction.It
     *  isoptional,andmaybeusedbyawidgettoshareinformationfromthe
     *  momentafieldchangeeventistriggeredtothemomentareset
     *  operationisapplied.
     *@returns{Promise}Apromise,whichresolveswhenthewidgetrendering
     *  iscomplete
     */
    reset:function(record,event){
        this._reset(record,event);
        returnthis._render()||Promise.resolve();
    },
    /**
     *Removetheinvalidclassonafield
     */
    removeInvalidClass:function(){
        this.$el.removeClass('o_field_invalid');
        this.$el.removeAttr('aria-invalid');
    },
    /**
     *Setsthegivenidonthefocusableelementofthefieldandas'for'
     *attributeofpotentialinternallabels.
     *
     *@param{string}id
     */
    setIDForLabel:function(id){
        this.getFocusableElement().attr('id',id);
    },
    /**
     *addtheinvalidclassonafield
     */
    setInvalidClass:function(){
        this.$el.addClass('o_field_invalid');
        this.$el.attr('aria-invalid','true');
    },
    /**
     *Updatethemodifierswiththenewestvalue.
     *Nowthis.attrs.modifiersValuecanbeusedconsistantlyevenwith
     *conditionalmodifiersinsidefieldwidgets,andwithoutneedingnew
     *eventsorsynchronizationbetweenthewidgets,rendererandcontroller
     *
     *@param{Object|null}modifiers theupdatedmodifiers
     *@override
     */
    updateModifiersValue:function(modifiers){
        this.attrs.modifiersValue=modifiers||{};
    },


    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Applyfielddecorations(onlyiffield-specificdecorationshavebeen
     *definedinanattribute).
     *
     *@private
     */
    _applyDecorations:function(){
        varself=this;
        this.attrs.decorations.forEach(function(dec){
            varisToggled=py.PY_isTrue(
                py.evaluate(dec.expression,self.record.evalContext)
            );
            constclassName=self._getClassFromDecoration(dec.name);
            self.$el.toggleClass(className,isToggled);
        });
    },
    /**
     *Convertsthevaluefromthefieldtoastringrepresentation.
     *
     *@private
     *@param{any}value(fromthefieldtype)
     *@param{string}[formatType=this.formatType]theformattertouse
     *@returns{string}
     */
    _formatValue:function(value,formatType){
        formatType=formatType||this.formatType;
        if(!formatType){
            thrownewError(`Missingformattypefor'${this.name}'valuefromthe'${this.model}'model`);
        }
        varoptions=_.extend({},this.nodeOptions,{data:this.recordData},this.formatOptions);
        returnfield_utils.format[formatType](value,this.field,options);
    },
    /**
     *ReturnstheclassNamecorrespondingtoagivendecoration.A
     *decorationisoftheform'decoration-%s'.Bydefault,replaces
     *'decoration'by'text'.
     *
     *@private
     *@param{string}decorationmustbeoftheform'decoration-%s'
     *@returns{string}
     */
    _getClassFromDecoration:function(decoration){
        return`text-${decoration.split('-')[1]}`;
    },
    /**
     *Comparesthegivenvaluewiththelastvaluethathasbeenset.
     *Notethatwecompareunparsedvalues.Handlesthespecialcasewhereno
     *valuehasbeensetyet,andthegivenvalueistheemptystring.
     *
     *@private
     *@param{any}value
     *@returns{boolean}trueiffvaluesarethesame
     */
    _isLastSetValue:function(value){
        returnthis.lastSetValue===value||(this.value===false&&value==='');
    },
    /**
     *Thismethodcheckifavalueisthesameasthecurrentvalueofthe
     *field. Forexample,afieldDatewidgetmightwanttousethemoment
     *specificvalueisSameinsteadof===.
     *
     *Thismethodisusedbythe_setValuemethod.
     *
     *@private
     *@param{any}value
     *@returns{boolean}
     */
    _isSameValue:function(value){
        returnthis.value===value;
    },
    /**
     *Convertsastringrepresentationtoavalidvalue.
     *
     *@private
     *@param{string}value
     *@returns{any}
     */
    _parseValue:function(value){
        returnfield_utils.parse[this.formatType](value,this.field,this.parseOptions);
    },
    /**
     *mainrenderingfunction. Overridethisifyourwidgethasthesamerender
     *foreachmode. Notethatthisfunctionissupposedtobeidempotent:
     *theresultofcalling'render'twiceisthesameascallingitonce.
     *Also,theuserexperiencewillbebetterifyourrenderingfunctionis
     *synchronous.
     *
     *@private
     *@returns{Promise|undefined}
     */
    _render:function(){
        if(this.attrs.decorations){
            this._applyDecorations();
        }
        if(this.mode==='edit'){
            returnthis._renderEdit();
        }elseif(this.mode==='readonly'){
            returnthis._renderReadonly();
        }
    },
    /**
     *Renderthewidgetineditmode. Theactualimplementationislefttothe
     *concretewidget.
     *
     *@private
     *@returns{Promise|undefined}
     */
    _renderEdit:function(){
    },
    /**
     *Renderthewidgetinreadonlymode. Theactualimplementationisleftto
     *theconcretewidget.
     *
     *@private
     *@returns{Promise|undefined}
     */
    _renderReadonly:function(){
    },
    /**
     *pureversionofreset,canbeoverridden,calledbeforerender()
     *
     *@private
     *@param{any}record
     *@param{FlectraEvent}eventtheeventthattriggeredthechange
     */
    _reset:function(record,event){
        this.lastSetValue=undefined;
        this.record=record;
        this.value=record.data[this.name];
        this.recordData=record.data;
    },
    /**
     *thismethodiscalledbythewidget,tochangeitsvalueandtonotify
     *theoutsideworldofitsnewstate. Thismethodalsovalidatesthenew
     *value. Notethatthismethoddoesnotrerenderthewidget,itshouldbe
     *handledbythewidgetitself,ifnecessary.
     *
     *@private
     *@param{any}value
     *@param{Object}[options]
     *@param{boolean}[options.doNotSetDirty=false]iftrue,thebasicmodel
     *  willnotconsiderthatthisfieldisdirty,eventhoughitwaschanged.
     *  Pleasedonotusethisflagunlessyoureallyneedit. Ouronlyuse
     *  caseiscurrentlythepadwidget,whichdoesa_setValueinthe
     *  renderEditmethod.
     *@param{boolean}[options.notifyChange=true]iffalse,thebasicmodel
     *  willnotnotifyandnottriggertheonchange,eventhoughitwaschanged.
     *@param{boolean}[options.forceChange=false]iftrue,thechangeeventwillbe
     *  triggeredevenifthenewvalueisthesameastheoldone
     *@returns{Promise}
     */
    _setValue:function(value,options){
        //wetrytoavoiddoinguselesswork,ifthevaluegivenhasnotchanged.
        if(this._isLastSetValue(value)){
            returnPromise.resolve();
        }
        this.lastSetValue=value;
        try{
            value=this._parseValue(value);
            this._isValid=true;
        }catch(e){
            this._isValid=false;
            this.trigger_up('set_dirty',{dataPointID:this.dataPointID});
            returnPromise.reject({message:"Valuesetisnotvalid"});
        }
        if(!(options&&options.forceChange)&&this._isSameValue(value)){
            returnPromise.resolve();
        }
        varself=this;
        returnnewPromise(function(resolve,reject){
            varchanges={};
            changes[self.name]=value;
            self.trigger_up('field_changed',{
                dataPointID:self.dataPointID,
                changes:changes,
                viewType:self.viewType,
                doNotSetDirty:options&&options.doNotSetDirty,
                notifyChange:!options||options.notifyChange!==false,
                allowWarning:options&&options.allowWarning,
                onSuccess:resolve,
                onFailure:reject,
            });
        });
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Interceptsnavigationkeyboardeventstopreventtheirdefaultbehavior
     *andnotifiestheviewsothatitcanhandleititsownway.
     *
     *Note:thenavigationkeyboardeventsarestoppedsothatpotentialparent
     *abstractfielddoesnottriggerthenavigation_moveeventasecondtime.
     *However,thismightbecontroversial,wemightwannalettheevent
     *continueitspropagationandflagittosaythatnavigationhasalready
     *beenhandled(TODO?).
     *
     *@private
     *@param{KeyEvent}ev
     */
    _onKeydown:function(ev){
        switch(ev.which){
            case$.ui.keyCode.TAB:
                varevent=this.trigger_up('navigation_move',{
                    direction:ev.shiftKey?'previous':'next',
                });
                if(event.is_stopped()){
                    ev.preventDefault();
                    ev.stopPropagation();
                }
                break;
            case$.ui.keyCode.ENTER:
                //WepreventDefaulttheENTERkeybecauseoftwocoexistingbehaviours:
                //-InHTML5,pressingENTERona<button>triggerstwoevents:a'keydown'ANDa'click'
                //-Whencreatingandopeningadialog,thefocusisautomaticallygiventotheprimarybutton
                //TheendresultcausedsomeissueswhereamodalopenedbyanENTERkeypress(e.g.saving
                //changesinmultipleedition)confirmedthemodalwithoutanyintentionnaluserinput.
                ev.preventDefault();
                ev.stopPropagation();
                this.trigger_up('navigation_move',{direction:'next_line'});
                break;
            case$.ui.keyCode.ESCAPE:
                this.trigger_up('navigation_move',{direction:'cancel',originalEvent:ev});
                break;
            case$.ui.keyCode.UP:
                ev.stopPropagation();
                this.trigger_up('navigation_move',{direction:'up'});
                break;
            case$.ui.keyCode.RIGHT:
                ev.stopPropagation();
                this.trigger_up('navigation_move',{direction:'right'});
                break;
            case$.ui.keyCode.DOWN:
                ev.stopPropagation();
                this.trigger_up('navigation_move',{direction:'down'});
                break;
            case$.ui.keyCode.LEFT:
                ev.stopPropagation();
                this.trigger_up('navigation_move',{direction:'left'});
                break;
        }
    },
    /**
     *UpdatesthetargetdatavaluewiththecurrentAbstractFieldinstance.
     *Thisallowstoconsidertheparentfieldincaseofnestedfields.The
     *fieldwhichtriggeredtheeventisstillaccessiblethroughev.target.
     *
     *@private
     *@param{FlectraEvent}ev
     */
    _onNavigationMove:function(ev){
        ev.data.target=this;
    },
});

returnAbstractField;

});
