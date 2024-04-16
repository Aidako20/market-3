flectra.define('website_event.website_event',function(require){

varajax=require('web.ajax');
varcore=require('web.core');
varWidget=require('web.Widget');
varpublicWidget=require('web.public.widget');

var_t=core._t;

//Catchregistrationformevent,becauseofJSforattendeedetails
varEventRegistrationForm=Widget.extend({

    /**
     *@override
     */
    start:function(){
        varself=this;
        varres=this._super.apply(this.arguments).then(function(){
            $('#registration_form.a-submit')
                .off('click')
                .click(function(ev){
                    self.on_click(ev);
                })
                .prop('disabled',false);
        });
        returnres;
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{Event}ev
     */
    on_click:function(ev){
        ev.preventDefault();
        ev.stopPropagation();
        var$form=$(ev.currentTarget).closest('form');
        var$button=$(ev.currentTarget).closest('[type="submit"]');
        varpost={};
        $('#registration_formtable').siblings('.alert').remove();
        $('#registration_formselect').each(function(){
            post[$(this).attr('name')]=$(this).val();
        });
        vartickets_ordered=_.some(_.map(post,function(value,key){returnparseInt(value);}));
        if(!tickets_ordered){
            $('<divclass="alertalert-info"/>')
                .text(_t('Pleaseselectatleastoneticket.'))
                .insertAfter('#registration_formtable');
            returnnewPromise(function(){});
        }else{
            $button.attr('disabled',true);
            returnajax.jsonRpc($form.attr('action'),'call',post).then(function(modal){
                var$modal=$(modal);
                $modal.modal({backdrop:'static',keyboard:false});
                $modal.find('.modal-body>div').removeClass('container');//retrocompatibility-REMOVEMEinmaster/saas-19
                $modal.appendTo('body').modal();
                $modal.on('click','.js_goto_event',function(){
                    $modal.modal('hide');
                    $button.prop('disabled',false);
                });
                $modal.on('click','.close',function(){
                    $button.prop('disabled',false);
                });
            });
        }
    },
});

publicWidget.registry.EventRegistrationFormInstance=publicWidget.Widget.extend({
    selector:'#registration_form',

    /**
     *@override
     */
    start:function(){
        vardef=this._super.apply(this,arguments);
        this.instance=newEventRegistrationForm(this);
        returnPromise.all([def,this.instance.attachTo(this.$el)]);
    },
    /**
     *@override
     */
    destroy:function(){
        this.instance.setElement(null);
        this._super.apply(this,arguments);
        this.instance.setElement(this.$el);
    },
});

returnEventRegistrationForm;
});
