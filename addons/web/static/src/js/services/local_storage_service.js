flectra.define('web.LocalStorageService',function(require){
'usestrict';

/**
 *ThismoduledefinesaservicetoaccessthelocalStorageobject.
 */

varAbstractStorageService=require('web.AbstractStorageService');
varcore=require('web.core');
varlocalStorage=require('web.local_storage');

varLocalStorageService=AbstractStorageService.extend({
    storage:localStorage,
});

core.serviceRegistry.add('local_storage',LocalStorageService);

returnLocalStorageService;

});
