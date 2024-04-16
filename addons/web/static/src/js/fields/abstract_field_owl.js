flectra.define('web.AbstractFieldOwl',function(require){
    "usestrict";

    constfield_utils=require('web.field_utils');
    const{useListener}=require('web.custom_hooks');

    const{onMounted,onPatched}=owl.hooks;

    /**
     *ThisfiledefinestheOwlversionoftheAbstractField.Specificfields
     *writteninOwlshouldoverridethiscomponent.
     *
     *=========================================================================
     *
     */!\Thisapiworksalmostexactlylikethelegacyonebut
     */!\itstillcouldchange!Therearealreadyafewmethodsthatwillbe
     */!\removedlikesetIdForLabel,setInvalidClass,etc..
     *
     *=========================================================================
     *
     *Thisisthebasicfieldcomponentusedbyalltheviewstorenderafieldinaview.
     *Thesefieldcomponentsaremostlycommontoallviews,inparticularformandlist
     *views.
     *
     *Theresponsabilitiesofafieldcomponentaremainly:
     *-renderavisualrepresentationofthecurrentvalueofafield
     *-thatrepresentationiseitherin'readonly'orin'edit'mode
     *-notifytherestofthesystemwhenthefieldhasbeenchangedby
     *  theuser(ineditmode)
     *
     *Notes
     *-thecomponentisnotsupposedtobeabletoswitchbetweenmodes.Ifanother
     *  modeisrequired,theviewwilltakecareofinstantiatinganothercomponent.
     *-notifythesystemwhenitsvaluehaschangedanditsmodeischangedto'readonly'
     *-notifythesystemwhensomeactionhastobetaken,suchasopeningarecord
     *-theFieldcomponentshouldnot,ever,underanycircumstance,beawareof
     *  itsparent.Thewayitcommunicateschangeswiththerestofthesystemisby
     *  triggeringevents.Theseeventsbubbleupandareinterpreted
     *  bythemostappropriateparent.
     *
     *Also,insomecases,itmaynotbepracticaltohavethesamecomponentforall
     *views.Inthatsituation,youcanhavea'viewspecificcomponent'.Justregister
     *thecomponentintheregistryprefixedbytheviewtypeandadot.So,forexample,
     *aformspecificmany2onecomponentshouldberegisteredas'form.many2one'.
     *
     *@moduleweb.AbstractFieldOwl
     */
    classAbstractFieldextendsowl.Component{
        /**
         *Abstractfieldclass
         *
         *@constructor
         *@param{Component}parent
         *@param{Object}props
         *@param{string}props.fieldNameThefieldnamedefinedinthemodel
         *@param{Object}props.recordArecordobject(resultofthegetmethod
         *     ofabasicmodel)
         *@param{Object}[props.options]
         *@param{string}[props.options.mode=readonly]shouldbe'readonly'or'edit'
         *@param{string}[props.options.viewType=default]
         */
        constructor(){
            super(...arguments);

            this._isValid=true;
            //thisisthelastvaluethatwassetbytheuser,unparsed.Thisis
            //usedtoavoidsettingthevaluetwiceinarowwiththeexactvalue.
            this._lastSetValue=undefined;

            useListener('keydown',this._onKeydown);
            useListener('navigation-move',this._onNavigationMove);
            onMounted(()=>this._applyDecorations());
            onPatched(()=>this._applyDecorations());
        }
        /**
         *Hack:studiotriestofindthefieldwithaselectorbaseonits
         *name,beforeitismountedintotheDOM.Ideally,thisshouldbe
         *doneintheonMountedhook,butinthiscasewearetoolate,and
         *Studiofindsnothing.Asaconsequence,thefieldcan'tbeedited
         *byclickingonitslabel(orontherowformedbythepairlabel-field).
         *
         *TODO:movethistomountedatsomepoint?
         *
         *@override
         */
        __patch(){
            constres=super.__patch(...arguments);
            this.el.setAttribute('name',this.name);
            this.el.classList.add('o_field_widget');
            returnres;
        }
        /**
         *@async
         *@param{Object}[nextProps]
         *@returns{Promise}
         */
        asyncwillUpdateProps(nextProps){
            this._lastSetValue=undefined;
            returnsuper.willUpdateProps(nextProps);
        }

        //----------------------------------------------------------------------
        //Getters
        //----------------------------------------------------------------------

        /**
         *Thiscontainstheattributestopassthroughthecontext.
         *
         *@returns{Object}
         */
        getadditionalContext(){
            returnthis.options.additionalContext||{};
        }
        /**
         *Thiscontainstheattributesofthexml'field'tag,theinnerviews...
         *
         *@returns{Object}
         */
        getattrs(){
            constfieldsInfo=this.record.fieldsInfo[this.viewType];
            returnthis.options.attrs||(fieldsInfo&&fieldsInfo[this.name])||{};
        }
        /**
         *Idcorrespondingtothecurrentrecordinthemodel.
         *Itsintendeduseistobeabletotaganymessagesgoingupstream,
         *sotheviewknowswhichrecordswaschangedforexample.
         *
         *@returns{string}
         */
        getdataPointId(){
            returnthis.record.id;
        }
        /**
         *Thisisadescriptionofallthevariousfieldproperties,
         *suchasthetype,thecomodel(relation),...
         *
         *@returns{string}
         */
        getfield(){
            returnthis.record.fields[this.name];
        }
        /**
         *Returnsthemainfield'sDOMelementwhichcanbefocusedbythebrowser.
         *
         *@returns{HTMLElement|null}mainfocusableelementinsidethecomponent
         */
        getfocusableElement(){
            returnnull;
        }
        /**
         *Returnstheadditionaloptionspasstotheformatfunction.
         *Overridethisgettertoaddoptions.
         *
         *@returns{Object}
         */
        getformatOptions(){
            return{};
        }
        /**
         *Usedtodeterminewhichformat(andparse)functions
         *tocalltoformatthefield'svaluetoinsertintotheDOM(typically
         *putintoaspanoraninput),andtoparsethevaluefromtheinput
         *tosendittotheserver.Thesefunctionsarechosenaccordingto
         *the'widget'attrsifisisgiven,andifitisavalidkey,witha
         *fallbackonthefieldtype,ensuringthatthevalueisformattedand
         *displayedaccordingtothechosenwidget,ifany.
         *
         *@returns{string}
         */
        getformatType(){
            returnthis.attrs.widgetinfield_utils.format?
                this.attrs.widget:this.field.type;
        }
        /**
         *Returnswhetherornotthefieldisemptyandcanthusbehidden.This
         *methodistypicallycalledwhenthecomponentisinreadonly,tohideit
         *(anditslabel)ifitisempty.
         *
         *@returns{boolean}
         */
        getisEmpty(){
            return!this.isSet;
        }
        /**
         *Returnstrueifthecomponenthasavisibleelementthatcantakethefocus
         *
         *@returns{boolean}
         */
        getisFocusable(){
            constfocusable=this.focusableElement;
            //checkifelementisvisible
            returnfocusable&&!!(focusable.offsetWidth||
                focusable.offsetHeight||focusable.getClientRects().length);
        }
        /**
         *Determinesifthefieldvalueissettoameaningful
         *value.Thisisusefultodetermineifafieldshouldbedisplayedasempty
         *
         *@returns{boolean}
         */
        getisSet(){
            return!!this.value;
        }
        /**
         *Tracksifthecomponentisinavalidstate,meaningthatthecurrent
         *valuerepresentedintheDOMisavaluethatcanbeparsedandsaved.
         *Forexample,afloatfieldcanonlyuseanumberandnotastring.
         *
         *@returns{boolean}
         */
        getisValid(){
            returnthis._isValid;
        }
        /**
         *Fieldscanbeintwomodes:'edit'or'readonly'.
         *
         *@returns{string}
         */
        getmode(){
            returnthis.options.mode||"readonly";
        }
        /**
         *Usefulmostlytotriggerrpcsonthecorrectmodel.
         *
         *@returns{string}
         */
        getmodel(){
            returnthis.record.model;
        }
        /**
         *Thefieldnamedisplayedbythiscomponent.
         *
         *@returns{string}
         */
        getname(){
            returnthis.props.fieldName;
        }
        /**
         *Componentcanoftenbeconfiguredinthe'options'attributeinthe
         *xml'field'tag.Theseoptionsaresaved(andevaled)innodeOptions.
         *
         *@returns{Object}
         */
        getnodeOptions(){
            returnthis.attrs.options||{};
        }
        /**
         *@returns{Object}
         */
        getoptions(){
            returnthis.props.options||{};
        }
        /**
         *Returnstheadditionaloptionspassedtotheparsefunction.
         *Overridethisgettertoaddoptions.
         *
         *@returns{Object}
         */
        getparseOptions(){
            return{};
        }
        /**
         *Thedatapointfetchedfromthemodel.
         *
         *@returns{Object}
         */
        getrecord(){
            returnthis.props.record;
        }
        /**
         *Tracksthevaluesfortheotherfieldsforthesamerecord.
         *notethatitisexpectedtobemostlyareadonlyproperty,youcannot
         *usethistotrytochangeotherfieldsvalue,thisisnothowitis
         *supposedtowork.Also,donotusethis.recordData[this.name]toget
         *thecurrentvalue,thiscouldbeoutofsyncaftera_setValue.
         *
         *@returns{Object}
         */
        getrecordData(){
            returnthis.record.data;
        }
        /**
         *Ifthisflagissettotrue,thefieldcomponentwillbereseton
         *everychangewhichismadeintheview(iftheviewsupportsit).
         *Thisiscurrentlyaformviewfeature.
         *
         */!\Thisgettercouldberemovedwhenbasicviews(form,list,kanban)
         *areconverted.
         *
         *@returns{boolean}
         */
        getresetOnAnyFieldChange(){
            return!!this.attrs.decorations;
        }
        /**
         *Theres_idoftherecordindatabase.
         *Whentheuseriscreatinganewrecord,thereisnores_id.
         *Whentherecordwillbecreated,thefieldcomponentwill
         *bedestroyed(whentheformviewswitchestoreadonlymode)anda
         *newcomponentwithares_idinmodereadonlywillbecreated.
         *
         *@returns{Number}
         */
        getresId(){
            returnthis.record.res_id;
        }
        /**
         *Humanreadable(andtranslated)descriptionofthefield.
         *Mostlyusefultobedisplayedinvariousplacesinthe
         *UI,suchastooltipsorcreatedialogs.
         *
         *@returns{string}
         */
        getstring(){
            returnthis.attrs.string||this.field.string||this.name;
        }
        /**
         *Tracksthecurrent(parsedifneeded)valueofthefield.
         *
         *@returns{any}
         */
        getvalue(){
            returnthis.record.data[this.name];
        }
        /**
         *Thetypeoftheviewinwhichthefieldcomponentisinstantiated.
         *Forstandalonecomponents,a'default'viewTypeisset.
         *
         *@returns{string}
         */
        getviewType(){
            returnthis.options.viewType||'default';
        }

        //----------------------------------------------------------------------
        //Public
        //----------------------------------------------------------------------

        /**
         *Activatesthefieldcomponent.Bydefault,activationmeansfocusingand
         *selecting(ifpossible)theassociatedfocusableelement.Theselecting
         *partcanbedisabled.Inthatcase,notethatthefocusedinput/textarea
         *willhavethecursorattheveryend.
         *
         *@param{Object}[options]
         *@param{boolean}[options.noselect=false]iffalseandtheinput
         *  isoftypetextortextarea,thecontentwillalsobeselected
         *@param{Event}[options.event]theeventwhichfiredthisactivation
         *@returns{boolean}trueifthecomponentwasactivated,falseifthe
         *                   focusableelementwasnotfoundorinvisible
         */
        activate(options){
            if(this.isFocusable){
                constfocusable=this.focusableElement;
                focusable.focus();
                if(focusable.matches('input[type="text"],textarea')){
                    focusable.selectionStart=focusable.selectionEnd=focusable.value.length;
                    if(options&&!options.noselect){
                        focusable.select();
                    }
                }
                returntrue;
            }
            returnfalse;
        }
        /**
         *Thisfunctionshouldbeimplementedbycomponentsthatarenotableto
         *notifytheirenvironmentwhentheirvaluechanges(maybebecausetheir
         *arenotawareofthechanges)orthatmayhaveavalueinatemporary
         *state(maybebecausesomeactionshouldbeperformedtovalidateit
         *beforenotifyingit).Thisistypicallycalledbeforetryingtosavethe
         *component'svalue,soitshouldcall_setValue()tonotifytheenvironment
         *ifthevaluechangedbutwasnotnotified.
         *
         *@abstract
         *@returns{Promise|undefined}
         */
        commitChanges(){}
        /**
         *Removetheinvalidclassonafield
         *
         *ThisfunctionshouldberemovedwhenBasicRendererwillberewritteninowl
         */
        removeInvalidClass(){
            this.el.classList.remove('o_field_invalid');
            this.el.removeAttribute('aria-invalid');
        }
        /**
         *Setsthegivenidonthefocusableelementofthefieldandas'for'
         *attributeofpotentialinternallabels.
         *
         *ThisfunctionshouldberemovedwhenBasicRendererwillberewritteninowl
         *
         *@param{string}id
         */
        setIdForLabel(id){
            if(this.focusableElement){
                this.focusableElement.setAttribute('id',id);
            }
        }
        /**
         *addtheinvalidclassonafield
         *
         *ThisfunctionshouldberemovedwhenBasicRendererwillberewritteninowl
         */
        setInvalidClass(){
            this.el.classList.add('o_field_invalid');
            this.el.setAttribute('aria-invalid','true');
        }

        //----------------------------------------------------------------------
        //Private
        //----------------------------------------------------------------------

        /**
         *Applyfielddecorations(onlyiffield-specificdecorationshavebeen
         *definedinanattribute).
         *
         *ThisfunctionshouldberemovedwhenBasicRendererwillberewritteninowl
         *
         *@private
         */
        _applyDecorations(){
            for(constdecofthis.attrs.decorations||[]){
                constisToggled=py.PY_isTrue(
                    py.evaluate(dec.expression,this.record.evalContext)
                );
                constclassName=this._getClassFromDecoration(dec.name);
                this.el.classList.toggle(className,isToggled);
            }
        }
        /**
         *Convertsthevaluefromthefieldtoastringrepresentation.
         *
         *@private
         *@param{any}value(fromthefieldtype)
         *@returns{string}
         */
        _formatValue(value){
            constoptions=Object.assign({},this.nodeOptions,
                {data:this.recordData},this.formatOptions);
            returnfield_utils.format[this.formatType](value,this.field,options);
        }
        /**
         *ReturnstheclassNamecorrespondingtoagivendecoration.A
         *decorationisoftheform'decoration-%s'.Bydefault,replaces
         *'decoration'by'text'.
         *
         *@private
         *@param{string}decorationmustbeoftheform'decoration-%s'
         *@returns{string}
         */
        _getClassFromDecoration(decoration){
            return`text-${decoration.split('-')[1]}`;
        }
        /**
         *Comparesthegivenvaluewiththelastvaluethathasbeenset.
         *Notethatwecompareunparsedvalues.Handlesthespecialcasewhereno
         *valuehasbeensetyet,andthegivenvalueistheemptystring.
         *
         *@private
         *@param{any}value
         *@returns{boolean}trueiffvaluesarethesame
         */
        _isLastSetValue(value){
            returnthis._lastSetValue===value||(this.value===false&&value==='');
        }
        /**
         *Thismethodcheckifavalueisthesameasthecurrentvalueofthe
         *field.Forexample,afieldDatecomponentmightwanttousethemoment
         *specificvalueisSameinsteadof===.
         *
         *Thismethodisusedbythe_setValuemethod.
         *
         *@private
         *@param{any}value
         *@returns{boolean}
         */
        _isSameValue(value){
            returnthis.value===value;
        }
        /**
         *Convertsastringrepresentationtoavalidvalue.
         *
         *@private
         *@param{string}value
         *@returns{any}
         */
        _parseValue(value){
            returnfield_utils.parse[this.formatType](value,this.field,this.parseOptions);
        }
        /**
         *Thismethodiscalledbythecomponent,tochangeitsvalueandtonotify
         *theoutsideworldofitsnewstate.Thismethodalsovalidatesthenew
         *value.Notethatthismethoddoesnotrerenderthecomponent,itshouldbe
         *handledbythecomponentitself,ifnecessary.
         *
         *@private
         *@param{any}value
         *@param{Object}[options]
         *@param{boolean}[options.doNotSetDirty=false]iftrue,thebasicmodel
         *  willnotconsiderthatthisfieldisdirty,eventhoughitwaschanged.
         *  Pleasedonotusethisflagunlessyoureallyneedit.Ouronlyuse
         *  caseiscurrentlythepadcomponent,whichdoesa_setValueinthe
         *  renderEditmethod.
         *@param{boolean}[options.notifyChange=true]iffalse,thebasicmodel
         *  willnotnotifyandnottriggertheonchange,eventhoughitwaschanged.
         *@param{boolean}[options.forceChange=false]iftrue,thechangeeventwillbe
         *  triggeredevenifthenewvalueisthesameastheoldone
         *@returns{Promise}
         */
        _setValue(value,options){
            //wetrytoavoiddoinguselesswork,ifthevaluegivenhasnotchanged.
            if(this._isLastSetValue(value)){
                returnPromise.resolve();
            }
            this._lastSetValue=value;
            try{
                value=this._parseValue(value);
                this._isValid=true;
            }catch(e){
                this._isValid=false;
                this.trigger('set-dirty',{dataPointID:this.dataPointId});
                returnPromise.reject({message:"Valuesetisnotvalid"});
            }
            if(!(options&&options.forceChange)&&this._isSameValue(value)){
                returnPromise.resolve();
            }
            returnnewPromise((resolve,reject)=>{
                constchanges={};
                changes[this.name]=value;
                this.trigger('field-changed',{
                    dataPointID:this.dataPointId,
                    changes:changes,
                    viewType:this.viewType,
                    doNotSetDirty:options&&options.doNotSetDirty,
                    notifyChange:!options||options.notifyChange!==false,
                    allowWarning:options&&options.allowWarning,
                    onSuccess:resolve,
                    onFailure:reject,
                });
            });
        }

        //----------------------------------------------------------------------
        //Handlers
        //----------------------------------------------------------------------

        /**
         *Interceptsnavigationkeyboardeventstopreventtheirdefaultbehavior
         *andnotifiestheviewsothatitcanhandleititsownway.
         *
         *@private
         *@param{KeyEvent}ev
         */
        _onKeydown(ev){
            switch(ev.which){
                case$.ui.keyCode.TAB:
                    this.trigger('navigation-move',{
                        direction:ev.shiftKey?'previous':'next',
                        originalEvent:ev,
                    });
                    break;
                case$.ui.keyCode.ENTER:
                    //WepreventDefaulttheENTERkeybecauseoftwocoexistingbehaviours:
                    //-InHTML5,pressingENTERona<button>triggerstwoevents:a'keydown'ANDa'click'
                    //-Whencreatingandopeningadialog,thefocusisautomaticallygiventotheprimarybutton
                    //TheendresultcausedsomeissueswhereamodalopenedbyanENTERkeypress(e.g.saving
                    //changesinmultipleedition)confirmedthemodalwithoutanyintentionnaluserinput.
                    ev.preventDefault();
                    ev.stopPropagation();
                    this.trigger('navigation-move',{direction:'next_line'});
                    break;
                case$.ui.keyCode.ESCAPE:
                    this.trigger('navigation-move',{direction:'cancel',originalEvent:ev});
                    break;
                case$.ui.keyCode.UP:
                    ev.stopPropagation();
                    this.trigger('navigation-move',{direction:'up'});
                    break;
                case$.ui.keyCode.RIGHT:
                    ev.stopPropagation();
                    this.trigger('navigation-move',{direction:'right'});
                    break;
                case$.ui.keyCode.DOWN:
                    ev.stopPropagation();
                    this.trigger('navigation-move',{direction:'down'});
                    break;
                case$.ui.keyCode.LEFT:
                    ev.stopPropagation();
                    this.trigger('navigation-move',{direction:'left'});
                    break;
            }
        }
        /**
         *UpdatesthetargetdatavaluewiththecurrentAbstractFieldinstance.
         *Thisallowstoconsidertheparentfieldincaseofnestedfields.The
         *fieldwhichtriggeredtheeventisstillaccessiblethroughev.target.
         *
         *@private
         *@param{CustomEvent}ev
         */
        _onNavigationMove(ev){
            ev.detail.target=this;
        }
    }

    /**
     *Anobjectrepresentingfieldstobefetchedbythemodeleventhoughnot
     *presentintheview.
     *Thisobjectcontains"fieldname"askeyandanobjectasvalue.
     *Thatvalueobjectmustcontainthekey"type"
     *@seeFieldBinaryImageforanexample.
     */
    AbstractField.fieldDependencies={};
    /**
     *Ifthisflagisgivenastring,therelatedBasicModelwillbeusedto
     *initializespecialDatathefieldmightneed.Thisdatawillbeavailable
     *throughthis.record.specialData[this.name].
     *
     *@seeBasicModel._fetchSpecialData
     */
    AbstractField.specialData=false;
    /**
     *tooverridetoindicatewhichfieldtypesaresupportedbythecomponent
     *
     *@typeArray<string>
     */
    AbstractField.supportedFieldTypes=[];
    /**
     *Tooverridetogiveauserfriendlynametothecomponent.
     *
     *@typestring
     */
    AbstractField.description="";
    /**
     *Currentlyonlyusedinlistview.
     *Ifthisflagissettotrue,thelistcolumnnamewillbeempty.
     */
    AbstractField.noLabel=false;
    /**
     *Currentlyonlyusedinlistview.
     *Ifset,thisvaluewillbedisplayedascolumnname.
     */
    AbstractField.label="";

    returnAbstractField;
});
