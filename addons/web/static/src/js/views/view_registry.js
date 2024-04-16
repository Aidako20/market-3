flectra.define('web.view_registry',function(require){
"usestrict";

/**
 *Thismoduledefinestheview_registry.Webviewsareaddedtotheregistry
 *inthe'web._view_registry'moduletoavoidcyclicdependencies.
 *Viewsdefinedinotheraddonsshouldbeaddedinthisregistryaswell,
 *ideallyinanothermodulethantheonedefiningtheview,inorderto
 *separatethedeclarativepartofamodule(theviewdefinition)fromits
 *'side-effects'part.
 */

varRegistry=require('web.Registry');

returnnewRegistry();

});

flectra.define('web._view_registry',function(require){
"usestrict";

/**
 *Thepurposeofthismoduleistoaddthewebviewsintheview_registry.
 *Thiscan'tbedonedirectlyinthemoduledefiningtheview_registryasit
 *wouldproducecyclicdependencies.
 */

varFormView=require('web.FormView');
varGraphView=require('web.GraphView');
varKanbanView=require('web.KanbanView');
varListView=require('web.ListView');
varPivotView=require('web.PivotView');
varCalendarView=require('web.CalendarView');
varview_registry=require('web.view_registry');

view_registry
    .add('form',FormView)
    .add('list',ListView)
    .add('kanban',KanbanView)
    .add('graph',GraphView)
    .add('pivot',PivotView)
    .add('calendar',CalendarView);

});
