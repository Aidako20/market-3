flectra.define('web.SessionStorageService',function(require){
'usestrict';

/**
 *ThismoduledefinesaservicetoaccessthesessionStorageobject.
 */

varAbstractStorageService=require('web.AbstractStorageService');
varcore=require('web.core');
varsessionStorage=require('web.sessionStorage');

varSessionStorageService=AbstractStorageService.extend({
    storage:sessionStorage,
});

core.serviceRegistry.add('session_storage',SessionStorageService);

returnSessionStorageService;

});
