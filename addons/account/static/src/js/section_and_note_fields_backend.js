
flectra.define('account.section_and_note_backend',function(require){
//ThegoalofthisfileistocontainJShacksrelatedtoallowing
//sectionandnoteonsaleorderandinvoice.

//[UPDATED]nowalsoallowsconfiguringproductsonsaleorder.

"usestrict";
varFieldChar=require('web.basic_fields').FieldChar;
varFieldOne2Many=require('web.relational_fields').FieldOne2Many;
varfieldRegistry=require('web.field_registry');
varListFieldText=require('web.basic_fields').ListFieldText;
varListRenderer=require('web.ListRenderer');

varSectionAndNoteListRenderer=ListRenderer.extend({
    /**
     *Wewantsectionandnotetotakethewholeline(excepthandleandtrash)
     *tolookbetterandtohidetheunnecessaryfields.
     *
     *@override
     */
    _renderBodyCell:function(record,node,index,options){
        var$cell=this._super.apply(this,arguments);

        varisSection=record.data.display_type==='line_section';
        varisNote=record.data.display_type==='line_note';

        if(isSection||isNote){
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
                $cell.removeClass('o_invisible_modifier');
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
     *Wewanttoadd.o_section_and_note_list_viewonthetabletohavestrongerCSS.
     *
     *@override
     *@private
     */
    _renderView:function(){
        varself=this;
        returnthis._super.apply(this,arguments).then(function(){
            self.$('.o_list_table').addClass('o_section_and_note_list_view');
        });
    }
});

//Wecreateacustomwidgetbecausethisisthecleanestwaytodoit:
//tobesurethiscustomcodewillonlyimpactselectedfieldshavingthewidget
//andnotappliedtoanyotherexistingListRenderer.
varSectionAndNoteFieldOne2Many=FieldOne2Many.extend({
    /**
     *Wewanttouseourcustomrendererforthelist.
     *
     *@override
     */
    _getRenderer:function(){
        if(this.view.arch.tag==='tree'){
            returnSectionAndNoteListRenderer;
        }
        returnthis._super.apply(this,arguments);
    },
});

//ThisisamergebetweenaFieldTextandaFieldChar.
//WewantaFieldCharforsection,
//andaFieldTextfortherest(productandnote).
varSectionAndNoteFieldText=function(parent,name,record,options){
    varisSection=record.data.display_type==='line_section';
    varConstructor=isSection?FieldChar:ListFieldText;
    returnnewConstructor(parent,name,record,options);
};

fieldRegistry.add('section_and_note_one2many',SectionAndNoteFieldOne2Many);
fieldRegistry.add('section_and_note_text',SectionAndNoteFieldText);

returnSectionAndNoteListRenderer;
});
