flectra.define('web.PivotRenderer',function(require){
    "usestrict";

    constOwlAbstractRenderer=require('web.AbstractRendererOwl');
    constfield_utils=require('web.field_utils');
    constpatchMixin=require('web.patchMixin');

    const{useExternalListener,useState,onMounted,onPatched}=owl.hooks;

    /**
     *HereisabasicexampleofthestructureofthePivotTable:
     *
     *┌─────────────────────────┬─────────────────────────────────────────────┬─────────────────┐
     *│                        │-web.PivotHeader                          │                │
     *│                        ├──────────────────────┬──────────────────────┤                │
     *│                        │+web.PivotHeader   │+web.PivotHeader   │                │
     *├─────────────────────────┼──────────────────────┼──────────────────────┼─────────────────┤
     *│                        │web.PivotMeasure    │web.PivotMeasure    │                │
     *├─────────────────────────┼──────────────────────┼──────────────────────┼─────────────────┤
     *│─web.PivotHeader      │                     │                     │                │
     *├─────────────────────────┼──────────────────────┼──────────────────────┼─────────────────┤
     *│   +web.PivotHeader   │                     │                     │                │
     *├─────────────────────────┼──────────────────────┼──────────────────────┼─────────────────┤
     *│   +web.PivotHeader   │                     │                     │                │
     *└─────────────────────────┴──────────────────────┴──────────────────────┴─────────────────┘
     *
     */

    classPivotRendererextendsOwlAbstractRenderer{
        /**
         *@override
         *@param{boolean}props.disableLinkingDisallowopeningrecordsbyclickingonacell
         *@param{Object}props.widgetsWidgetsdefinedinthearch
         */
        constructor(){
            super(...arguments);
            this.sampleDataTargets=['table'];
            this.state=useState({
                activeNodeHeader:{
                    groupId:false,
                    isXAxis:false,
                    click:false
                },
            });

            onMounted(()=>this._updateTooltip());

            onPatched(()=>this._updateTooltip());

            useExternalListener(window,'click',this._resetState);
        }

        //----------------------------------------------------------------------
        //Private
        //----------------------------------------------------------------------

        /**
         *Gettheformattedvalueofthecell
         *
         *@private
         *@param{Object}cell
         *@returns{string}Formattedvalue
         */
        _getFormattedValue(cell){
            consttype=this.props.widgets[cell.measure]||
                (this.props.fields[cell.measure].type==='many2one'?'integer':this.props.fields[cell.measure].type);
            constformatter=field_utils.format[type];
            returnformatter(cell.value,this.props.fields[cell.measure]);
        }

        /**
         *Gettheformattedvariationofacell
         *
         *@private
         *@param{Object}cell
         *@returns{string}Formattedvariation
         */
        _getFormattedVariation(cell){
            constvalue=cell.value;
            returnisNaN(value)?'-':field_utils.format.percentage(value,this.props.fields[cell.measure]);
        }

        /**
         *Retrievesthepaddingofaleftheader
         *
         *@private
         *@param{Object}cell
         *@returns{Number}Padding
         */
        _getPadding(cell){
            return5+cell.indent*30;
        }

        /**
         *Computeifacellisactive(withitsgroupId)
         *
         *@private
         *@param{Array}groupIdGroupIdofacell
         *@param{Boolean}isXAxistrueifthecellisonthexaxis
         *@returns{Boolean}trueifthecellisactive
         */
        _isClicked(groupId,isXAxis){
            return_.isEqual(groupId,this.state.activeNodeHeader.groupId)&&this.state.activeNodeHeader.isXAxis===isXAxis;
        }

        /**
         *Resetthestateofthenode.
         *
         *@private
         */
        _resetState(){
            //Thischeckisusedtoavoidthedestructionofthedropdown.
            //Theclickontheheaderbubblestowindowinordertohide
            //alltheotherdropdowns(inthiscomponentorothercomponents).
            //SoweneedisHeaderClickedtocancelthisbehaviour.
            if(this.isHeaderClicked){
                this.isHeaderClicked=false;
                return;
            }
            this.state.activeNodeHeader={
                groupId:false,
                isXAxis:false,
                click:false
            };
        }

        /**
         *Configurethetooltipsontheheaders.
         *
         *@private
         */
        _updateTooltip(){
            $(this.el).find('.o_pivot_header_cell_opened,.o_pivot_header_cell_closed').tooltip();
        }

        //----------------------------------------------------------------------
        //Handlers
        //----------------------------------------------------------------------


        /**
         *Handlesaclickonamenuiteminthedropdowntoselectagroupby.
         *
         *@private
         *@param{Object}field
         *@param{string}interval
         */
        _onClickMenuGroupBy(field,interval){
            this.trigger('groupby_menu_selection',{field,interval});
        }


        /**
         *Handlesaclickonaheadernode
         *
         *@private
         *@param{Object}cell
         *@param{string}typecolorrow
         */
        _onHeaderClick(cell,type){
            constgroupValues=cell.groupId[type==='col'?1:0];
            constgroupByLength=type==='col'?this.props.colGroupBys.length:this.props.rowGroupBys.length;
            if(cell.isLeaf&&groupValues.length>=groupByLength){
                this.isHeaderClicked=true;
                this.state.activeNodeHeader={
                    groupId:cell.groupId,
                    isXAxis:type==='col',
                    click:'leftClick'
                };
            }
            this.trigger(cell.isLeaf?'closed_header_click':'opened_header_click',{cell,type});
        }

        /**
         *Hoverthecolumninwhichthemouseis.
         *
         *@private
         *@param{MouseEvent}ev
         */
        _onMouseEnter(ev){
            varindex=[...ev.currentTarget.parentNode.children].indexOf(ev.currentTarget);
            if(ev.currentTarget.tagName==='TH'){
                index+=1;
            }
            this.el.querySelectorAll('td:nth-child('+(index+1)+')').forEach(elt=>elt.classList.add('o_cell_hover'));
        }

        /**
         *Removethehoveronthecolumns.
         *
         *@private
         */
        _onMouseLeave(){
            this.el.querySelectorAll('.o_cell_hover').forEach(elt=>elt.classList.remove('o_cell_hover'));
        }
    }

    PivotRenderer.template='web.PivotRenderer';

    returnpatchMixin(PivotRenderer);

});
