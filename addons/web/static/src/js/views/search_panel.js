flectra.define("web/static/src/js/views/search_panel.js",function(require){
    "usestrict";

    const{Model,useModel}=require("web/static/src/js/model.js");
    constpatchMixin=require("web.patchMixin");

    const{Component,hooks}=owl;
    const{useState,useSubEnv}=hooks;

    /**
     *Searchpanel
     *
     *Representanextensionofthesearchinterfacelocatedontheleftsideof
     *theview.Itisdividedinsectionsdefinedina"<searchpanel>"nodelocated
     *insideofa"<search>"arch.Eachsectionisrepresentedbyalistofdifferent
     *values(categoriesorungroupedfilters)orgroupsofvalues(groupedfilters).
     *Itsstateisdirectlyaffectedbyitsmodel(@seeSearchPanelModelExtension).
     *@extendsComponent
     */
    classSearchPanelextendsComponent{
        constructor(){
            super(...arguments);

            useSubEnv({searchModel:this.props.searchModel});

            this.state=useState({
                active:{},
                expanded:{},
            });
            this.model=useModel("searchModel");
            this.scrollTop=0;
            this.hasImportedState=false;

            this.importState(this.props.importedState);
        }

        asyncwillStart(){
            this._expandDefaultValue();
            this._updateActiveValues();
        }

        mounted(){
            this._updateGroupHeadersChecked();
            if(this.hasImportedState){
                this.el.scroll({top:this.scrollTop});
            }
        }

        asyncwillUpdateProps(){
            this._updateActiveValues();
        }

        //---------------------------------------------------------------------
        //Public
        //---------------------------------------------------------------------

        exportState(){
            constexported={
                expanded:this.state.expanded,
                scrollTop:this.el.scrollTop,
            };
            returnJSON.stringify(exported);
        }

        importState(stringifiedState){
            this.hasImportedState=Boolean(stringifiedState);
            if(this.hasImportedState){
                conststate=JSON.parse(stringifiedState);
                this.state.expanded=state.expanded;
                this.scrollTop=state.scrollTop;
            }
        }

        //---------------------------------------------------------------------
        //Private
        //---------------------------------------------------------------------

        /**
         *Expandscategoryvaluesholdingthedefaultvalueofacategory.
         *@private
         */
        _expandDefaultValue(){
            if(this.hasImportedState){
                return;
            }
            constcategories=this.model.get("sections",s=>s.type==="category");
            for(constcategoryofcategories){
                this.state.expanded[category.id]={};
                if(category.activeValueId){
                    constancestorIds=this._getAncestorValueIds(category,category.activeValueId);
                    for(constancestorIdofancestorIds){
                        this.state.expanded[category.id][ancestorId]=true;
                    }
                }
            }
        }

        /**
         *@private
         *@param{Object}category
         *@param{number}categoryValueId
         *@returns{number[]}listofidsoftheancestorsofthegivenvaluein
         *  thegivencategory.
         */
        _getAncestorValueIds(category,categoryValueId){
            const{parentId}=category.values.get(categoryValueId);
            returnparentId?[...this._getAncestorValueIds(category,parentId),parentId]:[];
        }

        /**
         *Preventunnecessarycallstothemodelbyensuringadifferentcategory
         *isclicked.
         *@private
         *@param{Object}category
         *@param{Object}value
         */
        async_toggleCategory(category,value){
            if(value.childrenIds.length){
                constcategoryState=this.state.expanded[category.id];
                if(categoryState[value.id]&&category.activeValueId===value.id){
                    deletecategoryState[value.id];
                }else{
                    categoryState[value.id]=true;
                }
            }
            if(category.activeValueId!==value.id){
                this.state.active[category.id]=value.id;
                this.model.dispatch("toggleCategoryValue",category.id,value.id);
            }
        }

        /**
         *@private
         *@param{number}filterId
         *@param{{values:Map<Object>}}group
         */
        _toggleFilterGroup(filterId,{values}){
            constvalueIds=[];
            constchecked=[...values.values()].every(
                (value)=>this.state.active[filterId][value.id]
            );
            values.forEach(({id})=>{
                valueIds.push(id);
                this.state.active[filterId][id]=!checked;
            });
            this.model.dispatch("toggleFilterValues",filterId,valueIds,!checked);
        }

        /**
         *@private
         *@param{number}filterId
         *@param{Object}[group]
         *@param{number}valueId
         *@param{MouseEvent}ev
         */
        _toggleFilterValue(filterId,valueId,{currentTarget}){
            this.state.active[filterId][valueId]=currentTarget.checked;
            this._updateGroupHeadersChecked();
            this.model.dispatch("toggleFilterValues",filterId,[valueId]);
        }

        _updateActiveValues(){
            for(constsectionofthis.model.get("sections")){
                if(section.type==="category"){
                    this.state.active[section.id]=section.activeValueId;
                }else{
                    this.state.active[section.id]={};
                    if(section.groups){
                        for(constgroupofsection.groups.values()){
                            for(constvalueofgroup.values.values()){
                                this.state.active[section.id][value.id]=value.checked;
                            }
                        }
                    }
                    if(section&&section.values){
                        for(constvalueofsection.values.values()){
                            this.state.active[section.id][value.id]=value.checked;
                        }
                    }
                }
            }
        }

        /**
         *Updatesthe"checked"or"indeterminate"stateofeachofthegroup
         *headersaccordingtothestateoftheirvalues.
         *@private
         */
        _updateGroupHeadersChecked(){
            constgroups=this.el.querySelectorAll(":scope.o_search_panel_filter_group");
            for(constgroupofgroups){
                constheader=group.querySelector(":scope.o_search_panel_group_headerinput");
                constvals=[...group.querySelectorAll(":scope.o_search_panel_filter_valueinput")];
                header.checked=false;
                header.indeterminate=false;
                if(vals.every((v)=>v.checked)){
                    header.checked=true;
                }elseif(vals.some((v)=>v.checked)){
                    header.indeterminate=true;
                }
            }
        }
    }
    SearchPanel.modelExtension="SearchPanel";

    SearchPanel.props={
        className:{type:String,optional:1},
        importedState:{type:String,optional:1},
        searchModel:Model,
    };
    SearchPanel.template="web.SearchPanel";

    returnpatchMixin(SearchPanel);
});
