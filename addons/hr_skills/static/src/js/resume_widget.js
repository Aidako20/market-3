flectra.define('web.FieldResume',function(require){
"usestrict";

vartime=require('web.time');
varFieldOne2Many=require('web.relational_fields').FieldOne2Many;
varFieldProgressBar=require('web.basic_fields').FieldProgressBar;
varListRenderer=require('web.ListRenderer');
varfield_registry=require('web.field_registry');

varcore=require('web.core');
varqweb=core.qweb;
var_t=core._t;

varAbstractGroupedOne2ManyRenderer=ListRenderer.extend({
    /**
     *Thisabstractrendererisusetorenderaone2manyfieldinaformview.
     *Therecordsintheone2manyfieldaredisplayedgroupedbyaspecificfield.
     *
     *Aconcreterenderercan/shouldset:
     * -groupBy:fieldtogrouprecords
     * -dataRowTemplate:templatetorenderarecord'sdata
     * -groupTitleTemplate(optional):templatetorendertheheaderrowofagroup
     * -addLineButtonTemplate(optional):templatetorenderthe'Addaline'buttonattheendofeachgroup(editmodeonly)
     **/

    groupBy:'',//Field:recordsaregroupedbasedonthisfield
    groupTitleTemplate:'hr_default_group_row',//Templateusedtorenderthetitlerowofagroup
    dataRowTemplate:'',   //Templateusedtorenderarecord
    addLineButtonTemplate:'group_add_item',

    /**
     *Don'tfreezethecolumnsbecauseastheheaderisempty,thealgorithm
     *won'twork.
     *
     *@override
     *@private
     */
    _freezeColumnWidths:function(){},

     /**
     *Rendersaemptyheader
     *
     *@override
     *@private
     */
    _renderHeader:function(){
        return$('<thead/>');
    },

     /**
     *Rendersaemptyfooter
     *
     *@override
     *@private
     */
    _renderFooter:function(){
        return$('<tfoot/>');
    },

    /**
     *@override
     *@private
     */
    _renderGroupRow:function(display_name){
        returnqweb.render(this.groupTitleTemplate,{display_name:display_name});
    },

    /**
     *Thismethodismeanttobeoverritenbyconcreterenderersand
     *iscalledeachtimearowisrendered.
     *Itisahooktoformatrecord'sdatabeforeit'sgiventotheqwebtemplate.
     *
     *@private
    */
    _formatData:function(data){
        returndata;
    },

    _renderRow:function(record,isLast){
        return$(qweb.render(this.dataRowTemplate,{
            id:record.id,
            data:this._formatData(record.data),
            is_last:isLast,
        }));
    },

    /**
     *Thismethodismeanttobeoverriddenbyconcreterenderers.
     *Returnsacontextusedforthe'Addaline'button.
     *It'susefultosetdefaultvalues.
     *An'Addaline'buttonisaddedaftereachgroupofrecords.
     *Thegrouppassedasparametersallowtosetadifferentcontextbasedonthegroup.
     *Ifnorecordsexist,groupisundefined.
     *
     *@private
    */
    _getCreateLineContext:function(group){
        return{};
    },

    _renderTrashIcon:function(){
        returnqweb.render('hr_trash_button');
    },

    _renderAddItemButton:function(group){
        returnqweb.render(this.addLineButtonTemplate,{
            context:JSON.stringify(this._getCreateLineContext(group)),
        });
    },

    _renderBody:function(){
        varself=this;

        vargrouped_by=_.groupBy(this.state.data,function(record){
            returnrecord.data[self.groupBy].res_id;
        });

        vargroupTitle;
        var$body=$('<tbody>');
        for(varkeyingrouped_by){
            vargroup=grouped_by[key];
            if(key==='undefined'){
                groupTitle=_t("Other");
            }else{
                groupTitle=group[0].data[self.groupBy].data.display_name;
            }
            var$title_row=$(self._renderGroupRow(groupTitle));
            $body.append($title_row);

            //Rendereachrows
            group.forEach(function(record,index){
                varisLast=(index+1===group.length);
                var$row=self._renderRow(record,isLast);
                if(self.addTrashIcon)$row.append(self._renderTrashIcon());
                $body.append($row);
            });

            if(self.addCreateLine){
                $title_row.find('.o_group_name').append(self._renderAddItemButton(group));
            }
        }

        if($body.is(':empty')&&self.addCreateLine){
            $body.append(this._renderAddItemButton());
        }
        return$body;
    },

});

varResumeLineRenderer=AbstractGroupedOne2ManyRenderer.extend({

    groupBy:'line_type_id',
    groupTitleTemplate:'hr_resume_group_row',
    dataRowTemplate:'hr_resume_data_row',

    _formatData:function(data){
        vardateFormat=time.getLangDateFormat();
        vardate_start=data.date_start&&data.date_start.format(dateFormat)||"";
        vardate_end=data.date_end&&data.date_end.format(dateFormat)||_t("Current");
        return_.extend(data,{
            date_start:date_start,
            date_end:date_end,
        });
    },

    _getCreateLineContext:function(group){
        varctx=this._super(group);
        returngroup?_.extend({default_line_type_id:group[0].data[this.groupBy]&&group[0].data[this.groupBy].data.id||""},ctx):ctx;
    },

    _render:function(){
        varself=this;
        returnthis._super().then(function(){
            self.$el.find('table').removeClass('table-stripedo_list_table_ungrouped');
            self.$el.find('table').addClass('o_resume_tabletable-borderless');
        });
    },
});


varSkillsRenderer=AbstractGroupedOne2ManyRenderer.extend({

    groupBy:'skill_type_id',
    dataRowTemplate:'hr_skill_data_row',

    _renderRow:function(record){
        var$row=this._super(record);
        //Addprogressbarwidgetattheendofrows
        var$td=$('<td/>',{class:'o_data_cello_skill_cell'});
        varprogress=newFieldProgressBar(this,'level_progress',record,{
            current_value:record.data.level_progress,
            attrs:this.arch.attrs,
        });
        progress.appendTo($td);
        return$row.append($td);
    },

    _getCreateLineContext:function(group){
        varctx=this._super(group);
        returngroup?_.extend({default_skill_type_id:group[0].data[this.groupBy].data.id},ctx):ctx;
    },

    _render:function(){
        varself=this;
        returnthis._super().then(function(){
            self.$el.find('table').toggleClass('table-striped');
        });
    },
});


varFieldResume=FieldOne2Many.extend({

    /**
     *@override
     *@private
     */
    _getRenderer:function(){
        returnResumeLineRenderer;
    },
});

varFieldSkills=FieldOne2Many.extend({

    /**
     *@override
     *@private
     */
    _getRenderer:function(){
        returnSkillsRenderer;
    },
});

field_registry.add('hr_resume',FieldResume);
field_registry.add('hr_skills',FieldSkills);

returnFieldResume;

});
