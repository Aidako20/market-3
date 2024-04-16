flectra.define('calendar.CalendarController',function(require){
    "usestrict";

    constController=require('web.CalendarController');
    constDialog=require('web.Dialog');
    const{qweb,_t}=require('web.core');

    constCalendarController=Controller.extend({

        _askRecurrenceUpdatePolicy(){
            returnnewPromise((resolve,reject)=>{
                newDialog(this,{
                    title:_t('EditRecurrentevent'),
                    size:'small',
                    $content:$(qweb.render('calendar.RecurrentEventUpdate')),
                    buttons:[{
                        text:_t('Confirm'),
                        classes:'btn-primary',
                        close:true,
                        click:function(){
                            resolve(this.$('input:checked').val());
                        },
                    }],
                }).open();
            });
        },

        //TODOfactorizeduplicatedcode
        /**
         *@override
         *@private
         *@param{FlectraEvent}event
         */
        async_onDropRecord(event){
            const_super=this._super;//referencetothis._superislostafterasynccall
            if(event.data.record.recurrency){
                constrecurrenceUpdate=awaitthis._askRecurrenceUpdatePolicy();
                event.data=_.extend({},event.data,{
                    'recurrenceUpdate':recurrenceUpdate,
                });
            }
            _super.apply(this,arguments);
        },

        /**
         *@override
         *@private
         *@param{FlectraEvent}event
         */
        async_onUpdateRecord(event){
            const_super=this._super; //referencetothis._superislostafterasynccall
            if(event.data.record.recurrency){
                constrecurrenceUpdate=awaitthis._askRecurrenceUpdatePolicy();
                event.data=_.extend({},event.data,{
                    'recurrenceUpdate':recurrenceUpdate,
                });
            }
            _super.apply(this,arguments);
        },

    });

    returnCalendarController;

});
