flectra.define('web.public.Notification',function(require){
'usestrict';

varNotification=require('web.Notification');

Notification.include({
    xmlDependencies:['/web/static/src/xml/notification.xml'],
});
});
