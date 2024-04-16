flectra.define('web.SearchBar',function(require){
    "usestrict";

    constDomain=require('web.Domain');
    constfield_utils=require('web.field_utils');
    const{useAutofocus}=require('web.custom_hooks');
    const{useModel}=require('web/static/src/js/model.js');

    constCHAR_FIELDS=['char','html','many2many','many2one','one2many','text'];
    const{Component,hooks}=owl;
    const{useExternalListener,useRef,useState}=hooks;

    letsourceId=0;

    /**
     *Searchbar
     *
     *Thiscomponenthastwomainroles:
     *1)Displaythecurrentsearchfacets
     *2)Createnewsearchfiltersusinganinputandanautocompletionvalues
     *   generator.
     *
     *Forthefirstbit,thecorelogiccanbefoundintheXMLtemplateofthis
     *component,searchfacetcomponentsorintheControlPanelModelitself.
     *
     *Theautocompletionmechanicworkswithtransientsubobjectscalled'sources'.
     *Sourcescontaintheinformationthatwillbeusedtogeneratenewsearchfacets.
     *Asourceisgeneratedeither:
     *a.Fromanundetermineduserinput:theuserwillgiveastringandselect
     *   afieldfromtheautocompletiondropdown>thiswillsearchtheselected
     *   fieldrecordswiththegivenpattern(withan'ilike'operator);
     *b.Fromagivenselection:whengivenaninputbytheuser,thesearchbar
     *   willpre-fetch'many2one'fieldrecordsmatchingtheinputvalueandfilter
     *   'select'fieldswiththesamevalue.Iftheuserclicksononeofthese
     *   fetched/filteredvalues,itwillgenerateamatchingsearchfacettargeting
     *   recordshavingthisexactvalue.
     *@extendsComponent
     */
    classSearchBarextendsComponent{
        constructor(){
            super(...arguments);

            this.focusOnUpdate=useAutofocus();
            this.inputRef=useRef('search-input');
            this.model=useModel('searchModel');
            this.state=useState({
                sources:[],
                focusedItem:0,
                inputValue:"",
            });

            this.autoCompleteSources=this.model.get('filters',f=>f.type==='field').map(
                filter=>this._createSource(filter)
            );
            this.noResultItem=[null,this.env._t("(noresult)")];

            useExternalListener(window,'click',this._onWindowClick);
            useExternalListener(window,'keydown',this._onWindowKeydown);
        }

        mounted(){
            //'search'willalwayspatchthesearchbar,'focus'willnever.
            this.env.searchModel.on('search',this,this.focusOnUpdate);
            this.env.searchModel.on('focus-control-panel',this,()=>{
                this.inputRef.el.focus();
            });
        }

        willUnmount(){
            this.env.searchModel.off('search',this);
            this.env.searchModel.off('focus-control-panel',this);
        }

        //---------------------------------------------------------------------
        //Private
        //---------------------------------------------------------------------

        /**
         *@private
         */
        _closeAutoComplete(){
            this.state.sources=[];
            this.state.focusedItem=0;
            this.state.inputValue="";
            this.inputRef.el.value="";
            this.focusOnUpdate();
        }

        /**
         *@private
         *@param{Object}filter
         *@returns{Object}
         */
        _createSource(filter){
            constfield=this.props.fields[filter.fieldName];
            consttype=field.type==="reference"?"char":field.type;
            constsource={
                active:true,
                description:filter.description,
                filterId:filter.id,
                filterOperator:filter.operator,
                id:sourceId++,
                operator:CHAR_FIELDS.includes(type)?'ilike':'=',
                parent:false,
                type,
            };
            switch(type){
                case'selection':{
                    source.active=false;
                    source.selection=field.selection||[];
                    break;
                }
                case'boolean':{
                    source.active=false;
                    source.selection=[
                        [true,this.env._t("Yes")],
                        [false,this.env._t("No")],
                    ];
                    break;
                }
                case'many2one':{
                    source.expand=true;
                    source.expanded=false;
                    source.context=field.context;
                    source.relation=field.relation;
                    if(filter.domain){
                        source.domain=filter.domain;
                    }
                }
            }
            returnsource;
        }

        /**
         *@private
         *@param{Object}source
         *@param{[any,string]}values
         *@param{boolean}[active=true]
         */
        _createSubSource(source,[value,label],active=true){
            constsubSource={
                active,
                filterId:source.filterId,
                filterOperator:source.filterOperator,
                id:sourceId++,
                label,
                operator:'=',
                parent:source,
                value,
            };
            returnsubSource;
        }

        /**
         *@private
         *@param{Object}source
         *@param{boolean}shouldExpand
         */
        async_expandSource(source,shouldExpand){
            source.expanded=shouldExpand;
            if(shouldExpand){
                letargs=source.domain;
                if(typeofargs==='string'){
                    try{
                        args=Domain.prototype.stringToArray(args);
                    }catch(err){
                        args=[];
                    }
                }
                constresults=awaitthis.rpc({
                    kwargs:{
                        args,
                        context:source.context,
                        limit:8,
                        name:this.state.inputValue.trim(),
                    },
                    method:'name_search',
                    model:source.relation,
                });
                constoptions=results.map(result=>this._createSubSource(source,result));
                constparentIndex=this.state.sources.indexOf(source);
                if(!options.length){
                    options.push(this._createSubSource(source,this.noResultItem,false));
                }
                this.state.sources.splice(parentIndex+1,0,...options);
            }else{
                this.state.sources=this.state.sources.filter(src=>src.parent!==source);
            }
        }

        /**
         *@private
         *@param{string}query
         */
        _filterSources(query){
            returnthis.autoCompleteSources.reduce(
                (sources,source)=>{
                    //Fieldselectionorboolean.
                    if(source.selection){
                        constoptions=[];
                        source.selection.forEach(result=>{
                            if(fuzzy.test(query,result[1].toLowerCase())){
                                options.push(this._createSubSource(source,result));
                            }
                        });
                        if(options.length){
                            sources.push(source,...options);
                        }
                    //Anyothertype.
                    }elseif(this._validateSource(query,source)){
                        sources.push(source);
                    }
                    //Foldanyexpandeditem.
                    if(source.expanded){
                        source.expanded=false;
                    }
                    returnsources;
                },
                []
            );
        }

        /**
         *Focusthesearchfacetatthedesignatedindexifany.
         *@private
         */
        _focusFacet(index){
            constfacets=this.el.getElementsByClassName('o_searchview_facet');
            if(facets.length){
                facets[index].focus();
            }
        }

        /**
         *TrytoparsethegivenrawValueaccordingtothetypeofthegiven
         *sourcefieldtype.Thereturnedformattedvalueistheonethatwill
         *supposedlybesenttotheserver.
         *@private
         *@param{string}rawValue
         *@param{Object}source
         *@returns{string}
         */
        _parseWithSource(rawValue,{type}){
            constparser=field_utils.parse[type];
            letparsedValue;
            switch(type){
                case'date':
                case'datetime':{
                    constparsedDate=parser(rawValue,{type},{timezone:true});
                    constdateFormat=type==='datetime'?'YYYY-MM-DDHH:mm:ss':'YYYY-MM-DD';
                    constmomentValue=moment(parsedDate,dateFormat);
                    if(!momentValue.isValid()){
                        thrownewError('Invaliddate');
                    }
                    parsedValue=parsedDate.toJSON();
                    break;
                }
                case'many2one':{
                    parsedValue=rawValue;
                    break;
                }
                default:{
                    parsedValue=parser(rawValue);
                }
            }
            returnparsedValue;
        }

        /**
         *@private
         *@param{Object}source
         */
        _selectSource(source){
            //Inactivesourcesare:
            //-Selectionsources
            //-"noresult"items
            if(source.active){
                constlabelValue=source.label||this.state.inputValue.trim();
                this.model.dispatch('addAutoCompletionValues',{
                    filterId:source.filterId,
                    value:"value"insource?source.value:this._parseWithSource(labelValue,source),
                    label:labelValue,
                    operator:source.filterOperator||source.operator,
                });
            }
            this._closeAutoComplete();
        }

        /**
         *@private
         *@param{string}query
         *@param{Object}source
         *@returns{boolean}
         */
        _validateSource(query,source){
            try{
                this._parseWithSource(query,source);
            }catch(err){
                returnfalse;
            }
            returntrue;
        }

        //---------------------------------------------------------------------
        //Handlers
        //---------------------------------------------------------------------

        /**
         *@private
         *@param{Object}facet
         *@param{number}facetIndex
         *@param{KeyboardEvent}ev
         */
        _onFacetKeydown(facet,facetIndex,ev){
            switch(ev.key){
                case'ArrowLeft':
                    if(facetIndex===0){
                        this.inputRef.el.focus();
                    }else{
                        this._focusFacet(facetIndex-1);
                    }
                    break;
                case'ArrowRight':
                    constfacets=this.el.getElementsByClassName('o_searchview_facet');
                    if(facetIndex===facets.length-1){
                        this.inputRef.el.focus();
                    }else{
                        this._focusFacet(facetIndex+1);
                    }
                    break;
                case'Backspace':
                    this._onFacetRemove(facet);
                    break;
            }
        }

        /**
         *@private
         *@param{Object}facet
         */
        _onFacetRemove(facet){
            this.model.dispatch('deactivateGroup',facet.groupId);
        }

        /**
         *@private
         *@param{KeyboardEvent}ev
         */
        _onSearchKeydown(ev){
            if(ev.isComposing){
                //ThiscasehappenswithanIMEforexample:weletithandleallkeyevents.
                return;
            }
            constcurrentItem=this.state.sources[this.state.focusedItem]||{};
            switch(ev.key){
                case'ArrowDown':
                    ev.preventDefault();
                    if(Object.keys(this.state.sources).length){
                        letnextIndex=this.state.focusedItem+1;
                        if(nextIndex>=this.state.sources.length){
                            nextIndex=0;
                        }
                        this.state.focusedItem=nextIndex;
                    }else{
                        this.env.bus.trigger('focus-view');
                    }
                    break;
                case'ArrowLeft':
                    if(currentItem.expanded){
                        //Priority1:foldexpandeditem.
                        ev.preventDefault();
                        this._expandSource(currentItem,false);
                    }elseif(currentItem.parent){
                        //Priority2:focusparentitem.
                        ev.preventDefault();
                        this.state.focusedItem=this.state.sources.indexOf(currentItem.parent);
                        //Priority3:Donothing(navigationinsidetext).
                    }elseif(ev.target.selectionStart===0){
                        //Priority4:navigatetorightmostfacet.
                        this._focusFacet(this.model.get("facets").length-1);
                    }
                    break;
                case'ArrowRight':
                    if(ev.target.selectionStart===this.state.inputValue.length){
                        //Priority1:Donothing(navigationinsidetext).
                        if(currentItem.expand){
                            //Priority2:gotofirstchildorexpanditem.
                            ev.preventDefault();
                            if(currentItem.expanded){
                                this.state.focusedItem++;
                            }else{
                                this._expandSource(currentItem,true);
                            }
                        }elseif(ev.target.selectionStart===this.state.inputValue.length){
                            //Priority3:navigatetoleftmostfacet.
                            this._focusFacet(0);
                        }
                    }
                    break;
                case'ArrowUp':
                    ev.preventDefault();
                    letpreviousIndex=this.state.focusedItem-1;
                    if(previousIndex<0){
                        previousIndex=this.state.sources.length-1;
                    }
                    this.state.focusedItem=previousIndex;
                    break;
                case'Backspace':
                    if(!this.state.inputValue.length){
                        constfacets=this.model.get("facets");
                        if(facets.length){
                            this._onFacetRemove(facets[facets.length-1]);
                        }
                    }
                    break;
                case'Enter':
                    if(!this.state.inputValue.length){
                        this.model.dispatch('search');
                        break;
                    }
                    /*fallsthrough*/
                case'Tab':
                    if(this.state.inputValue.length){
                        ev.preventDefault();//keepthefocusinsidethesearchbar
                        this._selectSource(currentItem);
                    }
                    break;
                case'Escape':
                    if(this.state.sources.length){
                        this._closeAutoComplete();
                    }
                    break;
            }
        }

        /**
         *@private
         *@param{InputEvent}ev
         */
        _onSearchInput(ev){
            this.state.inputValue=ev.target.value;
            constwasVisible=this.state.sources.length;
            constquery=this.state.inputValue.trim().toLowerCase();
            if(query.length){
                this.state.sources=this._filterSources(query);
            }elseif(wasVisible){
                this._closeAutoComplete();
            }
        }

        /**
         *Onlyhandlediftheuserhasmoveditscursoratleastonceafterthe
         *resultsareloadedanddisplayed.
         *@private
         *@param{number}resultIndex
         */
        _onSourceMousemove(resultIndex){
            this.state.focusedItem=resultIndex;
        }

        /**
         *@private
         *@param{MouseEvent}ev
         */
        _onWindowClick(ev){
            if(this.state.sources.length&&!this.el.contains(ev.target)){
                this._closeAutoComplete();
            }
        }

        /**
         *@private
         *@param{KeyboardEvent}ev
         */
        _onWindowKeydown(ev){
            if(ev.key==='Escape'&&this.state.sources.length){
                ev.preventDefault();
                ev.stopPropagation();
                this._closeAutoComplete();
            }
        }
    }

    SearchBar.defaultProps={
        fields:{},
    };
    SearchBar.props={
        fields:Object,
    };
    SearchBar.template='web.SearchBar';

    returnSearchBar;
});
