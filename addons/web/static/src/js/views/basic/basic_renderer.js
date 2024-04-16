flectra.define('web.BasicRenderer',function(require){
"usestrict";

/**
 *TheBasicRendererisanabstractclassdesignedtosharecodebetweenall
 *viewsthatusesaBasicModel.Themaingoalistokeeptrackofallfield
 *widgets,andproperlydestroythemwheneverarerenderisdone.Thewidgets
 *andmodifiersupdatesmechanismisalsosharedintheBasicRenderer.
 */
varAbstractRenderer=require('web.AbstractRenderer');
varconfig=require('web.config');
varcore=require('web.core');
vardom=require('web.dom');
constsession=require('web.session');
constutils=require('web.utils');
varwidgetRegistry=require('web.widget_registry');

const{WidgetAdapterMixin}=require('web.OwlCompatibility');
constFieldWrapper=require('web.FieldWrapper');

varqweb=core.qweb;
const_t=core._t;

varBasicRenderer=AbstractRenderer.extend(WidgetAdapterMixin,{
    custom_events:{
        navigation_move:'_onNavigationMove',
    },
    /**
     *Basicrenderersimplementstheconceptof"mode",theycaneitherbein
     *readonlymodeoreditablemode.
     *
     *@override
     */
    init:function(parent,state,params){
        this._super.apply(this,arguments);
        this.activeActions=params.activeActions;
        this.viewType=params.viewType;
        this.mode=params.mode||'readonly';
        this.widgets=[];
        //Thisattributeletsusknowifthereisahandlewidgetonafield,
        //andonwhichfielditisset.
        this.handleField=null;
    },
    /**
     *@override
     */
    destroy:function(){
        this._super.apply(this,arguments);
        WidgetAdapterMixin.destroy.call(this);
    },
    /**
     *CalledeachtimetherendererisattachedintotheDOM.
     */
    on_attach_callback:function(){
        this._isInDom=true;
        //callon_attach_callbackonfieldwidgets
        for(consthandleinthis.allFieldWidgets){
            this.allFieldWidgets[handle].forEach(widget=>{
                if(!utils.isComponent(widget.constructor)&&widget.on_attach_callback){
                    widget.on_attach_callback();
                }
            });
        }
        //callon_attach_callbackonwidgets
        this.widgets.forEach(widget=>{
            if(widget.on_attach_callback){
                widget.on_attach_callback();
            }
        });
        //callon_attach_callbackonchildcomponents(includingfieldcomponents)
        WidgetAdapterMixin.on_attach_callback.call(this);
    },
    /**
     *CalledeachtimetherendererisdetachedfromtheDOM.
     */
    on_detach_callback:function(){
        this._isInDom=false;
        //callon_detach_callbackonfieldwidgets
        for(consthandleinthis.allFieldWidgets){
            this.allFieldWidgets[handle].forEach(widget=>{
                if(!utils.isComponent(widget.constructor)&&widget.on_detach_callback){
                    widget.on_detach_callback();
                }
            });
        }
        //callon_detach_callbackonwidgets
        this.widgets.forEach(widget=>{
            if(widget.on_detach_callback){
                widget.on_detach_callback();
            }
        });
        //callon_detach_callbackonchildcomponents(includingfieldcomponents)
        WidgetAdapterMixin.on_detach_callback.call(this);
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Thismethodhastworesponsabilities:findeveryinvalidfieldsinthe
     *currentview,andmakingsurethattheyaredisplayedasinvalid,by
     *togglingtheo_form_invalidcssclass.Ithastobedonebothonthe
     *widget,andonthelabel,ifany.
     *
     *@param{string}recordID
     *@returns{string[]}thelistofinvalidfieldnames
     */
    canBeSaved:function(recordID){
        varself=this;
        varinvalidFields=[];
        _.each(this.allFieldWidgets[recordID],function(widget){
            varcanBeSaved=self._canWidgetBeSaved(widget);
            if(!canBeSaved){
                invalidFields.push(widget.name);
            }
            if(widget.el){//widgetmaynotbestartedyet
                widget.$el.toggleClass('o_field_invalid',!canBeSaved);
                widget.$el.attr('aria-invalid',!canBeSaved);
            }
        });
        returninvalidFields;
    },
    /**
     *Calls'commitChanges'onallfieldwidgets,sothattheycannotifythe
     *environmentwiththeircurrentvalue(usefulforwidgetsthatcan't
     *detectwhentheirvaluechangesorthathavetovalidatetheirchanges
     *beforenotifyingthem).
     *
     *@param{string}recordID
     *@return{Promise}
     */
    commitChanges:function(recordID){
        vardefs=_.map(this.allFieldWidgets[recordID],function(widget){
            returnwidget.commitChanges();
        });
        returnPromise.all(defs);
    },
    /**
     *Updatestheinternalstateoftherenderertothenewstate.Bydefault,
     *thisalsoimplementstherecomputationofthemodifiersandtheir
     *applicationtotheDOMandtheresetofthefieldwidgetsifneeded.
     *
     *Incasethegivenrecordisnotfoundanymore,awholere-renderingis
     *completed(possibleifachangeinarecordcausedanonchangewhich
     *erasedthecurrentrecord).
     *
     *Wecouldalwaysrerendertheviewfromscratch,butthenitwouldnotbe
     *asefficient,andwemightlosesomelocalstate,suchastheinputfocus
     *cursor,orthescrollingposition.
     *
     *@param{Object}state
     *@param{string}id
     *@param{string[]}fields
     *@param{FlectraEvent}ev
     *@returns{Promise<AbstractField[]>}resolvedwiththelistofwidgets
     *                                     thathavebeenreset
     */
    confirmChange:function(state,id,fields,ev){
        varself=this;
        this._setState(state);
        varrecord=this._getRecord(id);
        if(!record){
            returnthis._render().then(_.constant([]));
        }

        //resetallwidgets(fromthe<widget>tag)ifany:
        _.invoke(this.widgets,'updateState',state);

        vardefs=[];

        //Resetallthefieldwidgetsthataremarkedaschangedandtheones
        //whichareconfiguredtoalwaysberesetonanychange
        _.each(this.allFieldWidgets[id],function(widget){
            varfieldChanged=_.contains(fields,widget.name);
            if(fieldChanged||widget.resetOnAnyFieldChange){
                defs.push(widget.reset(record,ev,fieldChanged));
            }
        });

        //Themodifiersupdateisdoneafterwidgetresetsasmodifiers
        //associatedcallbacksneedtohaveallthewidgetswiththeproper
        //statebeforeevaluation
        defs.push(this._updateAllModifiers(record));

        returnPromise.all(defs).then(function(){
            return_.filter(self.allFieldWidgets[id],function(widget){
                varfieldChanged=_.contains(fields,widget.name);
                returnfieldChanged||widget.resetOnAnyFieldChange;
            });
        });
    },
    /**
     *Activatesthewidgetandmovethecursortothegivenoffset
     *
     *@param{string}id
     *@param{string}fieldName
     *@param{integer}offset
     */
    focusField:function(id,fieldName,offset){
        this.editRecord(id);
        if(typeofoffset==="number"){
            varfield=_.findWhere(this.allFieldWidgets[id],{name:fieldName});
            dom.setSelectionRange(field.getFocusableElement().get(0),{start:offset,end:offset});
        }
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Activatesthewidgetatthegivenindexforthegivenrecordifpossible
     *orthe"next"possibleone.Usually,awidgetcanbeactivatedifitis
     *ineditmode,andifitisvisible.
     *
     *@private
     *@param{Object}record
     *@param{integer}currentIndex
     *@param{Object}[options={}]
     *@param{integer}[options.inc=1]-theincrementtousewhensearchingforthe
     *  "next"possibleone
     *@param{boolean}[options.noAutomaticCreate=false]
     *@param{boolean}[options.wrap=false]iftrue,whenwearriveattheendofthe
     *  listofwidget,wewraparoundandtrytoactivatewidgetsstartingat
     *  thebeginning.Otherwise,wejuststoptryingandreturn-1
     *@returns{integer}theindexofthewidgetthatwasactivatedor-1if
     *  nonewaspossibletoactivate
     */
    _activateFieldWidget:function(record,currentIndex,options){
        options=options||{};
        _.defaults(options,{inc:1,wrap:false});
        currentIndex=Math.max(0,currentIndex);//donotallownegativecurrentIndex

        varrecordWidgets=this.allFieldWidgets[record.id]||[];
        for(vari=0;i<recordWidgets.length;i++){
            varactivated=recordWidgets[currentIndex].activate(
                {
                    event:options.event,
                    noAutomaticCreate:options.noAutomaticCreate||false
                });
            if(activated){
                returncurrentIndex;
            }

            currentIndex+=options.inc;
            if(currentIndex>=recordWidgets.length){
                if(options.wrap){
                    currentIndex-=recordWidgets.length;
                }else{
                    return-1;
                }
            }elseif(currentIndex<0){
                if(options.wrap){
                    currentIndex+=recordWidgets.length;
                }else{
                    return-1;
                }
            }
        }
        return-1;
    },
    /**
     *Thisisawrapperofthe{@see_activateFieldWidget}functiontoselect
     *thenextpossiblewidgetinsteadofthegivenone.
     *
     *@private
     *@param{Object}record
     *@param{integer}currentIndex
     *@param{Object|undefined}options
     *@return{integer}
     */
    _activateNextFieldWidget:function(record,currentIndex,options){
        currentIndex=(currentIndex+1)%(this.allFieldWidgets[record.id]||[]).length;
        returnthis._activateFieldWidget(record,currentIndex,_.extend({inc:1},options));
    },
    /**
     *Thisisawrapperofthe{@see_activateFieldWidget}functiontoselect
     *thepreviouspossiblewidgetinsteadofthegivenone.
     *
     *@private
     *@param{Object}record
     *@param{integer}currentIndex
     *@return{integer}
     */
    _activatePreviousFieldWidget:function(record,currentIndex){
        currentIndex=currentIndex?(currentIndex-1):((this.allFieldWidgets[record.id]||[]).length-1);
        returnthis._activateFieldWidget(record,currentIndex,{inc:-1});
    },
    /**
     *Addatooltipona$node,dependingonafielddescription
     *
     *@param{FieldWidget}widget
     *@param{$node}$node
     */
    _addFieldTooltip:function(widget,$node){
        //optionalargument$node,thejQueryelementonwhichthetooltip
        //shouldbeattachedifnotgiven,thetooltipisattachedonthe
        //widget's$el
        $node=$node.length?$node:widget.$el;
        $node.tooltip(this._getTooltipOptions(widget));
    },
    /**
     *DoesthenecessaryDOMupdatestomatchthegivenmodifiersdata.The
     *modifiersdataissupposedtocontaintheproperlyevaluatedmodifiers
     *associatedtothegivenrecordsandelements.
     *
     *@param{Object}modifiersData
     *@param{Object}record
     *@param{Object}[element]-dotheupdateonlyonthiselementifgiven
     */
    _applyModifiers:function(modifiersData,record,element){
        varself=this;
        varmodifiers=modifiersData.evaluatedModifiers[record.id]||{};

        if(element){
            _apply(element);
        }else{
            //Cloneisnecessaryasthelistmightchangeduring_.each
            _.each(_.clone(modifiersData.elementsByRecord[record.id]),_apply);
        }

        function_apply(element){
            //Iftheviewisineditmodeandthatawidgethavetoswitch
            //its"readonly"state,wehavetore-renderitcompletely
            if('readonly'inmodifiers&&element.widget){
                varmode=modifiers.readonly?'readonly':modifiersData.baseModeByRecord[record.id];
                if(mode!==element.widget.mode){
                    self._rerenderFieldWidget(element.widget,record,{
                        keepBaseMode:true,
                        mode:mode,
                    });
                    return;//Rerenderingalreadyappliedthemodifiers,noneedtogofurther
                }
            }

            //TogglemodifiersCSSclassesifnecessary
            element.$el.toggleClass("o_invisible_modifier",!!modifiers.invisible);
            element.$el.toggleClass("o_readonly_modifier",!!modifiers.readonly);
            element.$el.toggleClass("o_required_modifier",!!modifiers.required);

            if(element.widget&&element.widget.updateModifiersValue){
                element.widget.updateModifiersValue(modifiers);
            }

            //Callassociatedcallback
            if(element.callback){
                element.callback(element,modifiers,record);
            }
        }
    },
    /**
     *Determinesifagivenfieldwidgetvaluecanbesaved.Forthistobe
     *true,thewidgetmustbevalid(properlyparsedvalue)andhaveavalue
     *iftheassociatedviewfieldisrequired.
     *
     *@private
     *@param{AbstractField}widget
     *@returns{boolean|Promise<boolean>}@seeAbstractField.isValid
     */
    _canWidgetBeSaved:function(widget){
        varmodifiers=this._getEvaluatedModifiers(widget.__node,widget.record);
        returnwidget.isValid()&&(widget.isSet()||!modifiers.required);
    },
    /**
     *Destroysagivenwidgetassociatedtothegivenrecordandremovesit
     *frominternalreferencing.
     *
     *@private
     *@param{string}recordIDidofthelocalresource
     *@param{AbstractField}widget
     *@returns{integer}theindexoftheremovedwidget
     */
    _destroyFieldWidget:function(recordID,widget){
        varrecordWidgets=this.allFieldWidgets[recordID];
        varindex=recordWidgets.indexOf(widget);
        if(index>=0){
            recordWidgets.splice(index,1);
        }
        this._unregisterModifiersElement(widget.__node,recordID,widget);
        widget.destroy();
        returnindex;
    },
    /**
     *Searchesforthelastevaluationofthemodifiersassociatedtothegiven
     *data(modifiersevaluationaresupposedtoalwaysbeup-to-dateassoon
     *aspossible).
     *
     *@private
     *@param{Object}node
     *@param{Object}record
     *@returns{Object}theevaluatedmodifiersassociatedtothegivennode
     *                  andrecord(notrecomputedbythecall)
     */
    _getEvaluatedModifiers:function(node,record){
        varelement=this._getModifiersData(node);
        if(!element){
            return{};
        }
        returnelement.evaluatedModifiers[record.id]||{};
    },
    /**
     *Searchesthroughtheregisteredmodifiersdatafortheonewhichis
     *relatedtothegivennode.
     *
     *@private
     *@param{Object}node
     *@returns{Object|undefined}relatedmodifiersdataifany
     *                            undefinedotherwise
     */
    _getModifiersData:function(node){
        return_.findWhere(this.allModifiersData,{node:node});
    },
    /**
     *Thisfunctionismeanttobeoverriddeninrenderers.IttakesadataPoint
     *id(foradataPointoftyperecord),andshouldreturnthecorresponding
     *dataPoint.
     *
     *@abstract
     *@private
     *@param{string}[recordId]
     *@returns{Object|null}
     */
    _getRecord:function(recordId){
        returnnull;
    },
    /**
     *Gettheoptionsforthetooltip.Thisallowtochangethisoptionsinanothermodule.
     *@paramwidget
     *@return{{}}
     *@private
     */
    _getTooltipOptions:function(widget){
        return{
            title:function(){
                lethelp=widget.attrs.help||widget.field.help||'';
                if(session.display_switch_company_menu&&widget.field.company_dependent){
                    help+=(help?'\n\n':'')+_t('Valuessetherearecompany-specific.');
                }
                constdebug=config.isDebug();
                if(help||debug){
                    returnqweb.render('WidgetLabel.tooltip',{debug,help,widget});
                }
            }
        };
    },
    /**
     *@private
     *@param{jQueryElement}$el
     *@param{Object}node
     */
    _handleAttributes:function($el,node){
        if($el.is('button')){
            return;
        }
        if(node.attrs.class){
            $el.addClass(node.attrs.class);
        }
        if(node.attrs.style){
            $el.attr('style',node.attrs.style);
        }
        if(node.attrs.placeholder){
            $el.attr('placeholder',node.attrs.placeholder);
        }
    },
    /**
     *Usedbylistandkanbanrendererstodeterminewhetherornottodisplay
     *thenocontenthelper(ifthereisnodatainthestatetodisplay)
     *
     *@private
     *@returns{boolean}
     */
    _hasContent:function(){
        returnthis.state.count!==0&&(!('isSample'inthis.state)||!this.state.isSample);
    },
    /**
     *Forcetheresequencingoftherecordsaftermovingoneofthemtoagiven
     *index.
     *
     *@private
     *@param{string}recordIddatapointidofthemovedrecord
     *@param{integer}toIndexnewindexofthemovedrecord
     */
    _moveRecord:function(recordId,toIndex){
        varself=this;
        varrecords=this.state.data;
        varrecord=_.findWhere(records,{id:recordId});
        varfromIndex=records.indexOf(record);
        varlowerIndex=Math.min(fromIndex,toIndex);
        varupperIndex=Math.max(fromIndex,toIndex)+1;
        varorder=_.findWhere(this.state.orderedBy,{name:this.handleField});
        varasc=!order||order.asc;
        varreorderAll=false;
        varsequence=(asc?-1:1)*Infinity;

        //determineifweneedtoreorderallrecords
        _.each(records,function(record,index){
            if(((index<lowerIndex||index>=upperIndex)&&
                ((asc&&sequence>=record.data[self.handleField])||
                 (!asc&&sequence<=record.data[self.handleField])))||
                (index>=lowerIndex&&index<upperIndex&&sequence===record.data[self.handleField])){
                reorderAll=true;
            }
            sequence=record.data[self.handleField];
        });

        if(reorderAll){
            records=_.without(records,record);
            records.splice(toIndex,0,record);
        }else{
            records=records.slice(lowerIndex,upperIndex);
            records=_.without(records,record);
            if(fromIndex>toIndex){
                records.unshift(record);
            }else{
                records.push(record);
            }
        }

        varsequences=_.pluck(_.pluck(records,'data'),this.handleField);
        varrecordIds=_.pluck(records,'id');
        if(!asc){
            recordIds.reverse();
        }

        this.trigger_up('resequence_records',{
            handleField:this.handleField,
            offset:_.min(sequences),
            recordIds:recordIds,
        });
    },
    /**
     *Thisfunctioniscalledeachtimeafieldwidgetiscreated,whenitis
     *ready(afteritswillStartandStartmethodsarecomplete). Thisisthe
     *placewhereworkhavingtodowith$elshouldbedone.
     *
     *@private
     *@param{Widget}widgetthefieldwidgetinstance
     *@param{Object}nodetheattrscomingfromthearch
     */
    _postProcessField:function(widget,node){
        this._handleAttributes(widget.$el,node);
    },
    /**
     *Registersorupdatesthemodifiersdataassociatedtothegivennode.
     *Thismethodisquietcomplexasithandlesalltheneedsofthebasic
     *renderers:
     *
     *-Onfirstregistration,themodifiersareevaluatedthankstothegiven
     *  record.ThisallowsnodesthatwillproduceanAbstractFieldinstance
     *  tohavetheirmodifiersregisteredbeforethisfieldcreationaswe
     *  needthereadonlymodifiertobeabletoinstantiatetheAbstractField.
     *
     *-Onadditionalregistrations,ifthenodewasalreadyregisteredbutthe
     *  recordisdifferent,weevaluatethemodifiersforthisrecordand
     *  savestheminthesameobject(withoutreparsingthemodifiers).
     *
     *-Onadditionalregistrations,themodifiersarenotreparsed(or
     *  reevaluatedforanalreadyseenrecord)butthegivenwidgetorDOM
     *  elementisassociatedtothenodemodifiers.
     *
     *-Thenewelementsareimmediatelyadaptedtomatchthemodifiersandthe
     *  givenassociatedcallbackiscalledevenifthereisnomodifierson
     *  thenode(@see_applyModifiers).Thisisindeednecessaryasthe
     *  callbackisadescriptionofwhattodowhenamodifierchanges.Even
     *  ifthereisnomodifiers,thisactionmustbeperformedonfirst
     *  renderingtoavoidcodeduplication.Ifthereisnomodifiers,they
     *  willhowevernotberegisteredformodifiersupdates.
     *
     *-Whenanewelementisgiven,itdoesnotreplacetheoldone,itis
     *  addedasanadditionalelement.Thisisindeedusefulfornodesthat
     *  willproducemultipleDOM(asalistcellanditsinternalwidgetor
     *  aformfieldanditsassociatedlabel).
     *  (@see_unregisterModifiersElementforremovinganassociatedelement.)
     *
     *Note:alsoonviewrerendering,allthemodifiersareforgottensothat
     *therendereronlykeepstheonesassociatedtothecurrentDOMstate.
     *
     *@private
     *@param{Object}node
     *@param{Object}record
     *@param{jQuery|AbstractField}[element]
     *@param{Object}[options]
     *@param{Object}[options.callback]thecallbacktocallonregistration
     *  andonmodifiersupdates
     *@param{boolean}[options.keepBaseMode=false]thisfunctionregistersthe
     *  'baseMode'ofthenodeonaperrecordbasis;
     *  thisisafieldwidgetspecificsettingswhich
     *  representsthegenericmodeofthewidget,regardlessofitsmodifiers
     *  (theinterestingcaseisthelistview:allwidgetsaresupposedtobe
     *  inthebaseMode'readonly',excepttheonesthatareinthelinethat
     *  iscurrentlybeingedited).
     *  Withoption'keepBaseMode'settotrue,thebaseModeoftherecord's
     *  nodeisn'toverridden(thisisparticularilyusefulwhenafieldwidget
     *  isre-renderedbecauseitsreadonlymodifierchanged,asinthiscase,
     *  wedon'twanttochangeitsbasemode).
     *@param{string}[options.mode]the'baseMode'oftherecord'snodeissettothis
     *  value(ifnotgiven,itissettothis.mode,themodeoftherenderer)
     *@returns{Object}forcodeefficiency,returnsthelastevaluated
     *  modifiersforthegivennodeandrecord.
     *@throws{Error}ifoneofthemodifierdomainsisnotvalid
     */
    _registerModifiers:function(node,record,element,options){
        options=options||{};
        //Checkifwealreadyregisteredthemodifiersforthegivennode
        //Ifyes,thisissimplyanupdateoftherelatedelement
        //Ifnot,checkthemodifierstoseeifitneedsregistration
        varmodifiersData=this._getModifiersData(node);
        if(!modifiersData){
            varmodifiers=node.attrs.modifiers||{};
            modifiersData={
                node:node,
                modifiers:modifiers,
                evaluatedModifiers:{},
                elementsByRecord:{},
                baseModeByRecord:{},
            };
            if(!_.isEmpty(modifiers)){//Registeronlyifmodifiersmightchange(TODOconditionmightbeimprovedhere)
                this.allModifiersData.push(modifiersData);
            }
        }

        //Computetherecord'sbasemode
        if(!modifiersData.baseModeByRecord[record.id]||!options.keepBaseMode){
            modifiersData.baseModeByRecord[record.id]=options.mode||this.mode;
        }

        //Evaluateifnecessary
        if(!modifiersData.evaluatedModifiers[record.id]){
            try{
                modifiersData.evaluatedModifiers[record.id]=record.evalModifiers(modifiersData.modifiers);
            }catch(e){
                thrownewError(_.str.sprintf(
                    "Whileparsingmodifiersfor%s%s:%s",
                    node.tag,node.tag==='field'?''+node.attrs.name:'',
                    e.message
                ));
            }
        }

        //Elementmightnotbegivenyet(asecondcalltothefunctioncan
        //updatetheregistrationwiththeelement)
        if(element){
            varnewElement={};
            if(elementinstanceofjQuery){
                newElement.$el=element;
            }else{
                newElement.widget=element;
                newElement.$el=element.$el;
            }
            if(options&&options.callback){
                newElement.callback=options.callback;
            }

            if(!modifiersData.elementsByRecord[record.id]){
                modifiersData.elementsByRecord[record.id]=[];
            }
            modifiersData.elementsByRecord[record.id].push(newElement);

            this._applyModifiers(modifiersData,record,newElement);
        }

        returnmodifiersData.evaluatedModifiers[record.id];
    },
    /**
     *@override
     */
    async_render(){
        constoldAllFieldWidgets=this.allFieldWidgets;
        this.allFieldWidgets={};//TODOmaybemergingallFieldWidgetsandallModifiersDatainto"nodesData"insomewaycouldbegreat
        this.allModifiersData=[];
        constoldWidgets=this.widgets;
        this.widgets=[];

        awaitthis._super(...arguments);

        for(constidinoldAllFieldWidgets){
            for(constwidgetofoldAllFieldWidgets[id]){
                widget.destroy();
            }
        }
        for(constwidgetofoldWidgets){
            widget.destroy();
        }
        if(this._isInDom){
            for(consthandleinthis.allFieldWidgets){
                this.allFieldWidgets[handle].forEach(widget=>{
                    if(!utils.isComponent(widget.constructor)&&widget.on_attach_callback){
                        widget.on_attach_callback();
                    }
                });
            }
            this.widgets.forEach(widget=>{
                if(widget.on_attach_callback){
                    widget.on_attach_callback();
                }
            });
            //callon_attach_callbackonchildcomponents(includingfieldcomponents)
            WidgetAdapterMixin.on_attach_callback.call(this);
        }
    },
    /**
     *InstantiatestheappropriateAbstractFieldspecializationforthegiven
     *nodeandpreparesitsrenderingandadditiontotheDOM.Indeed,the
     *renderingofthewidgetwillbestartedandtheassociatedpromisewill
     *beaddedtothe'defs'attribute.Thisissupposedtobecreatedand
     *deletedbythecallingcodeifnecessary.
     *
     *Note:wealwaysreturna$el. Ifthefieldwidgetisasynchronous,this
     *$elwillbereplacedbythereal$el,wheneverthewidgetisready(start
     *methodisdone). Thismeansthatthisisnotthecorrectplacetomake
     *changesonthewidget$el. Forthis,@see_postProcessFieldmethod
     *
     *@private
     *@param{Object}node
     *@param{Object}record
     *@param{Object}[options]passedto@_registerModifiers
     *@param{string}[options.mode]either'edit'or'readonly'(defaultsto
     *  this.mode,themodeoftherenderer)
     *@returns{jQueryElement}
     */
    _renderFieldWidget:function(node,record,options){
        options=options||{};
        varfieldName=node.attrs.name;
        //Registerthenode-associatedmodifiers
        varmode=options.mode||this.mode;
        varmodifiers=this._registerModifiers(node,record,null,options);
        //Initializeandregisterthewidget
        //Readonlystatusisknownasthemodifiershavejustbeenregistered
        varWidget=record.fieldsInfo[this.viewType][fieldName].Widget;
        constlegacy=!(Widget.prototypeinstanceofowl.Component);
        constwidgetOptions={
            mode:modifiers.readonly?'readonly':mode,
            viewType:this.viewType,
        };
        letwidget;
        if(legacy){
            widget=newWidget(this,fieldName,record,widgetOptions);
        }else{
            widget=newFieldWrapper(this,Widget,{
                fieldName,
                record,
                options:widgetOptions,
            });
        }

        //Registerthewidgetsothatitcaneasilybefoundagain
        if(this.allFieldWidgets[record.id]===undefined){
            this.allFieldWidgets[record.id]=[];
        }
        this.allFieldWidgets[record.id].push(widget);

        widget.__node=node;//TODOgetridofthisifpossibleoneday

        //Preparewidgetrenderingandsavetherelatedpromise
        var$el=$('<div>');
        letdef;
        if(legacy){
            def=widget._widgetRenderAndInsert(function(){});
        }else{
            def=widget.mount(document.createDocumentFragment());
        }

        this.defs.push(def);

        //Updatethemodifiersregistrationbyassociatingthewidgetandby
        //givingthemodifiersoptionsnow(asthepotentialcallbackis
        //associatedtonewwidget)
        varself=this;
        def.then(function(){
            //whenthecallerofrenderFieldWidgetusessomethinglike
            //this.renderFieldWidget(...).addClass(...),theclassisaddedon
            //thetemporarydivandnotontheactualelementthatwillbe
            //rendered.Aswedonotreturnapromiseandsomecallerscannot
            //waitforthis.defs,wecopythoseclassnamestothefinalelement.
            widget.$el.addClass($el.attr('class'));

            $el.replaceWith(widget.$el);
            self._registerModifiers(node,record,widget,{
                callback:function(element,modifiers,record){
                    element.$el.toggleClass('o_field_empty',!!(
                        record.data.id&&
                        (modifiers.readonly||mode==='readonly')&&
                        element.widget.isEmpty()
                    ));
                },
                keepBaseMode:!!options.keepBaseMode,
                mode:mode,
            });
            self._postProcessField(widget,node);
        });

        return$el;
    },
    /**
     *Instantiatecustomwidgets
     *
     *@private
     *@param{Object}record
     *@param{Object}node
     *@returns{jQueryElement}
     */
    _renderWidget:function(record,node){
        varWidget=widgetRegistry.get(node.attrs.name);
        varwidget=newWidget(this,record,node);

        this.widgets.push(widget);

        //Preparewidgetrenderingandsavetherelatedpromise
        vardef=widget._widgetRenderAndInsert(function(){});
        this.defs.push(def);
        var$el=$('<div>');

        varself=this;
        def.then(function(){
            self._handleAttributes(widget.$el,node);
            self._registerModifiers(node,record,widget);
            widget.$el.addClass('o_widget');
            $el.replaceWith(widget.$el);
        });

        return$el;
    },
    /**
     *Rerendersagivenwidgetandmakesuretheassociateddatawhich
     *referencedtheoldoneisupdated.
     *
     *@private
     *@param{Widget}widget
     *@param{Object}record
     *@param{Object}[options]optionspassedto@_renderFieldWidget
     */
    _rerenderFieldWidget:function(widget,record,options){
        //Renderthenewfieldwidget
        var$el=this._renderFieldWidget(widget.__node,record,options);
        //getthenewwidgetthathasjustbeenpushedinallFieldWidgets
        constrecordWidgets=this.allFieldWidgets[record.id];
        constnewWidget=recordWidgets[recordWidgets.length-1];
        constdef=this.defs[this.defs.length-1];//thisisthewidget'sdef,resolvedwhenitisready
        const$div=$('<div>');
        $div.append($el);//$elwillbereplacedwhenwidgetisready(see_renderFieldWidget)
        def.then(()=>{
            widget.$el.replaceWith($div.children());

            //Destroytheoldwidgetandpositionthenewoneattheoldone's
            //(ithasbeentemporarilyinsertedattheendofthelist)
            recordWidgets.splice(recordWidgets.indexOf(newWidget),1);
            varoldIndex=this._destroyFieldWidget(record.id,widget);
            recordWidgets.splice(oldIndex,0,newWidget);

            //Mountnewwidgetifnecessary(mainlyforOwlcomponents)
            if(this._isInDom&&newWidget.on_attach_callback){
                newWidget.on_attach_callback();
            }
        });
    },
    /**
     *Unregistersanelementofthemodifiersdataassociatedtothegiven
     *nodeandrecord.
     *
     *@param{Object}node
     *@param{string}recordIDidofthelocalresource
     *@param{jQuery|AbstractField}element
     */
    _unregisterModifiersElement:function(node,recordID,element){
        varmodifiersData=this._getModifiersData(node);
        if(modifiersData){
            varelements=modifiersData.elementsByRecord[recordID];
            varindex=_.findIndex(elements,function(oldElement){
                returnoldElement.widget===element
                    ||oldElement.$el[0]===element[0];
            });
            if(index>=0){
                elements.splice(index,1);
            }
        }
    },
    /**
     *Doestwoactions,foreachregisteredmodifiers:
     *1)Recomputesthemodifiersassociatedtothegivenrecordandsavesthem
     *   (asbooleanvalues)intheappropriatemodifiersdata.
     *2)Updatestherenderingoftheviewelementsassociatedtothegiven
     *   recordtomatchthenewmodifiers.
     *
     *@see_applyModifiers
     *
     *@private
     *@param{Object}record
     *@returns{Promise}resolvedoncefinished
     */
    _updateAllModifiers:function(record){
        varself=this;

        vardefs=[];
        this.defs=defs;//Potentiallyfilledbywidgetrerendering
        _.each(this.allModifiersData,function(modifiersData){
            //`allModifiersData`mightcontainmodifiersregisteredforother
            //recordsthanthegivenrecord(e.g.<groupby>inlist)
            if(record.idinmodifiersData.evaluatedModifiers){
                modifiersData.evaluatedModifiers[record.id]=record.evalModifiers(modifiersData.modifiers);
                self._applyModifiers(modifiersData,record);
            }
        });
        deletethis.defs;

        returnPromise.all(defs);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *WhensomeonepressestheTAB/UP/DOWN/...keyinawidget,itisniceto
     *beabletonavigateintheview(defaultbrowserbehaviorsaredisabled
     *byFlectra).
     *
     *@abstract
     *@private
     *@param{FlectraEvent}ev
     */
    _onNavigationMove:function(ev){},
});

returnBasicRenderer;
});
