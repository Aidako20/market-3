flectra.define('account.activity',function(require){
"usestrict";

varAbstractField=require('web.AbstractField');
varcore=require('web.core');
varfield_registry=require('web.field_registry');

varQWeb=core.qweb;
var_t=core._t;

varVatActivity=AbstractField.extend({
    className:'o_journal_activity_kanban',
    events:{
        'click.see_all_activities':'_onOpenAll',
        'click.see_activity':'_onOpenActivity',
    },
    init:function(){
        this.MAX_ACTIVITY_DISPLAY=5;
        this._super.apply(this,arguments);
    },
    //------------------------------------------------------------
    //Private
    //------------------------------------------------------------
    _render:function(){
        varself=this;
        varinfo=JSON.parse(this.value);
        if(!info){
            this.$el.html('');
            return;
        }
        info.more_activities=false;
        if(info.activities.length>this.MAX_ACTIVITY_DISPLAY){
            info.more_activities=true;
            info.activities=info.activities.slice(0,this.MAX_ACTIVITY_DISPLAY);
        }
        this.$el.html(QWeb.render('accountJournalDashboardActivity',info));
    },

    _onOpenActivity:function(e){
        e.preventDefault();
        varself=this;
        self.do_action({
            type:'ir.actions.act_window',
            name:_t('JournalEntry'),
            target:'current',
            res_id:$(e.target).data('resId'),
            res_model: 'account.move',
            views:[[false,'form']],
        });
    },

    _onOpenAll:function(e){
        e.preventDefault();
        varself=this;
        self.do_action({
            type:'ir.actions.act_window',
            name:_t('JournalEntries'),
            res_model: 'account.move',
            views:[[false,'kanban'],[false,'form']],
            search_view_id:[false],
            domain:[['journal_id','=',self.res_id],['activity_ids','!=',false]],
        });
    }
})

field_registry.add('kanban_vat_activity',VatActivity);

returnVatActivity;
});
