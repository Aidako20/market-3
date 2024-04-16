
flectra.define('resource.section_backend',function(require){
//ThegoalofthisfileistocontainJShacksrelatedtoallowing
//sectiononresourcecalendar.

"usestrict";
varFieldOne2Many=require('web.relational_fields').FieldOne2Many;
varfieldRegistry=require('web.field_registry');
varListRenderer=require('web.ListRenderer');

varSectionListRenderer=ListRenderer.extend({
    /**
     *Wewantsectiontotakethewholeline(excepthandleandtrash)
     *tolookbetterandtohidetheunnecessaryfields.
     *
     *@override
     */
    _renderBodyCell:function(record,node,index,options){
        var$cell=this._super.apply(this,arguments);

        varisSection=record.data.display_type==='line_section';

        if(isSection){
            if(node.attrs.widget==="handle"){
                return$cell;
            }elseif(node.attrs.name==="name"){
                varnbrColumns=this._getNumberOfCols();
                if(this.handleField){
                    nbrColumns--;
                }
                if(this.addTrashIcon){
                    nbrColumns--;
                }
                $cell.attr('colspan',nbrColumns);
            }else{
                return$cell.addClass('o_hidden');
            }
        }

        return$cell;
    },
    /**
     *Weaddtheo_is_{display_type}classtoallowcustombehaviourbothinJSandCSS.
     *
     *@override
     */
    _renderRow:function(record,index){
        var$row=this._super.apply(this,arguments);

        if(record.data.display_type){
            $row.addClass('o_is_'+record.data.display_type);
        }

        return$row;
    },
    /**
     *Wewanttoadd.o_section_list_viewonthetabletohavestrongerCSS.
     *
     *@override
     *@private
     */
    _renderView:function(){
        varself=this;
        returnthis._super.apply(this,arguments).then(function(){
            self.$('.o_list_table').addClass('o_section_list_view');
        });
    },
});

//Wecreateacustomwidgetbecausethisisthecleanestwaytodoit:
//tobesurethiscustomcodewillonlyimpactselectedfieldshavingthewidget
//andnotappliedtoanyotherexistingListRenderer.
varSectionFieldOne2Many=FieldOne2Many.extend({
    /**
     *Wewanttouseourcustomrendererforthelist.
     *
     *@override
     */
    _getRenderer:function(){
        if(this.view.arch.tag==='tree'){
            returnSectionListRenderer;
        }
        returnthis._super.apply(this,arguments);
    },
});

fieldRegistry.add('section_one2many',SectionFieldOne2Many);

});
