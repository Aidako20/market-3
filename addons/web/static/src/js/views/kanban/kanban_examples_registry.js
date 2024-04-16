flectra.define('web.kanban_examples_registry',function(require){
"usestrict";

/**
 *Thisfileinstantiatesandexportsaregistry.Thepurposeofthisregistry
 *istostorestaticdatadisplayedinadialogtohelptheenduserto
 *configureitscolumnsinthegroupedKanbanview.
 *
 *ToactivatealinkontheColumnQuickCreatewidgetonopensuchadialog,the
 *attribute'examples'ontherootarchnodemustbesettoavalidkeyinthis
 *registry.
 *
 *EachvalueinthisregistrymustbeanarrayofObjectscontainingthe
 *followingkeys:
 *  -name(string)
 *  -columns(Array[string])
 *  -description(string,optional)BECAREFUL[*]
 *
 *[*]Thedescriptionisaddedwithat-rawsothetranslatedtextsmustbe
 *    properlyescaped.
 */

varRegistry=require('web.Registry');

returnnewRegistry();

});
