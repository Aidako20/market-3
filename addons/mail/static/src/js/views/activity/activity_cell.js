flectra.define("mail.ActivityCell",function(require){
    "usestrict";

    require("mail.Activity");
    constfield_registry=require('web.field_registry');

    constKanbanActivity=field_registry.get('kanban_activity');

    constActivityCell=KanbanActivity.extend({
        /**
         *@override
         *@private
         */
        _render(){
            //replaceclockbyclosestdeadline
            const$date=$('<divclass="o_closest_deadline">');
            constdate=moment(this.record.data.closest_deadline).toDate();
            //Toremoveyearonlyifcurrentyear
            if(moment().year()===moment(date).year()){
                $date.text(date.toLocaleDateString(moment().locale(),{
                    day:'numeric',month:'short'
                }));
            }else{
                $date.text(moment(date).format('ll'));
            }
            this.$('a').html($date);
            if(this.record.data.activity_ids.res_ids.length>1){
                this.$('a').append($('<span>',{
                    class:'badgebadge-lightbadge-pillborder-0'+this.record.data.activity_state,
                    text:this.record.data.activity_ids.res_ids.length,
                }));
            }
            if(this.$el.hasClass('show')){
                //note:thispartoftherenderingmightbeasynchronous
                this._renderDropdown();
            }
        }
    });

    returnActivityCell;

});
