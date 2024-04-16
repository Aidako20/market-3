flectra.define('web.PivotController',function(require){
    "usestrict";
    /**
     *FlectraPivotTableController
     *
     *ThisclassistheControllerforthepivottableview. Ithastocoordinate
     *theactionscomingfromthesearchview(throughtheupdatemethod),from
     *therenderer,fromthemodel,andfromthecontrolpanel.
     *
     *Itcandisplayactionbuttonsinthecontrolpanel,toselectadifferent
     *measure,ortoperformsomeotheractionssuchasdownload/expand/flipthe
     *view.
     */

    constAbstractController=require('web.AbstractController');
    constcore=require('web.core');
    constframework=require('web.framework');
    constsession=require('web.session');

    const_t=core._t;
    constQWeb=core.qweb;

    constPivotController=AbstractController.extend({
        custom_events:Object.assign({},AbstractController.prototype.custom_events,{
            closed_header_click:'_onClosedHeaderClicked',
            open_view:'_onOpenView',
            opened_header_click:'_onOpenedHeaderClicked',
            sort_rows:'_onSortRows',
            groupby_menu_selection:'_onGroupByMenuSelection',
        }),

        /**
         *@override
         *@paramparent
         *@parammodel
         *@paramrenderer
         *@param{Object}params
         *@param{Object}params.groupableFieldsamapfromfieldnamestofield
         *  props
         */
        init:function(parent,model,renderer,params){
            this._super(...arguments);

            this.disableLinking=params.disableLinking;
            this.measures=params.measures;
            this.title=params.title;
            //viewstouseintheactiontriggeredwhenadatacellisclicked
            this.views=params.views;
            this.groupSelected=null;
        },
        /**
         *@override
         */
        destroy:function(){
            if(this.$buttons){
                //removejquery'stooltip()handlers
                this.$buttons.find('button').off();
            }
            returnthis._super(...arguments);
        },

        //--------------------------------------------------------------------------
        //Public
        //--------------------------------------------------------------------------

        /**
         *Returnsthecurrentmeasuresandgroupbys,sowecanrestoretheview
         *whenwesavethecurrentstateinthesearchview,orwhenweadditto
         *thedashboard.
         *
         *@overridemethodfromAbstractController
         *@returns{Object}
         */
        getOwnedQueryParams:function(){
            conststate=this.model.get({raw:true});
            return{
                context:{
                    pivot_measures:state.measures,
                    pivot_column_groupby:state.colGroupBys,
                    pivot_row_groupby:state.rowGroupBys,
                }
            };
        },
        /**
         *RenderthebuttonsaccordingtothePivotView.buttonstemplateand
         *addlistenersonit.
         *Setthis.$buttonswiththeproducedjQueryelement
         *
         *@override
         *@param{jQuery}[$node]ajQuerynodewheretherenderedbuttonsshould
         *  beinserted.$nodemaybeundefined,inwhichcasethePivotView
         *  doesnothing
         */
        renderButtons:function($node){
            constcontext=this._getRenderButtonContext();
            this.$buttons=$(QWeb.render('PivotView.buttons',context));
            this.$buttons.click(this._onButtonClick.bind(this));
            this.$buttons.find('button').tooltip();
            if($node){
                this.$buttons.appendTo($node);
            }
        },
        /**
         *@override
         */
        updateButtons:function(){
            if(!this.$buttons){
                return;
            }
            conststate=this.model.get({raw:true});
            Object.entries(this.measures).forEach(elt=>{
                constname=elt[0];
                constisSelected=state.measures.includes(name);
                this.$buttons.find('.dropdown-item[data-field="'+name+'"]')
                    .toggleClass('selected',isSelected);

            });
            constnoDataDisplayed=!state.hasData||!state.measures.length;
            this.$buttons.find('.o_pivot_flip_button').prop('disabled',noDataDisplayed);
            this.$buttons.find('.o_pivot_expand_button').prop('disabled',noDataDisplayed);
            this.$buttons.find('.o_pivot_download').prop('disabled',noDataDisplayed);
        },

        //--------------------------------------------------------------------------
        //Private
        //--------------------------------------------------------------------------

        /**
         *Exportthecurrentpivottabledatainaxlsfile.Forthis,wehaveto
         *serializethecurrentstate,thencalltheserver/web/pivot/export_xlsx.
         *Forceareloadbeforeexportingtoensuretoexportup-to-datedata.
         *
         *@private
         */
        _downloadTable:function(){
            if(this.model.getTableWidth()>16384){
                this.call('crash_manager','show_message',_t("ForExcelcompatibility,datacannotbeexportediftherearemorethan16384columns.\n\nTip:trytoflipaxis,filterfurtherorreducethenumberofmeasures."));
                framework.unblockUI();
                return;
            }
            consttable=this.model.exportData();
            table.title=this.title;
            session.get_file({
                url:'/web/pivot/export_xlsx',
                data:{data:JSON.stringify(table)},
                complete:framework.unblockUI,
                error:(error)=>this.call('crash_manager','rpc_error',error),
            });
        },

        //--------------------------------------------------------------------------
        //Handlers
        //--------------------------------------------------------------------------

        /**
         *Thishandleriscalledwhentheuserclickedonabuttoninthecontrol
         *panel. Wethenhavetoreactproperly:itcaneitherbeachangeinthe
         *currentmeasures,orarequesttoflip/expand/downloaddata.
         *
         *@private
         *@param{MouseEvent}ev
         */
        _onButtonClick:asyncfunction(ev){
            const$target=$(ev.target);
            if($target.hasClass('o_pivot_flip_button')){
                this.model.flip();
                this.update({},{reload:false});
            }
            if($target.hasClass('o_pivot_expand_button')){
                awaitthis.model.expandAll();
                this.update({},{reload:false});
            }
            if(ev.target.closest('.o_pivot_measures_list')){
                ev.preventDefault();
                ev.stopPropagation();
                constfield=ev.target.dataset.field;
                if(field){
                    this.update({measure:field});
                }
            }
            if($target.hasClass('o_pivot_download')){
                this._downloadTable();
            }

            awaitthis._addIncludedButtons(ev);
        },

        /**
         *Declaredtobeoverwritteninincludesofpivotcontroller
         *
         *@param{MouseEvent}ev
         *@returns{Promise<void>}
         *@private
         */
        _addIncludedButtons:asyncfunction(ev){},
        /**
         *Getthecontextofrenderingofthebuttons
         *
         *@returns{Object}
         *@private
         */
        _getRenderButtonContext:function(){
            return{
                measures:Object.entries(this.measures)
                .filter(x=>x[0]!=='__count')
                .sort((a,b)=>a[1].string.toLowerCase()>b[1].string.toLowerCase()?1:-1),
            };
        },
        /**
         *
         *@private
         *@param{FlectraEvent}ev
         */
        _onCloseGroup:function(ev){
            this.model.closeGroup(ev.data.groupId,ev.data.type);
            this.update({},{reload:false});
        },
        /**
         *@param{CustomEvent}ev
         *@private
         **/
        _onOpenedHeaderClicked:function(ev){
            this.model.closeGroup(ev.data.cell.groupId,ev.data.type);
            this.update({},{reload:false});
        },
        /**
         *@param{CustomEvent}ev
         *@private
         **/
        _onClosedHeaderClicked:asyncfunction(ev){
            constcell=ev.data.cell;
            constgroupId=cell.groupId;
            consttype=ev.data.type;

            constgroup={
                rowValues:groupId[0],
                colValues:groupId[1],
                type:type
            };

            conststate=this.model.get({raw:true});
            constgroupValues=type==='row'?groupId[0]:groupId[1];
            constgroupBys=type==='row'?
                state.rowGroupBys:
                state.colGroupBys;
            this.selectedGroup=group;
            if(groupValues.length<groupBys.length){
                constgroupBy=groupBys[groupValues.length];
                awaitthis.model.expandGroup(this.selectedGroup,groupBy);
                this.update({},{reload:false});
            }
        },
        /**
         *Thishandleriscalledwhentheuserselectsagroupbyinthedropdownmenu.
         *
         *@private
         *@param{CustomEvent}ev
         */
        _onGroupByMenuSelection:asyncfunction(ev){
            ev.stopPropagation();

            letgroupBy=ev.data.field.name;
            constinterval=ev.data.interval;
            if(interval){
                groupBy=groupBy+':'+interval;
            }
            this.model.addGroupBy(groupBy,this.selectedGroup.type);
            awaitthis.model.expandGroup(this.selectedGroup,groupBy);
            this.update({},{reload:false});
        },
        /**
         *@private
         *@param{CustomEvent}ev
         */
        _onOpenView:function(ev){
            ev.stopPropagation();
            constcell=ev.data;
            if(cell.value===undefined||this.disableLinking){
                return;
            }

            constcontext=Object.assign({},this.model.data.context);
            Object.keys(context).forEach(x=>{
                if(x==='group_by'||x.startsWith('search_default_')){
                    deletecontext[x];
                }
            });

            constgroup={
                rowValues:cell.groupId[0],
                colValues:cell.groupId[1],
                originIndex:cell.originIndexes[0]
            };

            constdomain=this.model._getGroupDomain(group);

            this.do_action({
                type:'ir.actions.act_window',
                name:this.title,
                res_model:this.modelName,
                views:this.views,
                view_mode:'list',
                target:'current',
                context:context,
                domain:domain,
            });
        },
        /**
         *@private
         *@param{CustomEvent}ev
         */
        _onSortRows:function(ev){
            this.model.sortRows({
                groupId:ev.data.groupId,
                measure:ev.data.measure,
                order:(ev.data.order||'desc')==='asc'?'desc':'asc',
                originIndexes:ev.data.originIndexes,
            });
            this.update({},{reload:false});
        },
    });

    returnPivotController;

});
