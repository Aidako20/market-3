flectra.define('event.EventConfiguratorFormView',function(require){
"usestrict";

varEventConfiguratorFormController=require('event.EventConfiguratorFormController');
varFormView=require('web.FormView');
varviewRegistry=require('web.view_registry');

/**
 *@seeEventConfiguratorFormControllerformoreinformation
 */
varEventConfiguratorFormView=FormView.extend({
    config:_.extend({},FormView.prototype.config,{
        Controller:EventConfiguratorFormController
    }),
});

viewRegistry.add('event_configurator_form',EventConfiguratorFormView);

returnEventConfiguratorFormView;

});
