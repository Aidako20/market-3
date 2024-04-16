flectra.define('web.ControlPanel',function(require){
    "usestrict";

    constActionMenus=require('web.ActionMenus');
    constComparisonMenu=require('web.ComparisonMenu');
    constActionModel=require('web/static/src/js/views/action_model.js');
    constFavoriteMenu=require('web.FavoriteMenu');
    constFilterMenu=require('web.FilterMenu');
    constGroupByMenu=require('web.GroupByMenu');
    constpatchMixin=require('web.patchMixin');
    constPager=require('web.Pager');
    constSearchBar=require('web.SearchBar');
    const{useModel}=require('web/static/src/js/model.js');

    const{Component,hooks}=owl;
    const{useRef,useSubEnv}=hooks;

    /**
     *TODO:removethiswholemechanismassoonas`cp_content`iscompletelyremoved.
     *Extractthe'cp_content'keyofthegivenpropsandreturnthemaswellas
     *theextractedcontent.
     *@param{Object}props
     *@returns{Object}
     */
    functiongetAdditionalContent(props){
        constadditionalContent={};
        if('cp_content'inprops){
            constcontent=props.cp_content||{};
            if('$buttons'incontent){
                additionalContent.buttons=content.$buttons;
            }
            if('$searchview'incontent){
                additionalContent.searchView=content.$searchview;
            }
            if('$pager'incontent){
                additionalContent.pager=content.$pager;
            }
            if('$searchview_buttons'incontent){
                additionalContent.searchViewButtons=content.$searchview_buttons;
            }
        }
        returnadditionalContent;
    }

    /**
     *Controlpanel
     *
     *Thecontrolpaneloftheaction|view.Initsstandardform,itiscomposedof
     *severalsections/subcomponents.Hereisasimplifiedgraphrepresentingthe
     *action|viewanditscontrolpanel:
     *
     *┌ViewController|Action----------------------------------------------------------┐
     *|┌ControlPanel──────────────┬──────────────────────────────────────────────────┐|
     *|│┌Breadcrumbs────────────┐│┌SearchView─────────────────────────────────┐│|
     *|││[1]/[2]              │││[3][================4=================]││|
     *|│└─────────────────────────┘│└──────────────────────────────────────────────┘│|
     *|├─────────────────────────────┼──────────────────────────────────────────────────┤|
     *|│┌Buttons┐┌ActionMenus┐│┌SearchMenus─────┐┌Pager┐┌Viewswitcher┐│|
     *|││[5]    ││[6]        │││[7][8][9][10] ││[11] ││[12]         ││|
     *|│└─────────┘└─────────────┘│└───────────────────┘└───────┘└───────────────┘│|
     *|└─────────────────────────────┴──────────────────────────────────────────────────┘|
     *|┌ViewRenderer|Actioncontent────────────────────────────────────────────────┐|
     *|│                                                                               │|
     *|│ ...                                                                          │|
     *|│                                                                               │|
     *|│                                                                               │|
     *|│                                                                               │|
     *|└────────────────────────────────────────────────────────────────────────────────┘|
     *└------------------------------------------------------------------------------------┘
     *
     *1.Breadcrumbs:listoflinkscomposedbythe`props.breadcrumbs`collection.
     *2.Title:thetitleoftheaction|view.Canbeemptyandwillyield'Unnamed'.
     *3.Searchfacets:acollectionoffacetcomponentsgeneratedbythe`ControlPanelModel`
     *   andhandledbythe`SearchBar`component.@seeSearchFacet
     *4.SearchBar:@seeSearchBar
     *5.Buttons:sectioninwhichtheaction|controllerismeanttoinjectitscontrol
     *            buttons.Thetemplateprovidesaslotforthispurpose.
     *6.Actionmenus:@seeActionMenus
     *7.Filtermenu:@seeFilterMenu
     *8.Groupbymenu:@seeGroupByMenu
     *9.Comparisonmenu:@seeComparisonMenu
     *10.Favoritemenu:@seeFavoriteMenu
     *11.Pager:@seePager
     *12.Viewswitcherbuttons:listofbuttonscomposedbythe`props.views`collection.
     *
     *Subcomponents(especiallyinthe[SearchMenus]section)willcall
     *theControlPanelModeltogetprocessedinformationaboutthecurrentview|action.
     *@seeControlPanelModelformoredetails.
     *
     *Note:anadditionaltemporary(andugly)mechanicallowstoinjectajQueryelement
     *givenin`props.cp_content`inarelatedsection:
     *     $buttons->[Buttons]
     *     $searchview->[SearchView]
     *     $searchview_buttons->[SearchMenus]
     *     $pager->[Pager]
     *Thissystemmustbereplacedbyproperslotusageandthestatictemplate
     *inheritancemechanismwhenconvertingtheviews/actions.
     *@extendsComponent
     */
    classControlPanelextendsComponent{
        constructor(){
            super(...arguments);

            this.additionalContent=getAdditionalContent(this.props);

            useSubEnv({
                action:this.props.action,
                searchModel:this.props.searchModel,
                view:this.props.view,
            });

            //Connecttothemodel
            //TODO:movethisinenterprisewheneverpossible
            if(this.env.searchModel){
                this.model=useModel('searchModel');
            }

            //Referencehooks
            this.contentRefs={
                buttons:useRef('buttons'),
                pager:useRef('pager'),
                searchView:useRef('searchView'),
                searchViewButtons:useRef('searchViewButtons'),
            };

            this.fields=this._formatFields(this.props.fields);

            this.sprintf=_.str.sprintf;
        }

        mounted(){
            this._attachAdditionalContent();
        }

        patched(){
            this._attachAdditionalContent();
        }

        asyncwillUpdateProps(nextProps){
            //Note:actionandsearchModelarenotlikelytochangeduring
            //thelifespanofaControlPanelinstance,soweonlyneedtoupdate
            //theviewinformation.
            if('view'innextProps){
                this.env.view=nextProps.view;
            }
            if('fields'innextProps){
                this.fields=this._formatFields(nextProps.fields);
            }
            this.additionalContent=getAdditionalContent(nextProps);
        }

        //---------------------------------------------------------------------
        //Private
        //---------------------------------------------------------------------

        /**
         *Attachadditionalcontentextractedfromtheprops'cp_content'key,ifany.
         *@private
         */
        _attachAdditionalContent(){
            for(constkeyinthis.additionalContent){
                if(this.additionalContent[key]&&this.additionalContent[key].length){
                    consttarget=this.contentRefs[key].el;
                    if(target){
                        target.innerHTML="";
                        target.append(...this.additionalContent[key]);
                    }
                }
            }
        }

        /**
         *Give`name`and`description`keystothefieldsgiventothecontrol
         *panel.
         *@private
         *@param{Object}fields
         *@returns{Object}
         */
        _formatFields(fields){
            constformattedFields={};
            for(constfieldNameinfields){
                formattedFields[fieldName]=Object.assign({
                    description:fields[fieldName].string,
                    name:fieldName,
                },fields[fieldName]);
            }
            returnformattedFields;
        }
    }
    ControlPanel.modelExtension="ControlPanel";

    ControlPanel.components={
        SearchBar,
        ActionMenus,Pager,
        ComparisonMenu,FilterMenu,GroupByMenu,FavoriteMenu,
    };
    ControlPanel.defaultProps={
        breadcrumbs:[],
        fields:{},
        searchMenuTypes:[],
        views:[],
        withBreadcrumbs:true,
        withSearchBar:true,
    };
    ControlPanel.props={
        action:Object,
        breadcrumbs:Array,
        searchModel:ActionModel,
        cp_content:{type:Object,optional:1},
        fields:Object,
        pager:{validate:p=>typeofp==='object'||p===null,optional:1},
        searchMenuTypes:Array,
        actionMenus:{validate:s=>typeofs==='object'||s===null,optional:1},
        title:{type:String,optional:1},
        view:{type:Object,optional:1},
        views:Array,
        withBreadcrumbs:Boolean,
        withSearchBar:Boolean,
    };
    ControlPanel.template='web.ControlPanel';

    returnpatchMixin(ControlPanel);
});
