flectra.define('job.update_kanban',function(require){
    'usestrict';
    varKanbanRecord=require('web.KanbanRecord');

    KanbanRecord.include({
        /**
         *@override
         *@private
         */
        _openRecord:function(){
            if(this.modelName==='hr.job'&&this.$(".o_hr_job_boxesa").length){
                this.$(".o_hr_job_boxesa").first().click();
            }else{
                this._super.apply(this,arguments);
            }
        }
    });
});
