flectra.define('website_event_track.website_event_track_reminder',function(require){
'usestrict';

varcore=require('web.core');
var_t=core._t;
varutils=require('web.utils');
varpublicWidget=require('web.public.widget');

publicWidget.registry.websiteEventTrackReminder=publicWidget.Widget.extend({
    selector:'.o_wetrack_js_reminder',
    events:{
        'click':'_onReminderToggleClick',
    },

    /**
     *@override
     */
    init:function(){
        this._super.apply(this,arguments);
        this._onReminderToggleClick=_.debounce(this._onReminderToggleClick,500,true);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //-------------------------------------------------------------------------

    /**
     *@private
     *@param{Event}ev
     */
    _onReminderToggleClick:function(ev){
        ev.stopPropagation();
        ev.preventDefault();
        varself=this;
        var$trackLink=$(ev.currentTarget).find('i');

        if(this.reminderOn===undefined){
            this.reminderOn=$trackLink.data('reminderOn');
        }

        varreminderOnValue=!this.reminderOn;

        this._rpc({
            route:'/event/track/toggle_reminder',
            params:{
                track_id:$trackLink.data('trackId'),
                set_reminder_on:reminderOnValue,
            },
        }).then(function(result){
            if(result.error&&result.error==='ignored'){
                self.displayNotification({
                    type:'info',
                    title:_t('Error'),
                    message:_.str.sprintf(_t('TalkalreadyinyourFavorites')),
                });
            }else{
                self.reminderOn=reminderOnValue;
                varreminderText=self.reminderOn?_t('FavoriteOn'):_t('SetFavorite');
                self.$('.o_wetrack_js_reminder_text').text(reminderText);
                self._updateDisplay();
                varmessage=self.reminderOn?_t('TalkaddedtoyourFavorites'):_t('TalkremovedfromyourFavorites');
                self.displayNotification({
                    type:'info',
                    title:message
                });
            }
            if(result.visitor_uuid){
                utils.set_cookie('visitor_uuid',result.visitor_uuid);
            }
        });
    },

    _updateDisplay:function(){
        var$trackLink=this.$el.find('i');
        varisReminderLight=$trackLink.data('isReminderLight');
        if(this.reminderOn){
            $trackLink.addClass('fa-bell').removeClass('fa-bell-o');
            $trackLink.attr('title',_t('FavoriteOn'));

            if(!isReminderLight){
                this.$el.addClass('btn-primary');
                this.$el.removeClass('btn-outline-primary');
            }
        }else{
            $trackLink.addClass('fa-bell-o').removeClass('fa-bell');
            $trackLink.attr('title',_t('SetFavorite'));

            if(!isReminderLight){
                this.$el.removeClass('btn-primary');
                this.$el.addClass('btn-outline-primary');
            }
        }
    },

});

returnpublicWidget.registry.websiteEventTrackReminder;

});
